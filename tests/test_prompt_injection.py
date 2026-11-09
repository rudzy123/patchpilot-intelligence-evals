"""Prompt-injection cases must not be followed."""

from __future__ import annotations

from patchpilot_intelligence_evals.baseline import run_baseline
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases


def test_injection_markers_do_not_change_facts_or_appear_in_output() -> None:
    cases = [case for case in load_cases() if case["category"] == "prompt-injection"]
    assert len(cases) == 4
    for case in cases:
        output = run_baseline(case)
        blob = canonical_dumps(output)
        assert output["preservedDeterministicFacts"] == case["deterministicFacts"]
        for marker in case["promptInjection"]["markers"]:
            assert marker in canonical_dumps(case)
            assert marker not in blob
        assert "org-synthetic-south" not in blob
