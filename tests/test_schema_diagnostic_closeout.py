"""Closeout records completion, retention, and blockers without selecting a candidate."""

from __future__ import annotations

from patchpilot_intelligence_evals.schema_diagnostic_closeout import (
    build_closeout,
    load_closeout_template,
)
from patchpilot_intelligence_evals.schema_diagnostic_plan import load_schema_diagnostic_plan
from patchpilot_intelligence_evals.schema_diagnostic_summary import (
    build_summary,
    placeholder_result,
)


def _summary(stop: str | None, qualifying: int) -> dict[str, object]:
    plan = load_schema_diagnostic_plan()
    rows = [placeholder_result(run) for run in plan["runs"]]
    for index, row in enumerate(rows):
        row["sealed"] = stop is None or index == 0
        if not row["sealed"]:
            continue
        row["exitClassification"] = "schema-failure" if index < qualifying else "success"
        row["schemaStatus"] = "invalid" if index < qualifying else "valid"
        row["qualifyingCandidateOutputSchemaFailure"] = index < qualifying
        if index < qualifying:
            row["responseFailureAuthority"] = "candidate-output"
            row["unexpectedFields"] = ["deterministicFacts"]
            row["missingRequired"] = ["explanationText"]
    if stop == "telemetry-unresolved":
        rows[0]["responseFailureAuthority"] = "measurement-infrastructure"
        rows[0]["qualifyingCandidateOutputSchemaFailure"] = False
        rows[0]["schemaStatus"] = "not-performed"
        rows[0]["exitClassification"] = "telemetry-unresolved"
    return build_summary(plan, rows, stop)


def test_committed_closeout_is_not_closed() -> None:
    document = load_closeout_template()
    assert document["closeoutState"] == "not-closed"
    assert document["blocker"] == "not-executed"
    assert document["diagnosticConclusion"] == "not-executed"
    assert document["automaticCandidateSelection"] is False


def test_closeout_covers_each_diagnostic_outcome() -> None:
    plan = load_schema_diagnostic_plan()
    established = _summary(None, 6)
    closeout = build_closeout(plan, established, None, cleanup="reaped", retention="retained")
    assert closeout["closeoutState"] == "closed"
    assert closeout["diagnosticConclusion"] == "systematic-schema-failure-established"
    assert closeout["blocker"] == "none"
    absent = _summary(None, 0)
    absent_closeout = build_closeout(plan, absent, None, cleanup="reaped", retention="retained")
    assert absent_closeout["diagnosticConclusion"] == "systematic-schema-failure-not-established"
    unreliable = _summary(None, 2)
    unreliable_closeout = build_closeout(
        plan, unreliable, None, cleanup="reaped", retention="retained"
    )
    assert unreliable_closeout["diagnosticConclusion"] == "schema-behavior-unreliable-or-unresolved"
    stopped = _summary("telemetry-unresolved", 0)
    stopped_closeout = build_closeout(
        plan,
        stopped,
        "telemetry-unresolved",
        cleanup="reaped",
        retention="retained",
    )
    assert stopped_closeout["closeoutState"] == "stopped"
    assert stopped_closeout["diagnosticConclusion"] == "diagnostic-incomplete"
    assert stopped_closeout["productionReady"] is False
