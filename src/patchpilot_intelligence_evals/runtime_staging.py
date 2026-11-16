"""Runtime inventory classification. This module does not download or execute."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.finalist_budget import (
    RUNTIME_LISTED_BYTES,
    RUNTIME_LISTED_SHA256,
    RUNTIME_PACKAGE,
    RUNTIME_REVISION,
    RUNTIME_TAG,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_TEMPLATE = Path("candidates/templates/acquired-runtime-manifest-template.json")
_LIBRARY = "libonnxruntime.so.1.31.1"
_NOTICE = "ThirdPartyNotices.txt"
_ELF = b"\x7fELF"
_MAX_LIBRARY = 134_217_728
_API_VERSION = re.compile(r"#define\s+ORT_API_VERSION\s+([0-9]+)")
_LOGGING = re.compile(r"ORT_LOGGING_LEVEL_ERROR\s*=\s*([0-9]+)")
_REQUIRED_API = (
    "CreateEnv",
    "CreateSession",
    "CreateSessionOptions",
    "DisableTelemetryEvents",
    "GetErrorMessage",
    "ReleaseEnv",
    "ReleaseSession",
    "ReleaseSessionOptions",
    "SessionGetInputCount",
    "SessionGetOutputCount",
)


class RuntimeStagingError(ValueError):
    """A runtime inventory failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def digest_document(document: dict[str, Any]) -> dict[str, Any]:
    """Attach the identity digest and validate the runtime manifest."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    payload["identityDigest"] = sha256_text(canonical_dumps(payload))
    reject_sensitive(payload)
    validate("acquired-runtime-manifest", payload)
    return payload


def not_acquired_runtime_manifest() -> dict[str, Any]:
    """Build the committed empty runtime manifest."""
    return digest_document(
        {
            "acquisitionStatus": "not-acquired",
            "archiveMembers": [],
            "calibrationStatus": "not-approved",
            "conversionStatus": "not-performed",
            "executionFromQuarantine": "prohibited",
            "executionStatus": "not-executed",
            "expectedArchive": {
                "expectedBytes": RUNTIME_LISTED_BYTES,
                "fileName": RUNTIME_PACKAGE,
                "upstreamSha256": RUNTIME_LISTED_SHA256,
            },
            "installationAuthorized": False,
            "licenseName": "MIT",
            "locallyObservedArtifactDigests": [],
            "manifestState": "not-acquired",
            "measurementPerformed": False,
            "noticePresent": False,
            "observedArchive": None,
            "productionReady": False,
            "promotion": "rename-noreplace",
            "promotionFiles": [],
            "quantizationApproved": False,
            "realModelExecuted": False,
            "runtimeId": "onnxruntime",
            "runtimeInstallationStatus": "not-installed",
            "runtimeRevision": RUNTIME_REVISION,
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
            "telemetry": "absent",
            "upstreamDigestComparison": "not-compared",
            "versionTag": RUNTIME_TAG,
        }
    )


def load_runtime_manifest_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed template and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeStagingError("record-type")
    validate("acquired-runtime-manifest", loaded)
    if loaded != not_acquired_runtime_manifest():
        raise RuntimeStagingError("record-drift")
    return loaded


def member_disposition(name: str, kind: str) -> str:
    """Classify one archive member. Unexpected regular libraries are rejected."""
    if name.startswith("/") or "\\" in name or "\x00" in name or ".." in name.split("/"):
        return "rejected"
    base = name.rsplit("/", 1)[-1]
    if kind in {"symlink", "directory"}:
        return "excluded"
    if kind != "regular":
        return "rejected"
    if base == _LIBRARY:
        return "promotion-library"
    if base == "libonnxruntime_providers_shared.so":
        return "excluded"
    if ".so" in base:
        return "rejected"
    if base == "LICENSE":
        return "promotion-license"
    if base == _NOTICE:
        return "promotion-notice"
    if base.endswith(".py"):
        return "rejected"
    return "excluded"


def ort_api_version(header: str) -> int:
    """Read ORT_API_VERSION from an official header."""
    match = _API_VERSION.search(header)
    if match is None:
        raise RuntimeStagingError("missing-file")
    value = int(match.group(1))
    if value < 1 or value > 100:
        raise RuntimeStagingError("version-mismatch")
    return value


def logging_level_error(header: str) -> int:
    """Read the error logging enumerator from an official header."""
    match = _LOGGING.search(header)
    if match is not None:
        return int(match.group(1))
    block = re.search(r"typedef\s+enum\s+OrtLoggingLevel\s*\{([^}]*)\}", header, re.DOTALL)
    if block is None:
        raise RuntimeStagingError("missing-file")
    value = 0
    code = "\n".join(
        re.split(r"\s*(?://|/\*)", line, maxsplit=1)[0] for line in block.group(1).splitlines()
    )
    for raw in code.split(","):
        token = raw.strip()
        if not token:
            continue
        name, separator, assigned = token.partition("=")
        if separator:
            value = int(assigned.strip())
        if name.strip() == "ORT_LOGGING_LEVEL_ERROR":
            return value
        value += 1
    raise RuntimeStagingError("missing-file")


def ort_api_indices(header: str) -> dict[str, int]:
    """Return function-pointer indexes from the OrtApi struct."""
    marker = "struct OrtApi {"
    start = header.find(marker)
    if start < 0:
        raise RuntimeStagingError("api-layout")
    stripped = re.sub(r"/\*.*?\*/|//.*?$", "", header[start:], flags=re.DOTALL | re.MULTILINE)
    depth = 0
    end = None
    for index, char in enumerate(stripped):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index
                break
    if end is None:
        raise RuntimeStagingError("api-layout")
    pattern = re.compile(
        r"ORT_API_CALL\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)"
        r"|ORT_API2_STATUS\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)"
        r"|ORT_CLASS_RELEASE\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)"
    )
    names: list[str] = []
    for match in pattern.finditer(stripped[:end]):
        direct, status, released = match.groups()
        if released is not None:
            names.append(f"Release{released}")
        else:
            names.append(str(direct or status))
    if len(names) != len(set(names)):
        raise RuntimeStagingError("api-layout")
    indexes = {name: index for index, name in enumerate(names)}
    if any(name not in indexes for name in _REQUIRED_API):
        raise RuntimeStagingError("api-layout")
    return indexes


def runtime_identity_bytes(api_version: int) -> bytes:
    """Build the local telemetry-disabled identity file."""
    document = {
        "ortApiVersion": api_version,
        "runtimeId": "onnxruntime",
        "telemetry": "disabled",
        "versionTag": RUNTIME_TAG,
    }
    return (json.dumps(document, sort_keys=True) + "\n").encode("utf-8")


def require_library(payload: bytes) -> None:
    """Accept one ELF shared library inside the published size cap."""
    if not payload.startswith(_ELF):
        raise RuntimeStagingError("unsupported-executable-format")
    if len(payload) > _MAX_LIBRARY:
        raise RuntimeStagingError("size-mismatch")


def require_license(payload: bytes) -> None:
    """Accept the MIT grant text."""
    if b"MIT" not in payload or b"Permission is hereby granted" not in payload:
        raise RuntimeStagingError("license-mismatch")


def require_notice(payload: bytes) -> None:
    """Accept a non-empty third-party notice."""
    if not payload.strip():
        raise RuntimeStagingError("missing-file")


def require_archive(payload: bytes) -> str:
    """Return the local digest when the archive matches the published identity."""
    if len(payload) != RUNTIME_LISTED_BYTES:
        raise RuntimeStagingError("size-mismatch")
    digest = sha256_text_bytes(payload)
    if digest != RUNTIME_LISTED_SHA256:
        raise RuntimeStagingError("digest-mismatch")
    return digest


def sha256_text_bytes(payload: bytes) -> str:
    """SHA-256 of raw bytes."""
    import hashlib

    return hashlib.sha256(payload).hexdigest()
