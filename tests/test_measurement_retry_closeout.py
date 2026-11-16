"""Closeout withholds later phases and keeps calibration unapproved."""

from __future__ import annotations

import json
from pathlib import Path

from patchpilot_intelligence_evals.measurement_retry_closeout import (
    build_closeout,
    load_closeout_template,
)
from patchpilot_intelligence_evals.measurement_retry_plan import PHASE_ORDER


def test_template_is_not_closed() -> None:
    document = load_closeout_template()
    assert document["closeoutState"] == "not-closed"
    assert document["calibrationStatus"] == "not-approved"
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False
    assert [item["phase"] for item in document["phases"]] == list(PHASE_ORDER)
    assert {item["status"] for item in document["phases"]} == {"not-executed"}


def test_failed_phase_withholds_later_phases(tmp_path: Path) -> None:
    root = tmp_path / "result"
    root.mkdir()
    (root / "preflight.json").write_text(
        json.dumps({"status": "ok", "runInvoked": False}),
        encoding="utf-8",
    )
    (root / "template-compatibility.json").write_text(
        json.dumps({"compatibility": "identity-mismatch", "runInvoked": False}),
        encoding="utf-8",
    )
    document = build_closeout(root)
    statuses = {item["phase"]: item["status"] for item in document["phases"]}
    assert statuses["template-compatibility"] == "failed"
    assert statuses["one-token-smoke"] == "withheld"
    assert statuses["context-8192"] == "withheld"
    assert statuses["corpus-evaluation"] == "withheld"
    assert document["closeoutState"] == "stopped"
    assert document["behavioralConclusion"] == "withheld"
    assert document["calibrationRemainedNotApproved"] is True
    assert document["productionReady"] is False
