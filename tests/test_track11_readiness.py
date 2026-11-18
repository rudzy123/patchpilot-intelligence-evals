"""Track 11 readiness stays advisory for every diagnostic conclusion."""

from __future__ import annotations

from patchpilot_intelligence_evals.schema_diagnostic_closeout import build_closeout
from patchpilot_intelligence_evals.schema_diagnostic_plan import load_schema_diagnostic_plan
from patchpilot_intelligence_evals.schema_diagnostic_summary import (
    build_summary,
    placeholder_result,
)
from patchpilot_intelligence_evals.track11_readiness import load_track11_template, recommend


def _ready(qualifying: int, stop: str | None) -> dict[str, object]:
    plan = load_schema_diagnostic_plan()
    rows = [placeholder_result(run) for run in plan["runs"]]
    for index, row in enumerate(rows):
        row["sealed"] = stop is None or index == 0
        if not row["sealed"]:
            continue
        row["schemaStatus"] = "invalid" if index < qualifying else "valid"
        row["exitClassification"] = "schema-failure" if index < qualifying else "success"
        row["qualifyingCandidateOutputSchemaFailure"] = index < qualifying
        if index < qualifying:
            row["responseFailureAuthority"] = "candidate-output"
            row["unexpectedFields"] = ["deterministicFacts"]
            row["missingRequired"] = ["explanationText"]
    if stop == "gold-visible":
        rows[0]["sealed"] = True
        rows[0]["qualifyingCandidateOutputSchemaFailure"] = False
        rows[0]["responseFailureAuthority"] = "security-boundary"
        rows[0]["exitClassification"] = "isolation-failure"
    summary = build_summary(plan, rows, stop)
    cleanup = "not-performed" if stop is None and qualifying == 0 and False else "reaped"
    retention = "retained" if summary["completedRuns"] else "not-performed"
    closeout = build_closeout(plan, summary, stop, cleanup=cleanup, retention=retention)
    return recommend(closeout, summary)


def test_committed_readiness_is_not_executed() -> None:
    document = load_track11_template()
    assert document["readinessOutcome"] == "not-executed"
    assert document["authorizesFullCorpus"] is False
    assert document["authorizesRejection"] is False
    assert document["authorizesSelection"] is False
    assert document["rejectionEligibleForReview"] is False
    assert document["productionReady"] is False


def test_readiness_follows_the_diagnostic_conclusion() -> None:
    established = _ready(6, None)
    assert established["readinessOutcome"] == "ready-for-disposition-review"
    assert established["rejectionEligibleForReview"] is True
    assert established["authorizesRejection"] is False
    assert established["authorizesFullCorpus"] is False
    assert established["nextRecommendation"] == "disposition-review-eligible"
    absent = _ready(0, None)
    assert absent["readinessOutcome"] == "advisory-not-established"
    assert absent["proportionalityReviewEligible"] is True
    assert absent["authorizesFullCorpus"] is False
    unreliable = _ready(2, None)
    assert unreliable["readinessOutcome"] == "not-ready"
    incomplete = _ready(0, "telemetry-unresolved")
    assert incomplete["readinessOutcome"] == "not-ready"
    blocked = _ready(0, "gold-visible")
    assert blocked["readinessOutcome"] == "blocked"
    assert blocked["verdict"] == "BLOCKED BY UNRESOLVED AUTHORITY"
    assert blocked["selectionOutcome"] == "no-selection"
