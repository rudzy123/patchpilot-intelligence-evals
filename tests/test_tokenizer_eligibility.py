"""Tokenizer eligibility rejects assumed licenses."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.tokenizer_eligibility import (
    TokenizerError,
    decide_tokenizer_eligibility,
    load_tokenizer_eligibility,
    tokenizer_eligible,
    validate_tokenizer_eligibility,
)


def test_committed_tokenizer_decisions(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_tokenizer_eligibility()
    assert document == decide_tokenizer_eligibility()
    outcomes = [item["eligibilityOutcome"] for item in document["families"]]
    assert outcomes == ["fail", "fail", "fail", "fail", "fail"]
    qwen15, qwen3, smol, olmo, gemma = document["families"]
    assert qwen15["licenseInstrument"] == "terms-do-not-name-tokenizer"
    assert qwen3["licenseInstrument"] == "terms-do-not-name-tokenizer"
    assert qwen15["commercialUse"] == "unresolved"
    assert qwen3["commercialUse"] == "unresolved"
    assert qwen15["revision"] != qwen3["revision"]
    assert {name["fileName"] for name in qwen15["fileInventory"]} == {
        "merges.txt",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.json",
    }
    assert smol["licenseInstrument"] == "absent"
    assert olmo["licenseInstrument"] == "absent"
    assert gemma["licenseInstrument"] == "terms-do-not-name-tokenizer"
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert main(["tokenizer-eligibility-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["passingFamilies"] == 0
    assert summary["productionReady"] is False


def test_assumed_and_missing_licenses_fail() -> None:
    assert tokenizer_eligible("revision-license-file") is True
    assert tokenizer_eligible("separate-instrument") is True
    assert tokenizer_eligible("assumed-from-model-license") is False
    assert tokenizer_eligible("absent") is False
    assert tokenizer_eligible("terms-do-not-name-tokenizer") is False
    document = decide_tokenizer_eligibility()
    smol = json.loads(json.dumps(document["families"][2]))
    smol["licenseInstrument"] = "assumed-from-model-license"
    smol["eligibilityOutcome"] = "pass"
    document["families"][2] = smol
    with pytest.raises(TokenizerError) as caught:
        validate_tokenizer_eligibility(document)
    assert caught.value.code == "tokenizer-eligibility"
