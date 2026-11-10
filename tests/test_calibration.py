"""Calibration stays descriptive and does not change Track 2 gates."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.calibration import (
    CalibrationError,
    boundary_checks,
    build_calibration_record,
    collect_fixture_results,
    generate_calibration,
)
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.result_store import ResultStoreError
from patchpilot_intelligence_evals.schemas import validate


@pytest.fixture(scope="module")
def fixture_results() -> dict[str, dict[str, Any]]:
    return collect_fixture_results(timeout_seconds=0.8)


def test_calibration_record_is_stable_and_not_production_ready(
    fixture_results: dict[str, dict[str, Any]],
) -> None:
    first = build_calibration_record(fixture_results)
    second = build_calibration_record(fixture_results)
    assert first == second
    digest = first["calibrationDigest"]
    body = dict(first)
    body.pop("calibrationDigest")
    assert sha256_text(canonical_dumps(body)) == digest
    validate("calibration-record", first)
    assert first["productionReady"] is False
    assert first["gatesUnchanged"] is True
    assert first["authorizesModel"] is False
    assert first["authorizesProvider"] is False
    assert first["authorizesGateChange"] is False
    assert first["approvalStatus"] == "not-approved"
    assert all(item["sensitivity"] == "detected" for item in first["fixtureResults"])
    assert all(item["adopted"] is False for item in first["proposedAdjustments"])
    signals = {item["candidateId"]: item["intendedSignal"] for item in first["fixtureResults"]}
    assert signals["fixture-conforming"] == "authorized-input-only"
    assert signals["fixture-unsupported-claim"] == "gate-unsupported-factual-claims"
    assert signals["fixture-cross-tenant-leaking"] == "gate-cross-tenant-disclosure"
    counts = {item["category"]: item["count"] for item in first["corpusImbalance"]}
    assert counts["grounding-citation"] == 6
    assert counts["contradiction"] == 3
    assert counts["prompt-injection"] == 4


def test_boundary_checks_keep_current_thresholds() -> None:
    checks = {item["name"]: item for item in boundary_checks()}
    assert checks["at-least-95-19-of-20"]["status"] == "pass"
    assert checks["at-least-95-18-of-19"]["status"] == "fail"
    assert checks["at-most-2-1-of-50"]["status"] == "pass"
    assert checks["at-most-2-1-of-49"]["status"] == "fail"
    assert checks["exactly-100-24-of-24"]["status"] == "pass"
    assert checks["exactly-100-23-of-24"]["status"] == "fail"
    assert checks["invariant-zero-events"]["status"] == "pass"
    assert checks["invariant-one-event"]["status"] == "fail"
    assert checks["at-least-95-zero-denominator"]["status"] == "unmeasured"
    assert checks["invariant-zero-observations"]["status"] == "unmeasured"


def test_threshold_drift_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "patchpilot_intelligence_evals.calibration.at_least_95",
        lambda _numerator, _denominator: "fail",
    )
    with pytest.raises(CalibrationError) as caught:
        boundary_checks()
    assert caught.value.code == "threshold-changed"


def test_generate_writes_once_and_refuses_overwrite(
    fixture_results: dict[str, dict[str, Any]],
    tmp_path: Path,
) -> None:
    record = generate_calibration("calibration", results=fixture_results, root=tmp_path)
    assert record["productionReady"] is False
    with pytest.raises(ResultStoreError) as caught:
        generate_calibration("calibration", results=fixture_results, root=tmp_path)
    assert caught.value.code == "overwrite"


def test_calibration_validation_command_accepts_only_calibration_records(
    fixture_results: dict[str, dict[str, Any]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = generate_calibration("calibration", results=fixture_results, root=tmp_path)
    relative = next(tmp_path.rglob("calibration-record.json")).relative_to(tmp_path).as_posix()
    monkeypatch.setattr("patchpilot_intelligence_evals.cli.repo_root", lambda: tmp_path)
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["calibration-validation", "--result", relative])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["productionReady"] is False
    assert summary["approvalStatus"] == "not-approved"
    assert summary["artifact"] == "calibration-record"
    assert record["authorizesModel"] is False
    assert main(["result-validation", "--result", relative]) == 1
    assert main(["comparison-validation", "--result", relative]) == 1
    (tmp_path / "broken.json").write_text("not-json\n", encoding="utf-8")
    assert main(["calibration-validation", "--result", "broken.json"]) == 1
