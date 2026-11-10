"""Synthetic artifact inventory checks.

SHA-256, size, and file-name checks apply to caller-supplied bytes. Executable
sniffing looks for permission bits, a shebang, or ELF magic only. It is not
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

_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,120}\.safetensors$")
_ELF = b"\x7fELF"
_METADATA_NAMES = frozenset({"rejection.json", "verification.json"})
_REASON_PRIORITY = (
    "path-traversal",
    "symlink-escape",
    "remote-code",
    "unsupported-format",
    "unexpected-file",
    "missing-file",
    "count-mismatch",
    "executable-content",
    "size-mismatch",
    "digest-mismatch",
    "missing-provenance",
    "identity-changed",
)
_TEMPLATE = Path("candidates/templates/model-artifact-verification-template.json")


class VerificationError(ValueError):
    """An artifact inventory failed a closed check. The message is a code."""

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
    """Validate one verification manifest and its identity digest."""
    validate("model-artifact-verification", document)
    if document["identityDigest"] != identity_digest(document):
        raise VerificationError("identity-digest")
    if document["malwareDetectionClaimed"] is not False:
        raise VerificationError("malware-claim")
    if document["acquisitionStatus"] != "not-acquired":
        raise VerificationError("acquisition-status")
    if document["executionStatus"] != "not-executed":
        raise VerificationError("execution-status")
    return document


def load_verification_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed not-acquired verification template."""
    base = root if root is not None else repo_root()
    return load_verification_manifest(_TEMPLATE.as_posix(), root=base)


def load_verification_manifest(relative_path: str, root: Path | None = None) -> dict[str, Any]:
    """Load one repository-relative verification manifest."""
    from patchpilot_intelligence_evals.network_guard import BoundaryError, assert_inside_repository

    base = root if root is not None else repo_root()
    try:
        assert_inside_repository(relative_path, base)
    except BoundaryError as exc:
        raise VerificationError("path-traversal") from exc
    file_path = base.joinpath(*Path(relative_path).parts)
    if file_path.is_symlink() or not file_path.is_file():
        raise VerificationError("missing-manifest")
    loaded = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise VerificationError("manifest-type")
    return validate_verification(loaded)


def not_acquired_verification() -> dict[str, Any]:
    """Build the empty pre-acquisition verification record."""
    return seal_verification(
        {
            "schemaVersion": "1.0.0",
            "productionReady": False,
            "verificationState": "not-acquired",
            "attemptId": None,
            "acquisitionStatus": "not-acquired",
            "executionStatus": "not-executed",
            "expectedFiles": [],
            "observedFiles": [],
            "locallyObservedArtifactDigests": [],
            "upstreamDigestComparison": "not-applicable",
            "approvedFormat": "safetensors",
            "remoteCodeRequired": False,
            "executableContentDetected": False,
            "tokenizerProvenanceRecorded": False,
            "licenseReferenceRecorded": False,
            "malwareDetectionClaimed": False,
            "reasonCodes": [],
        }
    )


def inspect_attempt(
    directory: Path,
    expected: list[dict[str, Any]],
    *,
    attempt_id: str,
    remote_code_required: bool = False,
    tokenizer_provenance_recorded: bool = False,
    license_reference_recorded: bool = False,
) -> dict[str, Any]:
    """Compare one directory with an expected inventory. This does not execute it."""
    normalized = _normalize_expected(expected)
    reasons: list[str] = []
    observed: list[dict[str, Any]] = []
    executable = False
    if not normalized:
        reasons.append("missing-file")
    if remote_code_required:
        reasons.append("remote-code")
    if not tokenizer_provenance_recorded or not license_reference_recorded:
        reasons.append("missing-provenance")
    if ".." in directory.parts:
        reasons.append("path-traversal")
    elif not directory.is_dir() or directory.is_symlink():
        reasons.append("missing-file")
        if directory.is_symlink():
            reasons.append("symlink-escape")
    else:
        executable, observed, walk_reasons = _walk(directory, normalized)
        reasons.extend(walk_reasons)
    comparison = _comparison(normalized, observed)
    if comparison == "mismatch":
        reasons.append("digest-mismatch")
    ordered = _order_reasons(reasons)
    state = "rejected" if ordered else "verified"
    if state == "verified" and comparison == "mismatch":
        state = "rejected"
    digests = [str(item["sha256"]) for item in observed] if state == "verified" else []
    return seal_verification(
        {
            "schemaVersion": "1.0.0",
            "productionReady": False,
            "verificationState": state,
            "attemptId": attempt_id,
            "acquisitionStatus": "not-acquired",
            "executionStatus": "not-executed",
            "expectedFiles": normalized,
            "observedFiles": observed,
            "locallyObservedArtifactDigests": digests,
            "upstreamDigestComparison": comparison
            if state == "verified"
            else _rejected_comparison(comparison),
            "approvedFormat": "safetensors",
            "remoteCodeRequired": remote_code_required,
            "executableContentDetected": executable,
            "tokenizerProvenanceRecorded": tokenizer_provenance_recorded,
            "licenseReferenceRecorded": license_reference_recorded,
            "malwareDetectionClaimed": False,
            "reasonCodes": ordered,
        }
    )


def assert_verified_identity(directory: Path, manifest: dict[str, Any]) -> None:
    """Re-read verified bytes and reject any changed identity."""
    if manifest.get("verificationState") != "verified":
        raise VerificationError("not-verified")
    attempt_id = manifest.get("attemptId")
    if not isinstance(attempt_id, str):
        raise VerificationError("not-verified")
    expected = manifest.get("expectedFiles")
    if not isinstance(expected, list):
        raise VerificationError("not-verified")
    refreshed = inspect_attempt(
        directory,
        expected,
        attempt_id=attempt_id,
        remote_code_required=False,
        tokenizer_provenance_recorded=True,
        license_reference_recorded=True,
    )
    if refreshed["identityDigest"] != manifest["identityDigest"]:
        raise VerificationError("identity-changed")
    if refreshed["observedFiles"] != manifest["observedFiles"]:
        raise VerificationError("identity-changed")


def _normalize_expected(expected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in expected:
        name = str(item["fileName"])
        if not _NAME.fullmatch(name) or ".." in Path(name).parts:
            raise VerificationError("unsupported-format")
        upstream = item["upstreamSha256"]
        if upstream is not None and not isinstance(upstream, str):
            raise VerificationError("digest-mismatch")
        normalized.append(
            {
                "fileName": name,
                "expectedBytes": int(item["expectedBytes"]),
                "upstreamSha256": upstream,
            }
        )
    normalized.sort(key=lambda item: str(item["fileName"]))
    names = [str(item["fileName"]) for item in normalized]
    if len(names) != len(set(names)):
        raise VerificationError("unexpected-file")
    return normalized


def _walk(
    directory: Path,
    expected: list[dict[str, Any]],
) -> tuple[bool, list[dict[str, Any]], list[str]]:
    reasons: list[str] = []
    observed: list[dict[str, Any]] = []
    executable = False
    expected_by_name = {str(item["fileName"]): item for item in expected}
    seen: set[str] = set()
    for entry in sorted(directory.iterdir(), key=lambda path: path.name):
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
            reasons.append("unsupported-format")
            continue
        if name not in expected_by_name:
            reasons.append("unexpected-file")
            continue
        data = entry.read_bytes()
        seen.add(name)
        digest = hashlib.sha256(data).hexdigest()
        observed.append({"fileName": name, "observedBytes": len(data), "sha256": digest})
        spec = expected_by_name[name]
        if int(spec["expectedBytes"]) != len(data):
            reasons.append("size-mismatch")
        upstream = spec["upstreamSha256"]
        if isinstance(upstream, str) and upstream != digest:
            reasons.append("digest-mismatch")
        if _executable(entry, data):
            reasons.append("executable-content")
            executable = True
    for name in expected_by_name:
        if name not in seen:
            reasons.append("missing-file")
    regular = [entry for entry in directory.iterdir() if entry.is_file() and not entry.is_symlink()]
    if len(regular) != len(expected):
        reasons.append("count-mismatch")
    observed.sort(key=lambda item: str(item["fileName"]))
    return executable, observed, reasons


def _executable(path: Path, data: bytes) -> bool:
    if path.stat().st_mode & 0o111:
        return True
    return data.startswith(b"#!") or data.startswith(_ELF)


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
    if comparison == "matched":
        return "matched"
    if comparison == "mismatch":
        return "mismatch"
    return "not-provided"


def _order_reasons(reasons: list[str]) -> list[str]:
    present = set(reasons)
    return [code for code in _REASON_PRIORITY if code in present]
