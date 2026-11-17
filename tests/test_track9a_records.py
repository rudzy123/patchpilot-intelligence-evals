"""Closed Track 9A corrections. They do not call Run or rewrite external files."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.corpus_continuation_plan import load_corpus_plan
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track9a_records import (
    PLAN_DIGEST,
    confirm_retained_files,
    load_corrected_interpretation,
    load_plan_disposition,
    load_proportionality_review,
    load_schema_forensics,
    load_stopped_attempt,
    load_telemetry_defect,
    load_track9a_review,
    load_track10_not_ready,
)

_RESULT_ROOT = Path("/var/tmp/patchpilot-evals-track9a-corpus")


def test_stopped_attempt_keeps_the_one_sealed_run() -> None:
    document = load_stopped_attempt()
    assert document["planDigest"] == PLAN_DIGEST
    assert document["plannedRuns"] == 72
    assert document["completedRuns"] == 1
    assert document["missingRuns"] == 71
    assert document["attemptOutcome"] == "stopped"
    assert document["stopCause"] == "telemetry-unresolved"
    assert document["executionStopAuthority"] == "measurement-infrastructure"
    assert document["externalEvidenceRewritten"] is False
    assert document["comparisonWinner"] is None
    assert document["calibrationStatus"] == "not-approved"
    assert document["selectionOutcome"] == "no-selection"
    assert document["productionReady"] is False
    assert len(document["retainedFiles"]) == 10
    if _RESULT_ROOT.is_dir():
        confirm_retained_files(_RESULT_ROOT)


def test_telemetry_defect_seals_the_complete_window() -> None:
    document = load_telemetry_defect()
    assert document["defect"] == "post-exit-read-downgrade"
    assert document["correctedDisposition"] == "sealed-complete-window"
    assert document["childState"] == "exited"
    assert document["postExitScope"] == "retained"
    assert document["cgroupCurrentBytes"] == 3_129_344
    assert document["cgroupPeakBytes"] == 5_709_541_376
    assert document["oomEvents"] == 0
    assert document["aggregatedWindowTelemetry"] == "complete"
    assert document["cleanup"] == "reaped"
    assert document["networkResult"] == "denied"
    assert document["downgradeRequiresContradiction"] is True
    assert document["incompleteTelemetryFailClosed"] is True
    assert document["sealedLaunchOmission"] is False
    assert document["observedExitClassification"] == "telemetry-unresolved"


def test_schema_forensics_separates_the_two_authorities() -> None:
    document = load_schema_forensics()
    assert document["runId"] == "case-ground-001-r1"
    assert document["rawContainsDeterministicFacts"] is True
    assert document["rawContainsFindingExplanation"] is True
    assert document["extractionPreservedObject"] is True
    assert document["jsonKeysPreserved"] is True
    assert document["innerObjectUnchanged"] is True
    assert document["fallbackShape"] is False
    assert document["adapterRenamedFields"] is False
    assert document["adapterRemovedFields"] is False
    assert document["adapterAddedInnerFields"] is False
    assert document["adapterWrappedEnvelope"] is True
    assert document["promptContractPresent"] is True
    assert document["promptContainsFindingExplanation"] is False
    assert document["responseSchemaVersion"] == "1.0.0"
    assert document["missingRequiredFields"] == [
        "schemaVersion",
        "candidate",
        "authorizedOrganizationId",
        "findingId",
        "refused",
        "refusalReason",
        "preservedDeterministicFacts",
        "sourceFacts",
        "supportedClaims",
        "remediationSuggestions",
        "uncertainty",
        "citations",
        "safetyWarnings",
        "explanationText",
        "nonAuthoritative",
    ]
    assert document["unexpectedFields"] == ["deterministicFacts", "findingExplanation"]
    assert document["stdoutTruncated"] is False
    assert document["stderrTruncated"] is False
    assert document["outputLimitStatus"] == "within-limit"
    assert document["responseFailureAuthority"] == "candidate-output"
    assert document["executionStopAuthority"] == "measurement-infrastructure"
    assert document["executionStopCause"] == "telemetry-unresolved"
    assert document["stdoutBytes"] == 542
    assert document["extractedBytes"] == 264
    assert document["stderrBytes"] == 0


def test_corrected_interpretation_stays_partial() -> None:
    document = load_corrected_interpretation()
    assert document["behavioralMeasurementAttempted"] is True
    assert document["behavioralMeasurementCompleted"] is False
    assert document["completedRuns"] == 1
    assert document["missingRuns"] == 71
    assert document["behavioralConclusion"] == "partial-inconclusive"
    assert document["candidateMetricsProduced"] is False
    assert document["candidateEvaluatedCompletely"] is False
    assert document["comparisonWinner"] is None
    assert document["calibrationStatus"] == "not-approved"
    assert document["selectionOutcome"] == "no-selection"
    assert document["productionReady"] is False


def test_plan_disposition_consumes_the_digest_without_a_replacement() -> None:
    document = load_plan_disposition()
    plan = load_corpus_plan()
    assert document["planDigest"] == plan["planDigest"] == PLAN_DIGEST
    assert plan["planDigest"] not in {row["planDigest"] for row in plan["consumedPlans"]}
    assert document["planDisposition"] == "consumed"
    assert document["reusable"] is False
    assert document["replacementPlanDigest"] == "not-issued"
    assert document["furtherPlanAssumed"] is False
    review = load_track9a_review()
    assert review["planDisposition"] == "consumed"
    assert review["replacementPlanDigest"] == "not-issued"
    assert "another Run" in review["notAuthorized"]
    assert "a replacement corpus plan" in review["notAuthorized"]
    proportionality = load_proportionality_review()
    assert proportionality["authorizesAnotherRun"] is False
    assert proportionality["authorizesReplacementPlan"] is False
    ready = load_track10_not_ready()
    assert ready["readinessOutcome"] == "not-ready"
    assert ready["verdict"] == "TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY"
    assert ready["reason"] == "telemetry-unresolved"
    assert ready["candidateMetricsProduced"] is False


def test_confirm_rejects_a_changed_retained_file(tmp_path: Path) -> None:
    with pytest.raises(MeasurementError) as caught:
        confirm_retained_files(tmp_path)
    assert caught.value.code == "record-drift"
    with pytest.raises(MeasurementError) as caught:
        confirm_retained_files(tmp_path / "absent")
    assert caught.value.code == "result-root-reuse"
