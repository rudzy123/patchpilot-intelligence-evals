"""Closeout and cleanup. No external artifact is present."""

from __future__ import annotations

from pathlib import Path

from patchpilot_intelligence_evals.acquisition_closeout import (
    build_closeout,
    cleanup_incomplete,
    load_closeout_template,
    not_closed_closeout,
)


def test_closeout_template_is_not_closed() -> None:
    document = load_closeout_template()
    assert document == not_closed_closeout()
    assert document["closeoutState"] == "not-closed"
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["measurementPerformed"] is False
    assert document["productionReady"] is False
    assert document["gitTrackedArtifact"] is False


def test_rejected_closeout_does_not_select() -> None:
    document = build_closeout(
        [{"kind": "runtime", "outcome": "rejected", "reason": "digest-mismatch"}],
        promoted=[],
        reclaimed_bytes=0,
        approval="required",
    )
    assert document["acquisitionStatus"] == "rejected"
    assert document["selectionOutcome"] == "no-selection"
    assert document["realModelExecuted"] is False
    assert document["installationAuthorized"] is False


def test_cleanup_is_idempotent(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    attempt = cache / "quarantine" / "clean-1"
    attempt.mkdir(parents=True)
    (attempt / "note.txt").write_bytes(b"abc")
    reclaimed = cleanup_incomplete(cache, "clean-1")
    assert reclaimed == 3
    assert cleanup_incomplete(cache, "clean-1") == 0
