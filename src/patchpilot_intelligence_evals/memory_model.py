"""Authoritative memory-model contract for the Track 7 finalist.

Logical FP32 parameter bytes are not resident peak process memory. An unknown
required upper bound stays unresolved and is never replaced with zero.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/candidate-memory-model.json")
RETRIEVED_ON = "2026-11-12"
PARAMETER_COUNT = 1_170_340_608
BYTES_PER_FP32 = 4
LOGICAL_PARAMETER_BYTES = 4_681_362_432
GIBIBYTE = 1024**3
DECIMAL_GIGABYTE = 1000**3
_DOMAIN_MAX = 2**63 - 1
CONTEXTS = (4096, 8192)
CATEGORY_IDS = (
    "static_parameter_memory",
    "graph_and_initializer_overhead",
    "runtime_process_baseline",
    "allocator_and_optimization_overhead",
    "activation_memory",
    "architecture_state_memory",
    "input_output_tensor_memory",
    "tokenizer_and_configuration_memory",
    "hardened_execution_overhead",
    "safety_margin",
)
EVIDENCE_STATUSES = (
    "authoritative-measured",
    "authoritative-published-bound",
    "deterministic-calculation",
    "conservative-assumption",
    "unresolved",
)
RESIDENT_DOMAINS = (
    "resident",
    "logical-storage",
    "virtual-address",
    "allocator-capacity",
    "mapped-file",
)
_REJECTED_UNITS = frozenset({"GB", "gb", "decimal-gigabytes", "GiB", "gib"})


class MemoryModelError(ValueError):
    """A memory-model check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def checked_int(value: object) -> int:
    """Accept a non-negative signed 64-bit integer. Booleans fail closed."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise MemoryModelError("integer")
    if value < 0 or value > _DOMAIN_MAX:
        raise MemoryModelError("integer")
    return value


def add_bytes(left: int, right: int) -> int:
    """Add two byte counts or raise on signed overflow."""
    total = checked_int(left) + checked_int(right)
    if total > _DOMAIN_MAX:
        raise MemoryModelError("overflow")
    return total


def fp32_parameter_product(parameter_count: int, bytes_per_parameter: int) -> int:
    """Multiply a parameter count by a byte width. The product is logical."""
    count = checked_int(parameter_count)
    width = checked_int(bytes_per_parameter)
    if width != 0 and count > _DOMAIN_MAX // width:
        raise MemoryModelError("overflow")
    return count * width


def reject_unit(unit: object) -> None:
    """Resident arithmetic accepts bytes only. Decimal and binary labels are not bytes."""
    if not isinstance(unit, str) or unit in _REJECTED_UNITS or unit != "bytes":
        raise MemoryModelError("unit")


def classify_peak(
    rows: Sequence[Mapping[str, Any]],
    *,
    ceiling: int = MEMORY_CAP,
) -> dict[str, Any]:
    """Classify a resident peak. A missing required upper bound is unresolved."""
    checked_int(ceiling)
    ids = [row["categoryId"] for row in rows]
    if len(ids) != len(set(ids)) or tuple(ids) != CATEGORY_IDS:
        raise MemoryModelError("category-set")
    payload = [row["categoryId"] for row in rows if row["countsParameterPayload"] is True]
    if payload != ["static_parameter_memory"]:
        raise MemoryModelError("double-count")
    unresolved: list[str] = []
    total = 0
    lower = 0
    lower_complete = True
    for row in rows:
        reject_unit(row["unit"])
        if row["memoryDomain"] not in RESIDENT_DOMAINS:
            raise MemoryModelError("domain")
        if row["includedInTotal"] is not True:
            raise MemoryModelError("required-exclusion")
        if row["memoryDomain"] != "resident":
            raise MemoryModelError("domain")
        status = row["evidenceStatus"]
        if status not in EVIDENCE_STATUSES:
            raise MemoryModelError("evidence-status")
        upper = row["upperBoundBytes"]
        lower_bound = row["lowerBoundBytes"]
        if status == "unresolved":
            if upper is not None or lower_bound is not None:
                raise MemoryModelError("zero-fill" if upper == 0 else "unresolved-bound")
            unresolved.append(str(row["categoryId"]))
            lower_complete = False
            continue
        upper_bytes = checked_int(upper)
        if lower_bound is None:
            lower_complete = False
        else:
            lower = add_bytes(lower, checked_int(lower_bound))
        total = add_bytes(total, upper_bytes)
    if unresolved:
        return {
            "classification": "unresolved",
            "lowerBoundBytes": None,
            "upperBoundBytes": None,
            "ceilingBytes": ceiling,
            "ceilingComparison": "unresolved",
            "bytesRelativeToCeiling": None,
            "unresolvedCategoryIds": unresolved,
            "partialLowerBoundComplete": lower_complete,
        }
    comparison = "pass" if total <= ceiling else "fail"
    classification = "proven-pass" if comparison == "pass" else "proven-fail"
    return {
        "classification": classification,
        "lowerBoundBytes": lower if lower_complete else None,
        "upperBoundBytes": total,
        "ceilingBytes": ceiling,
        "ceilingComparison": comparison,
        "bytesRelativeToCeiling": total - ceiling,
        "unresolvedCategoryIds": [],
        "partialLowerBoundComplete": lower_complete,
    }


def decide_memory_model() -> dict[str, Any]:
    """Build the closed category contract. It does not assert a resident total."""
    product = fp32_parameter_product(PARAMETER_COUNT, BYTES_PER_FP32)
    if product != LOGICAL_PARAMETER_BYTES:
        raise MemoryModelError("parameter-product")
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
        "precision": "fp32",
        "batchSize": 1,
        "processCount": 1,
        "executionProvider": "cpu",
        "quantizationApproved": False,
        "speculativeExecution": False,
        "automaticBatching": False,
        "ceilingBytes": MEMORY_CAP,
        "gibibyteBytes": GIBIBYTE,
        "decimalGigabyteRejected": True,
        "roundingRule": "integer-exact",
        "overflowDomain": "signed-int64",
        "envelopeContextTokens": list(CONTEXTS),
        "parameterRepresentation": {
            "parameterCount": PARAMETER_COUNT,
            "bytesPerParameter": BYTES_PER_FP32,
            "logicalProductBytes": product,
            "logicalProductIncludedInPeak": False,
            "weightTyingStated": False,
        },
        "categories": [_contract_row(category_id) for category_id in CATEGORY_IDS],
    }
    return validate_memory_model(document)


def validate_memory_model(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the category contract and the disabled execution flags."""
    validate("candidate-memory-model", document)
    if contains_private_marker(document):
        raise MemoryModelError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise MemoryModelError("local-digest")
    if document["ceilingBytes"] != MEMORY_CAP or document["gibibyteBytes"] != GIBIBYTE:
        raise MemoryModelError("ceiling")
    if DECIMAL_GIGABYTE == GIBIBYTE:
        raise MemoryModelError("unit")
    product = document["parameterRepresentation"]
    expected = fp32_parameter_product(PARAMETER_COUNT, BYTES_PER_FP32)
    included = product["logicalProductIncludedInPeak"] is not False
    if product["logicalProductBytes"] != expected or included:
        raise MemoryModelError("parameter-product")
    if product["weightTyingStated"] is not False:
        raise MemoryModelError("weight-tying")
    rows = document["categories"]
    if [row["categoryId"] for row in rows] != list(CATEGORY_IDS):
        raise MemoryModelError("category-set")
    payload = [row["categoryId"] for row in rows if row["countsParameterPayload"] is True]
    if payload != ["static_parameter_memory"]:
        raise MemoryModelError("double-count")
    for row in rows:
        reject_unit(row["unit"])
        if row["includedInTotal"] is not True or row["requiredForEnvelope"] is not True:
            raise MemoryModelError("required-exclusion")
        if row["residentDomain"] != "resident":
            raise MemoryModelError("domain")
        if row["envelopeContextTokens"] != list(CONTEXTS):
            raise MemoryModelError("context")
    return document


def load_memory_model(root: Path | None = None) -> dict[str, Any]:
    """Load the committed model and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MemoryModelError("record-type")
    document = validate_memory_model(loaded)
    if document != decide_memory_model():
        raise MemoryModelError("record-drift")
    return document


def _contract_row(category_id: str) -> dict[str, Any]:
    meaning, formula, context_dependent = _CATEGORY_TEXT[category_id]
    return {
        "categoryId": category_id,
        "meaning": meaning,
        "unit": "bytes",
        "residentDomain": "resident",
        "includedInTotal": True,
        "requiredForEnvelope": True,
        "countsParameterPayload": category_id == "static_parameter_memory",
        "contextDependent": context_dependent,
        "formula": formula,
        "unresolvedBehavior": "null-upper-bound",
        "envelopeContextTokens": list(CONTEXTS),
    }


_CATEGORY_TEXT: dict[str, tuple[str, str, bool]] = {
    "static_parameter_memory": (
        "Logical FP32 parameter payload. It is not a resident session copy.",
        "parameter_count * bytes_per_fp32_parameter",
        False,
    ),
    "graph_and_initializer_overhead": (
        "Resident graph and initializer bytes beyond the counted parameter payload.",
        "resident_initializer_bytes_excluding_counted_parameter_payload",
        False,
    ),
    "runtime_process_baseline": (
        "Resident bytes for the runtime process, shared libraries, and CPU session.",
        "runtime_process_resident_bytes",
        False,
    ),
    "allocator_and_optimization_overhead": (
        "Resident arena, memory-pattern, graph-optimization, and thread-pool overhead.",
        "arena_pattern_optimizer_and_thread_pool_resident_bytes",
        False,
    ),
    "activation_memory": (
        "Resident activations for one batch and the envelope sequence length.",
        "batch_size * sequence_tokens * activation_bytes_per_token",
        True,
    ),
    "architecture_state_memory": (
        "Resident attention state plus convolution or recurrent state at the envelope length.",
        "attention_state_bytes + convolution_state_bytes",
        True,
    ),
    "input_output_tensor_memory": (
        "Resident input ids, masks, and logits for one batch and the envelope length.",
        "input_id_bytes + mask_bytes + logits_bytes",
        True,
    ),
    "tokenizer_and_configuration_memory": (
        "Resident tokenizer and configuration bytes, excluding logical file size.",
        "resident_tokenizer_bytes + resident_configuration_bytes",
        False,
    ),
    "hardened_execution_overhead": (
        "Resident launcher, IPC, and attestation bytes. Address-space limits are excluded.",
        "launcher_ipc_and_attestation_resident_bytes",
        False,
    ),
    "safety_margin": (
        "Explicit byte margin applied only after every required upper bound is known.",
        "explicit_margin_bytes_after_complete_upper_bounds",
        False,
    ),
}
