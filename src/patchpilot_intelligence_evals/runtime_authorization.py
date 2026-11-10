"""Runtime assessment records. This module does not install a runtime."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from patchpilot_intelligence_evals.schemas import repo_root, validate

CRITERIA: tuple[str, ...] = (
    "approved-format-support",
    "bounded-context-and-output",
    "cpu-support",
    "deterministic-controls",
    "documented-artifact-loading",
    "explicit-open-source-license",
    "explicit-telemetry-disablement",
    "immutable-version",
    "local-artifact-paths",
    "maintainable-security-posture",
    "no-mandatory-cloud",
    "no-mandatory-telemetry",
    "no-production-dependency",
    "no-trust-remote-code",
    "offline-local-loading",
    "subprocess-compatibility",
)
RUNTIME_IDS: tuple[str, ...] = ("llama-cpp", "onnxruntime", "transformers")
_ASSESSMENT = Path("candidates/authorization/runtime-assessment.json")
_AUTHORIZATION = Path("candidates/authorization/runtime-authorization.json")


class RuntimeAuthorizationError(ValueError):
    """A runtime record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def failing_criteria(runtime: dict[str, Any]) -> list[str]:
    """Return failed criterion names in schema order."""
    criteria = runtime["criteria"]
    return [name for name in CRITERIA if criteria[name] == "fail"]


def validate_assessment(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the three-runtime assessment."""
    validate("runtime-assessment", document)
    if document["installedDuringSession"] is not False:
        raise RuntimeAuthorizationError("runtime-installed")
    identifiers = [str(item["runtimeId"]) for item in document["runtimes"]]
    if sorted(identifiers) != sorted(RUNTIME_IDS) or len(set(identifiers)) != 3:
        raise RuntimeAuthorizationError("runtime-set")
    for runtime in document["runtimes"]:
        if list(runtime["disqualifiers"]) != failing_criteria(runtime):
            raise RuntimeAuthorizationError("disqualifier-mismatch")
    return document


def validate_authorization(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one runtime authorization outcome."""
    validate("runtime-authorization", document)
    if document["installedDuringSession"] is not False:
        raise RuntimeAuthorizationError("runtime-installed")
    if document["locallyObservedArtifactDigests"]:
        raise RuntimeAuthorizationError("local-digest")
    failed_ids = {str(item["runtimeId"]) for item in document["disqualifiers"]}
    outcome = document["authorizationOutcome"]
    runtime_id = document["runtimeId"]
    if outcome == "no-runtime":
        if runtime_id is not None or document["versionTag"] is not None:
            raise RuntimeAuthorizationError("runtime-selected")
        if document["immutableRevision"] is not None:
            raise RuntimeAuthorizationError("runtime-selected")
        return document
    if runtime_id is None or runtime_id in failed_ids:
        raise RuntimeAuthorizationError("runtime-selected")
    if len(document["assessedRuntimeIds"]) - len(failed_ids) != 1:
        raise RuntimeAuthorizationError("runtime-count")
    return document


def decide(assessment: dict[str, Any]) -> dict[str, Any]:
    """Authorize one runtime, or record no-runtime when that bar is not met."""
    document = validate_assessment(assessment)
    passing = [item for item in document["runtimes"] if not failing_criteria(item)]
    disqualifiers = [
        {"runtimeId": item["runtimeId"], "criteria": failing_criteria(item)}
        for item in document["runtimes"]
        if failing_criteria(item)
    ]
    if len(passing) == 1:
        chosen = passing[0]
        outcome = "authorized"
        runtime_id = chosen["runtimeId"]
        version_tag = chosen["versionTag"]
        revision = chosen["immutableRevision"]
    else:
        outcome = "no-runtime"
        runtime_id = None
        version_tag = None
        revision = None
    return validate_authorization(
        {
            "schemaVersion": "1.0.0",
            "productionReady": False,
            "retrievedOn": document["retrievedOn"],
            "authorizationOutcome": outcome,
            "runtimeId": runtime_id,
            "versionTag": version_tag,
            "immutableRevision": revision,
            "assessedRuntimeIds": [item["runtimeId"] for item in document["runtimes"]],
            "disqualifiers": disqualifiers,
            "acquisitionStatus": "not-acquired",
            "executionStatus": "not-executed",
            "locallyObservedArtifactDigests": [],
            "installedDuringSession": False,
        }
    )


def load_assessment(root: Path | None = None) -> dict[str, Any]:
    """Load the committed runtime assessment."""
    return _load(root, _ASSESSMENT, validate_assessment)


def load_authorization(root: Path | None = None) -> dict[str, Any]:
    """Load the committed authorization and require it to match the assessment."""
    base = root if root is not None else repo_root()
    document = _load(base, _AUTHORIZATION, validate_authorization)
    if document != decide(load_assessment(base)):
        raise RuntimeAuthorizationError("authorization-drift")
    return document


def _load(
    root: Path | None,
    relative: Path,
    checker: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeAuthorizationError("record-type")
    return checker(cast(dict[str, Any], loaded))
