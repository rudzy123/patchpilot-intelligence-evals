"""Seal and promote a populated quarantine attempt without copying bytes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.atomic_promotion import (
    PromotionError,
    close_populated_attempt,
    promote_sealed_attempt,
    seal_closed_attempt,
)
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.filesystem_identity import IdentityError, rename_noreplace
from patchpilot_intelligence_evals.schemas import repo_root, validate

_SOURCE = Path(__file__).read_text(encoding="utf-8")


class ArtifactValidationError(ValueError):
    """Promotion coordination failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def promotion_is_atomic() -> bool:
    """True when this module delegates to rename and does not copy bytes."""
    banned = ("sh" + "util", "copy" + "file(", "copy" + "2(")
    if any(token in _SOURCE for token in banned):
        return False
    return "promote_sealed_attempt" in _SOURCE and "rename_noreplace" in _SOURCE


def promote_closed_attempt(
    cache: Path,
    attempt_id: str,
    expected: list[dict[str, Any]],
    *,
    repository: Path | None = None,
) -> dict[str, Any]:
    """Seal a closed attempt and rename it into the verified root."""
    if not promotion_is_atomic():
        raise ArtifactValidationError("copy-fallback")
    try:
        seal = seal_closed_attempt(
            cache,
            attempt_id,
            expected,
            repository=repository,
        )
        receipt = promote_sealed_attempt(cache, attempt_id, repository=repository)
    except PromotionError as exc:
        raise ArtifactValidationError(exc.code) from exc
    if receipt.get("copyFallbackUsed") is not False:
        raise ArtifactValidationError("copy-fallback")
    return {"receipt": receipt, "seal": seal}


def close_and_promote(
    cache: Path,
    attempt_id: str,
    expected: list[dict[str, Any]],
    *,
    repository: Path | None = None,
) -> dict[str, Any]:
    """Close a populated directory, then seal and promote it."""
    try:
        close_populated_attempt(cache, attempt_id, repository=repository)
    except PromotionError as exc:
        raise ArtifactValidationError(exc.code) from exc
    return promote_closed_attempt(cache, attempt_id, expected, repository=repository)


def reject_attempt(cache: Path, attempt_id: str, reason: str) -> None:
    """Move one quarantine attempt to rejected and keep a reason record."""
    source = cache / "quarantine" / attempt_id
    if source.is_symlink() or not source.is_dir():
        raise ArtifactValidationError("missing-quarantine")
    parent = cache / "rejected"
    if parent.is_symlink():
        raise ArtifactValidationError("symlink")
    parent.mkdir(exist_ok=True)
    destination = parent / attempt_id
    if destination.exists() or destination.is_symlink():
        raise ArtifactValidationError("destination-collision")
    record = {
        "execution": "prohibited",
        "reason": reason,
    }
    validate_reason(record)
    (source / "rejection.json").write_text(json.dumps(record) + "\n", encoding="utf-8")
    try:
        rename_noreplace(source, destination)
    except IdentityError as exc:
        raise ArtifactValidationError(exc.code) from exc


def not_acquired_digests() -> dict[str, Any]:
    """Build the committed empty local-digest record."""
    document: dict[str, Any] = {
        "acquisitionStatus": "not-acquired",
        "calibrationStatus": "not-approved",
        "configurationDigests": [],
        "conversionStatus": "not-performed",
        "digestAuthority": "local-sha256",
        "executionStatus": "not-executed",
        "installationAuthorized": False,
        "licenseDigests": [],
        "measurementPerformed": False,
        "modelDigests": [],
        "noticeDigests": [],
        "productionReady": False,
        "quantizationApproved": False,
        "realModelExecuted": False,
        "runtimeDigests": [],
        "runtimeInstallationStatus": "not-installed",
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "tokenizerDigests": [],
    }
    document["identityDigest"] = sha256_text(canonical_dumps(document))
    validate("local-artifact-digests", document)
    return document


def load_digest_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed digest template and require it to match the builder."""
    base = root if root is not None else repo_root()
    path = base / "candidates/templates/local-artifact-digests-template.json"
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ArtifactValidationError("record-type")
    validate("local-artifact-digests", loaded)
    if loaded != not_acquired_digests():
        raise ArtifactValidationError("record-drift")
    return loaded


def validate_reason(record: dict[str, Any]) -> None:
    """Reject a reason record that carries a path or credential marker."""
    from patchpilot_intelligence_evals.acquisition_plan import PlanError, reject_sensitive

    try:
        reject_sensitive(record)
    except PlanError as exc:
        raise ArtifactValidationError(exc.code) from exc
