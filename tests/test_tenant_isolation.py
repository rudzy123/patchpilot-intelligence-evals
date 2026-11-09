"""Cross-tenant negative controls stay out of candidate input and output."""

from __future__ import annotations

from patchpilot_intelligence_evals.baseline import run_baseline
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases, to_candidate_input


def test_negative_controls_are_excluded() -> None:
    cases = [case for case in load_cases() if case["category"] == "cross-tenant-negative-control"]
    assert len(cases) == 4
    for case in cases:
        assert case["negativeControls"]
        output_blob = canonical_dumps(run_baseline(case))
        input_blob = canonical_dumps(to_candidate_input(case))
        for control in case["negativeControls"]:
            assert control["organizationId"] != case["authorizedOrganizationId"]
            for token in control.values():
                assert token not in output_blob
                assert token not in input_blob
