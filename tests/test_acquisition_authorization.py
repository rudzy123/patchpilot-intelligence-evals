"""Track 6 stays withheld unless every prerequisite passes."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.acquisition_authorization import (
    PREREQUISITES,
    AcquisitionError,
    decide,
    load_track6_authorization,
)
from patchpilot_intelligence_evals.cli import main

_IDENTITY = {
    "modelId": "example/not-selected",
    "revision": "0" * 40,
    "runtimeId": "llama-cpp",
}


def test_committed_track6_decision_is_not_authorized(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_track6_authorization()
    assert document["authorizationOutcome"] == "not-authorized"
    assert document["selectionOutcome"] == "no-selection"
    assert document["selectedModelId"] is None
    assert document["runtimeId"] is None
    assert document["immutableRevision"] is None
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["executionStatus"] == "not-executed"
    assert document["productionReady"] is False
    assert document["gatesChanged"] is False
    assert document["locallyObservedArtifactDigests"] == []
    blockers = [item["prerequisiteId"] for item in document["blockers"]]
    assert blockers == [
        "one-qualifying-candidate",
        "one-authorized-runtime",
        "isolation-without-acquisition-blocker",
        "immutable-revision-and-source",
        "tokenizer-provenance",
        "weight-license-and-commercial-use",
        "redistribution-unnecessary",
    ]
    passed = [
        item["prerequisiteId"] for item in document["prerequisites"] if item["status"] == "pass"
    ]
    assert passed == ["cache-and-verification", "hardware-fit", "no-gate-change"]
    assert main(["track6-authorization-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["authorizationOutcome"] == "not-authorized"
    assert summary["productionReady"] is False


def test_complete_prerequisites_authorize_without_acquisition() -> None:
    authorized = decide({name: True for name in PREREQUISITES}, _IDENTITY)
    assert authorized["authorizationOutcome"] == "authorized"
    assert authorized["selectionOutcome"] == "selected"
    assert authorized["selectedModelId"] == _IDENTITY["modelId"]
    assert authorized["runtimeId"] == "llama-cpp"
    assert authorized["blockers"] == []
    assert authorized["acquisitionStatus"] == "not-acquired"
    assert authorized["executionStatus"] == "not-executed"
    assert authorized["productionReady"] is False
    assert authorized["locallyObservedArtifactDigests"] == []


@pytest.mark.parametrize("missing", PREREQUISITES)
def test_each_missing_prerequisite_fails_closed(missing: str) -> None:
    prerequisites = {name: True for name in PREREQUISITES}
    prerequisites[missing] = False
    withheld = decide(prerequisites, _IDENTITY)
    assert withheld["authorizationOutcome"] == "not-authorized"
    assert [item["prerequisiteId"] for item in withheld["blockers"]] == [missing]
    assert withheld["selectedModelId"] is None
    assert withheld["locallyObservedArtifactDigests"] == []
    assert withheld["acquisitionStatus"] == "not-acquired"


def test_incomplete_prerequisite_set_is_rejected() -> None:
    prerequisites = {name: True for name in PREREQUISITES}
    del prerequisites["hardware-fit"]
    with pytest.raises(AcquisitionError, match="prerequisite-set"):
        decide(prerequisites, _IDENTITY)
    with pytest.raises(AcquisitionError, match="missing-identity"):
        decide({name: True for name in PREREQUISITES})
