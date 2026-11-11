"""Explanation suitability from official documentation only.

The record does not claim measured grounding or hallucination performance.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
    decide_candidate_discovery,
    evidence,
)
from patchpilot_intelligence_evals.candidate_eligibility import RETRIEVED_ON
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/finalist-explanation-suitability.json")
TOPICS = (
    "instructionFollowing",
    "structuredOutput",
    "englishLanguage",
    "contextSufficiency",
    "conciseGeneration",
    "factualExplanationLimitations",
    "safetyLimitations",
    "citationIdReproduction",
    "refusalAndUncertainty",
    "deploymentCaveats",
)
_POSITIVE = frozenset({"supported", "stated"})
_OPEN = frozenset({"not-stated", "unresolved"})
_BANNED = (
    "measured hallucination",
    "hallucination rate",
    "benchmark rank",
    "grounding accuracy",
    "measured grounding",
)
_CARD = f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/{LFM_SOURCE_REVISION}/README.md"
_ONNX = (
    f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/{LFM_ONNX_REVISION}/README.md"
)


class SuitabilityError(ValueError):
    """A suitability record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def suitability_outcome(topics: Mapping[str, str]) -> str:
    """Unsupported evidence is unsuitable. Any open topic stays unresolved."""
    if set(topics) != set(TOPICS):
        raise SuitabilityError("topic-set")
    if any(topics[name] == "unsupported" for name in TOPICS):
        return "unsuitable"
    if any(topics[name] in _OPEN for name in TOPICS):
        return "unresolved"
    if all(topics[name] in _POSITIVE for name in TOPICS):
        return "suitable-for-offline-evaluation"
    return "unresolved"


def rejects_quality_claim(document: dict[str, Any]) -> bool:
    """True when a record asserts measured explanation quality."""
    text = json.dumps(document).lower()
    return any(phrase in text for phrase in _BANNED)


def decide_explanation_suitability() -> dict[str, Any]:
    """Build the committed suitability decision for the discovery finalist."""
    _require_finalist()
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "finalistCount": 1,
        "finalistModelIds": [LFM_MODEL_ID],
        "measuredQualityClaimed": False,
        "locallyObservedArtifactDigests": [],
        "finalists": [_lfm()],
    }
    return validate_explanation_suitability(document)


def validate_explanation_suitability(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one suitability record."""
    validate("finalist-explanation-suitability", document)
    if contains_private_marker(document):
        raise SuitabilityError("identity")
    if rejects_quality_claim(document):
        raise SuitabilityError("quality-claim")
    if document["locallyObservedArtifactDigests"] != []:
        raise SuitabilityError("local-digest")
    if document["measuredQualityClaimed"] is not False:
        raise SuitabilityError("quality-claim")
    _require_finalist(document["finalistModelIds"])
    finalists = document["finalists"]
    if [item["modelId"] for item in finalists] != document["finalistModelIds"]:
        raise SuitabilityError("finalist-boundary")
    if document["finalistCount"] != len(finalists):
        raise SuitabilityError("finalist-count")
    for item in finalists:
        topics = {entry["topic"]: entry["status"] for entry in item["assessments"]}
        if item["suitabilityOutcome"] != suitability_outcome(topics):
            raise SuitabilityError("outcome")
        evidence_ids = {entry["evidenceId"] for entry in item["evidence"]}
        for entry in item["assessments"]:
            if entry["evidenceId"] not in evidence_ids:
                raise SuitabilityError("evidence")
        if not any(entry["evidenceClass"] == "authoritative" for entry in item["evidence"]):
            raise SuitabilityError("evidence")
    return document


def load_explanation_suitability(root: Path | None = None) -> dict[str, Any]:
    """Load the committed suitability record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SuitabilityError("record-type")
    document = validate_explanation_suitability(loaded)
    if document != decide_explanation_suitability():
        raise SuitabilityError("suitability-drift")
    return document


def _require_finalist(model_ids: list[str] | None = None) -> None:
    expected = decide_candidate_discovery()["finalistModelIds"]
    if expected != [LFM_MODEL_ID]:
        raise SuitabilityError("finalist-boundary")
    if model_ids is not None and model_ids != expected:
        raise SuitabilityError("finalist-boundary")


def _lfm() -> dict[str, Any]:
    statuses = {
        "instructionFollowing": "supported",
        "structuredOutput": "supported",
        "englishLanguage": "supported",
        "contextSufficiency": "supported",
        "conciseGeneration": "supported",
        "factualExplanationLimitations": "stated",
        "safetyLimitations": "not-stated",
        "citationIdReproduction": "unresolved",
        "refusalAndUncertainty": "unresolved",
        "deploymentCaveats": "stated",
    }
    card_topics = {
        "instructionFollowing",
        "structuredOutput",
        "englishLanguage",
        "contextSufficiency",
        "conciseGeneration",
        "factualExplanationLimitations",
        "safetyLimitations",
        "citationIdReproduction",
        "refusalAndUncertainty",
    }
    assessments = [
        {
            "topic": topic,
            "status": statuses[topic],
            "evidenceId": "lfm-suitability-card"
            if topic in card_topics
            else "lfm-suitability-onnx",
        }
        for topic in TOPICS
    ]
    return {
        "modelId": LFM_MODEL_ID,
        "assessments": assessments,
        "suitabilityOutcome": suitability_outcome(statuses),
        "evidence": [
            evidence(
                "lfm-suitability-card",
                "LFM2.5-1.2B-Instruct model card",
                _CARD,
                "Liquid AI",
                LFM_SOURCE_REVISION,
                (
                    "The pinned card describes an English-capable instruction model with "
                    "32768 tokens of context, tool-calling guidance, and a stated limit "
                    "for knowledge-intensive tasks and programming. Safety, citation, and "
                    "refusal behavior are not stated."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "restrictive-reading",
            ),
            evidence(
                "lfm-suitability-onnx",
                "LFM2.5 ONNX model card",
                _ONNX,
                "Liquid AI",
                LFM_ONNX_REVISION,
                (
                    "The pinned ONNX card documents local ONNX Runtime execution for this "
                    "export and requires the external-data files beside the graph."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "none",
            ),
        ],
    }
