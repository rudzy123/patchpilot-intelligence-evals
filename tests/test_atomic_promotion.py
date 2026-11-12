"""Same-filesystem atomic promotion. Copy-and-delete is not a fallback."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.atomic_promotion import (
    PromotionError,
    PromotionHooks,
    covers_contract,
    execution_allowed,
    later_session_eligible,
    prepare_attempt,
    promote_sealed_attempt,
    read_journal,
    run_synthetic_storage_check,
    seal_closed_attempt,
    transition,
)
from patchpilot_intelligence_evals.filesystem_identity import IdentityError

_MTIME = 1_700_000_000_000_000_000
_PAYLOAD = b"synthetic-track7a"


def _cache(tmp_path: Path) -> Path:
    root = tmp_path / "cache"
    root.mkdir(parents=True)
    return root


def _expected(payload: bytes = _PAYLOAD) -> list[dict[str, object]]:
    return [{"relativeName": "note.txt", "logicalBytes": len(payload), "sha256": None}]


def _seal(cache: Path, attempt_id: str = "attempt-1", payload: bytes = _PAYLOAD) -> None:
    prepare_attempt(cache, attempt_id, {"note.txt": payload})
    path = cache / "quarantine" / attempt_id / "note.txt"
    os.utime(path, ns=(_MTIME, _MTIME))
    seal_closed_attempt(cache, attempt_id, _expected(payload))


def test_successful_promotion_renames_without_a_second_copy(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    _seal(cache)
    receipt = promote_sealed_attempt(cache, "attempt-1")
    destination = cache / "verified" / "attempt-1" / "note.txt"
    assert receipt["receiptState"] == "verified"
    assert receipt["copyFallbackUsed"] is False
    assert receipt["executionEligibility"] == "prohibited"
    assert execution_allowed("verified") is False
    assert later_session_eligible("verified") is True
    assert destination.read_bytes() == _PAYLOAD
    assert not (cache / "quarantine" / "attempt-1").exists()
    assert receipt["syncSteps"] == [
        "file-data",
        "manifest-file",
        "quarantine-directory",
        "rename-noreplace",
        "verified-parent-directory",
        "receipt-file",
        "verified-parent-directory-after-receipt",
    ]
    assert covers_contract() is True


def test_promotion_failures_stay_fail_closed(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    _seal(cache)

    def cross_device(source: Path, destination: Path) -> None:
        raise IdentityError("cross-device")

    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-1", hooks=PromotionHooks(rename=cross_device))
    assert caught.value.code == "cross-device"
    assert (cache / "quarantine" / "attempt-1" / "note.txt").read_bytes() == _PAYLOAD
    assert read_journal(cache / "quarantine" / "attempt-1")["attemptState"] == "sealed"
    (cache / "verified" / "attempt-1").mkdir(parents=True)
    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-1")
    assert caught.value.code == "destination-collision"
    destination = cache / "verified" / "attempt-1"
    destination.rmdir()
    source = cache / "quarantine" / "attempt-1"
    (source / "note.txt").write_bytes(b"changed-after-seal")
    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-1")
    assert caught.value.code == "changed-after-seal"
    assert source.is_dir()


def test_missing_and_invalid_seals_are_rejected(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    prepare_attempt(cache, "attempt-1", {"note.txt": _PAYLOAD})
    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-1")
    assert caught.value.code == "not-sealed"
    _seal(cache, "attempt-2")
    seal_path = cache / "quarantine" / "attempt-2" / "verification-seal.json"
    document = json.loads(seal_path.read_text(encoding="utf-8"))
    document["identityDigest"] = "0" * 64
    seal_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-2")
    assert caught.value.code == "invalid-seal"


def test_sync_and_rename_failures_do_not_copy(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    _seal(cache)

    def fail_file(path: Path) -> None:
        raise OSError(path.name)

    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-1", hooks=PromotionHooks(sync_file=fail_file))
    assert caught.value.code == "synchronization-failure"
    assert (cache / "quarantine" / "attempt-1").is_dir()
    assert not (cache / "verified" / "attempt-1").exists()
    assert read_journal(cache / "quarantine" / "attempt-1")["attemptState"] == "sealed"

    def fail_rename(source: Path, destination: Path) -> None:
        raise IdentityError("rename-failure")

    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-1", hooks=PromotionHooks(rename=fail_rename))
    assert caught.value.code == "rename-failure"
    assert (cache / "quarantine" / "attempt-1").is_dir()

    calls = {"count": 0}

    def fail_parent(path: Path) -> None:
        if path.name == "verified":
            calls["count"] += 1
            raise OSError("parent")

    with pytest.raises(PromotionError) as caught:
        promote_sealed_attempt(cache, "attempt-1", hooks=PromotionHooks(sync_directory=fail_parent))
    assert caught.value.code == "synchronization-failure"
    journal = read_journal(cache / "verified" / "attempt-1")
    assert journal["attemptState"] == "indeterminate"
    assert journal["operatorReviewRequired"] is True
    assert not (cache / "quarantine" / "attempt-1").exists()
    assert (cache / "verified" / "attempt-1" / "note.txt").read_bytes() == _PAYLOAD


def test_receipts_match_when_metadata_is_frozen(tmp_path: Path) -> None:
    first_cache = _cache(tmp_path / "left")
    second_cache = _cache(tmp_path / "right")
    _seal(first_cache)
    _seal(second_cache)
    first = promote_sealed_attempt(first_cache, "attempt-1")
    second = promote_sealed_attempt(second_cache, "attempt-1")
    assert first == second


def test_synthetic_summary_omits_host_paths() -> None:
    summary = run_synthetic_storage_check()
    rendered = json.dumps(summary)
    assert summary["status"] == "ok"
    assert summary["sealState"] == "sealed"
    assert summary["receiptState"] == "verified"
    assert summary["classification"] == "verified"
    assert summary["cleanupStatus"] == "clean"
    assert summary["copyFallbackUsed"] is False
    assert summary["executionEligibility"] == "prohibited"
    assert "/" not in rendered
    assert "\\" not in rendered


def test_prohibited_transitions_and_copy_absence() -> None:
    with pytest.raises(PromotionError) as caught:
        transition("quarantine-open", "verified")
    assert caught.value.code == "prohibited-transition"
    with pytest.raises(PromotionError) as caught:
        transition("rejected", "verified")
    assert caught.value.code == "prohibited-transition"
    source = Path("src/patchpilot_intelligence_evals/atomic_promotion.py").read_text(
        encoding="utf-8"
    )
    for token in ("shutil", "copyfile(", "os.replace(", "sendfile("):
        assert token not in source
