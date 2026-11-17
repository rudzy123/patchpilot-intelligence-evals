"""Corpus evaluation hides gold and keeps a null comparison winner."""

from __future__ import annotations

import pytest

from patchpilot_intelligence_evals.inference_behavioral_measurement import (
    _config,
    load_summary_template,
)
from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan, phase_by_name
from patchpilot_intelligence_evals.measurement_plan import MeasurementError


def test_summary_template_has_no_winner() -> None:
    summary = load_summary_template()
    assert summary["comparisonWinner"] is None
    assert summary["gatesUnchanged"] is True
    assert summary["percentageGatesCalibrated"] is False
    assert summary["productionReady"] is False
    assert summary["calibrationStatus"] == "not-approved"


def test_gold_in_the_child_config_is_rejected() -> None:
    plan = load_inference_plan()
    phase = phase_by_name(plan, "corpus-evaluation")
    with pytest.raises(MeasurementError) as exc:
        _config(plan, phase, {}, "template", {"goldSupportedClaims": []})
    assert exc.value.code == "gold-visible"
