"""Fail-closed Track 8 authorization and empty digest arrays."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root
from patchpilot_intelligence_evals.track8_authorization import (
    Track8AuthorizationError,
    decide_track8_authorization,
    load_track8_authorization,
    validate_track8_authorization,
)

_RECORD = "candidates/authorization/track8-acquisition-authorization.json"


def test_track8_withholds_acquisition() -> None:
    document = load_track8_authorization()
    assert document["authorizationOutcome"] == "not-authorized"
    assert document["verdict"] == "TRACK 8 CONTROLLED ACQUISITION NOT AUTHORIZED"
    assert document["selectionOutcome"] == "no-selection"
    assert document["selectedModelId"] is None
    assert document["installationAuthorized"] is False
    assert document["conversionAuthorized"] is False
    assert document["quantizationApproved"] is False
    assert document["runtimeInstallationStatus"] == "not-installed"
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["conversionStatus"] == "not-performed"
    assert document["executionStatus"] == "not-executed"
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["locallyObservedRuntimeDigests"] == []
    assert document["locallyObservedModelDigests"] == []
    assert document["locallyObservedTokenizerDigests"] == []
    assert document["locallyObservedConfigurationDigests"] == []
    assert "local-resource-fit" in document["blockers"]
    assert "explanation-suitability-unresolved" in document["blockers"]


def test_authorized_outcome_and_local_digest_fail() -> None:
    before = (repo_root() / _RECORD).read_bytes()
    authorized = json.loads(json.dumps(decide_track8_authorization()))
    authorized["authorizationOutcome"] = "authorized"
    authorized["verdict"] = "TRACK 8 CONTROLLED ACQUISITION AUTHORIZED"
    with pytest.raises(Track8AuthorizationError) as caught:
        validate_track8_authorization(authorized)
    assert caught.value.code == "verdict"
    digested = json.loads(json.dumps(decide_track8_authorization()))
    digested["locallyObservedModelDigests"] = ["abc"]
    with pytest.raises(SchemaValidationError):
        validate_track8_authorization(digested)
    assert (repo_root() / _RECORD).read_bytes() == before


def test_track8_acquisition_authorization_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["track8-acquisition-authorization-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["authorizationOutcome"] == "not-authorized"
    assert payload["verdict"] == "TRACK 8 CONTROLLED ACQUISITION NOT AUTHORIZED"
    assert payload["installationAuthorized"] is False
    assert payload["productionReady"] is False
