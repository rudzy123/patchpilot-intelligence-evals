"""Track 6A runtime security assessment.

This module does not install a runtime, download a model, or execute inference.
Track 5 safetensors approval stays a candidate-acquisition gap. It is not, by
itself, a Track 6A runtime disqualifier.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from patchpilot_intelligence_evals.schemas import repo_root, validate

CRITERIA: tuple[str, ...] = (
    "explicit-license",
    "immutable-version",
    "official-source",
    "clear-artifact-format",
    "cpu-only",
    "offline-loading",
    "local-artifact-paths",
    "no-remote-code-required",
    "no-mandatory-telemetry",
    "telemetry-can-be-disabled",
    "deterministic-settings",
    "advisories-reviewed",
    "subprocess-integration",
    "independent-acquisition-verification",
    "not-production-dependency",
)
RUNTIME_IDS: tuple[str, ...] = ("llama-cpp", "onnxruntime", "transformers")
_ASSESSMENT = Path("candidates/authorization/runtime-security-assessment.json")
_AUTHORIZATION = Path("candidates/authorization/runtime-authorization-v2.json")


class RuntimeSecurityError(ValueError):
    """A Track 6A runtime record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def failing_criteria(runtime: dict[str, Any]) -> list[str]:
    """Return failed criterion names in checklist order."""
    criteria = runtime["criteria"]
    return [name for name in CRITERIA if criteria[name] == "fail"]


def validate_assessment(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the three-runtime assessment."""
    validate("runtime-security-assessment", document)
    if document["installedDuringSession"] is not False:
        raise RuntimeSecurityError("runtime-installed")
    identifiers = [str(item["runtimeId"]) for item in document["runtimes"]]
    if identifiers != list(RUNTIME_IDS):
        raise RuntimeSecurityError("runtime-set")
    for runtime in document["runtimes"]:
        if list(runtime["disqualifiers"]) != failing_criteria(runtime):
            raise RuntimeSecurityError("disqualifier-mismatch")
        if runtime["criteria"]["advisories-reviewed"] == "fail" and not runtime["advisoryIds"]:
            raise RuntimeSecurityError("advisory-missing")
    return document


def validate_authorization(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one runtime authorization. Installation stays unauthorized."""
    validate("runtime-authorization-v2", document)
    if document["installedDuringSession"] is not False:
        raise RuntimeSecurityError("runtime-installed")
    if document["installationAuthorized"] is not False:
        raise RuntimeSecurityError("installation-authorized")
    if document["candidateSelected"] is not False:
        raise RuntimeSecurityError("candidate-selected")
    if document["locallyObservedArtifactDigests"]:
        raise RuntimeSecurityError("local-digest")
    failed = {str(item["runtimeId"]) for item in document["disqualifiers"]}
    outcome = str(document["authorizationOutcome"])
    runtime_id = document["runtimeId"]
    if outcome == "no-runtime":
        if runtime_id is not None or document["versionTag"] is not None:
            raise RuntimeSecurityError("runtime-selected")
        if document["immutableRevision"] is not None or document["artifactFormat"] is not None:
            raise RuntimeSecurityError("runtime-selected")
        if not document["disqualifiers"]:
            raise RuntimeSecurityError("disqualifier-missing")
        return document
    if not isinstance(runtime_id, str) or runtime_id in failed:
        raise RuntimeSecurityError("runtime-selected")
    if len(RUNTIME_IDS) - len(failed) != 1:
        raise RuntimeSecurityError("runtime-count")
    if document["candidateFormatGap"] is not True:
        raise RuntimeSecurityError("format-gap")
    return document


def decide(assessment: dict[str, Any]) -> dict[str, Any]:
    """Authorize one runtime, or preserve no-runtime when that bar is not met."""
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
        artifact_format = chosen["artifactFormat"]
    else:
        outcome = "no-runtime"
        runtime_id = None
        version_tag = None
        revision = None
        artifact_format = None
    return validate_authorization(
        {
            "schemaVersion": "1.0.0",
            "productionReady": False,
            "realModelExecuted": False,
            "retrievedOn": document["retrievedOn"],
            "authorizationOutcome": outcome,
            "runtimeId": runtime_id,
            "versionTag": version_tag,
            "immutableRevision": revision,
            "artifactFormat": artifact_format,
            "approvedCandidateFormat": "safetensors",
            "candidateFormatGap": True,
            "assessedRuntimeIds": [item["runtimeId"] for item in document["runtimes"]],
            "disqualifiers": disqualifiers,
            "acquisitionStatus": "not-acquired",
            "executionStatus": "not-executed",
            "locallyObservedArtifactDigests": [],
            "installedDuringSession": False,
            "installationAuthorized": False,
            "candidateSelected": False,
        }
    )


def load_assessment(root: Path | None = None) -> dict[str, Any]:
    """Load the committed Track 6A runtime assessment."""
    return _load(root, _ASSESSMENT, validate_assessment)


def load_authorization(root: Path | None = None) -> dict[str, Any]:
    """Load the committed authorization and require it to match the assessment."""
    base = root if root is not None else repo_root()
    document = _load(base, _AUTHORIZATION, validate_authorization)
    if document != decide(load_assessment(base)):
        raise RuntimeSecurityError("authorization-drift")
    return document


def _load(
    root: Path | None,
    relative: Path,
    checker: Any,
) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeSecurityError("record-type")
    return cast(dict[str, Any], checker(cast(dict[str, Any], loaded)))
