"""Candidate inventory checks. This module does not download or execute."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import chosen_files, reject_sensitive
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
)
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.schemas import repo_root, validate

_TEMPLATE = Path("candidates/templates/acquired-candidate-manifest-template.json")
_PROHIBITED = ("fp16", "q4", "quant")


class CandidateStagingError(ValueError):
    """A candidate inventory failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def digest_document(document: dict[str, Any]) -> dict[str, Any]:
    """Attach the identity digest and validate the candidate manifest."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    payload["identityDigest"] = sha256_text(canonical_dumps(payload))
    reject_sensitive(payload)
    validate("acquired-candidate-manifest", payload)
    return payload


def expected_candidate_files() -> list[dict[str, Any]]:
    """Return the eleven selected files and no quantized rows."""
    return [
        {
            "expectedBytes": item.listed_byte_count,
            "path": item.path,
            "role": item.role,
            "upstreamSha256": item.published_sha256,
        }
        for item in chosen_files()
    ]


def not_acquired_candidate_manifest() -> dict[str, Any]:
    """Build the committed empty candidate manifest."""
    return digest_document(
        {
            "acquisitionStatus": "not-acquired",
            "calibrationStatus": "not-approved",
            "conversionStatus": "not-performed",
            "executionFromQuarantine": "prohibited",
            "executionStatus": "not-executed",
            "expectedFiles": expected_candidate_files(),
            "installationAuthorized": False,
            "licenseName": "LFM Open License v1.0",
            "locallyObservedArtifactDigests": [],
            "manifestState": "not-acquired",
            "measurementPerformed": False,
            "modelId": LFM_MODEL_ID,
            "noticePresent": False,
            "observedFiles": [],
            "onnxRevision": LFM_ONNX_REVISION,
            "productionReady": False,
            "promotion": "rename-noreplace",
            "quantizationApproved": False,
            "realModelExecuted": False,
            "runtimeInstallationStatus": "not-installed",
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
            "sourceRevision": LFM_SOURCE_REVISION,
        }
    )


def load_candidate_manifest_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed template and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise CandidateStagingError("record-type")
    validate("acquired-candidate-manifest", loaded)
    if loaded != not_acquired_candidate_manifest():
        raise CandidateStagingError("record-drift")
    return loaded


def require_selected_path(relative: str) -> None:
    """Reject any path that is not one of the eleven selected files."""
    lowered = relative.casefold()
    if any(token in lowered for token in _PROHIBITED):
        raise CandidateStagingError("unexpected-file")
    if relative.endswith(".py") or relative.endswith(".so"):
        raise CandidateStagingError("remote-code")
    known = {item.path for item in chosen_files()}
    if relative not in known:
        raise CandidateStagingError("unexpected-file")


def compare_selected_file(relative: str, size: int, digest: str) -> str:
    """Return the upstream comparison for one selected file."""
    require_selected_path(relative)
    spec = next(item for item in chosen_files() if item.path == relative)
    if size != spec.listed_byte_count:
        raise CandidateStagingError("size-mismatch")
    if spec.published_sha256 is None:
        return "not-provided"
    if digest != spec.published_sha256:
        raise CandidateStagingError("digest-mismatch")
    return "matched"


def require_license_text(payload: bytes) -> None:
    """Accept the LFM Open License text."""
    if b"LFM Open License" not in payload:
        raise CandidateStagingError("license-mismatch")
