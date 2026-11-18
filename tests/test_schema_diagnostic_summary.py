"""Threshold counts, category coverage, and response-shape consistency."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.candidate_inference_main import pre_wrap_field_names
from patchpilot_intelligence_evals.response_diagnostics import diagnose_response, generation_facts
from patchpilot_intelligence_evals.schema_diagnostic_attribution import attribution_chain
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    load_schema_diagnostic_plan,
    systematic_threshold,
)
from patchpilot_intelligence_evals.schema_diagnostic_summary import (
    build_summary,
    classify_diagnostic,
    load_summary_template,
    placeholder_result,
)


def _inventory() -> list[dict[str, Any]]:
    plan = load_schema_diagnostic_plan()
    return [placeholder_result(run) for run in plan["runs"]]


def _seal(row: dict[str, Any], *, schema_status: str = "valid") -> None:
    row["sealed"] = True
    row["schemaStatus"] = schema_status
    row["exitClassification"] = "success" if schema_status == "valid" else "schema-failure"


def _qualify(row: dict[str, Any], category: str, field: str = "deterministicFacts") -> None:
    _seal(row, schema_status="invalid")
    row["qualifyingCandidateOutputSchemaFailure"] = True
    row["responseFailureAuthority"] = "candidate-output"
    row["category"] = category
    row["unexpectedFields"] = [field]
    row["missingRequired"] = ["explanationText"]


def test_committed_summary_is_not_executed() -> None:
    document = load_summary_template()
    assert document["diagnosticConclusion"] == "not-executed"
    assert document["thresholdMet"] is False
    assert document["plannedRuns"] == 6
    assert document["percentageMetrics"] is False
    assert document["systematicThreshold"] == systematic_threshold()
    assert len(document["runResults"]) == 6


def test_threshold_matrix_covers_counts_and_categories() -> None:
    categories = [row["category"] for row in _inventory()]

    def conclude(
        qualifying: list[tuple[int, str]], *, unresolved: int = 0, stop: str | None = None
    ) -> str:
        rows = _inventory()
        for index, _category in enumerate(rows):
            _seal(rows[index])
        for index, category in qualifying:
            _qualify(rows[index], category)
        for index in range(unresolved):
            rows[index]["sealed"] = True
            rows[index]["qualifyingCandidateOutputSchemaFailure"] = False
            rows[index]["responseFailureAuthority"] = "unresolved"
            rows[index]["schemaStatus"] = "invalid"
        decision = classify_diagnostic(rows, stop)
        return str(decision["diagnosticConclusion"])

    assert conclude([]) == "systematic-schema-failure-not-established"
    assert conclude([(0, categories[0])]) == "systematic-schema-failure-not-established"
    assert conclude([(0, categories[0]), (1, categories[1])]) == (
        "schema-behavior-unreliable-or-unresolved"
    )
    assert conclude([(0, categories[0]), (1, categories[1]), (2, categories[2])]) == (
        "schema-behavior-unreliable-or-unresolved"
    )
    four_two = conclude(
        [
            (0, categories[0]),
            (1, categories[0]),
            (2, categories[1]),
            (3, categories[1]),
        ]
    )
    assert four_two == "schema-behavior-unreliable-or-unresolved"
    four_three = conclude(
        [
            (0, categories[0]),
            (1, categories[0]),
            (2, categories[1]),
            (3, categories[2]),
        ]
    )
    assert four_three == "systematic-schema-failure-established"
    assert conclude([(index, categories[index]) for index in range(5)]) == (
        "systematic-schema-failure-established"
    )
    assert conclude([(index, categories[index]) for index in range(6)]) == (
        "systematic-schema-failure-established"
    )
    assert conclude([], unresolved=1) == "schema-behavior-unreliable-or-unresolved"
    assert conclude([], stop="telemetry-unresolved") == "diagnostic-incomplete"
    assert conclude([], stop="oom") == "diagnostic-incomplete"
    assert conclude([], stop="gold-visible") == "blocked-by-unresolved-authority"


def test_divergent_shapes_do_not_veto_a_met_threshold() -> None:
    rows = _inventory()
    categories = [row["category"] for row in rows]
    for index, row in enumerate(rows):
        _qualify(
            row, categories[index], "deterministicFacts" if index < 3 else "findingExplanation"
        )
    decision = classify_diagnostic(rows, None)
    assert decision["thresholdMet"] is True
    assert decision["diagnosticConclusion"] == "systematic-schema-failure-established"
    assert decision["responseShapeConsistency"] == "divergent"
    summary = build_summary(load_schema_diagnostic_plan(), rows, None)
    assert summary["automaticCandidateRejection"] is False
    assert summary["comparisonWinner"] is None


def test_attribution_chain_counts_only_complete_candidate_failures() -> None:
    raw = {
        "outputLimitStatus": "within-limit",
        "retentionStatus": "retained",
        "stderrTruncated": False,
        "stdoutTruncated": False,
    }
    diagnostic = {
        "adapterFallback": False,
        "adapterTruncated": False,
        "extractedDigest": "a" * 64,
        "extractionStatus": "extracted",
        "parseStatus": "parsed",
        "schemaStatus": "invalid",
        "trailingBytes": 0,
    }
    qualifying = attribution_chain(
        exit_classification="schema-failure",
        raw=raw,
        diagnostic=diagnostic,
        side_names=["explanationText"],
        extracted_names=["explanationText"],
    )
    assert qualifying["qualifyingCandidateOutputSchemaFailure"] is True
    assert qualifying["responseFailureAuthority"] == "candidate-output"
    mutated = attribution_chain(
        exit_classification="schema-failure",
        raw=raw,
        diagnostic=diagnostic,
        side_names=["explanationText"],
        extracted_names=["deterministicFacts"],
    )
    assert mutated["responseFailureAuthority"] == "adapter"
    assert mutated["qualifyingCandidateOutputSchemaFailure"] is False
    truncated = attribution_chain(
        exit_classification="schema-failure",
        raw={**raw, "stdoutTruncated": True},
        diagnostic=diagnostic,
        side_names=["explanationText"],
        extracted_names=["explanationText"],
    )
    assert truncated["qualifyingCandidateOutputSchemaFailure"] is False
    limited = attribution_chain(
        exit_classification="excessive-output",
        raw={**raw, "outputLimitStatus": "stdout-limit-exceeded"},
        diagnostic=diagnostic,
        side_names=["explanationText"],
        extracted_names=["explanationText"],
    )
    assert limited["responseFailureAuthority"] == "protocol"
    unresolved = attribution_chain(
        exit_classification="malformed-response",
        raw=raw,
        diagnostic={**diagnostic, "parseStatus": "malformed-json", "schemaStatus": "not-performed"},
        side_names=None,
        extracted_names=None,
    )
    assert unresolved["responseFailureAuthority"] == "unresolved"
    empty = attribution_chain(
        exit_classification="malformed-response",
        raw=raw,
        diagnostic={
            **diagnostic,
            "extractedDigest": None,
            "extractionStatus": "empty",
            "parseStatus": "empty",
            "schemaStatus": "not-performed",
        },
        side_names=None,
        extracted_names=None,
    )
    assert empty["qualifyingCandidateOutputSchemaFailure"] is False
    evaluator = attribution_chain(
        exit_classification="evaluator-failure",
        raw=raw,
        diagnostic=diagnostic,
        side_names=["explanationText"],
        extracted_names=["explanationText"],
    )
    assert evaluator["responseFailureAuthority"] == "evaluator"
    assert pre_wrap_field_names('{"explanationText":"hidden","surprise":1}') == [
        "explanationText",
        "surprise",
    ]
    assert pre_wrap_field_names('prose {"explanationText":1}') is None
    assert pre_wrap_field_names("") is None
    facts = generation_facts(
        b'{"adapterFallback":false,"innerFieldNames":["explanationText"],"parseCategory":"parsed",'
        b'"trailingBytes":0,"utf8":true}'
    )
    assert facts["innerFieldNames"] == ["explanationText"]
    diagnosed = diagnose_response(
        {
            "extractedBytes": 2,
            "extractedDigest": "b" * 64,
            "extractionStatus": "extracted",
            "parsed": {"findingExplanationOutput": {"surpriseField": "hidden-value"}},
        },
        facts,
    )
    assert "surpriseField" in diagnosed["unexpectedFields"]
    assert "hidden-value" not in str(diagnosed)
    assert any("evidence" in item or item for item in diagnosed["evidenceIdFindings"]) or (
        diagnosed["schemaStatus"] == "invalid"
    )
