"""Durable correction records. They do not rewrite the external result."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.measurement_retry_plan import (
    load_retry_approval,
    load_retry_plan,
    require_open_retry_plan,
)
from patchpilot_intelligence_evals.retry_track9_readiness import load_track9_template
from patchpilot_intelligence_evals.track8b_r1_records import (
    SMOKE_PEAK_BYTES,
    load_corrected_closeout,
    load_dependency_defect,
    load_memory_defect,
    load_retry_disposition,
    load_stopped_attempt,
    load_stopped_track9,
    load_track8b_r1_review,
)


def test_stopped_attempt_preserves_the_fail_closed_facts() -> None:
    plan = load_retry_plan()
    attempt = load_stopped_attempt()
    closeout = load_corrected_closeout()
    assert plan["executionStatus"] == "not-executed"
    assert plan["planDigest"] == attempt["planDigest"]
    assert load_retry_approval()["approvalStatus"] == "not-approved"
    for document in (attempt, closeout):
        assert document["attemptOutcome"] == "stopped"
        assert document["failureCategory"] == "inference-failure"
        assert document["failureAuthority"] == "measurement-infrastructure"
        assert document["runInvoked"] is False
        assert document["modelSessionCreated"] is False
        assert document["realModelExecuted"] is False
        assert document["shortGeneration"] == "withheld"
        assert document["context4096"] == "withheld"
        assert document["context8192"] == "withheld"
        assert document["corpusEvaluation"] == "not-started"
        assert document["candidateMetrics"] == "not-produced"
        assert document["selectionOutcome"] == "no-selection"
        assert document["calibrationStatus"] == "not-approved"
        assert document["track9Readiness"] == "not-ready"
        assert document["productionReady"] is False
        assert document["measurementPerformed"] is False


def test_corrected_closeout_does_not_use_smoke_as_context_eligibility() -> None:
    document = load_corrected_closeout()
    defect = load_memory_defect()
    assert document["memoryConclusion"] == "unavailable"
    assert document["closeoutState"] == "stopped"
    assert document["smokePeakBytes"] == SMOKE_PEAK_BYTES
    assert document["smokeEvidenceRole"] == "smoke-only"
    assert document["smokeEstablishesContextEligibility"] is False
    assert defect["correctedConclusion"] == "unavailable"
    assert defect["emptyPhaseSetWasWithinCeiling"] is True
    assert defect["smokePeakBytes"] == SMOKE_PEAK_BYTES


def test_plan_disposition_is_consumed_and_not_reusable() -> None:
    document = load_retry_disposition()
    assert document["planDigest"] == load_retry_plan()["planDigest"]
    assert document["planDisposition"] == "consumed"
    assert document["reusable"] is False
    assert document["replacementPlanDigest"] == "not-issued"
    assert document["executionStatus"] == "not-executed"
    assert document["nextRunRequiresNewPlan"] is True
    assert document["nextRunRequiresNewSession"] is True
    assert document["nextRunRequiresFreshResultRoot"] is True
    assert document["nextRunRequiresOperatorApproval"] is True
    assert document["runInvoked"] is False
    with pytest.raises(MeasurementError) as caught:
        require_open_retry_plan()
    assert caught.value.code == "plan-consumed"


def test_track9_stays_not_ready() -> None:
    template = load_track9_template()
    observed = load_stopped_track9()
    review = load_track8b_r1_review()
    assert template["readinessOutcome"] == "not-ready"
    assert template["reason"] == "measurement-not-performed"
    assert observed["readinessOutcome"] == "not-ready"
    assert observed["reason"] == "inference-failure"
    assert observed["verdict"] == "TRACK 9 EVALUATION REVIEW NOT READY"
    assert observed["realModelExecuted"] is False
    assert review["track9Readiness"] == "not-ready"
    assert review["memoryConclusion"] == "unavailable"
    assert review["planDisposition"] == "consumed"
    assert review["replacementPlanDigest"] == "not-issued"
    assert review["reviewDigest"] == review_digest(review)


def test_dependency_record_has_no_host_path() -> None:
    document = load_dependency_defect()
    text = Path("candidates/authorization/track8b-r1-dependency-mount-defect.json").read_text(
        encoding="utf-8"
    )
    assert "/" not in text
    assert document["providerMounted"] is False
    assert document["broadDirectoryMounted"] is False
    assert document["modelSessionCreated"] is False
    assert document["runInvoked"] is False
    assert document["networkUsed"] is False
    assert document["failureBeforeSession"] == "before-create-session"
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["track8b-r1-dependency-mount-defect-validation"])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["status"] == "ok"
    assert summary["defectStatus"] == "corrected-before-commit"
    assert summary["providerMounted"] is False
