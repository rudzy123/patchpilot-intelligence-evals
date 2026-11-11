"""Selection keeps a null score for every disqualified family."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.candidate_eligibility import (
    CATEGORY_WEIGHTS,
    MANDATORY,
    weighted_score,
)
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.track6d_readiness import (
    SelectionCandidate,
    decide_track6d_readiness,
    load_track6d_readiness,
    select_candidate,
)

_RECORD = Path("candidates/authorization/track6d-acquisition-readiness.json")


def _candidate(model_id: str, **overrides: object) -> SelectionCandidate:
    values: dict[str, object] = {
        "model_id": model_id,
        "weighted_score": 80,
        "mandatory_pass": True,
        "tokenizer_pass": True,
        "direct_onnx": True,
        "budget_pass": True,
        "subprocess_pass": True,
        "fixed_revision": True,
        "unresolved_conflict": False,
        "conversion_authorized": False,
        "quantization_approved": False,
        "licensing_clarity": 1,
        "custom_or_remote_code": False,
        "peak_memory_bytes": 100,
        "artifact_bytes": 100,
        "immutable_identity": 1,
        "model_card_disclosure": 1,
        "runtime_maturity": 1,
    }
    values.update(overrides)
    return SelectionCandidate(**values)  # type: ignore[arg-type]


def test_committed_track6d_is_not_ready(capsys: pytest.CaptureFixture[str]) -> None:
    before = _RECORD.read_bytes()
    document = load_track6d_readiness()
    assert document == decide_track6d_readiness()
    assert document["readinessOutcome"] == "not-ready"
    assert document["verdict"] == "TRACK 6D CONTROLLED ACQUISITION NOT READY"
    assert document["selectionOutcome"] == "no-selection"
    assert document["selectedModelId"] is None
    assert document["scoringApplied"] is False
    assert document["qualifyingCandidateCount"] == 0
    assert document["installationAuthorized"] is False
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert "bounded-subprocess-compatibility" in document["blockers"]
    assert main(["track6d-readiness-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["verdict"] == "TRACK 6D CONTROLLED ACQUISITION NOT READY"
    assert _RECORD.read_bytes() == before


def test_tie_break_and_disqualification_do_not_rewrite_the_record() -> None:
    before = _RECORD.read_bytes()
    lower_memory = _candidate("Qwen/Qwen2.5-1.5B-Instruct", peak_memory_bytes=10)
    higher_memory = _candidate("Qwen/Qwen2.5-3B-Instruct", peak_memory_bytes=20)
    assert select_candidate([higher_memory, lower_memory]) == "Qwen/Qwen2.5-1.5B-Instruct"
    stronger = _candidate("google/gemma-3-1b-it", weighted_score=90, peak_memory_bytes=500)
    weaker = _candidate(
        "allenai/OLMo-2-0425-1B-Instruct",
        weighted_score=70,
        peak_memory_bytes=5,
    )
    assert select_candidate([weaker, stronger]) == "google/gemma-3-1b-it"
    failing = dict.fromkeys(MANDATORY, "pass")
    failing["explicit-weight-use-license"] = "fail"
    full_points = dict(CATEGORY_WEIGHTS)
    assert weighted_score(failing, full_points) is None
    disqualified = _candidate(
        "HuggingFaceTB/SmolLM2-1.7B-Instruct",
        weighted_score=None,
        mandatory_pass=False,
    )
    assert select_candidate([disqualified]) is None
    assert _RECORD.read_bytes() == before
