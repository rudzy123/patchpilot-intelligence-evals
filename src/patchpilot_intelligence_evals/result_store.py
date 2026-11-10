"""Immutable candidate artifacts.

Results are research records. They are not PatchPilot audit records, Findings,
or priority reviews. The writer refuses to replace an existing artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.network_guard import BoundaryError, assert_inside_repository
from patchpilot_intelligence_evals.protocol import experiment_id
from patchpilot_intelligence_evals.schemas import SCHEMA_IDS, repo_root, validate


class ResultStoreError(ValueError):
    """A result path or artifact failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _destination(relative_path: str, root: Path) -> Path:
    try:
        assert_inside_repository(relative_path, root)
    except BoundaryError as exc:
        raise ResultStoreError("path") from exc
    return root.joinpath(*Path(relative_path).parts)


def write_canonical(
    relative_path: str,
    document: dict[str, Any],
    *,
    schema_name: str,
    root: Path | None = None,
) -> str:
    """Write one canonical document. Refuse when the file already exists."""
    validate(schema_name, document)
    base = root if root is not None else repo_root()
    destination = _destination(relative_path, base)
    if destination.exists():
        raise ResultStoreError("overwrite")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(canonical_dumps(document) + "\n", encoding="utf-8")
    return relative_path


def read_json(relative_path: str, root: Path | None = None) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    destination = _destination(relative_path, base)
    if destination.is_symlink() or not destination.is_file():
        raise ResultStoreError("missing-result")
    loaded = json.loads(destination.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ResultStoreError("result-type")
    return loaded


def experiment_manifest_for(result: dict[str, Any]) -> dict[str, Any]:
    """Track 2 experiment manifest for a test double.

    The Track 2 schema has no test-double kind. The manifest uses
    ``future-candidate`` and the execution result keeps
    ``deterministic-test-double``.
    """
    document = {
        "schemaVersion": "1.0.0",
        "experimentId": result["experimentId"],
        "purpose": "candidate-performance",
        "productionReady": False,
        "corpusVersion": result["corpusVersion"],
        "corpusDigest": result["corpusDigest"],
        "candidate": {
            "kind": "future-candidate",
            "name": result["candidateId"],
            "version": result["candidateVersion"],
        },
        "softwareVersions": {
            "python": result["pythonVersion"],
            "package": "0.0.0",
            "jsonschema": result["jsonschemaVersion"],
        },
        "deterministicSettings": result["deterministicSettings"],
        "promptIdentity": result["promptIdentity"],
        "schemaIds": list(SCHEMA_IDS),
    }
    validate("experiment-manifest", document)
    return document


def execution_result_paths(output_dir: str, experiment: str) -> tuple[str, str]:
    if len(experiment) != 64:
        raise ResultStoreError("experiment-id")
    base = output_dir.strip("/")
    directory = f"{base}/{experiment}"
    return (
        f"{directory}/candidate-execution-result.json",
        f"{directory}/experiment-manifest.json",
    )


def prepare_execution_write(
    output_dir: str,
    experiment: str,
    *,
    root: Path | None = None,
) -> None:
    """Reject an illegal or occupied artifact path before a run starts."""
    result_path, manifest_path = execution_result_paths(output_dir, experiment)
    base = root if root is not None else repo_root()
    if _destination(result_path, base).exists() or _destination(manifest_path, base).exists():
        raise ResultStoreError("overwrite")


def assert_result_identity(result: dict[str, Any]) -> None:
    validate("candidate-execution-result", result)
    expected = experiment_id(
        manifest_digest=str(result["candidateManifestDigest"]),
        corpus_digest=str(result["corpusDigest"]),
    )
    if result["experimentId"] != expected:
        raise ResultStoreError("experiment-id")
    if result["productionReady"] is not False:
        raise ResultStoreError("production-ready")
    digest = sha256_text(canonical_dumps(experiment_manifest_for(result)))
    if result["experimentManifestDigest"] != digest:
        raise ResultStoreError("experiment-manifest-digest")


def write_execution_result(
    output_dir: str,
    result: dict[str, Any],
    *,
    root: Path | None = None,
) -> str:
    """Write the execution result and its Track 2 experiment manifest."""
    assert_result_identity(result)
    result_path, manifest_path = execution_result_paths(output_dir, str(result["experimentId"]))
    base = root if root is not None else repo_root()
    result_file = _destination(result_path, base)
    manifest_file = _destination(manifest_path, base)
    if result_file.exists() or manifest_file.exists():
        raise ResultStoreError("overwrite")
    manifest = experiment_manifest_for(result)
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(canonical_dumps(result) + "\n", encoding="utf-8")
    manifest_file.write_text(canonical_dumps(manifest) + "\n", encoding="utf-8")
    return result_path


def read_execution_result(relative_path: str, root: Path | None = None) -> dict[str, Any]:
    loaded = read_json(relative_path, root=root)
    assert_result_identity(loaded)
    return loaded


def _exclusive_kind(document: dict[str, Any]) -> str:
    execution = "perCase" in document and "experimentId" in document
    comparison = "gateComparison" in document and "winner" in document and "left" in document
    calibration = "fixtureResults" in document and "calibrationDigest" in document
    matches = [
        name
        for name, present in (
            ("candidate-execution-result", execution),
            ("comparison-result", comparison),
            ("calibration-record", calibration),
        )
        if present
    ]
    if len(matches) != 1:
        raise ResultStoreError("artifact-kind")
    return matches[0]


def validate_comparison_artifact(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one comparison result. A production winner is rejected."""
    validate("comparison-result", document)
    if document["winner"] is not None or document["productionReady"] is not False:
        raise ResultStoreError("production-ready")
    return document


def validate_calibration_artifact(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one calibration record, including its digest and closed approvals."""
    validate("calibration-record", document)
    if document["productionReady"] is not False or document["approvalStatus"] != "not-approved":
        raise ResultStoreError("production-ready")
    for key in (
        "authorizesModel",
        "authorizesProvider",
        "authorizesShadowMode",
        "authorizesProductionComposition",
        "authorizesGateChange",
    ):
        if document[key] is not False:
            raise ResultStoreError("authorization")
    body = {key: value for key, value in document.items() if key != "calibrationDigest"}
    if document["calibrationDigest"] != sha256_text(canonical_dumps(body)):
        raise ResultStoreError("calibration-digest")
    return document


def validate_artifact(document: dict[str, Any]) -> str:
    """Dispatch on a closed set of artifact keys and return the artifact kind."""
    kind = _exclusive_kind(document)
    if kind == "candidate-execution-result":
        assert_result_identity(document)
    elif kind == "comparison-result":
        validate_comparison_artifact(document)
    else:
        validate_calibration_artifact(document)
    return kind


def read_validated_artifact(
    relative_path: str,
    kind: str,
    root: Path | None = None,
) -> dict[str, Any]:
    """Load one artifact and require the requested kind."""
    loaded = read_json(relative_path, root=root)
    if validate_artifact(loaded) != kind:
        raise ResultStoreError("artifact-kind")
    return loaded
