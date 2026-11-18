"""Plan identity, consumed-plan rejection, and the fresh result root."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    FRESH_RESULT_ROOT,
    TRACK10_AUTHORIZATION_DIGEST,
    TRACK10_REVIEW_DIGEST,
    diagnostic_rejections,
    load_schema_diagnostic_approval,
    load_schema_diagnostic_plan,
    require_schema_diagnostic_approval,
    systematic_threshold,
    validate_diagnostic_root,
)
from patchpilot_intelligence_evals.six_run_diagnostic_authorization import (
    load_six_run_authorization,
)
from patchpilot_intelligence_evals.track9a_records import PLAN_DIGEST as CORPUS_PLAN_DIGEST

_CONSUMED = (
    "8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2",
    "572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b",
    "2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350",
    CORPUS_PLAN_DIGEST,
)


def test_plan_binds_track10_and_stays_not_executed() -> None:
    plan = load_schema_diagnostic_plan()
    approval = load_schema_diagnostic_approval()
    authorization = load_six_run_authorization()
    assert plan["planDigest"] not in _CONSUMED
    assert plan["sessionId"] == "intelligence-track-10a"
    assert plan["plannedRuns"] == 6
    assert plan["repetitionsPerCase"] == 1
    assert plan["retries"] == 0
    assert plan["currentExecutionAuthority"] is False
    assert plan["executionStatus"] == "not-executed"
    assert plan["resultRootState"] == "not-created"
    assert plan["fullCorpusExecuted"] is False
    assert plan["memoryRerun"] is False
    assert plan["contextMemoryRerun"] is False
    assert plan["percentageMetrics"] is False
    assert plan["promotionGateAttempt"] is False
    assert plan["selectionOutcome"] == "no-selection"
    assert plan["calibrationStatus"] == "not-approved"
    assert plan["comparisonWinner"] is None
    assert plan["productionReady"] is False
    assert plan["systematicThreshold"] == systematic_threshold()
    assert plan["track10AuthorizationDigest"] == TRACK10_AUTHORIZATION_DIGEST
    assert plan["track10ReviewDigest"] == TRACK10_REVIEW_DIGEST
    assert approval["approvalStatus"] == "not-approved"
    assert approval["planDigest"] == plan["planDigest"]
    assert approval["runs"] == plan["runs"]
    assert authorization["futurePlanDigest"] == "not-issued"
    assert authorization["operationalCaseIds"] == "not-selected"
    assert authorization["currentExecutionAuthority"] is False
    assert plan["historicalResponse"]["countedInDiagnostic"] is False
    assert "full-corpus" in plan["omittedPhases"]
    assert "context-4096" in plan["omittedPhases"]
    assert "context-8192" in plan["omittedPhases"]


def test_historical_plans_are_rejected_before_launch() -> None:
    rows = diagnostic_rejections()
    assert [row["digest"] for row in rows] == list(_CONSUMED)
    assert {row["result"] for row in rows} == {"plan-consumed"}
    for digest in _CONSUMED:
        with pytest.raises(MeasurementError) as caught:
            require_schema_diagnostic_approval(digest)
        assert caught.value.code == "plan-consumed"
    plan = require_schema_diagnostic_approval(load_schema_diagnostic_plan()["planDigest"])
    assert plan["runInvoked"] is False


def test_historical_result_roots_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(MeasurementError) as caught:
        validate_diagnostic_root(Path("/var/tmp/patchpilot-evals-track9a-corpus"), resume=False)
    assert caught.value.code == "result-root-reuse"
    root = tmp_path / "fresh-diagnostic"
    root.mkdir(mode=0o700)
    validated = validate_diagnostic_root(root, resume=False)
    assert validated == root.resolve()
    assert FRESH_RESULT_ROOT.name == "patchpilot-evals-track10a-schema"
    assert "track9a" not in FRESH_RESULT_ROOT.name
