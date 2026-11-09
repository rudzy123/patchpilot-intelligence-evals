"""Deterministic baseline behavior. The baseline is not a model."""

from __future__ import annotations

from patchpilot_intelligence_evals.baseline import CANDIDATE, run_baseline
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases
from patchpilot_intelligence_evals.schemas import validate


def test_outputs_are_stable_schema_valid_and_do_not_mutate_input() -> None:
    for case in load_cases():
        before = canonical_dumps(case)
        first = run_baseline(case)
        second = run_baseline(case)
        assert canonical_dumps(case) == before
        assert canonical_dumps(first) == canonical_dumps(second)
        validate("finding-explanation-output", first)
        assert first["candidate"] == CANDIDATE
        assert first["explanationLabel"] == "deterministic-baseline-assistance"
        assert first["nonAuthoritative"] is True
        assert first["preservedDeterministicFacts"] == case["deterministicFacts"]
        assert case["assistanceRequest"] not in canonical_dumps(first)


def test_refusal_emits_no_claims_or_citations() -> None:
    for case in load_cases():
        output = run_baseline(case)
        if case["expectedRefusal"]:
            assert output["refused"] is True
            assert output["supportedClaims"] == []
            assert output["citations"] == []
            assert output["remediationSuggestions"] == []
            assert output["missingEvidence"] == case["missingEvidence"]
        else:
            assert output["refused"] is False
            assert output["refusalReason"] == ""


def test_grounding_case_keeps_remediation_non_authoritative() -> None:
    case = next(item for item in load_cases() if item["caseId"] == "case-ground-006")
    output = run_baseline(case)
    assert output["remediationSuggestions"] == [
        {
            "text": "A future human review could inspect the synthetic package coordinate.",
            "nonAuthoritative": True,
        }
    ]
    assert "complete" not in output["remediationSuggestions"][0]["text"]
