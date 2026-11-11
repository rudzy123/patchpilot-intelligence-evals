"""Candidate eligibility stays fail-closed. Disqualified scores stay null."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.candidate_eligibility import (
    CATEGORY_WEIGHTS,
    MANDATORY,
    EligibilityError,
    decide_candidate_eligibility,
    load_candidate_eligibility,
    validate_candidate_eligibility,
    weighted_score,
)
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.schemas import repo_root

_CATEGORIES = dict(CATEGORY_WEIGHTS)


def test_committed_eligibility_selects_nobody(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_candidate_eligibility()
    assert document == decide_candidate_eligibility()
    assert document["selectionOutcome"] == "no-selection"
    assert document["selectedModelId"] is None
    assert document["scoringApplied"] is False
    assert document["qualifyingCandidateCount"] == 0
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["executionStatus"] == "not-executed"
    assert document["conversionStatus"] == "not-performed"
    assert document["runtimeInstallationStatus"] == "not-installed"
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["locallyObservedArtifactDigests"] == []
    assert [item["modelId"] for item in document["candidates"]] == [
        "Qwen/Qwen2.5-1.5B-Instruct",
        "Qwen/Qwen2.5-3B-Instruct",
        "HuggingFaceTB/SmolLM2-1.7B-Instruct",
        "allenai/OLMo-2-0425-1B-Instruct",
        "google/gemma-3-1b-it",
    ]
    for item in document["candidates"]:
        assert item["weightedScore"] is None
        assert item["scoringEligible"] is False
        assert item["mandatoryStatus"] == "fail"
    qwen15, qwen3, smol, olmo, gemma = document["candidates"]
    assert qwen15["weightLicenseResult"] == "pass"
    assert qwen15["commercialGrant"] == "granted"
    assert qwen15["mandatoryCriteria"]["tokenizer-provenance"] == "fail"
    assert qwen15["modelCardLimitationsResult"] == "fail"
    assert qwen3["commercialGrant"] == "not-granted"
    assert qwen3["mandatoryCriteria"]["tokenizer-provenance"] == "fail"
    assert qwen3["revision"] != qwen15["revision"]
    assert smol["weightLicenseResult"] == "fail"
    assert smol["commercialUseResult"] == "unresolved"
    assert "local-resource-fit" in smol["disqualifiers"]
    assert olmo["commercialGrant"] == "restricted"
    assert olmo["redistributionResult"] == "unresolved"
    assert gemma["mandatoryCriteria"]["fully-offline-runtime-support"] == "fail"
    assert gemma["codeLicenseResult"] == "unresolved"
    text = json.dumps(document)
    assert "/home/" not in text
    assert "ip-26-0-174-36" not in text
    assert main(["candidate-eligibility-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["selectionOutcome"] == "no-selection"
    assert summary["qualifyingCandidateCount"] == 0
    assert summary["productionReady"] is False


def test_disqualified_score_is_null_and_a_full_pass_can_score() -> None:
    failed = {name: "pass" for name in MANDATORY}
    failed["documented-limitations"] = "fail"
    assert weighted_score(failed, _CATEGORIES) is None
    assert weighted_score({name: "pass" for name in MANDATORY}, _CATEGORIES) == 100
    with pytest.raises(EligibilityError) as caught:
        weighted_score({name: "pass" for name in MANDATORY}, {"license-provenance": 26})
    assert caught.value.code == "score-categories"


def test_one_passing_candidate_does_not_rewrite_the_record() -> None:
    root = repo_root()
    path = root / "candidates/authorization/candidate-eligibility-closure.json"
    before = path.read_text(encoding="utf-8")
    document = json.loads(before)
    passed = document["candidates"][0]
    passed["mandatoryCriteria"] = {name: "pass" for name in MANDATORY}
    passed["mandatoryStatus"] = "pass"
    passed["scoringEligible"] = True
    passed["weightedScore"] = 100
    passed["disqualifiers"] = []
    passed["weightLicenseResult"] = "pass"
    passed["commercialUseResult"] = "pass"
    passed["redistributionResult"] = "pass"
    passed["remoteCodeResult"] = "pass"
    passed["modelCardLimitationsResult"] = "pass"
    document["selectionOutcome"] = "selected"
    document["selectedModelId"] = passed["modelId"]
    document["scoringApplied"] = True
    document["qualifyingCandidateCount"] = 1
    validated = validate_candidate_eligibility(document)
    assert validated["selectionOutcome"] == "selected"
    assert validated["qualifyingCandidateCount"] == 1
    assert path.read_text(encoding="utf-8") == before
    blocked = json.loads(json.dumps(validated))
    blocked["candidates"][0]["weightedScore"] = None
    with pytest.raises(EligibilityError) as caught:
        validate_candidate_eligibility(blocked)
    assert caught.value.code == "weighted-score"
