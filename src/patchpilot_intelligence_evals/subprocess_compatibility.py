"""Bounded-subprocess compatibility for the Track 6B adapter contract.

A runtime note does not make a candidate compatible without an official graph.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_eligibility import (
    MODEL_IDS,
    EligibilityError,
    reject_private_markers,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/bounded-subprocess-compatibility.json")
_ADAPTER = Path("candidates/authorization/runtime-adapter-contract.json")
PROPERTIES: tuple[str, ...] = (
    "verified-runtime-identity",
    "verified-onnx-graph",
    "complete-external-data",
    "verified-tokenizer-configuration",
    "direct-argument-arrays",
    "no-shell",
    "hardened-launcher",
    "offline-execution",
    "telemetry-disabled",
    "no-automatic-retrieval",
    "no-remote-code",
    "no-automatic-conversion",
    "bounded-startup",
    "bounded-generation",
    "one-request-one-response",
    "process-tree-cleanup",
)


class SubprocessError(ValueError):
    """A subprocess record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def subprocess_compatible(properties: dict[str, str], direct_onnx_eligible: bool) -> bool:
    """Every property must pass, and the official ONNX path must already qualify."""
    if set(properties) != set(PROPERTIES):
        raise SubprocessError("property-set")
    return direct_onnx_eligible and all(properties[name] == "pass" for name in PROPERTIES)


def decide_subprocess_compatibility() -> dict[str, Any]:
    """Build the committed fail-closed compatibility record."""
    _require_adapter()
    families = [
        {
            "modelId": model_id,
            "directOnnxEligible": False,
            "properties": [{"name": name, "result": "fail"} for name in PROPERTIES],
            "compatibilityOutcome": "fail",
        }
        for model_id in MODEL_IDS
    ]
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": "2026-11-11",
        "adapterId": "patchpilot-onnxruntime-adapter",
        "adapterVersion": "1.0.0",
        "versionTag": "v1.31.1",
        "immutableRevision": "6af1a932e2286d5c58166085d24c68783033edee",
        "profileId": "linux-bwrap-systemd-v1",
        "runtimeNoteQualifiesCandidate": False,
        "locallyObservedArtifactDigests": [],
        "families": families,
        "evidence": [
            {
                "evidenceId": "onnxruntime-v1311",
                "sourceName": "ONNX Runtime v1.31.1 release",
                "url": "https://github.com/microsoft/onnxruntime/releases/tag/v1.31.1",
                "publisher": "Microsoft",
                "retrievedOn": "2026-11-11",
                "claim": "The v1.31.1 tag matches the adapter revision and publishes no graph.",
                "evidenceClass": "authoritative",
            },
            {
                "evidenceId": "onnxruntime-v1310-telemetry",
                "sourceName": "ONNX Runtime v1.31.0 release",
                "url": "https://github.com/microsoft/onnxruntime/releases/tag/v1.31.0",
                "publisher": "Microsoft",
                "retrievedOn": "2026-11-11",
                "claim": "The source-build telemetry flag is inherited and qualifies no candidate.",
                "evidenceClass": "authoritative",
            },
            {
                "evidenceId": "onnxruntime-v1311-privacy",
                "sourceName": "ONNX Runtime v1.31.1 privacy document",
                "url": "https://github.com/microsoft/onnxruntime/blob/v1.31.1/docs/Privacy.md",
                "publisher": "Microsoft",
                "retrievedOn": "2026-11-11",
                "claim": "The v1.31.1 privacy document body was empty on this retrieval.",
                "evidenceClass": "unresolved",
            },
        ],
    }
    return validate_subprocess_compatibility(document)


def validate_subprocess_compatibility(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one compatibility record."""
    validate("bounded-subprocess-compatibility", document)
    try:
        reject_private_markers(document, EligibilityError)
    except EligibilityError as exc:
        raise SubprocessError(exc.code) from exc
    if document["runtimeNoteQualifiesCandidate"] is not False:
        raise SubprocessError("runtime-note")
    families = document["families"]
    if [item["modelId"] for item in families] != list(MODEL_IDS):
        raise SubprocessError("candidate-boundary")
    for item in families:
        mapping = {entry["name"]: entry["result"] for entry in item["properties"]}
        if [entry["name"] for entry in item["properties"]] != list(PROPERTIES):
            raise SubprocessError("property-order")
        expected = "pass" if subprocess_compatible(mapping, item["directOnnxEligible"]) else "fail"
        if item["compatibilityOutcome"] != expected:
            raise SubprocessError("compatibility")
    return document


def load_subprocess_compatibility(root: Path | None = None) -> dict[str, Any]:
    """Load the committed record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SubprocessError("record-type")
    document = validate_subprocess_compatibility(loaded)
    if document != decide_subprocess_compatibility():
        raise SubprocessError("subprocess-drift")
    return document


def _require_adapter() -> None:
    contract = json.loads((repo_root() / _ADAPTER).read_text(encoding="utf-8"))
    expected = {
        "adapterId": "patchpilot-onnxruntime-adapter",
        "adapterVersion": "1.0.0",
        "versionTag": "v1.31.1",
        "immutableRevision": "6af1a932e2286d5c58166085d24c68783033edee",
        "profileId": "linux-bwrap-systemd-v1",
        "argumentStyle": "direct-argument-vector",
        "shell": "prohibited",
        "telemetry": "disabled",
        "automaticRetrieval": "prohibited",
        "automaticConversion": "prohibited",
        "oneRequestOneResponse": True,
        "offlineMode": "required",
    }
    for key, value in expected.items():
        if contract[key] != value:
            raise SubprocessError("adapter-contract")
