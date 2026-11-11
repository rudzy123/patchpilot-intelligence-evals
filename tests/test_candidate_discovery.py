"""Discovery limits, prior-family exclusion, and pre-screen boundaries."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from typing import Any

import pytest

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    CONTEXT_FLOOR,
    PARAMETER_MAX,
    PARAMETER_MIN,
    DiscoveryError,
    decide_candidate_discovery,
    exclusion_reasons,
    load_candidate_discovery,
    parameter_in_band,
    validate_candidate_discovery,
)
from patchpilot_intelligence_evals.candidate_eligibility import MODEL_IDS
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root

_RECORD = "candidates/authorization/candidate-discovery.json"


def _bytes() -> bytes:
    return (repo_root() / _RECORD).read_bytes()


def _copy() -> dict[str, Any]:
    loaded = json.loads(json.dumps(decide_candidate_discovery()))
    if not isinstance(loaded, dict):
        raise DiscoveryError("record-type")
    return loaded


def _open_candidate(**overrides: object) -> dict[str, Any]:
    item: dict[str, Any] = {
        "modelId": "Example/Model",
        "familyId": "example",
        "revision": "a" * 40,
        "parameterCount": 1_000_000_000,
        "contextTokens": 8192,
        "instructionCapable": True,
        "officialCard": True,
        "directOnnxInitial": "official-nonquantized",
        "listedArtifactBytes": 1000,
        "conversionRequired": False,
        "quantizationRequired": False,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "cpuOnlyPlausible": True,
        "weightLicenseInitial": "revision-instrument",
    }
    item.update(overrides)
    return item


def test_committed_universe_matches_decision() -> None:
    document = load_candidate_discovery()
    assert document["discoveryCandidateCount"] == 8
    assert document["finalistCount"] == 1
    assert document["finalistModelIds"] == ["LiquidAI/LFM2.5-1.2B-Instruct"]
    assert document["productionReady"] is False
    assert document["realModelExecuted"] is False
    assert document["runtimeInstallationStatus"] == "not-installed"
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["conversionStatus"] == "not-performed"
    assert document["executionStatus"] == "not-executed"
    assert document["locallyObservedArtifactDigests"] == []
    ids = {item["modelId"] for item in document["candidates"]}
    revisions = {item["revision"] for item in document["candidates"]}
    prior_ids = {item["modelId"] for item in document["priorCheckpoints"]}
    prior_revisions = {item["revision"] for item in document["priorCheckpoints"]}
    assert ids.isdisjoint(MODEL_IDS)
    assert prior_ids == set(MODEL_IDS)
    assert revisions.isdisjoint(prior_revisions)


def test_parameter_and_size_boundaries() -> None:
    priors: set[str] = set()
    assert parameter_in_band(PARAMETER_MIN)
    assert parameter_in_band(PARAMETER_MAX)
    assert not parameter_in_band(PARAMETER_MIN - 1)
    assert not parameter_in_band(PARAMETER_MAX + 1)
    assert exclusion_reasons(_open_candidate(), set(MODEL_IDS), priors) == []
    assert "parameter-band" in exclusion_reasons(
        _open_candidate(parameterCount=3_836_021_760), set(MODEL_IDS), priors
    )
    assert "artifact-cap" in exclusion_reasons(
        _open_candidate(listedArtifactBytes=ARTIFACT_CAP + 1), set(MODEL_IDS), priors
    )
    assert (
        exclusion_reasons(_open_candidate(listedArtifactBytes=ARTIFACT_CAP), set(MODEL_IDS), priors)
        == []
    )
    assert "artifact-unknown" in exclusion_reasons(
        _open_candidate(listedArtifactBytes=None), set(MODEL_IDS), priors
    )
    assert (
        exclusion_reasons(_open_candidate(contextTokens=CONTEXT_FLOOR), set(MODEL_IDS), priors)
        == []
    )
    assert "context-floor" in exclusion_reasons(
        _open_candidate(contextTokens=CONTEXT_FLOOR - 1), set(MODEL_IDS), priors
    )
    assert "context-unknown" in exclusion_reasons(
        _open_candidate(contextTokens=None), set(MODEL_IDS), priors
    )


def test_prior_family_and_duplicate_detection() -> None:
    priors = set(MODEL_IDS)
    prefixed = _open_candidate(
        modelId="Qwen/Qwen2.5-0.5B-Instruct",
        familyId="qwen2.5",
    )
    assert "prior-checkpoint" in exclusion_reasons(prefixed, priors, set())
    mirror = _open_candidate(
        modelId="unsloth/gemma-3-1b-it",
        familyId="gemma-mirror",
        revision="b" * 40,
    )
    assert "prior-checkpoint" in exclusion_reasons(mirror, priors, set())
    quantized = _open_candidate(
        modelId="unsloth/Qwen2.5-3B-Instruct-Q4",
        familyId="mirror",
    )
    assert "prior-checkpoint" in exclusion_reasons(quantized, priors, set())
    other_size = _open_candidate(modelId="google/gemma-3-4b-it", familyId="gemma-3-4b")
    assert "prior-checkpoint" in exclusion_reasons(other_size, priors, set())
    later = _open_candidate(modelId="Qwen/Qwen3-1.7B", familyId="qwen3")
    assert "prior-checkpoint" not in exclusion_reasons(later, priors, set())
    renamed = _copy()
    renamed["candidates"][0]["modelId"] = "unsloth/gemma-3-1b-it"
    with pytest.raises(SchemaValidationError):
        validate_candidate_discovery(renamed)
    before = _bytes()
    document = _copy()
    document["candidates"][1]["familyId"] = document["candidates"][0]["familyId"]
    with pytest.raises(DiscoveryError) as caught:
        validate_candidate_discovery(document)
    assert caught.value.code == "duplicate-family"
    repeated = _copy()
    repeated["candidates"][1]["modelId"] = repeated["candidates"][0]["modelId"]
    with pytest.raises(DiscoveryError) as model_caught:
        validate_candidate_discovery(repeated)
    assert model_caught.value.code == "duplicate-model"
    oversized = _copy()
    oversized["candidates"].append(oversized["candidates"][0])
    with pytest.raises(SchemaValidationError):
        validate_candidate_discovery(oversized)
    marked = _copy()
    marked["candidates"][0]["materialDifference"] = "A private /home/researcher path is rejected."
    with pytest.raises(DiscoveryError) as identity:
        validate_candidate_discovery(marked)
    assert identity.value.code == "identity"
    assert _bytes() == before


def test_only_lfm_advances_and_smollm3_fails_the_cap() -> None:
    document = decide_candidate_discovery()
    outcomes = {item["modelId"]: item["exclusionReasons"] for item in document["candidates"]}
    assert outcomes["LiquidAI/LFM2.5-1.2B-Instruct"] == []
    assert outcomes["HuggingFaceTB/SmolLM3-3B"] == ["artifact-cap"]
    assert "prior-checkpoint" not in outcomes["Qwen/Qwen3-1.7B"]


def test_discovery_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["candidate-discovery-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["discoveryCandidateCount"] == 8
    assert payload["finalistCount"] == 1
    assert payload["productionReady"] is False
    assert payload["acquisitionStatus"] == "not-acquired"
