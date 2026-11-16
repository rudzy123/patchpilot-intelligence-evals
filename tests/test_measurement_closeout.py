"""Closeout keeps a stopped session reviewable and a finished session closed."""

from __future__ import annotations

import json
from pathlib import Path

from patchpilot_intelligence_evals.context_measurement import PHASE_FILES
from patchpilot_intelligence_evals.measurement_closeout import (
    build_closeout,
    load_closeout_template,
)
from patchpilot_intelligence_evals.measurement_plan import PHASE_ORDER


def test_template_is_not_closed() -> None:
    document = load_closeout_template()
    assert document["closeoutState"] == "not-closed"
    assert document["productionReady"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert [item["status"] for item in document["phases"]] == ["not-executed"] * len(PHASE_ORDER)


def test_failed_phase_stops_closeout(tmp_path: Path) -> None:
    (tmp_path / PHASE_FILES["preflight"]).write_text(
        json.dumps({"status": "ok", "realModelExecuted": False}),
        encoding="utf-8",
    )
    (tmp_path / PHASE_FILES["one-token-smoke"]).write_text(
        json.dumps(
            {
                "exitClassification": "oom",
                "processCleanup": "reaped",
                "realModelExecuted": True,
            }
        ),
        encoding="utf-8",
    )
    document = build_closeout(tmp_path)
    statuses = {item["phase"]: item["status"] for item in document["phases"]}
    assert statuses["preflight"] == "passed"
    assert statuses["one-token-smoke"] == "failed"
    assert statuses["short-generation"] == "not-executed"
    assert document["closeoutState"] == "stopped"
    assert document["stopCause"] == "oom"
    assert document["productionReady"] is False


def test_all_passed_phases_close(tmp_path: Path) -> None:
    for phase in PHASE_ORDER:
        if phase == "preflight":
            payload: dict[str, object] = {"status": "ok", "realModelExecuted": False}
        elif phase == "corpus-evaluation":
            payload = {
                "realModelExecuted": True,
                "ungatedCanonicalAgreement": "agree",
            }
        else:
            payload = {
                "exitClassification": "success",
                "processCleanup": "reaped",
                "realModelExecuted": True,
            }
        (tmp_path / PHASE_FILES[phase]).write_text(json.dumps(payload), encoding="utf-8")
    document = build_closeout(tmp_path)
    assert document["closeoutState"] == "closed"
    assert document["stopCause"] is None
    assert all(item["status"] == "passed" for item in document["phases"])
