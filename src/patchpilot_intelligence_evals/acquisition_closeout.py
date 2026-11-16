"""Closeout records. Cleanup stays inside the supplied cache root."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.cache_cleanup import CleanupError, cleanup_attempt
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.schemas import repo_root, validate

_TEMPLATE = Path("candidates/templates/acquisition-closeout-template.json")


class CloseoutError(ValueError):
    """Closeout failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def digest_document(document: dict[str, Any]) -> dict[str, Any]:
    """Attach the identity digest and validate a closeout record."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    payload["identityDigest"] = sha256_text(canonical_dumps(payload))
    reject_sensitive(payload)
    validate("acquisition-closeout", payload)
    return payload


def not_closed_closeout() -> dict[str, Any]:
    """Build the committed closeout template."""
    return digest_document(
        {
            "acquisitionStatus": "not-acquired",
            "attempts": [],
            "calibrationStatus": "not-approved",
            "closeoutState": "not-closed",
            "conversionStatus": "not-performed",
            "executionStatus": "not-executed",
            "gitTrackedArtifact": False,
            "installationAuthorized": False,
            "measurementPerformed": False,
            "operatorApproval": "required",
            "productionReady": False,
            "promotedIdentities": [],
            "quantizationApproved": False,
            "realModelExecuted": False,
            "runtimeInstallationStatus": "not-installed",
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
            "storageReclaimedBytes": 0,
        }
    )


def load_closeout_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed template and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise CloseoutError("record-type")
    validate("acquisition-closeout", loaded)
    if loaded != not_closed_closeout():
        raise CloseoutError("record-drift")
    return loaded


def build_closeout(
    attempts: list[dict[str, str]],
    *,
    promoted: list[str],
    reclaimed_bytes: int,
    approval: str,
) -> dict[str, Any]:
    """Build a closed record from reason codes. Paths are not stored."""
    acquired = "acquired" if promoted else "not-acquired"
    if any(item["outcome"] == "rejected" for item in attempts) and not promoted:
        acquired = "rejected"
    return digest_document(
        {
            "acquisitionStatus": acquired,
            "attempts": attempts,
            "calibrationStatus": "not-approved",
            "closeoutState": "closed",
            "conversionStatus": "not-performed",
            "executionStatus": "not-executed",
            "gitTrackedArtifact": False,
            "installationAuthorized": False,
            "measurementPerformed": False,
            "operatorApproval": approval,
            "productionReady": False,
            "promotedIdentities": promoted,
            "quantizationApproved": False,
            "realModelExecuted": False,
            "runtimeInstallationStatus": "not-installed",
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
            "storageReclaimedBytes": reclaimed_bytes,
        }
    )


def cleanup_incomplete(cache: Path, attempt_id: str, *, repository: Path | None = None) -> int:
    """Delete one quarantine attempt and return reclaimed bytes. A second call is clean."""
    try:
        result = cleanup_attempt(cache, attempt_id, state="quarantine", repository=repository)
    except CleanupError as exc:
        raise CloseoutError(exc.code) from exc
    reclaimed = result.get("reclaimedBytes")
    if not isinstance(reclaimed, int):
        raise CloseoutError("partial-cleanup")
    return reclaimed
