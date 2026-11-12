"""Official suitability evidence. Card statements do not prove measured behavior."""

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
from patchpilot_intelligence_evals.explanation_suitability import rejects_quality_claim
from patchpilot_intelligence_evals.memory_model import RETRIEVED_ON
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.suitability_contract import (
    CAPABILITY_IDS,
    SAFETY_CRITICAL,
    SuitabilityContractError,
    decide_suitability_contract,
)

_RECORD = Path("candidates/authorization/explanation-suitability-evidence.json")
_CARD = f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/{LFM_SOURCE_REVISION}/README.md"
_ONNX = (
    f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/{LFM_ONNX_REVISION}/README.md"
)
_RESULTS = (
    "supported-in-principle",
    "unsupported",
    "unresolved",
    "requires-empirical-evaluation",
)
_SUPPORTED = frozenset(
    {"instruction-following", "structured-output", "english-language", "context-capacity"}
)


class SuitabilityEvidenceError(ValueError):
    """A suitability-evidence record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def screening_outcome(rows: list[dict[str, Any]]) -> str:
    """Disqualifiers fail. Empirical gaps stay eligible rather than proven."""
    if [row["capabilityId"] for row in rows] != list(CAPABILITY_IDS):
        raise SuitabilityEvidenceError("capability-set")
    if any(
        row["result"] == "unsupported" or row["disqualifyingLimitation"] is True for row in rows
    ):
        return "disqualified"
    if any(row["empiricalEvaluationRequired"] is True for row in rows):
        return "eligible-for-controlled-evaluation"
    if all(row["result"] == "supported-in-principle" for row in rows):
        return "evidence-closed"
    return "unresolved"


def decide_suitability_evidence() -> dict[str, Any]:
    """Map the pinned card onto the contract without measured behavior claims."""
    contract = decide_suitability_contract()
    rows = [_assessment(row) for row in contract["capabilities"]]
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
        "screeningOutcome": screening_outcome(rows),
        "evidence": _catalog(),
        "capabilities": rows,
    }
    return validate_suitability_evidence(document)


def validate_suitability_evidence(document: dict[str, Any]) -> dict[str, Any]:
    """Validate evidence authority and the ban on unsupported quality claims."""
    validate("explanation-suitability-evidence", document)
    if contains_private_marker(document) or rejects_quality_claim(document):
        raise SuitabilityEvidenceError("quality-claim")
    if document["locallyObservedArtifactDigests"] != []:
        raise SuitabilityEvidenceError("local-digest")
    if document["measuredQualityClaimed"] is not False:
        raise SuitabilityEvidenceError("quality-claim")
    try:
        contract = {
            row["capabilityId"]: row for row in decide_suitability_contract()["capabilities"]
        }
    except SuitabilityContractError as exc:
        raise SuitabilityEvidenceError(exc.code) from exc
    catalog = {item["evidenceId"]: item for item in document["evidence"]}
    if len(catalog) != len(document["evidence"]) or "lfm-card-use" not in catalog:
        raise SuitabilityEvidenceError("evidence")
    rows = document["capabilities"]
    if document["screeningOutcome"] != screening_outcome(rows):
        raise SuitabilityEvidenceError("outcome")
    for row in rows:
        if row["result"] not in _RESULTS:
            raise SuitabilityEvidenceError("result")
        expected = contract[row["capabilityId"]]
        if row["metricName"] != expected["metricName"]:
            raise SuitabilityEvidenceError("metric")
        if row["empiricalEvaluationRequired"] != expected["empiricalEvaluationRequired"]:
            raise SuitabilityEvidenceError("empirical-required")
        if (
            row["capabilityId"] in SAFETY_CRITICAL
            and row["empiricalEvaluationRequired"] is not True
        ):
            raise SuitabilityEvidenceError("empirical-required")
        if row["result"] == "supported-in-principle" and row["capabilityId"] in SAFETY_CRITICAL:
            raise SuitabilityEvidenceError("quality-claim")
        for evidence_id in row["evidenceIds"]:
            if evidence_id not in catalog:
                raise SuitabilityEvidenceError("evidence")
            if catalog[evidence_id]["evidenceClass"] not in {
                "authoritative",
                "conflicting",
                "unresolved",
            }:
                raise SuitabilityEvidenceError("evidence")
    return document


def load_suitability_evidence(root: Path | None = None) -> dict[str, Any]:
    """Load the committed evidence and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SuitabilityEvidenceError("record-type")
    document = validate_suitability_evidence(loaded)
    if document != decide_suitability_evidence():
        raise SuitabilityEvidenceError("record-drift")
    return document


def _assessment(contract_row: dict[str, Any]) -> dict[str, Any]:
    capability_id = str(contract_row["capabilityId"])
    if capability_id in _SUPPORTED:
        result = "supported-in-principle"
    else:
        result = "requires-empirical-evaluation"
    return {
        "capabilityId": capability_id,
        "result": result,
        "metricName": contract_row["metricName"],
        "empiricalEvaluationRequired": contract_row["empiricalEvaluationRequired"],
        "disqualifyingLimitation": False,
        "evidenceIds": ["lfm-card-use", "lfm-card-shape"],
        "rationale": _RATIONALE[capability_id],
    }


def _catalog() -> list[dict[str, Any]]:
    return [
        _source(
            "lfm-card-use",
            "LFM2.5-1.2B-Instruct model card",
            _CARD,
            LFM_SOURCE_REVISION,
            (
                "The pinned card describes an instruction-tuned model with English among "
                "its languages, recommends agentic tasks, data extraction, and RAG, and "
                "says knowledge-intensive tasks and programming are not recommended. JSON "
                "tool definitions and optional JSON function calls are shown."
            ),
            "authoritative",
            "Pinned source card suitability statements",
            "restrictive-reading",
        ),
        _source(
            "lfm-card-shape",
            "LFM2.5-1.2B-Instruct model card",
            _CARD,
            LFM_SOURCE_REVISION,
            (
                "The pinned card states a 32768-token context and a 65536-token vocabulary. "
                "It does not state a 400-character or 1200-word output guarantee."
            ),
            "authoritative",
            "Pinned source card context and vocabulary",
            "none",
        ),
        _source(
            "lfm-docs-overview",
            "Liquid AI LFM2.5-1.2B-Instruct page",
            "https://docs.liquid.ai/lfm/models/lfm25-1.2b-instruct",
            None,
            (
                "The Liquid AI model page states an instruction-tuned dense model with a "
                "32K context and native tool calling. It does not measure refusal, citation, "
                "or tenant behavior."
            ),
            "authoritative",
            "Official model page for the same model id",
            "none",
        ),
        _source(
            "lfm-onnx-deployment",
            "LFM2.5-1.2B-Instruct-ONNX model card",
            _ONNX,
            LFM_ONNX_REVISION,
            (
                "The pinned ONNX card recommends Q4 for most uses and shows a quickstart for "
                "that variant. It does not measure citation, refusal, or schema validity."
            ),
            "authoritative",
            "Pinned ONNX card deployment notes, not measured behavior",
            "restrictive-reading",
        ),
    ]


def _source(
    evidence_id: str,
    source_name: str,
    url: str,
    revision: str | None,
    claim: str,
    evidence_class: str,
    applicability: str,
    disposition: str,
) -> dict[str, Any]:
    return {
        "evidenceId": evidence_id,
        "sourceName": source_name,
        "url": url,
        "publisher": "Liquid AI",
        "retrievedOn": RETRIEVED_ON,
        "immutableRevision": revision,
        "documentationVersion": None if revision is not None else "retrieved-2026-11-12",
        "claim": claim,
        "evidenceClass": evidence_class,
        "applicability": applicability,
        "valueType": "not-provided",
        "units": "not-applicable",
        "conflictDisposition": disposition,
    }


_RATIONALE = {
    "instruction-following": (
        "The card calls the model instruction-tuned. Actual following is unmeasured."
    ),
    "structured-output": (
        "The card shows JSON tool calls. Finding-explanation schema validity is unmeasured."
    ),
    "english-language": "The card lists English among the supported languages.",
    "context-capacity": (
        "The published 32768-token context covers the 8192 evaluation cap. Memory fit is separate."
    ),
    "bounded-generation": (
        "The card does not guarantee the 400-character or 1200-word output bounds."
    ),
    "deterministic-fact-separation": (
        "The knowledge-task caveat is not a prohibition of supplied-evidence explanation. "
        "Fact separation is unmeasured."
    ),
    "evidence-id-reproduction": "The card does not state evidence-identifier reproduction.",
    "missing-evidence-reporting": "The card does not state missing-evidence reporting.",
    "uncertainty-expression": "The card does not state uncertainty behavior.",
    "unsupported-request-refusal": "The card does not state refusal behavior.",
    "embedded-instruction-resistance": (
        "The card does not state resistance to embedded instructions."
    ),
    "state-mutation-avoidance": "The card does not state state-mutation behavior.",
    "cross-tenant-nondisclosure": "The card does not state cross-tenant behavior.",
    "schema-compatibility": "JSON tool guidance is not finding-explanation schema validity.",
}
