"""Synthetic runtime inventory checks.

SHA-256, size, role, and file-name checks apply to caller-supplied bytes.
Executable sniffing looks for ELF magic and permission bits only. It is not
malware detection and it is not a claim of binary safety.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.schemas import repo_root, validate

_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,120}$")
_ELF = b"\x7fELF"
_MAX_BYTES = 134217728
_LIBRARY = "libonnxruntime.so.1.31.1"
_ROLE_NAMES = {
    "shared-library": _LIBRARY,
    "license": "LICENSE",
    "notice": "ThirdPartyNotices.txt",
    "configuration": "runtime-identity.json",
    "adapter": "adapter-marker.json",
}
_REQUIRED_ROLES = ("shared-library", "license", "notice", "configuration")
_METADATA_NAMES = frozenset({"rejection.json", "verification.json"})
_REASON_PRIORITY = (
    "path-traversal",
    "symlink-escape",
    "unexpected-file",
    "missing-file",
    "count-mismatch",
    "unsupported-executable-format",
    "unapproved-shared-library",
    "writable-artifact",
    "size-mismatch",
    "digest-mismatch",
    "license-mismatch",
    "version-mismatch",
    "runtime-identity",
    "telemetry-enabled",
    "identity-changed",
)
_TEMPLATE = Path("candidates/templates/runtime-artifact-verification-template.json")
_IDENTITY = {
    "runtimeId": "onnxruntime",
    "versionTag": "v1.31.1",
    "immutableRevision": "6af1a932e2286d5c58166085d24c68783033edee",
    "distributionId": "onnxruntime-linux-x64-cpu",
    "packageFileName": "onnxruntime-linux-x64-1.31.1.tgz",
    "licenseName": "MIT",
}


class RuntimeVerificationError(ValueError):
    """A runtime inventory failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def identity_digest(document: dict[str, Any]) -> str:
    """SHA-256 of the canonical verification record without its digest field."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    return sha256_text(canonical_dumps(payload))


def seal_verification(document: dict[str, Any]) -> dict[str, Any]:
    """Return a copy whose identity digest matches the other fields."""
    sealed = dict(document)
    sealed.pop("identityDigest", None)
    sealed["identityDigest"] = identity_digest(sealed)
    return validate_verification(sealed)


def validate_verification(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one runtime verification manifest and its identity digest."""
    validate("runtime-artifact-verification", document)
    if document["identityDigest"] != identity_digest(document):
        raise RuntimeVerificationError("identity-digest")
    if document["malwareDetectionClaimed"] is not False:
        raise RuntimeVerificationError("malware-claim")
    if document["runtimeInstalled"] is not False:
        raise RuntimeVerificationError("runtime-installed")
    if document["installationAuthorized"] is not False:
        raise RuntimeVerificationError("installation-authorized")
    _reject_identity(document)
    return document


def load_verification_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed not-staged runtime verification template."""
    base = root if root is not None else repo_root()
    return load_verification_manifest(_TEMPLATE.as_posix(), root=base)


def load_verification_manifest(relative_path: str, root: Path | None = None) -> dict[str, Any]:
    """Load one repository-relative runtime verification manifest."""
    from patchpilot_intelligence_evals.network_guard import BoundaryError, assert_inside_repository

    base = root if root is not None else repo_root()
    try:
        assert_inside_repository(relative_path, base)
    except BoundaryError as exc:
        raise RuntimeVerificationError("path-traversal") from exc
    file_path = base.joinpath(*Path(relative_path).parts)
    if file_path.is_symlink() or not file_path.is_file():
        raise RuntimeVerificationError("missing-manifest")
    loaded = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeVerificationError("manifest-type")
    return validate_verification(loaded)


def not_staged_verification() -> dict[str, Any]:
    """Build the empty pre-staging verification record."""
    return seal_verification(
        {
            "schemaVersion": "1.0.0",
            "productionReady": False,
            "runtimeInstalled": False,
            "modelAcquired": False,
            "realModelExecuted": False,
            "installationAuthorized": False,
            "verificationState": "not-staged",
            "attemptId": None,
            "acquisitionStatus": "not-acquired",
            "executionStatus": "not-executed",
            "conversionStatus": "not-performed",
            **_IDENTITY,
            "telemetryConfiguration": "absent",
            "expectedFiles": [],
            "observedFiles": [],
            "locallyObservedArtifactDigests": [],
            "upstreamDigestComparison": "not-applicable",
            "malwareDetectionClaimed": False,
            "reasonCodes": [],
        }
    )


def inspect_runtime(
    directory: Path,
    expected: list[dict[str, Any]],
    *,
    attempt_id: str,
) -> dict[str, Any]:
    """Compare one directory with an expected runtime inventory. This does not execute it."""
    normalized = _normalize_expected(expected)
    reasons: list[str] = []
    observed: list[dict[str, Any]] = []
    telemetry = "absent"
    roles = {str(item["role"]) for item in normalized}
    for role in _REQUIRED_ROLES:
        if role not in roles:
            reasons.append("missing-file")
    if ".." in directory.parts:
        reasons.append("path-traversal")
    elif not directory.is_dir() or directory.is_symlink():
        reasons.append("missing-file")
        if directory.is_symlink():
            reasons.append("symlink-escape")
    else:
        observed, telemetry, walk_reasons = _walk(directory, normalized)
        reasons.extend(walk_reasons)
    comparison = _comparison(normalized, observed)
    if comparison == "mismatch":
        reasons.append("digest-mismatch")
    if telemetry != "disabled":
        reasons.append("telemetry-enabled")
    ordered = _order_reasons(reasons)
    state = "rejected" if ordered else "verified"
    digests = [str(item["sha256"]) for item in observed] if state == "verified" else []
    return seal_verification(
        {
            "schemaVersion": "1.0.0",
            "productionReady": False,
            "runtimeInstalled": False,
            "modelAcquired": False,
            "realModelExecuted": False,
            "installationAuthorized": False,
            "verificationState": state,
            "attemptId": attempt_id,
            "acquisitionStatus": "not-acquired",
            "executionStatus": "not-executed",
            "conversionStatus": "not-performed",
            **_IDENTITY,
            "telemetryConfiguration": telemetry
            if state == "verified"
            else _rejected_telemetry(telemetry),
            "expectedFiles": normalized,
            "observedFiles": observed,
            "locallyObservedArtifactDigests": digests,
            "upstreamDigestComparison": comparison
            if state == "verified"
            else _rejected_comparison(comparison),
            "malwareDetectionClaimed": False,
            "reasonCodes": ordered,
        }
    )


def assert_verified_runtime_identity(directory: Path, manifest: dict[str, Any]) -> None:
    """Re-read verified runtime bytes and reject any changed identity."""
    if manifest.get("verificationState") != "verified":
        raise RuntimeVerificationError("not-verified")
    attempt_id = manifest.get("attemptId")
    if not isinstance(attempt_id, str):
        raise RuntimeVerificationError("not-verified")
    expected = manifest.get("expectedFiles")
    if not isinstance(expected, list):
        raise RuntimeVerificationError("not-verified")
    refreshed = inspect_runtime(directory, expected, attempt_id=attempt_id)
    if refreshed["identityDigest"] != manifest["identityDigest"]:
        raise RuntimeVerificationError("identity-changed")
    if refreshed["observedFiles"] != manifest["observedFiles"]:
        raise RuntimeVerificationError("identity-changed")


def _normalize_expected(expected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in expected:
        name = str(item["fileName"])
        role = str(item["role"])
        if not _NAME.fullmatch(name) or ".." in Path(name).parts or "/" in name:
            raise RuntimeVerificationError("unexpected-file")
        required_name = _ROLE_NAMES.get(role)
        if required_name is not None and name != required_name:
            raise RuntimeVerificationError("unexpected-file")
        if role == "executable":
            raise RuntimeVerificationError("unapproved-shared-library")
        executable_format = str(item["executableFormat"])
        if role == "shared-library" and executable_format != "elf":
            raise RuntimeVerificationError("unsupported-executable-format")
        if role != "shared-library" and executable_format != "not-executable":
            raise RuntimeVerificationError("unsupported-executable-format")
        upstream = item["upstreamSha256"]
        if upstream is not None and not isinstance(upstream, str):
            raise RuntimeVerificationError("digest-mismatch")
        normalized.append(
            {
                "fileName": name,
                "role": role,
                "expectedBytes": int(item["expectedBytes"]),
                "upstreamSha256": upstream,
                "executableFormat": executable_format,
            }
        )
    normalized.sort(key=lambda item: str(item["fileName"]))
    names = [str(item["fileName"]) for item in normalized]
    if len(names) != len(set(names)):
        raise RuntimeVerificationError("unexpected-file")
    return normalized


def _walk(
    directory: Path,
    expected: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str, list[str]]:
    reasons: list[str] = []
    observed: list[dict[str, Any]] = []
    telemetry = "absent"
    expected_by_name = {str(item["fileName"]): item for item in expected}
    seen: set[str] = set()
    entries = sorted(directory.iterdir(), key=lambda path: path.name)
    if len(entries) > 32:
        reasons.append("count-mismatch")
    for entry in entries:
        name = entry.name
        if name in _METADATA_NAMES:
            reasons.append("unexpected-file")
            continue
        if entry.is_symlink():
            reasons.append("symlink-escape")
            continue
        if entry.is_dir() or not entry.is_file():
            reasons.append("unexpected-file")
            continue
        if not _NAME.fullmatch(name):
            reasons.append("unexpected-file")
            continue
        if _unapproved_library_name(name):
            reasons.append("unapproved-shared-library")
        if name not in expected_by_name:
            reasons.append("unexpected-file")
            continue
        size = entry.stat().st_size
        if size > _MAX_BYTES:
            reasons.append("size-mismatch")
            continue
        if entry.stat().st_mode & 0o222:
            reasons.append("writable-artifact")
        data = entry.read_bytes()
        seen.add(name)
        spec = expected_by_name[name]
        observed_format = "elf" if data.startswith(_ELF) else "not-executable"
        digest = hashlib.sha256(data).hexdigest()
        observed.append(
            {
                "fileName": name,
                "role": spec["role"],
                "observedBytes": len(data),
                "sha256": digest,
                "executableFormat": observed_format,
            }
        )
        if int(spec["expectedBytes"]) != len(data):
            reasons.append("size-mismatch")
        upstream = spec["upstreamSha256"]
        if isinstance(upstream, str) and upstream != digest:
            if spec["role"] == "license":
                reasons.append("license-mismatch")
            else:
                reasons.append("digest-mismatch")
        reasons.extend(_format_reasons(str(spec["role"]), observed_format, entry))
        if spec["role"] == "configuration":
            telemetry = _read_identity(data, reasons)
    for name in expected_by_name:
        if name not in seen:
            reasons.append("missing-file")
    regular = [
        entry
        for entry in directory.iterdir()
        if entry.is_file() and not entry.is_symlink() and entry.name not in _METADATA_NAMES
    ]
    if len(regular) != len(expected):
        reasons.append("count-mismatch")
    observed.sort(key=lambda item: str(item["fileName"]))
    return observed, telemetry, reasons


def _format_reasons(role: str, observed_format: str, path: Path) -> list[str]:
    reasons: list[str] = []
    executable_bit = bool(path.stat().st_mode & 0o111)
    if role == "shared-library":
        if observed_format != "elf":
            reasons.append("unsupported-executable-format")
        return reasons
    if observed_format == "elf" or executable_bit:
        reasons.append("unsupported-executable-format")
    return reasons


def _read_identity(data: bytes, reasons: list[str]) -> str:
    try:
        loaded = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        reasons.append("telemetry-enabled")
        return "enabled"
    if not isinstance(loaded, dict):
        reasons.append("telemetry-enabled")
        return "enabled"
    if loaded.get("runtimeId") != "onnxruntime":
        reasons.append("runtime-identity")
    if loaded.get("versionTag") != "v1.31.1":
        reasons.append("version-mismatch")
    telemetry = loaded.get("telemetry")
    if telemetry != "disabled":
        reasons.append("telemetry-enabled")
        return "enabled" if telemetry == "enabled" else "absent"
    return "disabled"


def _unapproved_library_name(name: str) -> bool:
    if name == _LIBRARY:
        return False
    return name.endswith(".so") or ".so." in name


def _comparison(expected: list[dict[str, Any]], observed: list[dict[str, Any]]) -> str:
    provided = [item for item in expected if item["upstreamSha256"] is not None]
    if not provided:
        return "not-provided"
    observed_by_name = {str(item["fileName"]): str(item["sha256"]) for item in observed}
    matched = all(
        observed_by_name.get(str(item["fileName"])) == item["upstreamSha256"] for item in provided
    )
    return "matched" if matched else "mismatch"


def _rejected_comparison(comparison: str) -> str:
    if comparison in {"matched", "mismatch"}:
        return comparison
    return "not-provided"


def _rejected_telemetry(telemetry: str) -> str:
    if telemetry == "disabled":
        return "disabled"
    if telemetry == "enabled":
        return "enabled"
    return "absent"


def _order_reasons(reasons: list[str]) -> list[str]:
    present = set(reasons)
    return [code for code in _REASON_PRIORITY if code in present]


def _reject_identity(document: dict[str, Any]) -> None:
    text = json.dumps(document)
    if "/home/" in text or "/Users/" in text or "AWS_SECRET" in text or "PRIVATE KEY" in text:
        raise RuntimeVerificationError("identity")
