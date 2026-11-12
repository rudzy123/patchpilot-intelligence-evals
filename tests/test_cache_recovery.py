"""Crash classification for every declared interruption point."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.atomic_promotion import (
    prepare_attempt,
    promote_sealed_attempt,
    read_journal,
    save_journal,
    seal_closed_attempt,
)
from patchpilot_intelligence_evals.cache_recovery import classify_attempt, recover_attempt

_MTIME = 1_700_000_000_000_000_000
_PAYLOAD = b"synthetic-track7a"


def _cache(tmp_path: Path) -> Path:
    root = tmp_path / "cache"
    root.mkdir(parents=True)
    return root


def _expected() -> list[dict[str, object]]:
    return [{"relativeName": "note.txt", "logicalBytes": len(_PAYLOAD), "sha256": None}]


def _seal(cache: Path) -> dict[str, object]:
    prepare_attempt(cache, "attempt-1", {"note.txt": _PAYLOAD})
    path = cache / "quarantine" / "attempt-1" / "note.txt"
    os.utime(path, ns=(_MTIME, _MTIME))
    return seal_closed_attempt(cache, "attempt-1", _expected())


def _rewrite(directory: Path, **updates: Any) -> None:
    journal = read_journal(directory)
    fields: dict[str, Any] = {
        "attempt_id": journal["attemptId"],
        "attempt_state": journal["attemptState"],
        "interruption_point": journal["interruptionPoint"],
        "inventory_identity": journal["inventoryIdentity"],
        "logical_bytes": journal["logicalInventoryBytes"],
        "same_filesystem": journal["sameFilesystem"],
        "sync_steps": list(journal["syncSteps"]),
        "pre_recorded": journal["preVerificationMetadata"]["recorded"],
        "post_recorded": journal["postVerificationMetadata"]["recorded"],
        "file_count": journal["postVerificationMetadata"]["fileCount"],
        "failure_category": journal["failureCategory"],
        "recovery_proof": journal["recoveryProof"],
        "later": journal["laterSessionEligibility"],
        "operator_review": journal["operatorReviewRequired"],
    }
    fields.update(updates)
    save_journal(directory, **fields)


def test_interruption_matrix(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    prepare_attempt(cache, "attempt-1", {"note.txt": _PAYLOAD})
    source = cache / "quarantine" / "attempt-1"
    before = classify_attempt(cache, "attempt-1")
    assert before["classification"] == "resumable-quarantine"
    assert read_journal(source)["interruptionPoint"] == "before-hashing"
    _rewrite(source, attempt_state="verifying", interruption_point="during-hashing")
    assert classify_attempt(cache, "attempt-1")["classification"] == "resumable-quarantine"
    _rewrite(source, interruption_point="before-seal")
    assert read_journal(source)["interruptionPoint"] == "before-seal"
    _rewrite(
        source,
        attempt_state="quarantine-closed",
        interruption_point="before-hashing",
    )
    path = source / "note.txt"
    os.utime(path, ns=(_MTIME, _MTIME))
    seal_closed_attempt(cache, "attempt-1", _expected())
    after_seal = classify_attempt(cache, "attempt-1")
    assert after_seal["classification"] == "resumable-quarantine"
    assert read_journal(source)["interruptionPoint"] == "after-seal"
    _rewrite(source, attempt_state="promoting", interruption_point="before-rename")
    before_rename = classify_attempt(cache, "attempt-1")
    assert before_rename["classification"] == "resumable-quarantine"
    (cache / "verified").mkdir()
    os.rename(cache / "quarantine" / "attempt-1", cache / "verified" / "attempt-1")
    after_rename = classify_attempt(cache, "attempt-1")
    assert after_rename["classification"] == "verified"
    assert after_rename["recoveryProof"] == "explicit"
    recovered = recover_attempt(cache, "attempt-1")
    assert recovered["classification"] == "verified"
    assert (cache / "verified" / "attempt-1.promotion-receipt.json").is_file()
    assert recover_attempt(cache, "attempt-1") == recovered


def test_completed_promotion_is_verified_and_idempotent(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    _seal(cache)
    promote_sealed_attempt(cache, "attempt-1")
    decision = classify_attempt(cache, "attempt-1")
    assert decision["classification"] == "verified"
    assert decision["recoveryProof"] == "none"
    assert decision["executionEligibility"] == "prohibited"
    assert recover_attempt(cache, "attempt-1") == decision


def test_directory_name_and_inconsistent_journals_are_indeterminate(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    _seal(cache)
    (cache / "verified").mkdir()
    os.rename(cache / "quarantine" / "attempt-1", cache / "verified" / "attempt-1")
    named_only = classify_attempt(cache, "attempt-1")
    assert named_only["classification"] == "indeterminate"
    assert named_only["operatorReviewRequired"] is True
    assert named_only["recoveryProof"] == "absent"
    journal_path = cache / "verified" / "attempt-1" / "promotion-journal.json"
    journal_path.write_text("{", encoding="utf-8")
    broken = classify_attempt(cache, "attempt-1")
    assert broken["classification"] == "indeterminate"
    assert broken["failureCategory"] == "inconsistent-journal"
    missing = _cache(tmp_path / "empty")
    absent = classify_attempt(missing, "attempt-1")
    assert absent["classification"] == "indeterminate"
    assert recover_attempt(missing, "attempt-1") == absent


def test_modified_inventory_keeps_verified_seal_bytes(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    _seal(cache)
    promote_sealed_attempt(cache, "attempt-1")
    seal_path = cache / "verified" / "attempt-1" / "verification-seal.json"
    original = seal_path.read_bytes()
    (cache / "verified" / "attempt-1" / "note.txt").write_bytes(b"changed")
    decision = classify_attempt(cache, "attempt-1")
    assert decision["classification"] == "indeterminate"
    assert decision["failureCategory"] == "modified-inventory"
    assert decision["operatorReviewRequired"] is True
    assert seal_path.read_bytes() == original
    assert recover_attempt(cache, "attempt-1") == decision
    quarantine = _cache(tmp_path / "quarantine-change")
    _seal(quarantine)
    (quarantine / "quarantine" / "attempt-1" / "note.txt").write_bytes(b"changed")
    rejected = classify_attempt(quarantine, "attempt-1")
    assert rejected["classification"] == "rejected"
    assert rejected["failureCategory"] == "changed-after-seal"
