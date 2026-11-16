"""Atomic promotion of a populated attempt. The payload is synthetic."""

from __future__ import annotations

import hashlib
from pathlib import Path

from patchpilot_intelligence_evals.acquired_artifact_validation import (
    close_and_promote,
    load_digest_template,
    not_acquired_digests,
    promotion_is_atomic,
)
from patchpilot_intelligence_evals.atomic_promotion import covers_contract


def test_promotion_delegates_to_rename() -> None:
    assert promotion_is_atomic()
    assert covers_contract()


def test_digest_template_is_empty() -> None:
    document = load_digest_template()
    assert document == not_acquired_digests()
    assert document["runtimeDigests"] == []
    assert document["modelDigests"] == []
    assert document["tokenizerDigests"] == []
    assert document["productionReady"] is False


def test_close_and_promote_renames(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    attempt = cache / "quarantine" / "note-1"
    attempt.mkdir(parents=True)
    payload = b"synthetic\n"
    (attempt / "note.txt").write_bytes(payload)
    expected = [
        {
            "logicalBytes": len(payload),
            "relativeName": "note.txt",
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    ]
    result = close_and_promote(cache, "note-1", expected)
    assert result["receipt"]["copyFallbackUsed"] is False
    assert result["receipt"]["receiptState"] == "verified"
    assert not attempt.exists()
    promoted = cache / "verified" / "note-1" / "note.txt"
    assert promoted.read_bytes() == payload
