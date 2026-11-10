"""Offline-local-model manifests. These tests do not download or execute a model."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, cast

import pytest

from patchpilot_intelligence_evals.candidate_manifest import ManifestError, load_manifest
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.real_candidate_manifest import (
    load_offline_manifest,
    manifest_digest,
    validate_offline_manifest,
)
from patchpilot_intelligence_evals.schemas import (
    AUTHORIZATION_SCHEMA_NAMES,
    CANDIDATE_SCHEMA_NAMES,
    SCHEMA_IDS,
    SCHEMA_NAMES,
    TRACK5_SCHEMA_NAMES,
    assert_schemas_closed,
    error_paths,
    repo_root,
)

_TEMPLATE = "candidates/templates/offline-local-model-manifest.json"


def _document() -> dict[str, Any]:
    path = repo_root() / _TEMPLATE
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AssertionError("record-type")
    return cast(dict[str, Any], loaded)


def _reseal(document: dict[str, Any]) -> dict[str, Any]:
    sealed = deepcopy(document)
    sealed["manifestDigest"] = manifest_digest(sealed)
    return sealed


def test_track5_schema_family_stays_disjoint() -> None:
    assert "offline-local-model-manifest" in TRACK5_SCHEMA_NAMES
    assert set(TRACK5_SCHEMA_NAMES).isdisjoint(SCHEMA_NAMES)
    assert set(TRACK5_SCHEMA_NAMES).isdisjoint(SCHEMA_IDS)
    assert set(TRACK5_SCHEMA_NAMES).isdisjoint(CANDIDATE_SCHEMA_NAMES)
    assert set(TRACK5_SCHEMA_NAMES).isdisjoint(AUTHORIZATION_SCHEMA_NAMES)
    assert len(SCHEMA_NAMES) == 5
    assert_schemas_closed()


def test_deterministic_fixtures_remain_valid() -> None:
    root = repo_root()
    fixtures = sorted((root / "candidates" / "fixtures").glob("*/manifest.json"))
    assert len(fixtures) == 8
    for path in fixtures:
        relative = path.relative_to(root).as_posix()
        manifest = load_manifest(relative)
        assert manifest["candidateKind"] == "deterministic-test-double"
        assert error_paths("offline-local-model-manifest", manifest)


def test_not_acquired_illustration_passes(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_offline_manifest(_TEMPLATE)
    assert document["candidateKind"] == "offline-local-model"
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["executionStatus"] == "not-executed"
    assert document["observedArtifacts"] == []
    assert document["locallyVerifiedArtifactIdentities"] == []
    assert document["productionReady"] is False
    assert document["reviewStatus"] == "not-authorized"
    assert document["runtimeId"] == "none"
    assert main(["real-candidate-manifest-validation", "--manifest", _TEMPLATE]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["status"] == "ok"
    assert summary["candidateKind"] == "offline-local-model"
    assert summary["productionReady"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("candidateKind", "deterministic-test-double"),
        ("immutableRevision", "main"),
        ("productionReady", True),
        ("remoteCodePolicy", "required"),
        ("telemetryPolicy", "required"),
        ("quantization", "int4"),
        ("acquisitionStatus", "acquired"),
        ("executionStatus", "executed"),
    ],
)
def test_closed_manifest_fields_reject_drift(field: str, value: object) -> None:
    document = _document()
    document[field] = value
    assert error_paths("offline-local-model-manifest", document)


def test_fabricated_local_digest_fails() -> None:
    document = _document()
    document["locallyVerifiedArtifactIdentities"] = ["a" * 64]
    assert error_paths("offline-local-model-manifest", document)
    document = _document()
    document["observedArtifacts"] = [
        {"fileName": "illustration.safetensors", "observedBytes": 1, "sha256": "a" * 64}
    ]
    assert error_paths("offline-local-model-manifest", document)


def test_missing_provenance_fails() -> None:
    document = _document()
    document.pop("weightLicenseUrl")
    assert error_paths("offline-local-model-manifest", document)
    document = _document()
    document["tokenizerLicenseUrl"] = ""
    assert error_paths("offline-local-model-manifest", document)
    document = _document()
    document["sourceCodeLicenseApplies"] = True
    document["sourceCodeLicenseUrl"] = None
    assert error_paths("offline-local-model-manifest", document)


def test_unauthorized_runtime_fails() -> None:
    document = _reseal({**_document(), "runtimeId": "unapproved-runtime"})
    document["runtimeVersionRequirement"] = "0"
    document = _reseal(document)
    with pytest.raises(ManifestError) as caught:
        validate_offline_manifest(document, authorized_runtime_ids=frozenset({"none"}))
    assert caught.value.code == "unauthorized-runtime"


def test_identity_bearing_path_fails() -> None:
    document = _document()
    document["officialSourceUrl"] = "https://example.invalid/home/model"
    document = _reseal(document)
    with pytest.raises(ManifestError) as caught:
        validate_offline_manifest(document)
    assert caught.value.code == "identity-bearing-path"


def test_manifest_digest_mismatch_fails() -> None:
    document = _document()
    document["candidateVersion"] = "9"
    with pytest.raises(ManifestError) as caught:
        validate_offline_manifest(document)
    assert caught.value.code == "manifest-digest"
