"""Verification seals for bounded synthetic quarantine trees."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.verification_seal import (
    SealError,
    inventory_identity,
    load_seal,
    not_acquired_seal,
    seal_directory,
)

_MTIME = 1_700_000_000_000_000_000


def _expected(payload: bytes, name: str = "note.txt") -> list[dict[str, object]]:
    return [{"relativeName": name, "logicalBytes": len(payload), "sha256": None}]


def _directory(tmp_path: Path, payload: bytes = b"synthetic") -> Path:
    directory = tmp_path / "attempt"
    directory.mkdir(parents=True)
    path = directory / "note.txt"
    path.write_bytes(payload)
    os.utime(path, ns=(_MTIME, _MTIME))
    return directory


def test_valid_inventory_seals_without_execution_authority(tmp_path: Path) -> None:
    payload = b"synthetic"
    directory = _directory(tmp_path, payload)
    seal = seal_directory(
        directory,
        _expected(payload),
        attempt_id="attempt-1",
    )
    assert seal["sealState"] == "sealed"
    assert seal["executionEligibility"] == "prohibited"
    assert seal["executionStatus"] == "not-executed"
    assert seal["laterSessionEligibility"] == "none"
    assert seal["locallyObservedArtifactDigests"] == []
    assert seal["logicalInventoryBytes"] == len(payload)
    assert seal["files"][0]["metadataMatches"] is True
    assert seal["files"][0]["preVerification"]["logicalBytes"] == len(payload)
    assert len(str(seal["files"][0]["sha256"])) == 64
    assert seal["files"][0]["expectedSha256"] is None
    assert load_seal(directory)["identityDigest"] == seal["identityDigest"]
    template = not_acquired_seal()
    assert template["sealState"] == "not-acquired"
    assert template["files"] == []


def test_inventory_identity_is_deterministic(tmp_path: Path) -> None:
    payload = b"synthetic"
    left = seal_directory(
        _directory(tmp_path / "left", payload), _expected(payload), attempt_id="a1"
    )
    right = seal_directory(
        _directory(tmp_path / "right", payload),
        _expected(payload),
        attempt_id="a1",
    )
    assert left["inventoryIdentity"] == right["inventoryIdentity"]
    assert left["identityDigest"] == right["identityDigest"]
    assert left["inventoryIdentity"] == inventory_identity(left["files"])


def test_missing_unexpected_size_and_digest(tmp_path: Path) -> None:
    directory = _directory(tmp_path)
    with pytest.raises(SealError) as caught:
        seal_directory(directory, [], attempt_id="attempt-1")
    assert caught.value.code == "missing-file"
    (directory / "extra.txt").write_bytes(b"extra")
    with pytest.raises(SealError) as caught:
        seal_directory(directory, _expected(b"synthetic"), attempt_id="attempt-1")
    assert caught.value.code == "unexpected-file"
    extra = tmp_path / "size"
    extra.mkdir()
    (extra / "note.txt").write_bytes(b"synthetic")
    with pytest.raises(SealError) as caught:
        seal_directory(
            extra,
            [{"relativeName": "note.txt", "logicalBytes": 2, "sha256": None}],
            attempt_id="attempt-1",
        )
    assert caught.value.code == "size-mismatch"
    digest = hashlib.sha256(b"other").hexdigest()
    with pytest.raises(SealError) as caught:
        seal_directory(
            _directory(tmp_path / "digest"),
            [{"relativeName": "note.txt", "logicalBytes": 9, "sha256": digest}],
            attempt_id="attempt-1",
        )
    assert caught.value.code == "digest-mismatch"


def test_content_and_metadata_mutation_fail(tmp_path: Path) -> None:
    directory = _directory(tmp_path)
    path = directory / "note.txt"

    def grow(target: Path) -> None:
        target.write_bytes(b"synthetic-mutated")

    with pytest.raises(SealError) as caught:
        seal_directory(directory, _expected(b"synthetic"), attempt_id="attempt-1", during_hash=grow)
    assert caught.value.code == "mutated-during-verification"
    path.write_bytes(b"synthetic")
    os.utime(path, ns=(_MTIME, _MTIME))

    def retouch(target: Path) -> None:
        os.utime(target, ns=(_MTIME + 5, _MTIME + 5))

    with pytest.raises(SealError) as caught:
        seal_directory(
            directory,
            _expected(b"synthetic"),
            attempt_id="attempt-1",
            during_hash=retouch,
        )
    assert caught.value.code == "mutated-during-verification"


def test_duplicate_case_and_non_utf8_paths(tmp_path: Path) -> None:
    directory = _directory(tmp_path)
    with pytest.raises(SealError) as caught:
        seal_directory(
            directory,
            _expected(b"synthetic") + _expected(b"synthetic"),
            attempt_id="attempt-1",
        )
    assert caught.value.code == "duplicate-path"
    folded = tmp_path / "case"
    folded.mkdir()
    (folded / "A.txt").write_bytes(b"A")
    (folded / "a.txt").write_bytes(b"a")
    with pytest.raises(SealError) as caught:
        seal_directory(
            folded,
            [
                {"relativeName": "A.txt", "logicalBytes": 1, "sha256": None},
                {"relativeName": "a.txt", "logicalBytes": 1, "sha256": None},
            ],
            attempt_id="attempt-1",
        )
    assert caught.value.code == "case-collision"
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "note.txt").write_bytes(b"abc")
    descriptor = os.open(
        os.path.join(os.fsencode(raw), b"bad-\xff.txt"),
        os.O_CREAT | os.O_WRONLY,
        0o644,
    )
    os.close(descriptor)
    with pytest.raises(SealError) as caught:
        seal_directory(raw, _expected(b"abc"), attempt_id="attempt-1")
    assert caught.value.code == "non-utf8-path"


def test_symlink_and_traversal_are_rejected(tmp_path: Path) -> None:
    directory = _directory(tmp_path)
    (directory / "link.txt").symlink_to(directory / "note.txt")
    with pytest.raises(SealError) as caught:
        seal_directory(directory, _expected(b"synthetic"), attempt_id="attempt-1")
    assert caught.value.code == "symlink"
    dangling = tmp_path / "dangling"
    dangling.mkdir()
    (dangling / "note.txt").write_bytes(b"synthetic")
    (dangling / "gone.txt").symlink_to(dangling / "missing.txt")
    with pytest.raises(SealError) as caught:
        seal_directory(dangling, _expected(b"synthetic"), attempt_id="attempt-1")
    assert caught.value.code == "dangling-symlink"
    with pytest.raises(SealError) as caught:
        seal_directory(
            _directory(tmp_path / "travel"),
            [{"relativeName": "../note.txt", "logicalBytes": 1, "sha256": None}],
            attempt_id="attempt-1",
        )
    assert caught.value.code == "path-traversal"
    with pytest.raises(SealError) as caught:
        seal_directory(
            _directory(tmp_path / "absolute"),
            [{"relativeName": "/tmp/note.txt", "logicalBytes": 1, "sha256": None}],
            attempt_id="attempt-1",
        )
    assert caught.value.code == "absolute-path"
