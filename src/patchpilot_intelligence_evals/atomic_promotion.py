"""Same-filesystem promotion of a sealed quarantine attempt.

The attempt directory is renamed with renameat2 and RENAME_NOREPLACE. Byte
copying is absent. A failed synchronization step does not publish a verified
receipt. Quarantine, sealed, and verified states all keep execution prohibited.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_cache import validate_cache_root
from patchpilot_intelligence_evals.filesystem_identity import (
    IdentityError,
    device_equal,
    fsync_directory,
    fsync_file,
    rename_noreplace,
    rename_replace_file,
    write_new_file,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root, validate
from patchpilot_intelligence_evals.storage_budget import ATOMIC_CONTRACT_REQUIREMENTS
from patchpilot_intelligence_evals.verification_seal import (
    JOURNAL_FILENAME,
    JOURNAL_TEMPORARY,
    SEAL_FILENAME,
    SealError,
    check_attempt_id,
    check_relative_name,
    document_digest,
    inventory_matches,
    load_seal,
    seal_directory,
)

_ATTEMPT_STATES = (
    "not-acquired",
    "quarantine-open",
    "quarantine-closed",
    "verifying",
    "sealed",
    "promoting",
    "verified",
    "rejected",
    "indeterminate",
)
_ALLOWED: dict[str, frozenset[str]] = {
    "quarantine-open": frozenset({"quarantine-closed"}),
    "quarantine-closed": frozenset({"verifying"}),
    "verifying": frozenset({"sealed", "rejected"}),
    "sealed": frozenset({"promoting", "rejected"}),
    "promoting": frozenset({"verified", "indeterminate"}),
    "indeterminate": frozenset({"rejected", "verified"}),
    "verified": frozenset(),
    "rejected": frozenset(),
    "not-acquired": frozenset(),
}
RECEIPT_SYNC_STEPS: tuple[str, ...] = (
    "file-data",
    "manifest-file",
    "quarantine-directory",
    "rename-noreplace",
    "verified-parent-directory",
    "receipt-file",
    "verified-parent-directory-after-receipt",
)
_SEAL_SYNC_STEPS = ("manifest-file", "quarantine-directory")


class PromotionError(ValueError):
    """A promotion failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass
class PromotionHooks:
    """Optional stand-ins for sync and rename. Tests use them to fail closed."""

    sync_file: Callable[[Path], None] | None = None
    sync_directory: Callable[[Path], None] | None = None
    rename: Callable[[Path, Path], None] | None = None


def transition(current: str, new: str, *, recovery_proof: bool = False) -> str:
    """Return the new state when the edge is authorized."""
    allowed = _ALLOWED.get(current)
    if allowed is None or new not in allowed:
        raise PromotionError("prohibited-transition")
    if current == "indeterminate" and new == "verified" and not recovery_proof:
        raise PromotionError("prohibited-transition")
    return new


def execution_allowed(attempt_state: str) -> bool:
    """Track 7A does not execute from any cache state."""
    if attempt_state not in _ATTEMPT_STATES:
        raise PromotionError("prohibited-transition")
    return False


def later_session_eligible(attempt_state: str) -> bool:
    """Only a promoted identity can be considered by a later session."""
    if attempt_state not in _ATTEMPT_STATES:
        raise PromotionError("prohibited-transition")
    return attempt_state == "verified"


def covers_contract() -> bool:
    """True when this module keeps the atomic contract and does not copy bytes."""
    source = Path(__file__).read_text(encoding="utf-8")
    banned = (
        "sh" + "util",
        "copy" + "file(",
        "copy" + "2(",
        "send" + "file(",
        "os." + "replace(",
    )
    if any(token in source for token in banned):
        return False
    required = ("rename_noreplace", "fsync_file", "fsync_directory", "device_equal")
    if any(token not in source for token in required):
        return False
    return tuple(ATOMIC_CONTRACT_REQUIREMENTS) == ATOMIC_CONTRACT_REQUIREMENTS


def not_acquired_attempt() -> dict[str, Any]:
    """Build the committed attempt template."""
    return _finalize_attempt(
        attempt_id=None,
        attempt_state="not-acquired",
        interruption_point="none",
    )


def not_acquired_receipt() -> dict[str, Any]:
    """Build the committed receipt template."""
    return _finalize_receipt(
        attempt_id=None,
        receipt_state="not-acquired",
        inventory_identity=None,
        seal_identity=None,
        logical_bytes=None,
        sync_steps=[],
        later="none",
        recovery_proof="none",
        same_filesystem=None,
    )


def validate_attempt(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one attempt journal and its digest."""
    validate("artifact-promotion-attempt", document)
    if document["identityDigest"] != document_digest(document):
        raise PromotionError("invalid-journal")
    if document["copyFallbackUsed"] is not False:
        raise PromotionError("copy-fallback")
    if document["executionEligibility"] != "prohibited":
        raise PromotionError("quarantine-execution")
    return document


def validate_receipt(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one promotion receipt and its digest."""
    validate("artifact-promotion-receipt", document)
    if document["identityDigest"] != document_digest(document):
        raise PromotionError("invalid-seal")
    if document["copyFallbackUsed"] is not False:
        raise PromotionError("copy-fallback")
    if document["executionEligibility"] != "prohibited":
        raise PromotionError("quarantine-execution")
    if document["receiptState"] == "verified":
        if document["syncSteps"] != list(RECEIPT_SYNC_STEPS):
            raise PromotionError("synchronization-failure")
        if document["sameFilesystem"] is not True:
            raise PromotionError("cross-device")
        if document["crossDevice"] is not False or document["destinationCollision"] is not False:
            raise PromotionError("destination-collision")
    return document


def prepare_attempt(
    cache: Path,
    attempt_id: str,
    files: Mapping[str, bytes],
    *,
    repository: Path | None = None,
) -> Path:
    """Create a closed synthetic quarantine attempt. This does not acquire a model."""
    root = validate_cache_root(cache, repository=repository)
    source = _source(root, attempt_id)
    if source.exists() or source.is_symlink():
        raise PromotionError("destination-collision")
    source.mkdir(parents=True)
    for name, payload in files.items():
        if not isinstance(payload, bytes):
            raise PromotionError("unknown-size")
        try:
            relative = check_relative_name(name)
        except SealError as exc:
            raise PromotionError(exc.code) from exc
        target = source.joinpath(*relative.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.exists():
            raise PromotionError("destination-collision")
        target.write_bytes(payload)
    _save_attempt(
        source,
        attempt_id=attempt_id,
        attempt_state="quarantine-open",
        interruption_point="before-hashing",
    )
    transition("quarantine-open", "quarantine-closed")
    _save_attempt(
        source,
        attempt_id=attempt_id,
        attempt_state="quarantine-closed",
        interruption_point="before-hashing",
    )
    return source


def seal_closed_attempt(
    cache: Path,
    attempt_id: str,
    expected: list[dict[str, Any]],
    *,
    repository: Path | None = None,
    during_hash: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    """Move a closed quarantine attempt through verification to sealed."""
    root = validate_cache_root(cache, repository=repository)
    source = _require_source(root, attempt_id)
    journal = read_journal(source)
    if journal["attemptId"] != attempt_id:
        raise PromotionError("invalid-journal")
    transition(str(journal["attemptState"]), "verifying")
    _save_attempt(
        source,
        attempt_id=attempt_id,
        attempt_state="verifying",
        interruption_point="during-hashing",
    )
    try:
        seal = seal_directory(source, expected, attempt_id=attempt_id, during_hash=during_hash)
    except SealError as exc:
        transition("verifying", "rejected")
        _save_attempt(
            source,
            attempt_id=attempt_id,
            attempt_state="rejected",
            interruption_point="before-seal",
            failure_category=exc.code,
        )
        raise PromotionError(exc.code) from exc
    transition("verifying", "sealed")
    _save_attempt(
        source,
        attempt_id=attempt_id,
        attempt_state="sealed",
        interruption_point="after-seal",
        inventory_identity=str(seal["inventoryIdentity"]),
        logical_bytes=int(seal["logicalInventoryBytes"]),
        same_filesystem=True,
        sync_steps=list(_SEAL_SYNC_STEPS),
        pre_recorded=True,
        post_recorded=True,
        file_count=len(seal["files"]),
    )
    if execution_allowed("sealed"):
        raise PromotionError("quarantine-execution")
    return seal


def promote_sealed_attempt(
    cache: Path,
    attempt_id: str,
    *,
    repository: Path | None = None,
    hooks: PromotionHooks | None = None,
) -> dict[str, Any]:
    """Rename a sealed attempt into verified state, or fail without copying."""
    root = validate_cache_root(cache, repository=repository)
    source = _require_source(root, attempt_id)
    verified_parent = _verified_parent(root)
    destination = verified_parent / attempt_id
    receipt_path = _receipt_path(verified_parent, attempt_id)
    _require_absent(destination)
    _require_absent(receipt_path)
    journal = read_journal(source)
    if journal["attemptId"] != attempt_id or journal["attemptState"] != "sealed":
        raise PromotionError("not-sealed")
    try:
        seal = load_seal(source)
    except SealError as exc:
        raise PromotionError(exc.code) from exc
    if seal["attemptId"] != attempt_id or seal["sealState"] != "sealed":
        raise PromotionError("invalid-seal")
    if not inventory_matches(source, seal):
        raise PromotionError("changed-after-seal")
    if not device_equal(source, root) or not device_equal(source, verified_parent):
        raise PromotionError("cross-device")
    _probe_rename(root)
    transition("sealed", "promoting")
    sealed_fields = _sealed_fields(attempt_id, seal)
    _save_attempt(
        source,
        **sealed_fields,
        attempt_state="promoting",
        interruption_point="before-rename",
    )
    try:
        _sync_tree(source, seal, hooks)
    except PromotionError as exc:
        _save_attempt(
            source,
            **sealed_fields,
            attempt_state="sealed",
            interruption_point="before-rename",
            failure_category=exc.code,
        )
        raise
    try:
        _rename(source, destination, hooks)
    except PromotionError as exc:
        _save_attempt(
            source,
            **sealed_fields,
            attempt_state="sealed",
            interruption_point="before-rename",
            failure_category=exc.code,
        )
        raise
    _save_attempt(
        destination,
        **_fields(
            sealed_fields,
            attempt_state="promoting",
            interruption_point="after-rename",
            sync_steps=[*_SEAL_SYNC_STEPS, "file-data", "rename-noreplace"],
        ),
    )
    try:
        _sync_directory(verified_parent, hooks)
    except PromotionError as exc:
        _save_attempt(
            destination,
            **_fields(
                sealed_fields,
                attempt_state="indeterminate",
                interruption_point="before-parent-sync",
                failure_category=exc.code,
                operator_review=True,
                sync_steps=[*_SEAL_SYNC_STEPS, "file-data", "rename-noreplace"],
            ),
        )
        raise
    try:
        receipt = install_receipt(
            verified_parent,
            seal,
            attempt_id=attempt_id,
            recovery_proof="none",
            hooks=hooks,
        )
    except PromotionError as exc:
        _save_attempt(
            destination,
            **_fields(
                sealed_fields,
                attempt_state="promoting",
                interruption_point="before-receipt",
                failure_category=exc.code,
                sync_steps=[
                    *_SEAL_SYNC_STEPS,
                    "file-data",
                    "rename-noreplace",
                    "verified-parent-directory",
                ],
            ),
        )
        raise
    transition("promoting", "verified")
    _save_attempt(
        destination,
        **_fields(
            sealed_fields,
            attempt_state="verified",
            interruption_point="after-receipt",
            sync_steps=list(RECEIPT_SYNC_STEPS),
            later="verified-identity-only",
        ),
    )
    if execution_allowed("verified") or not later_session_eligible("verified"):
        raise PromotionError("quarantine-execution")
    return receipt


def install_receipt(
    verified_parent: Path,
    seal: Mapping[str, Any],
    *,
    attempt_id: str,
    recovery_proof: str,
    hooks: PromotionHooks | None = None,
) -> dict[str, Any]:
    """Write a receipt beside the verified attempt. The sealed directory is unchanged."""
    receipt = _finalize_receipt(
        attempt_id=attempt_id,
        receipt_state="verified",
        inventory_identity=str(seal["inventoryIdentity"]),
        seal_identity=str(seal["identityDigest"]),
        logical_bytes=int(seal["logicalInventoryBytes"]),
        sync_steps=list(RECEIPT_SYNC_STEPS),
        later="verified-identity-only",
        recovery_proof=recovery_proof,
        same_filesystem=True,
        file_count=len(list(seal["files"])),
    )
    path = _receipt_path(verified_parent, attempt_id)
    temporary = verified_parent / f".{attempt_id}.promotion-receipt.json.tmp"
    _require_absent(path)
    _require_absent(temporary)
    payload = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")
    try:
        write_new_file(temporary, payload)
        _sync_file(temporary, hooks)
        _rename(temporary, path, hooks)
        _sync_directory(verified_parent, hooks)
    except (IdentityError, PromotionError) as exc:
        if temporary.is_file() and not temporary.is_symlink() and not path.exists():
            temporary.unlink()
        if isinstance(exc, PromotionError):
            raise
        raise PromotionError(exc.code) from exc
    return receipt


def read_journal(directory: Path) -> dict[str, Any]:
    """Load one attempt journal."""
    path = directory / JOURNAL_FILENAME
    if path.is_symlink() or not path.is_file():
        raise PromotionError("not-sealed")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PromotionError("invalid-journal") from exc
    if not isinstance(loaded, dict):
        raise PromotionError("invalid-journal")
    try:
        return validate_attempt(loaded)
    except SchemaValidationError as exc:
        raise PromotionError("invalid-journal") from exc


def read_receipt(verified_parent: Path, attempt_id: str) -> dict[str, Any]:
    """Load one receipt. A missing receipt raises."""
    path = _receipt_path(verified_parent, attempt_id)
    if path.is_symlink() or not path.is_file():
        raise PromotionError("missing-seal")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PromotionError("invalid-seal") from exc
    if not isinstance(loaded, dict):
        raise PromotionError("invalid-seal")
    try:
        return validate_receipt(loaded)
    except SchemaValidationError as exc:
        raise PromotionError("invalid-seal") from exc


def _save_attempt(directory: Path, **fields: Any) -> dict[str, Any]:
    document = _finalize_attempt(**fields)
    temporary = directory / JOURNAL_TEMPORARY
    destination = directory / JOURNAL_FILENAME
    if temporary.exists() or temporary.is_symlink():
        raise PromotionError("destination-collision")
    payload = (json.dumps(document, indent=2) + "\n").encode("utf-8")
    try:
        write_new_file(temporary, payload)
        fsync_file(temporary)
        rename_replace_file(temporary, destination)
        fsync_directory(directory)
    except IdentityError as exc:
        if temporary.is_file() and not temporary.is_symlink():
            temporary.unlink()
        raise PromotionError(exc.code) from exc
    return document


def _finalize_attempt(
    *,
    attempt_id: str | None,
    attempt_state: str,
    interruption_point: str,
    failure_category: str | None = None,
    inventory_identity: str | None = None,
    logical_bytes: int | None = None,
    same_filesystem: bool | None = None,
    sync_steps: list[str] | None = None,
    later: str = "none",
    recovery_proof: str = "none",
    operator_review: bool = False,
    pre_recorded: bool = False,
    post_recorded: bool = False,
    file_count: int = 0,
) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        **_disabled(),
        "attemptId": attempt_id,
        "attemptState": attempt_state,
        "interruptionPoint": interruption_point,
        "failureCategory": failure_category,
        "inventoryIdentity": inventory_identity,
        "logicalInventoryBytes": logical_bytes,
        "allocatedInventoryBytes": None,
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "sameFilesystem": same_filesystem,
        "syncSteps": list(sync_steps or []),
        "executionEligibility": "prohibited",
        "laterSessionEligibility": later,
        "copyFallbackUsed": False,
        "recoveryProof": recovery_proof,
        "operatorReviewRequired": operator_review,
        "preVerificationMetadata": _metadata(pre_recorded, logical_bytes, file_count),
        "postVerificationMetadata": _metadata(post_recorded, logical_bytes, file_count),
    }
    document["identityDigest"] = document_digest(document)
    return validate_attempt(document)


def _finalize_receipt(
    *,
    attempt_id: str | None,
    receipt_state: str,
    inventory_identity: str | None,
    seal_identity: str | None,
    logical_bytes: int | None,
    sync_steps: list[str],
    later: str,
    recovery_proof: str,
    same_filesystem: bool | None,
    file_count: int = 0,
) -> dict[str, Any]:
    recorded = receipt_state == "verified"
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        **_disabled(),
        "receiptState": receipt_state,
        "attemptId": attempt_id,
        "executionEligibility": "prohibited",
        "laterSessionEligibility": later,
        "logicalInventoryBytes": logical_bytes,
        "allocatedInventoryBytes": None,
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "sameFilesystem": same_filesystem,
        "syncSteps": sync_steps,
        "copyFallbackUsed": False,
        "crossDevice": False,
        "destinationCollision": False,
        "failureCategory": None,
        "inventoryIdentity": inventory_identity,
        "sealIdentity": seal_identity,
        "recoveryProof": recovery_proof,
        "operatorReviewRequired": False,
        "preVerificationMetadata": _metadata(recorded, logical_bytes, file_count),
        "postVerificationMetadata": _metadata(recorded, logical_bytes, file_count),
    }
    document["identityDigest"] = document_digest(document)
    return validate_receipt(document)


def _fields(base: Mapping[str, Any], **updates: Any) -> dict[str, Any]:
    merged = dict(base)
    merged.update(updates)
    return merged


def _sealed_fields(attempt_id: str, seal: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "attempt_id": attempt_id,
        "inventory_identity": str(seal["inventoryIdentity"]),
        "logical_bytes": int(seal["logicalInventoryBytes"]),
        "same_filesystem": True,
        "sync_steps": list(_SEAL_SYNC_STEPS),
        "pre_recorded": True,
        "post_recorded": True,
        "file_count": len(list(seal["files"])),
    }


def _metadata(recorded: bool, logical_bytes: int | None, file_count: int) -> dict[str, Any]:
    return {
        "recorded": recorded,
        "logicalBytes": logical_bytes if recorded else None,
        "fileCount": file_count if recorded else 0,
    }


def _disabled() -> dict[str, Any]:
    return {
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
    }


def _sync_tree(source: Path, seal: Mapping[str, Any], hooks: PromotionHooks | None) -> None:
    for item in seal["files"]:
        _sync_file(source.joinpath(*str(item["relativeName"]).split("/")), hooks)
    _sync_file(source / SEAL_FILENAME, hooks)
    _sync_file(source / JOURNAL_FILENAME, hooks)
    _sync_directory(source, hooks)


def _sync_file(path: Path, hooks: PromotionHooks | None) -> None:
    if hooks is not None and hooks.sync_file is not None:
        try:
            hooks.sync_file(path)
        except IdentityError as exc:
            raise PromotionError(exc.code) from exc
        except OSError as exc:
            raise PromotionError("synchronization-failure") from exc
        return
    try:
        fsync_file(path)
    except IdentityError as exc:
        raise PromotionError(exc.code) from exc


def _sync_directory(path: Path, hooks: PromotionHooks | None) -> None:
    if hooks is not None and hooks.sync_directory is not None:
        try:
            hooks.sync_directory(path)
        except IdentityError as exc:
            raise PromotionError(exc.code) from exc
        except OSError as exc:
            raise PromotionError("synchronization-failure") from exc
        return
    try:
        fsync_directory(path)
    except IdentityError as exc:
        raise PromotionError(exc.code) from exc


def _rename(source: Path, destination: Path, hooks: PromotionHooks | None) -> None:
    if hooks is not None and hooks.rename is not None:
        try:
            hooks.rename(source, destination)
        except IdentityError as exc:
            raise PromotionError(exc.code) from exc
        except OSError as exc:
            raise PromotionError("rename-failure") from exc
        return
    try:
        rename_noreplace(source, destination)
    except IdentityError as exc:
        raise PromotionError(exc.code) from exc


def _probe_rename(root: Path) -> None:
    source = root / ".rename-probe-src"
    destination = root / ".rename-probe-dst"
    for path in (source, destination):
        if path.is_symlink() or path.exists():
            raise PromotionError("destination-collision")
    source.mkdir()
    try:
        rename_noreplace(source, destination)
    except IdentityError as exc:
        raise PromotionError(exc.code) from exc
    finally:
        if destination.is_dir() and not destination.is_symlink():
            destination.rmdir()
        if source.is_dir() and not source.is_symlink():
            source.rmdir()


def _verified_parent(root: Path) -> Path:
    parent = root / "verified"
    if parent.is_symlink():
        raise PromotionError("symlink")
    if not parent.exists():
        parent.mkdir()
    if not parent.is_dir():
        raise PromotionError("destination-collision")
    return parent


def _source(root: Path, attempt_id: str) -> Path:
    try:
        check_attempt_id(attempt_id)
    except SealError as exc:
        raise PromotionError(exc.code) from exc
    return root / "quarantine" / attempt_id


def _require_source(root: Path, attempt_id: str) -> Path:
    source = _source(root, attempt_id)
    if source.is_symlink() or not source.is_dir():
        raise PromotionError("missing-quarantine")
    return source


def _require_absent(path: Path) -> None:
    if path.is_symlink() or path.exists():
        raise PromotionError("destination-collision")


def _receipt_path(verified_parent: Path, attempt_id: str) -> Path:
    return verified_parent / f"{attempt_id}.promotion-receipt.json"


def load_attempt_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed attempt template and require it to match the builder."""
    return _load_template(
        "candidates/templates/artifact-promotion-attempt-template.json",
        validate_attempt,
        not_acquired_attempt,
        root,
    )


def load_receipt_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed receipt template and require it to match the builder."""
    return _load_template(
        "candidates/templates/artifact-promotion-receipt-template.json",
        validate_receipt,
        not_acquired_receipt,
        root,
    )


def run_synthetic_storage_check() -> dict[str, Any]:
    """Promote one tiny temporary file and return a summary with no host path."""
    import os
    import tempfile

    from patchpilot_intelligence_evals.cache_cleanup import cleanup_attempt
    from patchpilot_intelligence_evals.cache_recovery import classify_attempt

    payload = b"synthetic-track7a"
    expected = [{"relativeName": "note.txt", "logicalBytes": len(payload), "sha256": None}]
    with tempfile.TemporaryDirectory(prefix="track7a-") as raw:
        cache = Path(raw) / "cache"
        cache.mkdir()
        prepare_attempt(cache, "attempt-1", {"note.txt": payload})
        os.utime(
            cache / "quarantine" / "attempt-1" / "note.txt",
            ns=(1_700_000_000_000_000_000, 1_700_000_000_000_000_000),
        )
        seal = seal_closed_attempt(cache, "attempt-1", expected)
        receipt = promote_sealed_attempt(cache, "attempt-1")
        prepare_attempt(cache, "attempt-2", {"note.txt": payload})
        cleaned = cleanup_attempt(cache, "attempt-2", state="quarantine")
        decision = classify_attempt(cache, "attempt-1")
    return {
        "status": "ok",
        "sealState": seal["sealState"],
        "receiptState": receipt["receiptState"],
        "classification": decision["classification"],
        "cleanupStatus": cleaned["status"],
        "reclaimedBytes": cleaned["reclaimedBytes"],
        "copyFallbackUsed": False,
        "executionEligibility": "prohibited",
        "sameFilesystem": True,
        "productionReady": False,
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
    }


def _load_template(
    relative: str,
    validator: Any,
    builder: Any,
    root: Path | None,
) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise PromotionError("record-type")
    document: dict[str, Any] = validator(loaded)
    if document != builder():
        raise PromotionError("record-drift")
    return document


save_journal = _save_attempt
