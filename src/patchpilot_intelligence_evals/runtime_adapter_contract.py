"""Closed runtime-adapter contract.

Safetensors is a source artifact for a future conversion. It is not an
executable ONNX Runtime model. The synthetic fixture tests protocol behavior
and is not a model artifact.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.schemas import repo_root, validate

_CONTRACT = Path("candidates/authorization/runtime-adapter-contract.json")
_FAILURES = (
    "conversion-attempt",
    "fallback-execution",
    "format-unavailable",
    "hardened-profile",
    "internal-harness-failure",
    "missing-external-data",
    "nonzero",
    "offline-required",
    "output-limit-exceeded",
    "protocol-malformed",
    "retrieval-attempt",
    "shell-rejected",
    "source-model-rejected",
    "telemetry-enabled",
    "timeout",
    "unexpected-external-data",
    "unverified-model",
    "unverified-runtime",
)
_GRAPH_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,80}\.onnx$")
_DATA_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,80}\.onnx_data$")
_ELF = b"\x7fELF"
_FORMAT_MESSAGE = "executable onnx artifact unavailable"
_PROFILE_ID = "linux-bwrap-systemd-v1"
_PROFILE_VERSION = "1.0.0"


class AdapterError(ValueError):
    """An adapter check failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_adapter_contract(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the closed adapter contract. It stores no filesystem path."""
    validate("runtime-adapter-contract", document)
    if tuple(document["failureCategories"]) != _FAILURES:
        raise AdapterError("failure-categories")
    if document["productionReady"] is not False or document["realModelExecuted"] is not False:
        raise AdapterError("production-ready")
    if document["runtimeInstalled"] is not False or document["installationAuthorized"] is not False:
        raise AdapterError("installation-authorized")
    if document["profileId"] != _PROFILE_ID or document["profileVersion"] != _PROFILE_VERSION:
        raise AdapterError("hardened-profile")
    source = document["sourceModel"]
    if source["format"] != "safetensors" or source["execution"] != "prohibited":
        raise AdapterError("source-model-rejected")
    executable = document["executableRuntimeModel"]
    if executable["format"] != "onnx" or executable["state"] != "unavailable":
        raise AdapterError("format-unavailable")
    if document["syntheticFixture"]["modelArtifact"] is not False:
        raise AdapterError("fallback-execution")
    if document["realCandidateOutcome"] != "format-unavailable":
        raise AdapterError("format-unavailable")
    if "approvedModelFormat" in document:
        raise AdapterError("source-model-rejected")
    text = json.dumps(document)
    if "/home/" in text or "/Users/" in text or "AWS_SECRET" in text:
        raise AdapterError("identity")
    return document


def load_adapter_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the committed adapter contract."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _CONTRACT).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AdapterError("contract-type")
    return validate_adapter_contract(loaded)


def execution_configuration(
    *,
    offline: bool = True,
    telemetry_disabled: bool = True,
    automatic_retrieval: bool = False,
    automatic_conversion: bool = False,
    fallback_execution: bool = False,
) -> dict[str, Any]:
    """Build the ephemeral execution flags. Paths stay out of this document."""
    document = {
        "offline": offline,
        "telemetryDisabled": telemetry_disabled,
        "automaticRetrieval": automatic_retrieval,
        "automaticConversion": automatic_conversion,
        "fallbackExecution": fallback_execution,
        "hardenedProfileId": _PROFILE_ID,
        "profileVersion": _PROFILE_VERSION,
    }
    require_execution(document)
    return document


def require_execution(execution: dict[str, Any]) -> None:
    """Reject an execution configuration that leaves the hardened contract."""
    if execution.get("hardenedProfileId") != _PROFILE_ID:
        raise AdapterError("hardened-profile")
    if execution.get("profileVersion") != _PROFILE_VERSION:
        raise AdapterError("hardened-profile")
    if execution.get("offline") is not True:
        raise AdapterError("offline-required")
    if execution.get("telemetryDisabled") is not True:
        raise AdapterError("telemetry-enabled")
    if execution.get("automaticRetrieval") is not False:
        raise AdapterError("retrieval-attempt")
    if execution.get("automaticConversion") is not False:
        raise AdapterError("conversion-attempt")
    if execution.get("fallbackExecution") is not False:
        raise AdapterError("fallback-execution")


def format_unavailable_response(request_id: str) -> dict[str, Any]:
    """Return the stable real-candidate response. No model is executed."""
    document = {
        "schemaVersion": "1.0.0",
        "protocolVersion": "1.0.0",
        "requestId": request_id,
        "candidateId": "fixture-format-unavailable",
        "candidateVersion": "1.0.0",
        "status": "unavailable",
        "failure": {"category": "unavailable", "message": _FORMAT_MESSAGE},
    }
    validate("candidate-response", document)
    return document


def require_executable_onnx(directory: Path, manifest: dict[str, Any]) -> None:
    """Reject every artifact that is not a verified ONNX graph plus its external data."""
    if _is_source_model(manifest):
        raise AdapterError("source-model-rejected")
    if (
        manifest.get("format") != "onnx"
        or manifest.get("artifactClass") != "executable-runtime-model"
    ):
        raise AdapterError("format-unavailable")
    if manifest.get("verificationState") != "verified":
        raise AdapterError("unverified-model")
    expected = _expected_onnx_files(manifest)
    if not directory.is_dir() or directory.is_symlink() or ".." in directory.parts:
        raise AdapterError("unverified-model")
    observed = _observed_names(directory)
    if any(name.endswith(".safetensors") for name in observed):
        raise AdapterError("source-model-rejected")
    if any(name.endswith(".onnx_data") and name not in expected for name in observed):
        raise AdapterError("unexpected-external-data")
    required = [name for name, item in expected.items() if item["role"] == "onnx-external-data"]
    if any(name not in observed for name in required):
        raise AdapterError("missing-external-data")
    if set(observed) != set(expected):
        raise AdapterError("unverified-model")
    for name, item in expected.items():
        _require_matching_file(directory / name, item)


def _is_source_model(manifest: dict[str, Any]) -> bool:
    if manifest.get("artifactClass") == "source-model":
        return True
    if manifest.get("format") == "safetensors" or manifest.get("approvedFormat") == "safetensors":
        return True
    files = manifest.get("files")
    expected = manifest.get("expectedFiles")
    names: list[str] = []
    if isinstance(files, list):
        names.extend(str(item.get("fileName", "")) for item in files if isinstance(item, dict))
    if isinstance(expected, list):
        names.extend(str(item.get("fileName", "")) for item in expected if isinstance(item, dict))
    return any(name.endswith(".safetensors") for name in names)


def _expected_onnx_files(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise AdapterError("unverified-model")
    expected: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict):
            raise AdapterError("unverified-model")
        name = str(item.get("fileName", ""))
        role = str(item.get("role", ""))
        if role == "onnx-graph" and _GRAPH_NAME.fullmatch(name):
            pass
        elif role == "onnx-external-data" and _DATA_NAME.fullmatch(name):
            pass
        else:
            raise AdapterError("unverified-model")
        if name in expected:
            raise AdapterError("unverified-model")
        expected[name] = item
    graphs = [name for name, item in expected.items() if item["role"] == "onnx-graph"]
    if len(graphs) != 1:
        raise AdapterError("unverified-model")
    declared = manifest.get("externalDataFiles")
    data_names = sorted(
        name for name, item in expected.items() if item["role"] == "onnx-external-data"
    )
    if not isinstance(declared, list) or sorted(str(name) for name in declared) != data_names:
        raise AdapterError("unverified-model")
    return expected


def _observed_names(directory: Path) -> list[str]:
    names: list[str] = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.is_symlink() or not path.is_file():
            raise AdapterError("unverified-model")
        names.append(path.name)
    return names


def _require_matching_file(path: Path, item: dict[str, Any]) -> None:
    if path.is_symlink() or not path.is_file():
        raise AdapterError("unverified-model")
    if path.stat().st_mode & 0o111:
        raise AdapterError("unverified-model")
    payload = path.read_bytes()
    if payload.startswith(_ELF):
        raise AdapterError("unverified-model")
    digest = hashlib.sha256(payload).hexdigest()
    if len(payload) != item.get("expectedBytes") or digest != item.get("sha256"):
        raise AdapterError("unverified-model")
