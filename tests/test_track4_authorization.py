"""Closed Track 4 authorization records. These tests do not download or execute a model."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, cast

import pytest

from patchpilot_intelligence_evals.protocol import _HIDDEN_INPUT_FIELDS, EXECUTION_OUTCOMES
from patchpilot_intelligence_evals.schemas import (
    AUTHORIZATION_SCHEMA_NAMES,
    CANDIDATE_SCHEMA_NAMES,
    SCHEMA_IDS,
    SCHEMA_NAMES,
    assert_schemas_closed,
    error_paths,
    load_schema,
    repo_root,
    validate,
)

_RECORDS = {
    "candidate-shortlist": "candidates/authorization/candidate-shortlist.json",
    "real-candidate-authorization": "candidates/authorization/first-real-candidate.json",
    "evaluation-hardware-profile": "candidates/authorization/evaluation-hardware-profile.json",
    "candidate-acquisition-manifest": "candidates/authorization/acquisition-manifest-template.json",
    "real-candidate-experiment-plan": (
        "candidates/authorization/first-real-candidate-experiment.json"
    ),
}

_CRITERIA = (
    "explicit-weight-use-license",
    "clear-commercial-use-position",
    "clear-redistribution-position",
    "immutable-official-revision",
    "no-remote-code-requirement",
    "fully-offline-runtime-support",
    "tokenizer-provenance",
    "artifact-digest-capability",
    "local-resource-fit",
    "bounded-subprocess-compatibility",
    "no-mandatory-telemetry",
    "no-tenant-data-requirement",
    "official-model-card",
    "documented-limitations",
    "no-production-dependency",
)

_ARTIFACT_SUFFIXES = {".safetensors", ".gguf", ".onnx", ".pt", ".pth", ".ckpt"}
_SKIP_PARTS = {".git", ".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache"}


def _load(name: str) -> dict[str, Any]:
    path = repo_root() / _RECORDS[name]
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _walk_keys(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            found.append(str(key))
            found.extend(_walk_keys(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_walk_keys(item))
    return found


def test_authorization_schemas_stay_outside_track2_and_track3_ids() -> None:
    assert len(SCHEMA_NAMES) == 5
    assert len(SCHEMA_IDS) == 5
    assert len(AUTHORIZATION_SCHEMA_NAMES) == 5
    assert set(AUTHORIZATION_SCHEMA_NAMES).isdisjoint(SCHEMA_NAMES)
    assert set(AUTHORIZATION_SCHEMA_NAMES).isdisjoint(CANDIDATE_SCHEMA_NAMES)
    assert_schemas_closed()
    for name in AUTHORIZATION_SCHEMA_NAMES:
        document = load_schema(name)
        assert document["additionalProperties"] is False
        assert document["$id"] == f"urn:patchpilot-intelligence-evals:schema:{name}:v1"
        assert document["properties"]["schemaVersion"]["const"] == "1.0.0"
        assert document["properties"]["productionReady"]["const"] is False


def test_track4_records_match_their_schemas() -> None:
    for name in AUTHORIZATION_SCHEMA_NAMES:
        validate(name, _load(name))


def test_shortlist_disqualifies_every_candidate_without_a_score() -> None:
    shortlist = _load("candidate-shortlist")
    assert shortlist["selectionOutcome"] == "no-selection"
    assert shortlist["selectedModelId"] is None
    assert shortlist["runtimeAuthorization"] == "not-authorized"
    assert shortlist["scoringApplied"] is False
    assert shortlist["productionReady"] is False
    points = [item["points"] for item in shortlist["scoringModel"]["components"]]
    assert points == [25, 20, 20, 20, 10, 5]
    assert sum(points) == shortlist["scoringModel"]["totalPoints"] == 100
    assert len(shortlist["candidates"]) == 5
    assert shortlist["mandatoryCriteria"] == list(_CRITERIA)
    for candidate in shortlist["candidates"]:
        failed = [name for name in _CRITERIA if candidate["mandatoryCriteria"][name] == "fail"]
        assert failed
        assert "bounded-subprocess-compatibility" in failed
        assert candidate["disqualifiers"] == failed
        assert candidate["mandatoryStatus"] == "fail"
        assert candidate["weightedScore"] is None
        assert candidate["locallyObservedArtifactDigests"] == []
        assert candidate["latencyClass"] == "unknown"
        assert candidate["publisherArtifact"]["byteCount"] <= 8 * 1024**3
        for item in candidate["evidence"]:
            assert item["retrievedOn"] == "2026-11-10"
            assert item["claim"]
            locator = item["locator"]
            assert locator["kind"] == "url"
            assert locator["url"].startswith("https://")


def test_authorization_template_and_experiment_stay_unexecuted() -> None:
    authorization = _load("real-candidate-authorization")
    acquisition = _load("candidate-acquisition-manifest")
    experiment = _load("real-candidate-experiment-plan")
    for record in (authorization, acquisition, experiment):
        assert record["productionReady"] is False
        assert record["selectionOutcome"] == "no-selection"
        assert record["acquisitionStatus"] == "not-acquired"
        assert record["executionStatus"] == "not-executed"
        assert record["locallyObservedArtifactDigests"] == []
    assert authorization["approvedModelId"] is None
    assert authorization["approvedRuntime"] is None
    assert authorization["approvedQuantization"] is None
    assert authorization["immutableRevision"] is None
    assert authorization["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert authorization["reviewDate"] == "2026-11-10"
    assert authorization["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert authorization["decision"] == "no candidate authorized"
    assert authorization["authorizedScope"] == (
        "This approval authorizes the no-selection record only."
    )
    assert authorization["approvalReasons"] == [
        "The current candidate protocol authorizes deterministic test doubles but "
        "does not yet represent or stage real-model artifacts.",
        "The current runner denies the required external weight-cache boundary.",
        "The current 15-second limit has not been justified for real-model startup.",
        "Every reviewed candidate has at least one independent mandatory licensing, "
        "provenance, model-card, tokenizer, digest, commercial-use, or remote-control "
        "blocker.",
    ]
    assert authorization["notAuthorized"] == [
        "any candidate",
        "model or tokenizer acquisition",
        "a runtime dependency",
        "quantization",
        "real-model execution",
        "changes to current evaluation gates",
        "shadow mode",
        "PatchPilot production composition",
    ]
    assert authorization["blockers"]
    assert acquisition["authorizationState"] == "not-authorized"
    assert acquisition["expectedFiles"] == []
    assert acquisition["observedFiles"] == []
    assert acquisition["redistributionAuthorized"] is False
    assert experiment["experimentAuthorized"] is False
    assert experiment["selectedCandidate"] is None
    assert experiment["selectedRuntime"] is None
    assert experiment["experimentId"] is None
    assert experiment["winner"] is None
    assert experiment["gatesUnchanged"] is True
    assert experiment["percentageGatesCalibrated"] is False
    assert experiment["decoding"]["temperature"] == 0
    assert experiment["decoding"]["topP"] == 1
    assert experiment["repetitionCount"] == 3
    assert tuple(experiment["executionOutcomes"]) == EXECUTION_OUTCOMES
    digest = hashlib.sha256(experiment["promptTemplate"].encode("utf-8")).hexdigest()
    assert experiment["promptTemplateDigest"] == digest
    corpus = json.loads((repo_root() / "corpus" / "manifest.json").read_text(encoding="utf-8"))
    assert experiment["corpusDigest"] == corpus["corpusDigest"]
    assert experiment["corpusVersion"] == corpus["corpusVersion"]
    serialized = json.dumps(experiment)
    for field in _HIDDEN_INPUT_FIELDS:
        assert field not in serialized
    keys = set(_walk_keys(experiment))
    assert keys.isdisjoint(_HIDDEN_INPUT_FIELDS)


def test_hardware_profile_has_no_prohibited_identifiers() -> None:
    profile = _load("evaluation-hardware-profile")
    assert profile["operatingSystemFamily"] == "Linux"
    assert profile["operatingSystemVersion"] == "Ubuntu 26.04.1 LTS"
    assert profile["kernelVersion"] == "7.0.0-43-generic"
    assert profile["cpuArchitecture"] == "x86_64"
    assert profile["logicalCpuCount"] == 16
    assert profile["totalMemoryKib"] == 31487340
    assert profile["storageBytes"] == 1964601909248
    assert profile["availableStorageBytes"] == 1403456720896
    assert profile["gpuAvailability"] == "unavailable"
    assert profile["gpuModel"] is None
    assert profile["resourceEnvelope"]["timeoutSeconds"] == 15
    assert profile["resourceEnvelope"]["quantizationApproved"] is False
    text = (repo_root() / _RECORDS["evaluation-hardware-profile"]).read_text(encoding="utf-8")
    lowered = text.lower()
    for needle in (
        "rudzy",
        "/home/",
        "/users/",
        "microcode",
        "password",
        "api_key",
        "begin private",
        "hostname",
    ):
        assert needle not in lowered
    assert re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text) is None
    assert re.search(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", lowered) is None
    for record_name in _RECORDS.values():
        keys = {
            key.lower() for key in _walk_keys(json.loads((repo_root() / record_name).read_text()))
        }
        for banned in ("password", "secret", "apikey", "hostname", "username", "macaddress"):
            assert banned not in keys


def test_repository_has_no_model_artifacts() -> None:
    root = repo_root()
    for path in root.rglob("*"):
        if not path.is_file() or _SKIP_PARTS.intersection(path.parts):
            continue
        assert path.suffix not in _ARTIFACT_SUFFIXES
        assert path.name not in {"tokenizer.json", "tokenizer.model", "tokenizer_config.json"}


def test_failed_candidate_cannot_carry_a_weighted_score() -> None:
    shortlist = _load("candidate-shortlist")
    candidate = shortlist["candidates"][0]
    candidate["weightedScore"] = {
        "total": 100,
        "licenseProvenance": 25,
        "securityOfflineIsolation": 20,
        "localHardwareFit": 20,
        "evaluationSuitability": 20,
        "modelCardDisclosure": 10,
        "runtimeMaturity": 5,
    }
    assert error_paths("candidate-shortlist", shortlist)
    candidate["mandatoryStatus"] = "pass"
    candidate["mandatoryCriteria"] = {name: "pass" for name in _CRITERIA}
    candidate["disqualifiers"] = []
    assert error_paths("candidate-shortlist", shortlist) == []


@pytest.mark.parametrize("name", list(AUTHORIZATION_SCHEMA_NAMES))
def test_authorization_records_reject_unknown_properties(name: str) -> None:
    document = _load(name)
    document["credential"] = "absent"
    assert error_paths(name, document)


def test_pyproject_and_lockfile_do_not_gain_model_runtimes() -> None:
    root = repo_root()
    combined = "\n".join(
        (
            (root / "pyproject.toml").read_text(encoding="utf-8"),
            (root / "uv.lock").read_text(encoding="utf-8"),
        )
    ).lower()
    for name in ("torch", "transformers", "tensorflow", "jax", "llama-cpp", "safetensors"):
        assert name not in combined
