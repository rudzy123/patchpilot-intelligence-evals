"""4,096-token and 8,192-token resident envelopes. Unknown upper bounds stay unresolved."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
)
from patchpilot_intelligence_evals.memory_evidence import decide_memory_evidence
from patchpilot_intelligence_evals.memory_model import (
    CATEGORY_IDS,
    CONTEXTS,
    GIBIBYTE,
    LOGICAL_PARAMETER_BYTES,
    PARAMETER_COUNT,
    RETRIEVED_ON,
    MemoryModelError,
    classify_peak,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/candidate-memory-budget.json")
_RUNTIME_REVISION = "6af1a932e2286d5c58166085d24c68783033edee"


class MemoryBudgetError(ValueError):
    """A memory-budget record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_memory_budget() -> dict[str, Any]:
    """Build both envelopes from the evidence dispositions. Unknown parts are not zero."""
    evidence = decide_memory_evidence()
    by_id = {row["categoryId"]: row for row in evidence["categories"]}
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
        "runtimeId": "onnxruntime",
        "runtimeVersionTag": "v1.31.1",
        "runtimeRevision": _RUNTIME_REVISION,
        "precision": "fp32",
        "batchSize": 1,
        "processCount": 1,
        "executionProvider": "cpu",
        "quantizationApproved": False,
        "speculativeExecution": False,
        "automaticBatching": False,
        "ceilingBytes": MEMORY_CAP,
        "gibibyteBytes": GIBIBYTE,
        "roundingRule": "integer-exact",
        "overflowDomain": "signed-int64",
        "measurementPerformed": False,
        "envelopes": [_envelope(context, by_id) for context in CONTEXTS],
    }
    return validate_memory_budget(document)


def validate_memory_budget(document: dict[str, Any]) -> dict[str, Any]:
    """Validate both envelopes against the fail-closed peak classifier."""
    validate("candidate-memory-budget", document)
    if contains_private_marker(document):
        raise MemoryBudgetError("identity")
    if (
        document["locallyObservedArtifactDigests"] != []
        or document["measurementPerformed"] is not False
    ):
        raise MemoryBudgetError("measurement")
    if document["ceilingBytes"] != MEMORY_CAP or document["gibibyteBytes"] != GIBIBYTE:
        raise MemoryBudgetError("ceiling")
    contexts = [item["contextTokens"] for item in document["envelopes"]]
    if contexts != list(CONTEXTS):
        raise MemoryBudgetError("context")
    for envelope in document["envelopes"]:
        rows = envelope["categories"]
        if [row["categoryId"] for row in rows] != list(CATEGORY_IDS):
            raise MemoryBudgetError("category-set")
        try:
            decision = classify_peak(rows, ceiling=document["ceilingBytes"])
        except MemoryModelError as exc:
            raise MemoryBudgetError(exc.code) from exc
        if envelope["classification"] != decision["classification"]:
            raise MemoryBudgetError("classification")
        if envelope["upperBoundBytes"] != decision["upperBoundBytes"]:
            raise MemoryBudgetError("upper-bound")
        if envelope["lowerBoundBytes"] != decision["lowerBoundBytes"]:
            raise MemoryBudgetError("lower-bound")
        if envelope["ceilingComparison"] != decision["ceilingComparison"]:
            raise MemoryBudgetError("ceiling")
        if envelope["unresolvedCategoryIds"] != decision["unresolvedCategoryIds"]:
            raise MemoryBudgetError("unresolved")
        static = rows[0]
        logical_excluded = static["logicalBytesIncludedInPeak"] is not False
        if static["logicalBytes"] != LOGICAL_PARAMETER_BYTES or logical_excluded:
            raise MemoryBudgetError("parameter-product")
        if static["upperBoundBytes"] is not None:
            raise MemoryBudgetError("storage-as-resident")
    return document


def load_memory_budget(root: Path | None = None) -> dict[str, Any]:
    """Load the committed budget and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MemoryBudgetError("record-type")
    document = validate_memory_budget(loaded)
    if document != decide_memory_budget():
        raise MemoryBudgetError("record-drift")
    return document


def _envelope(context: int, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = [_budget_row(by_id[category_id], context) for category_id in CATEGORY_IDS]
    decision = classify_peak(rows)
    return {
        "contextTokens": context,
        "classification": decision["classification"],
        "lowerBoundBytes": decision["lowerBoundBytes"],
        "upperBoundBytes": decision["upperBoundBytes"],
        "ceilingBytes": decision["ceilingBytes"],
        "ceilingComparison": decision["ceilingComparison"],
        "bytesRelativeToCeiling": decision["bytesRelativeToCeiling"],
        "unresolvedCategoryIds": decision["unresolvedCategoryIds"],
        "categories": rows,
    }


def _budget_row(evidence_row: dict[str, Any], context: int) -> dict[str, Any]:
    category_id = str(evidence_row["categoryId"])
    return {
        "categoryId": category_id,
        "unit": "bytes",
        "memoryDomain": "resident",
        "includedInTotal": True,
        "countsParameterPayload": category_id == "static_parameter_memory",
        "evidenceStatus": evidence_row["evidenceStatus"],
        "valueType": evidence_row["valueType"],
        "lowerBoundBytes": evidence_row["lowerBoundBytes"],
        "upperBoundBytes": evidence_row["upperBoundBytes"],
        "logicalBytes": evidence_row["logicalBytes"],
        "logicalBytesIncludedInPeak": evidence_row["logicalBytesIncludedInPeak"],
        "formula": _FORMULAS[category_id],
        "inputs": _inputs(category_id, context),
        "evidenceIds": list(evidence_row["evidenceIds"]),
        "uncertainty": evidence_row["uncertainty"],
        "contextTokens": context,
    }


def _inputs(category_id: str, context: int) -> list[str]:
    if category_id == "static_parameter_memory":
        return [
            f"parameterCount={PARAMETER_COUNT}",
            "bytesPerParameter=4",
            "logicalProductIncludedInPeak=false",
        ]
    if category_id in {
        "activation_memory",
        "architecture_state_memory",
        "input_output_tensor_memory",
    }:
        return ["batchSize=1", f"contextTokens={context}", "precision=fp32", "width=unknown"]
    if category_id == "safety_margin":
        return ["explicitMarginBytes=null", "completeUpperBounds=false"]
    return ["contextIndependent=true", "residentBytes=unknown"]


_FORMULAS = {
    "static_parameter_memory": "parameter_count * bytes_per_fp32_parameter",
    "graph_and_initializer_overhead": (
        "resident_initializer_bytes_excluding_counted_parameter_payload"
    ),
    "runtime_process_baseline": "runtime_process_resident_bytes",
    "allocator_and_optimization_overhead": (
        "arena_pattern_optimizer_and_thread_pool_resident_bytes"
    ),
    "activation_memory": "batch_size * sequence_tokens * activation_bytes_per_token",
    "architecture_state_memory": "attention_state_bytes + convolution_state_bytes",
    "input_output_tensor_memory": "input_id_bytes + mask_bytes + logits_bytes",
    "tokenizer_and_configuration_memory": (
        "resident_tokenizer_bytes + resident_configuration_bytes"
    ),
    "hardened_execution_overhead": "launcher_ipc_and_attestation_resident_bytes",
    "safety_margin": "explicit_margin_bytes_after_complete_upper_bounds",
}
