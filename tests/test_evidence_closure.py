"""Evidence closure over the accepted shortlist. The shortlist file stays unchanged."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.evidence_closure import (
    MANDATORY_CRITERIA,
    PINNED_REVISIONS,
    QWEN3_SHARDS,
    EvidenceError,
    assert_score_closed,
    load_closure,
    validate_closure,
)
from patchpilot_intelligence_evals.schemas import repo_root

_REJECTED_GEMMA_DIGEST = "3d4ef8d71c14db7e448a09ebe891cfb6bf32c57a9b44499ae0d1c098e48516b6"


def _shortlist() -> dict[str, Any]:
    path = repo_root() / "candidates/authorization/candidate-shortlist.json"
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_closure_keeps_no_selection_and_the_shortlist(capsys: pytest.CaptureFixture[str]) -> None:
    closure = load_closure()
    shortlist = _shortlist()
    prior = {item["modelId"]: item for item in shortlist["candidates"]}
    current = {item["modelId"]: item for item in closure["candidates"]}
    assert list(current) == list(PINNED_REVISIONS)
    assert closure["selectionOutcome"] == "no-selection"
    assert closure["selectedModelId"] is None
    assert closure["scoringApplied"] is False
    assert closure["qualifyingCandidateCount"] == 0
    assert closure["acquisitionStatus"] == "not-acquired"
    assert closure["executionStatus"] == "not-executed"
    assert closure["productionReady"] is False
    assert closure["locallyObservedArtifactDigests"] == []
    qwen3 = current["Qwen/Qwen2.5-3B-Instruct"]
    assert (
        prior["Qwen/Qwen2.5-3B-Instruct"]["mandatoryCriteria"]["artifact-digest-capability"]
        == "fail"
    )
    assert qwen3["mandatoryCriteria"]["artifact-digest-capability"] == "pass"
    assert qwen3["gaps"][0]["status"] == "resolved"
    shards = qwen3["publisherArtifact"]["shards"]
    assert [(item["fileName"], item["byteCount"], item["sha256"]) for item in shards] == list(
        QWEN3_SHARDS
    )
    for model_id, candidate in current.items():
        assert candidate["revision"] == PINNED_REVISIONS[model_id]
        assert candidate["weightedScore"] is None
        assert candidate["mandatoryCriteria"]["bounded-subprocess-compatibility"] == "fail"
        assert candidate["locallyObservedArtifactDigests"] == []
        assert "bounded-subprocess-compatibility" in candidate["disqualifiers"]
    for model_id in ("Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-3B-Instruct"):
        assert current[model_id]["mandatoryCriteria"]["tokenizer-provenance"] == "pass"
        assert current[model_id]["mandatoryCriteria"]["documented-limitations"] == "fail"
    for model_id in (
        "HuggingFaceTB/SmolLM2-1.7B-Instruct",
        "allenai/OLMo-2-0425-1B-Instruct",
    ):
        criteria = current[model_id]["mandatoryCriteria"]
        assert criteria["explicit-weight-use-license"] == "fail"
        assert criteria["tokenizer-provenance"] == "fail"
    gemma = current["google/gemma-3-1b-it"]["mandatoryCriteria"]
    assert gemma["tokenizer-provenance"] == "fail"
    assert gemma["artifact-digest-capability"] == "fail"
    assert gemma["fully-offline-runtime-support"] == "fail"
    raw = Path("candidates/authorization/candidate-evidence-closure.json").read_text(
        encoding="utf-8"
    )
    assert _REJECTED_GEMMA_DIGEST not in raw
    assert main(["evidence-closure-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["selectionOutcome"] == "no-selection"
    assert summary["qualifyingCandidateCount"] == 0


def test_scores_stay_null_until_every_criterion_passes() -> None:
    failed = {name: "pass" for name in MANDATORY_CRITERIA}
    failed["bounded-subprocess-compatibility"] = "fail"
    with pytest.raises(EvidenceError, match="score-forbidden"):
        assert_score_closed(failed, 1)
    passed = {name: "pass" for name in MANDATORY_CRITERIA}
    with pytest.raises(EvidenceError, match="score-required"):
        assert_score_closed(passed, None)
    assert_score_closed(passed, 0)


def test_closure_rejects_an_unauthorized_pass() -> None:
    document = load_closure()
    shortlist = _shortlist()
    candidate = document["candidates"][0]
    candidate["mandatoryCriteria"]["bounded-subprocess-compatibility"] = "pass"
    candidate["disqualifiers"] = [
        name for name in candidate["disqualifiers"] if name != "bounded-subprocess-compatibility"
    ]
    with pytest.raises(EvidenceError, match="unauthorized-change"):
        validate_closure(document, shortlist)
