"""Hardened offline-load proof. It does not run the corpus or a long context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive, validate_external_root
from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.filesystem_policy import Mount, dependency_mounts
from patchpilot_intelligence_evals.hardened_execution import (
    ExecutionResult,
    HardenedExecutionError,
    execute_hardened,
    host_supports_boundary,
)
from patchpilot_intelligence_evals.resource_controls import ResourceLimits
from patchpilot_intelligence_evals.runtime_staging import (
    RuntimeStagingError,
    ort_api_indices,
    ort_api_version,
)
from patchpilot_intelligence_evals.runtime_staging import logging_level_error as ort_logging_level
from patchpilot_intelligence_evals.schemas import repo_root, validate

_TEMPLATE = Path("candidates/templates/hardened-load-attestation-template.json")
_FIXTURE = Path(__file__).with_name("offline_load_main.py")
_LIBRARY = "libonnxruntime.so.1.31.1"
LOAD_LIMITS = ResourceLimits(
    memory_max_bytes=MEMORY_CAP,
    tasks_max=32,
    cpu_seconds=600,
    address_space_bytes=MEMORY_CAP,
    file_size_bytes=67_108_864,
    open_files=256,
    wall_clock_seconds=900,
    stdout_bytes=8192,
    stderr_bytes=262_144,
)


class LoadProofError(ValueError):
    """The load proof failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def digest_document(document: dict[str, Any]) -> dict[str, Any]:
    """Attach the identity digest and validate an attestation."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    payload["identityDigest"] = sha256_text(canonical_dumps(payload))
    reject_sensitive(payload)
    validate("hardened-load-attestation", payload)
    return payload


def not_performed_attestation() -> dict[str, Any]:
    """Build the committed attestation. No load has been performed."""
    return digest_document(
        {
            "calibrationStatus": "not-approved",
            "corpusExecuted": False,
            "generationPerformed": False,
            "inferencePerformed": False,
            "inputCount": None,
            "installationAuthorized": False,
            "loadStatus": "not-performed",
            "longContextMeasurement": False,
            "measurementPerformed": False,
            "memoryCeilingBytes": MEMORY_CAP,
            "networkDenial": "not-performed",
            "observedResidentBytes": None,
            "outputCount": None,
            "processCleanup": "not-performed",
            "productionReady": False,
            "profileId": "linux-bwrap-systemd-v1",
            "profileVersion": "1.0.0",
            "quantizationApproved": False,
            "realModelExecuted": False,
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
            "tokenizerInitialized": False,
        }
    )


def load_attestation_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed template and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise LoadProofError("record-type")
    validate("hardened-load-attestation", loaded)
    if loaded != not_performed_attestation():
        raise LoadProofError("record-drift")
    return loaded


def proof_is_generation_free() -> bool:
    """True when the child source does not call session Run or the corpus."""
    text = _FIXTURE.read_text(encoding="utf-8")
    banned = ("Run(", "tokenizers", "import onnxruntime", "corpus/cases")
    return all(token not in text for token in banned) and "inferencePerformed" in text


def proof_arguments(header: str) -> tuple[str, ...]:
    """Build the child argument vector from a real header. Run is not passed."""
    try:
        indexes = ort_api_indices(header)
        version = ort_api_version(header)
        level = ort_logging_level(header)
    except RuntimeStagingError as exc:
        raise LoadProofError(exc.code) from exc
    mapping = {
        "api_version": version,
        "create_env": indexes["CreateEnv"],
        "create_session": indexes["CreateSession"],
        "create_session_options": indexes["CreateSessionOptions"],
        "disable_telemetry": indexes["DisableTelemetryEvents"],
        "get_error_message": indexes["GetErrorMessage"],
        "input_count": indexes["SessionGetInputCount"],
        "logging_level": level,
        "output_count": indexes["SessionGetOutputCount"],
        "release_env": indexes["ReleaseEnv"],
        "release_session": indexes["ReleaseSession"],
        "release_session_options": indexes["ReleaseSessionOptions"],
    }
    if "Run" in mapping:
        raise LoadProofError("generation")
    return tuple(f"{name}={value}" for name, value in sorted(mapping.items()))


def attestation_from_result(result: ExecutionResult) -> dict[str, Any]:
    """Convert one launcher result into an attestation. Inference stays false."""
    if not proof_is_generation_free():
        raise LoadProofError("generation")
    if "--unshare-net" not in result.argv:
        network = "failed"
    else:
        network = "denied"
    cleanup = "reaped" if result.cleanup == "reaped" else "failed"
    report = _report(result.report)
    if report.get("inferencePerformed") is not False or report.get("generationTokens") not in {
        0,
        None,
    }:
        raise LoadProofError("generation")
    if report.get("corpusExecuted") is not False:
        raise LoadProofError("corpus")
    resident = report.get("residentBytes")
    if isinstance(resident, int) and resident > MEMORY_CAP:
        raise LoadProofError("memory-ceiling")
    loaded = report.get("loadStatus") == "loaded" and result.exit_classification == "success"
    denial = network
    if isinstance(report.get("network"), dict):
        observed = report["network"]
        if observed.get("ipv4") == "reached" or observed.get("dns") == "reached":
            denial = "failed"
    return digest_document(
        {
            "calibrationStatus": "not-approved",
            "corpusExecuted": False,
            "generationPerformed": False,
            "inferencePerformed": False,
            "inputCount": report.get("inputCount") if loaded else None,
            "installationAuthorized": False,
            "loadStatus": "loaded"
            if loaded and denial == "denied" and cleanup == "reaped"
            else "failed",
            "longContextMeasurement": False,
            "measurementPerformed": False,
            "memoryCeilingBytes": MEMORY_CAP,
            "networkDenial": denial,
            "observedResidentBytes": resident if isinstance(resident, int) else None,
            "outputCount": report.get("outputCount") if loaded else None,
            "processCleanup": cleanup,
            "productionReady": False,
            "profileId": "linux-bwrap-systemd-v1",
            "profileVersion": "1.0.0",
            "quantizationApproved": False,
            "realModelExecuted": False,
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
            "tokenizerInitialized": bool(report.get("tokenizerInitialized")) and loaded,
        }
    )


def launch_offline_load(
    runtime_root: Path,
    model_root: Path,
    header: str,
    *,
    repository: Path | None = None,
) -> dict[str, Any]:
    """Run one hardened load. Missing boundary support fails closed."""
    if not proof_is_generation_free():
        raise LoadProofError("generation")
    if not host_supports_boundary():
        raise LoadProofError("unsupported-capability")
    runtime = validate_external_root(runtime_root, repository=repository)
    model = validate_external_root(model_root, repository=repository)
    library = _verified_library(runtime)
    arguments = proof_arguments(header)
    mounts = (
        Mount(str(library.parent), "/verified-runtime", True),
        Mount(str(_verified_model(model)), "/verified-model", True),
        *dependency_mounts(library),
    )
    try:
        result = execute_hardened(
            _FIXTURE,
            arguments,
            limits=LOAD_LIMITS,
            environment=(("ORT_DISABLE_TELEMETRY", "1"),),
            extra_mounts=mounts,
        )
    except HardenedExecutionError as exc:
        raise LoadProofError(exc.code) from exc
    return attestation_from_result(result)


def _verified_library(root: Path) -> Path:
    matches = [
        path
        for path in (root / "verified").rglob(_LIBRARY)
        if path.is_file() and not path.is_symlink()
    ]
    if len(matches) != 1:
        raise LoadProofError("unverified-runtime")
    return matches[0]


def _verified_model(root: Path) -> Path:
    matches = [
        path.parent.parent
        for path in (root / "verified").rglob("model.onnx")
        if path.parent.name == "onnx" and path.is_file() and not path.is_symlink()
    ]
    if len(matches) != 1:
        raise LoadProofError("unverified-model")
    return matches[0]


def _report(payload: bytes) -> dict[str, Any]:
    if not payload:
        return {}
    try:
        loaded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LoadProofError("protocol-malformed") from exc
    if not isinstance(loaded, dict):
        raise LoadProofError("protocol-malformed")
    return loaded
