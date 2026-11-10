"""Manifest provenance, digests, and entry-point rejection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.candidate_manifest import (
    ManifestError,
    load_manifest,
    seal_manifest,
    validate_manifest,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError

_PROHIBITED = [
    "model-training",
    "production-decision",
    "provider-execution",
    "state-mutation",
    "tenant-analysis",
]


def _document(relative: str) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "protocolVersion": "1.0.0",
        "candidateId": "fixture-conforming",
        "candidateVersion": "1",
        "candidateKind": "deterministic-test-double",
        "implementation": {
            "interpreter": "current-python",
            "entryPoint": relative,
            "implementationPaths": [relative],
        },
        "source": "original-synthetic",
        "license": "Apache-2.0",
        "permittedUse": ["offline-harness-evaluation"],
        "prohibitedUse": list(_PROHIBITED),
        "executionRequirements": {
            "network": "prohibited",
            "determinism": "deterministic",
            "timeoutSeconds": 15,
            "maxStdoutBytes": 65536,
            "maxStderrBytes": 16384,
            "retries": 0,
        },
        "expectedDeterminism": "deterministic",
        "networkPolicy": "prohibited",
        "dataRetention": "no-retention",
        "reviewStatus": "accepted-by-principal-systems-architect",
    }


def _write_script(root: Path) -> str:
    relative = "candidates/fixtures/conforming/main.py"
    path = root / relative
    path.parent.mkdir(parents=True)
    path.write_text("print('synthetic')\n", encoding="utf-8")
    return relative


def test_valid_manifest_digest_is_stable(tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    first = seal_manifest(_document(relative), tmp_path)
    second = seal_manifest(_document(relative), tmp_path)
    assert first["manifestDigest"] == second["manifestDigest"]
    assert first["implementationDigest"] == second["implementationDigest"]
    assert first["configurationDigest"] == second["configurationDigest"]
    assert validate_manifest(first, root=tmp_path)["candidateKind"] == "deterministic-test-double"


def test_implementation_digest_tracks_file_bytes(tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    first = seal_manifest(_document(relative), tmp_path)
    script = tmp_path / relative
    script.write_text("print('changed')\n", encoding="utf-8")
    second = seal_manifest(_document(relative), tmp_path)
    assert first["implementationDigest"] != second["implementationDigest"]
    assert first["manifestDigest"] != second["manifestDigest"]


def test_digest_mismatch_fails(tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    sealed = seal_manifest(_document(relative), tmp_path)
    sealed["implementationDigest"] = "c" * 64
    with pytest.raises(ManifestError) as caught:
        validate_manifest(sealed, root=tmp_path)
    assert caught.value.code == "implementation-digest"


@pytest.mark.parametrize(
    ("relative", "code"),
    [
        ("../patchpilot/main.py", "path-traversal"),
        ("../neural-from-scratch/notebook.py", "path-traversal"),
        ("patchpilot/main.py", "sibling-repository"),
        ("neural-from-scratch/notebook.py", "sibling-repository"),
        ("/etc/passwd", "absolute-path"),
        ("candidates/main.py;rm", "shell-metacharacter"),
    ],
)
def test_unsafe_entry_points_fail(relative: str, code: str) -> None:
    document = _document("candidates/fixtures/conforming/main.py")
    document["implementation"] = {
        "interpreter": "current-python",
        "entryPoint": relative,
        "implementationPaths": [relative],
    }
    document["implementationDigest"] = "a" * 64
    document["configurationDigest"] = "a" * 64
    document["manifestDigest"] = "a" * 64
    with pytest.raises(ManifestError) as caught:
        validate_manifest(document)
    assert caught.value.code == code


def test_missing_provenance_license_and_protocol_fail(tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    sealed = seal_manifest(_document(relative), tmp_path)
    missing_license = dict(sealed)
    del missing_license["license"]
    with pytest.raises(SchemaValidationError):
        validate_manifest(missing_license, root=tmp_path)
    missing_source = dict(sealed)
    del missing_source["source"]
    with pytest.raises(SchemaValidationError):
        validate_manifest(missing_source, root=tmp_path)
    bad_protocol = dict(sealed)
    bad_protocol["protocolVersion"] = "9.9.9"
    with pytest.raises(SchemaValidationError):
        validate_manifest(bad_protocol, root=tmp_path)


@pytest.mark.parametrize("kind", ["model", "hosted-provider", "local-inference"])
def test_real_model_or_provider_claims_fail(kind: str, tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    sealed = seal_manifest(_document(relative), tmp_path)
    sealed["candidateKind"] = kind
    with pytest.raises(SchemaValidationError):
        validate_manifest(sealed, root=tmp_path)


def test_provider_credential_field_fails(tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    sealed = seal_manifest(_document(relative), tmp_path)
    sealed["apiKey"] = "not-a-real-credential"
    with pytest.raises(SchemaValidationError):
        validate_manifest(sealed, root=tmp_path)


def test_unreviewed_network_requirement_fails(tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    sealed = seal_manifest(_document(relative), tmp_path)
    sealed["networkPolicy"] = "required"
    with pytest.raises(SchemaValidationError):
        validate_manifest(sealed, root=tmp_path)


def test_load_manifest_round_trip(tmp_path: Path) -> None:
    relative = _write_script(tmp_path)
    sealed = seal_manifest(_document(relative), tmp_path)
    manifest_path = tmp_path / "candidates" / "fixtures" / "conforming" / "manifest.json"
    manifest_path.write_text(json.dumps(sealed), encoding="utf-8")
    loaded = load_manifest(
        "candidates/fixtures/conforming/manifest.json",
        root=tmp_path,
    )
    assert loaded["manifestDigest"] == sealed["manifestDigest"]
