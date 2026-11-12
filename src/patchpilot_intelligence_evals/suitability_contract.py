"""Explanation-suitability contract. Existing metrics and gates stay unchanged."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
)
from patchpilot_intelligence_evals.corpus import EXPECTED_COUNTS
from patchpilot_intelligence_evals.explanation_suitability import rejects_quality_claim
from patchpilot_intelligence_evals.memory_model import RETRIEVED_ON
from patchpilot_intelligence_evals.metrics import METRIC_NAMES
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/explanation-suitability-contract.json")
CAPABILITY_IDS = (
    "instruction-following",
    "structured-output",
    "english-language",
    "context-capacity",
    "bounded-generation",
    "deterministic-fact-separation",
    "evidence-id-reproduction",
    "missing-evidence-reporting",
    "uncertainty-expression",
    "unsupported-request-refusal",
    "embedded-instruction-resistance",
    "state-mutation-avoidance",
    "cross-tenant-nondisclosure",
    "schema-compatibility",
)
SAFETY_CRITICAL = frozenset(
    {
        "deterministic-fact-separation",
        "evidence-id-reproduction",
        "missing-evidence-reporting",
        "uncertainty-expression",
        "unsupported-request-refusal",
        "embedded-instruction-resistance",
        "state-mutation-avoidance",
        "cross-tenant-nondisclosure",
        "schema-compatibility",
    }
)
CORPUS_CATEGORIES = tuple(EXPECTED_COUNTS)
_ALL = list(CORPUS_CATEGORIES)


class SuitabilityContractError(ValueError):
    """A suitability contract failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_suitability_contract() -> dict[str, Any]:
    """Build the fourteen-capability contract without measured-quality claims."""
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
        "retrievedOn": RETRIEVED_ON,
        "finalistModelId": LFM_MODEL_ID,
        "sourceRevision": LFM_SOURCE_REVISION,
        "onnxRevision": LFM_ONNX_REVISION,
        "measuredQualityClaimed": False,
        "gatesUnchanged": True,
        "capabilities": [_capability(capability_id) for capability_id in CAPABILITY_IDS],
    }
    return validate_suitability_contract(document)


def validate_suitability_contract(document: dict[str, Any]) -> dict[str, Any]:
    """Validate capability coverage, metric names, and corpus categories."""
    validate("explanation-suitability-contract", document)
    if contains_private_marker(document) or rejects_quality_claim(document):
        raise SuitabilityContractError("quality-claim")
    if document["locallyObservedArtifactDigests"] != [] or document["gatesUnchanged"] is not True:
        raise SuitabilityContractError("gates")
    rows = document["capabilities"]
    if [row["capabilityId"] for row in rows] != list(CAPABILITY_IDS):
        raise SuitabilityContractError("capability-set")
    if len({row["capabilityId"] for row in rows}) != len(CAPABILITY_IDS):
        raise SuitabilityContractError("capability-set")
    for row in rows:
        metric = row["metricName"]
        if metric is not None and metric not in METRIC_NAMES:
            raise SuitabilityContractError("metric")
        if not set(row["corpusCategories"]) <= set(CORPUS_CATEGORIES):
            raise SuitabilityContractError("corpus")
        if (
            row["capabilityId"] in SAFETY_CRITICAL
            and row["empiricalEvaluationRequired"] is not True
        ):
            raise SuitabilityContractError("empirical-required")
        if row["officialEvidenceRequired"] is not True:
            raise SuitabilityContractError("evidence")
    return document


def load_suitability_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the committed contract and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SuitabilityContractError("record-type")
    document = validate_suitability_contract(loaded)
    if document != decide_suitability_contract():
        raise SuitabilityContractError("record-drift")
    return document


def _capability(capability_id: str) -> dict[str, Any]:
    metric, corpus, future, empirical, authority = _MAP[capability_id]
    return {
        "capabilityId": capability_id,
        "metricName": metric,
        "corpusCategories": corpus,
        "futureTestCategory": future,
        "officialEvidenceRequired": True,
        "empiricalEvaluationRequired": empirical,
        "passAuthority": authority,
        "disqualifyingLimitationRule": (
            "An official prohibition of evidence-bounded explanation disqualifies this capability."
        ),
    }


_MAP: dict[str, tuple[str | None, list[str], str, bool, str]] = {
    "instruction-following": (None, _ALL, "all-cases", True, "empirical-harness"),
    "structured-output": ("outputSchemaValidity", _ALL, "all-cases", True, "empirical-harness"),
    "english-language": (None, _ALL, "all-cases", False, "official-statement"),
    "context-capacity": (None, _ALL, "context-cap-8192", False, "official-statement"),
    "bounded-generation": (None, _ALL, "output-bound", True, "empirical-harness"),
    "deterministic-fact-separation": (
        "affectednessOrPriorityChange",
        ["grounding-citation", "contradiction"],
        "grounding-citation",
        True,
        "empirical-harness",
    ),
    "evidence-id-reproduction": (
        "citationValidity",
        ["grounding-citation"],
        "grounding-citation",
        True,
        "empirical-harness",
    ),
    "missing-evidence-reporting": (
        None,
        ["insufficient-evidence-refusal", "stale-unavailable-incomparable"],
        "insufficient-evidence-refusal",
        True,
        "empirical-harness",
    ),
    "uncertainty-expression": (
        "correctUncertainty",
        ["contradiction", "insufficient-evidence-refusal", "stale-unavailable-incomparable"],
        "contradiction",
        True,
        "empirical-harness",
    ),
    "unsupported-request-refusal": (
        "correctRefusal",
        ["insufficient-evidence-refusal"],
        "insufficient-evidence-refusal",
        True,
        "empirical-harness",
    ),
    "embedded-instruction-resistance": (
        "promptInjectionResistance",
        ["prompt-injection"],
        "prompt-injection",
        True,
        "empirical-harness",
    ),
    "state-mutation-avoidance": (
        "unauthorizedStateMutation",
        _ALL,
        "all-cases",
        True,
        "empirical-harness",
    ),
    "cross-tenant-nondisclosure": (
        "crossTenantDisclosure",
        ["cross-tenant-negative-control"],
        "cross-tenant-negative-control",
        True,
        "empirical-harness",
    ),
    "schema-compatibility": (
        "outputSchemaValidity",
        _ALL,
        "all-cases",
        True,
        "empirical-harness",
    ),
}
