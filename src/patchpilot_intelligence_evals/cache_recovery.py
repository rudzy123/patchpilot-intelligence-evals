"""Crash classification for one synthetic promotion attempt.

A verified result requires the seal, the inventory identity, and a consistent
journal together. The directory name is not proof. Indeterminate attempts stay
blocked for operator review.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_cache import validate_cache_root
from patchpilot_intelligence_evals.atomic_promotion import (
    PromotionError,
    install_receipt,
    read_journal,
    read_receipt,
    save_journal,
    transition,
)
from patchpilot_intelligence_evals.filesystem_identity import IdentityError, fsync_directory
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.verification_seal import (
    SealError,
    check_attempt_id,
    confinement_problems,
    document_digest,
    inventory_matches,
    load_seal,
    primary_problem,
)

_CLASSIFICATIONS = frozenset(
    {
        "not-acquired",
        "resumable-quarantine",
        "rejected",
        "verified",
        "indeterminate",
    }
)


class RecoveryError(ValueError):
    """Recovery failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def not_acquired_decision() -> dict[str, Any]:
    """Build the committed recovery template."""
    return _decision(
        classification="not-acquired",
        attempt_id=None,
        observed_state=None,
        inventory_identity=None,
        logical_bytes=None,
        same_filesystem=None,
        recovery_proof="none",
        review=False,
        failure=None,
        later="none",
        sync_steps=[],
    )


def load_recovery_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed recovery template and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads(
        (base / "candidates/templates/artifact-recovery-decision-template.json").read_text(
            encoding="utf-8"
        )
    )
    if not isinstance(loaded, dict):
        raise RecoveryError("record-type")
    document = validate_decision(loaded)
    if document != not_acquired_decision():
        raise RecoveryError("record-drift")
    return document


def validate_decision(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one recovery decision and its digest."""
    validate("artifact-recovery-decision", document)
    if document["identityDigest"] != document_digest(document):
        raise RecoveryError("invalid-journal")
    if document["classification"] not in _CLASSIFICATIONS:
        raise RecoveryError("inconsistent-journal")
    if (
        document["classification"] == "indeterminate"
        and document["operatorReviewRequired"] is not True
    ):
        raise RecoveryError("operator-review")
    if document["executionEligibility"] != "prohibited":
        raise RecoveryError("quarantine-execution")
    return document


def classify_attempt(
    cache: Path,
    attempt_id: str,
    *,
    repository: Path | None = None,
) -> dict[str, Any]:
    """Classify one attempt without guessing that a directory name is verified."""
    root = validate_cache_root(cache, repository=repository)
    try:
        check_attempt_id(attempt_id)
    except SealError as exc:
        raise RecoveryError(exc.code) from exc
    quarantine = root / "quarantine" / attempt_id
    verified = root / "verified" / attempt_id
    if quarantine.is_symlink() or verified.is_symlink():
        return _blocked(attempt_id, "symlink-escape")
    quarantine_real = quarantine.is_dir()
    verified_real = verified.is_dir()
    if quarantine_real and verified_real:
        return _blocked(attempt_id, "inconsistent-journal")
    if not quarantine_real and not verified_real:
        return _blocked(attempt_id, "inconsistent-journal")
    directory = quarantine if quarantine_real else verified
    try:
        journal = read_journal(directory)
    except PromotionError:
        return _blocked(attempt_id, "inconsistent-journal")
    if journal["attemptId"] != attempt_id:
        return _blocked(attempt_id, "inconsistent-journal")
    state = str(journal["attemptState"])
    if state == "indeterminate":
        return _blocked(
            attempt_id, str(journal["failureCategory"] or "inconsistent-journal"), state
        )
    if state == "rejected":
        return _finished(
            attempt_id,
            "rejected",
            journal,
            failure=journal["failureCategory"],
        )
    if quarantine_real:
        return _classify_quarantine(attempt_id, directory, journal)
    return _classify_verified(root, attempt_id, directory, journal)


def recover_attempt(
    cache: Path,
    attempt_id: str,
    *,
    repository: Path | None = None,
) -> dict[str, Any]:
    """Apply one idempotent recovery step. Indeterminate state stays blocked."""
    decision = classify_attempt(cache, attempt_id, repository=repository)
    root = validate_cache_root(cache, repository=repository)
    if decision["classification"] == "verified" and decision["recoveryProof"] == "explicit":
        _complete_verified(root, attempt_id)
    elif decision["classification"] == "rejected":
        _mark_rejected(root, attempt_id)
    return classify_attempt(cache, attempt_id, repository=repository)


def _classify_quarantine(
    attempt_id: str, directory: Path, journal: dict[str, Any]
) -> dict[str, Any]:
    state = str(journal["attemptState"])
    if state in {"verified"}:
        return _blocked(attempt_id, "inconsistent-journal", state)
    if state in {"sealed", "promoting"}:
        try:
            seal = load_seal(directory)
        except SealError as exc:
            return _finished(attempt_id, "rejected", journal, failure=exc.code)
        if seal["attemptId"] != attempt_id or not inventory_matches(directory, seal):
            return _finished(attempt_id, "rejected", journal, failure="changed-after-seal")
        return _finished(attempt_id, "resumable-quarantine", journal, failure=None)
    if state in {"quarantine-open", "quarantine-closed", "verifying"}:
        problem = primary_problem(confinement_problems(directory))
        if problem is not None:
            return _finished(attempt_id, "rejected", journal, failure=problem)
        return _finished(attempt_id, "resumable-quarantine", journal, failure=None)
    return _blocked(attempt_id, "inconsistent-journal", state)


def _classify_verified(
    root: Path,
    attempt_id: str,
    directory: Path,
    journal: dict[str, Any],
) -> dict[str, Any]:
    state = str(journal["attemptState"])
    try:
        seal = load_seal(directory)
    except SealError:
        return _blocked(attempt_id, "inconsistent-journal", state)
    if seal["attemptId"] != attempt_id or not inventory_matches(directory, seal):
        return _blocked(attempt_id, "modified-inventory", state)
    if state not in {"promoting", "verified"}:
        return _blocked(attempt_id, "inconsistent-journal", state)
    receipt_ok = _receipt_ok(root, attempt_id, str(seal["inventoryIdentity"]))
    if state == "verified" and not receipt_ok:
        return _blocked(attempt_id, "inconsistent-journal", state)
    if state == "verified" and receipt_ok:
        proof = str(journal["recoveryProof"])
        if proof not in {"none", "explicit"}:
            proof = "none"
        return _finished(attempt_id, "verified", journal, failure=None, proof=proof)
    if state == "promoting" and receipt_ok is False and _receipt_conflicts(root, attempt_id, seal):
        return _blocked(attempt_id, "inconsistent-journal", state)
    return _finished(attempt_id, "verified", journal, failure=None, proof="explicit")


def _complete_verified(root: Path, attempt_id: str) -> None:
    directory = root / "verified" / attempt_id
    journal = read_journal(directory)
    if journal["attemptState"] == "verified":
        return
    seal = load_seal(directory)
    parent = root / "verified"
    try:
        fsync_directory(parent)
    except IdentityError as exc:
        raise RecoveryError(exc.code) from exc
    if not _receipt_ok(root, attempt_id, str(seal["inventoryIdentity"])):
        if _receipt_conflicts(root, attempt_id, seal):
            return
        install_receipt(
            parent,
            seal,
            attempt_id=attempt_id,
            recovery_proof="explicit",
        )
    transition(str(journal["attemptState"]), "verified", recovery_proof=True)
    _save_from_journal(
        directory,
        journal,
        attempt_state="verified",
        interruption_point="after-receipt",
        failure_category=None,
        recovery_proof="explicit",
        later="verified-identity-only",
        operator_review=False,
        sync_steps=[
            "file-data",
            "manifest-file",
            "quarantine-directory",
            "rename-noreplace",
            "verified-parent-directory",
            "receipt-file",
            "verified-parent-directory-after-receipt",
        ],
    )


def _mark_rejected(root: Path, attempt_id: str) -> None:
    directory = root / "quarantine" / attempt_id
    if not directory.is_dir() or directory.is_symlink():
        return
    try:
        journal = read_journal(directory)
    except PromotionError:
        return
    state = str(journal["attemptState"])
    if state == "rejected":
        return
    if state not in {"verifying", "sealed"}:
        return
    failure = "changed-after-seal"
    try:
        seal = load_seal(directory)
        if inventory_matches(directory, seal):
            problem = primary_problem(confinement_problems(directory))
            failure = problem or "changed-after-seal"
    except SealError as exc:
        failure = exc.code
    transition(state, "rejected")
    _save_from_journal(
        directory,
        journal,
        attempt_state="rejected",
        interruption_point="modified-inventory",
        failure_category=failure,
        recovery_proof="none",
        later="none",
        operator_review=False,
    )


def _save_from_journal(directory: Path, journal: dict[str, Any], **updates: Any) -> None:
    pre = journal["preVerificationMetadata"]
    post = journal["postVerificationMetadata"]
    fields: dict[str, Any] = {
        "attempt_id": journal["attemptId"],
        "inventory_identity": journal["inventoryIdentity"],
        "logical_bytes": journal["logicalInventoryBytes"],
        "same_filesystem": journal["sameFilesystem"],
        "sync_steps": list(journal["syncSteps"]),
        "pre_recorded": bool(pre["recorded"]),
        "post_recorded": bool(post["recorded"]),
        "file_count": int(post["fileCount"]),
        "attempt_state": journal["attemptState"],
        "interruption_point": journal["interruptionPoint"],
        "failure_category": journal["failureCategory"],
        "recovery_proof": journal["recoveryProof"],
        "later": journal["laterSessionEligibility"],
        "operator_review": journal["operatorReviewRequired"],
    }
    fields.update(updates)
    save_journal(directory, **fields)


def _receipt_ok(root: Path, attempt_id: str, inventory_identity: str) -> bool:
    try:
        receipt = read_receipt(root / "verified", attempt_id)
    except PromotionError:
        return False
    return bool(
        receipt["attemptId"] == attempt_id
        and receipt["inventoryIdentity"] == inventory_identity
        and receipt["receiptState"] == "verified"
    )


def _receipt_conflicts(root: Path, attempt_id: str, seal: dict[str, Any]) -> bool:
    path = root / "verified" / f"{attempt_id}.promotion-receipt.json"
    if not path.exists():
        return False
    return not _receipt_ok(root, attempt_id, str(seal["inventoryIdentity"]))


def _finished(
    attempt_id: str,
    classification: str,
    journal: dict[str, Any],
    *,
    failure: str | None,
    proof: str = "none",
) -> dict[str, Any]:
    later = "verified-identity-only" if classification == "verified" else "none"
    return _decision(
        classification=classification,
        attempt_id=attempt_id,
        observed_state=str(journal["attemptState"]),
        inventory_identity=journal["inventoryIdentity"],
        logical_bytes=journal["logicalInventoryBytes"],
        same_filesystem=journal["sameFilesystem"],
        recovery_proof=proof,
        review=False,
        failure=failure if isinstance(failure, str) else None,
        later=later,
        sync_steps=list(journal["syncSteps"]),
        file_count=int(journal["postVerificationMetadata"]["fileCount"]),
        recorded=bool(journal["postVerificationMetadata"]["recorded"]),
    )


def _blocked(attempt_id: str, failure: str, observed: str | None = None) -> dict[str, Any]:
    return _decision(
        classification="indeterminate",
        attempt_id=attempt_id,
        observed_state=observed,
        inventory_identity=None,
        logical_bytes=None,
        same_filesystem=None,
        recovery_proof="absent",
        review=True,
        failure=failure,
        later="none",
        sync_steps=[],
    )


def _decision(
    *,
    classification: str,
    attempt_id: str | None,
    observed_state: str | None,
    inventory_identity: str | None,
    logical_bytes: int | None,
    same_filesystem: bool | None,
    recovery_proof: str,
    review: bool,
    failure: str | None,
    later: str,
    sync_steps: list[str],
    file_count: int = 0,
    recorded: bool = False,
) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
        "classification": classification,
        "operatorReviewRequired": review,
        "recoveryProof": recovery_proof,
        "attemptId": attempt_id,
        "observedAttemptState": observed_state,
        "inventoryIdentity": inventory_identity if isinstance(inventory_identity, str) else None,
        "logicalInventoryBytes": logical_bytes,
        "allocatedInventoryBytes": None,
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "sameFilesystem": same_filesystem,
        "syncSteps": sync_steps,
        "executionEligibility": "prohibited",
        "laterSessionEligibility": later,
        "copyFallbackUsed": False,
        "failureCategory": failure,
        "preVerificationMetadata": {
            "recorded": recorded,
            "logicalBytes": logical_bytes if recorded else None,
            "fileCount": file_count if recorded else 0,
        },
        "postVerificationMetadata": {
            "recorded": recorded,
            "logicalBytes": logical_bytes if recorded else None,
            "fileCount": file_count if recorded else 0,
        },
    }
    document["identityDigest"] = document_digest(document)
    return validate_decision(document)
