"""No-selection, null scores, and Track 6D tie-breaks."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track6d_readiness import SelectionCandidate, select_candidate
from patchpilot_intelligence_evals.track7_selection import (
    Track7SelectionError,
    choose_candidate,
    decide_track7_selection,
    load_track7_selection,
    validate_track7_selection,
)

_RECORD = "candidates/authorization/track7-selection.json"


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
        "licensing_clarity": 3,
        "custom_or_remote_code": False,
        "peak_memory_bytes": 100,
        "artifact_bytes": 100,
        "immutable_identity": 2,
        "model_card_disclosure": 2,
        "runtime_maturity": 2,
    }
    values.update(overrides)
    return SelectionCandidate(**values)  # type: ignore[arg-type]


def test_committed_selection_is_empty() -> None:
    document = load_track7_selection()
    assert document["selectionOutcome"] == "no-selection"
    assert document["selectedModelId"] is None
    assert document["scoringApplied"] is False
    assert document["qualifyingCandidateCount"] == 0
    assert document["candidates"][0]["weightedScore"] is None
    assert document["candidates"][0]["qualifies"] is False
    assert document["productionReady"] is False
    assert document["realModelExecuted"] is False


def test_score_mutation_tie_and_single_selection() -> None:
    before = (repo_root() / _RECORD).read_bytes()
    scored = json.loads(json.dumps(decide_track7_selection()))
    scored["candidates"][0]["weightedScore"] = 90
    with pytest.raises(Track7SelectionError) as caught:
        validate_track7_selection(scored)
    assert caught.value.code == "selection-drift"
    selected = json.loads(json.dumps(decide_track7_selection()))
    selected["selectionOutcome"] = "selected"
    selected["selectedModelId"] = selected["candidates"][0]["modelId"]
    with pytest.raises(Track7SelectionError) as selection_error:
        validate_track7_selection(selected)
    assert selection_error.value.code == "selection"
    low = _candidate("Example/Low", peak_memory_bytes=50, artifact_bytes=40)
    high = _candidate("Example/High", peak_memory_bytes=80, artifact_bytes=70)
    assert select_candidate([low, high]) == "Example/Low"
    twin = _candidate("Example/Tie", peak_memory_bytes=50, artifact_bytes=40)
    assert select_candidate([low, twin]) is None
    unscored = _candidate("Example/Null", weighted_score=None, mandatory_pass=False)
    assert select_candidate([unscored, high]) == "Example/High"
    gap = {
        "modelId": "Example/Suitability-gap",
        "weightedScore": 80,
        "mandatoryStatus": "pass",
        "tokenizerOutcome": "pass",
        "directOnnxOutcome": "pass",
        "hardwareFit": "pass",
        "executionOutcome": "pass",
        "suitabilityOutcome": "unresolved",
        "fixedRevision": True,
        "unresolvedConflict": False,
    }
    assert choose_candidate([gap]) is None
    gap["suitabilityOutcome"] = "suitable-for-offline-evaluation"
    assert choose_candidate([gap]) == "Example/Suitability-gap"
    assert (repo_root() / _RECORD).read_bytes() == before


def test_track7_selection_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["track7-selection-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["selectionOutcome"] == "no-selection"
    assert payload["selectedModelId"] is None
    assert payload["scoringApplied"] is False
    assert payload["productionReady"] is False
