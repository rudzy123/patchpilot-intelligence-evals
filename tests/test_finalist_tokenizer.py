"""Tokenizer license applicability and offline eligibility."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.finalist_tokenizer import (
    FinalistTokenizerError,
    decide_finalist_tokenizer,
    load_finalist_tokenizer,
    tokenizer_eligible,
    validate_finalist_tokenizer,
)
from patchpilot_intelligence_evals.schemas import repo_root

_RECORD = "candidates/authorization/finalist-tokenizer.json"


def test_revision_license_passes_and_assumption_fails() -> None:
    document = load_finalist_tokenizer()
    finalist = document["finalists"][0]
    assert finalist["eligibilityOutcome"] == "pass"
    assert finalist["licenseInstrument"] == "revision-license-file"
    assert finalist["commercialUse"] == "restricted"
    assert finalist["automaticRetrievalRequired"] is False
    assert document["locallyObservedArtifactDigests"] == []
    assumed = json.loads(json.dumps(decide_finalist_tokenizer()))
    assumed["finalists"][0]["licenseInstrument"] = "assumed-from-model-license"
    assert tokenizer_eligible(assumed["finalists"][0]) is False
    before = (repo_root() / _RECORD).read_bytes()
    with pytest.raises(FinalistTokenizerError) as caught:
        validate_finalist_tokenizer(assumed)
    assert caught.value.code == "eligibility"
    assert (repo_root() / _RECORD).read_bytes() == before


def test_finalist_tokenizer_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["finalist-tokenizer-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["eligibilityOutcome"] == "pass"
    assert payload["productionReady"] is False
    assert payload["acquisitionStatus"] == "not-acquired"
