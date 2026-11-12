"""Official memory evidence. Generic edge figures are not resident bounds."""

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
from patchpilot_intelligence_evals.memory_model import (
    CATEGORY_IDS,
    LOGICAL_PARAMETER_BYTES,
    PARAMETER_COUNT,
    RETRIEVED_ON,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/candidate-memory-evidence.json")
_CARD = f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/{LFM_SOURCE_REVISION}/README.md"
_ONNX = (
    f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/{LFM_ONNX_REVISION}/README.md"
)
_SESSION = (
    "https://raw.githubusercontent.com/microsoft/onnxruntime/v1.31.1/"
    "onnxruntime/core/framework/session_options.h"
)
_RUNTIME_REVISION = "6af1a932e2286d5c58166085d24c68783033edee"


class MemoryEvidenceError(ValueError):
    """A memory-evidence record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_memory_evidence() -> dict[str, Any]:
    """Build the evidence catalog and the unresolved resident disposition of each category."""
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
        "graphParsed": False,
        "evidence": _catalog(),
        "categories": [_category(category_id) for category_id in CATEGORY_IDS],
    }
    return validate_memory_evidence(document)


def validate_memory_evidence(document: dict[str, Any]) -> dict[str, Any]:
    """Validate authority, units, and the prohibition on inapplicable byte bounds."""
    validate("candidate-memory-evidence", document)
    if contains_private_marker(document):
        raise MemoryEvidenceError("identity")
    if document["locallyObservedArtifactDigests"] != [] or document["graphParsed"] is not False:
        raise MemoryEvidenceError("acquisition")
    catalog = {item["evidenceId"]: item for item in document["evidence"]}
    if len(catalog) != len(document["evidence"]):
        raise MemoryEvidenceError("evidence")
    if [row["categoryId"] for row in document["categories"]] != list(CATEGORY_IDS):
        raise MemoryEvidenceError("category-set")
    for row in document["categories"]:
        if row["unit"] != "bytes":
            raise MemoryEvidenceError("unit")
        if row["upperBoundBytes"] is not None:
            for evidence_id in row["evidenceIds"]:
                item = catalog.get(evidence_id)
                if item is None:
                    raise MemoryEvidenceError("evidence")
                if item["units"] == "decimal-gigabytes":
                    raise MemoryEvidenceError("inapplicable-bound")
        if row["evidenceStatus"] == "unresolved" and (
            row["upperBoundBytes"] is not None or row["lowerBoundBytes"] is not None
        ):
            raise MemoryEvidenceError("unresolved-bound")
        if row["logicalBytesIncludedInPeak"] is not False:
            raise MemoryEvidenceError("double-count")
        if row["categoryId"] == "static_parameter_memory":
            if row["logicalBytes"] != LOGICAL_PARAMETER_BYTES:
                raise MemoryEvidenceError("parameter-product")
        elif row["logicalBytes"] is not None:
            raise MemoryEvidenceError("storage-as-resident")
        for evidence_id in row["evidenceIds"]:
            if evidence_id not in catalog:
                raise MemoryEvidenceError("evidence")
    memory = catalog["lfm-card-memory"]
    restrictive = memory["conflictDisposition"] != "restrictive-reading"
    if restrictive or memory["byteBoundPermitted"] is not False:
        raise MemoryEvidenceError("conflict")
    return document


def load_memory_evidence(root: Path | None = None) -> dict[str, Any]:
    """Load the committed evidence and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MemoryEvidenceError("record-type")
    document = validate_memory_evidence(loaded)
    if document != decide_memory_evidence():
        raise MemoryEvidenceError("record-drift")
    return document


def _source(
    evidence_id: str,
    source_name: str,
    url: str,
    publisher: str,
    revision: str | None,
    documentation_version: str | None,
    claim: str,
    evidence_class: str,
    applicability: str,
    value_type: str,
    units: str,
    disposition: str,
    *,
    byte_bound_permitted: bool = False,
) -> dict[str, Any]:
    return {
        "evidenceId": evidence_id,
        "sourceName": source_name,
        "url": url,
        "publisher": publisher,
        "retrievedOn": RETRIEVED_ON,
        "immutableRevision": revision,
        "documentationVersion": documentation_version,
        "claim": claim,
        "evidenceClass": evidence_class,
        "applicability": applicability,
        "valueType": value_type,
        "units": units,
        "conflictDisposition": disposition,
        "byteBoundPermitted": byte_bound_permitted,
    }


def _catalog() -> list[dict[str, Any]]:
    return [
        _source(
            "lfm-card-shape",
            "LFM2.5-1.2B-Instruct model card",
            _CARD,
            "Liquid AI",
            LFM_SOURCE_REVISION,
            None,
            (
                "The pinned card states a 1.17B parameter count, 16 layers with 10 "
                "double-gated convolution blocks and 6 GQA blocks, a 32768-token context, "
                "and a 65536-token vocabulary. Hidden size, head count, and weight tying "
                "are not stated."
            ),
            "authoritative",
            "Pinned source card for LiquidAI/LFM2.5-1.2B-Instruct",
            "not-provided",
            "not-applicable",
            "none",
        ),
        _source(
            "lfm-card-use",
            "LFM2.5-1.2B-Instruct model card",
            _CARD,
            "Liquid AI",
            LFM_SOURCE_REVISION,
            None,
            (
                "The pinned card describes an instruction-tuned model with English among "
                "its languages, recommends agentic tasks, data extraction, and RAG, and "
                "says knowledge-intensive tasks and programming are not recommended. JSON "
                "tool definitions and optional JSON function calls are shown."
            ),
            "authoritative",
            "Pinned source card suitability statements",
            "not-provided",
            "not-applicable",
            "restrictive-reading",
        ),
        _source(
            "lfm-card-memory",
            "LFM2.5-1.2B-Instruct model card",
            _CARD,
            "Liquid AI",
            LFM_SOURCE_REVISION,
            None,
            (
                "The pinned card says the model runs under 1GB of memory and lists 0.9GB "
                "for NPU NexaML rows and 719MB for a llama.cpp Q4_0 CPU row. Those figures "
                "are not an FP32 ONNX CPU resident peak."
            ),
            "conflicting",
            "NPU NexaML and llama.cpp Q4_0 rows only",
            "published-measurement",
            "decimal-gigabytes",
            "restrictive-reading",
        ),
        _source(
            "lfm-onnx-fp32",
            "LFM2.5-1.2B-Instruct-ONNX model card",
            _ONNX,
            "Liquid AI",
            LFM_ONNX_REVISION,
            None,
            (
                "The pinned ONNX card labels model.onnx as the FP32 graph and the "
                "model.onnx_data files as FP32 weights. Q4, FP16, and Q8 size rows are "
                "separate, and no FP32 resident peak is stated."
            ),
            "authoritative",
            "Pinned FP32 ONNX files, not Q4 FP16 or Q8 rows",
            "not-provided",
            "bytes",
            "restrictive-reading",
        ),
        _source(
            "lfm-onnx-state",
            "LFM2.5-1.2B-Instruct-ONNX model card",
            _ONNX,
            "Liquid AI",
            LFM_ONNX_REVISION,
            None,
            (
                "The pinned ONNX quickstart names past_key_values and past_conv cache "
                "tensors for the caller to supply. It does not state shapes, dtypes, or "
                "byte sizes at 4096 or 8192 tokens."
            ),
            "authoritative",
            "Pinned ONNX interface, without parsing the graph",
            "not-provided",
            "bytes",
            "none",
        ),
        _source(
            "lfm-docs-overview",
            "Liquid AI LFM2.5-1.2B-Instruct page",
            "https://docs.liquid.ai/lfm/models/lfm25-1.2b-instruct",
            "Liquid AI",
            None,
            "retrieved-2026-11-12",
            (
                "The Liquid AI model page states an instruction-tuned dense LFM2.5 model "
                "with a 32K context and native tool calling. It does not state FP32 ONNX "
                "resident memory or hidden dimensions."
            ),
            "authoritative",
            "Official model page, not a hidden-size or memory bound",
            "not-provided",
            "tokens",
            "none",
        ),
        _source(
            "ort-session-defaults",
            "ONNX Runtime v1.31.1 SessionOptions header",
            _SESSION,
            "Microsoft",
            _RUNTIME_REVISION,
            "v1.31.1",
            (
                "The v1.31.1 session header defaults enable_mem_pattern, enable_mem_reuse, "
                "and enable_cpu_mem_arena to true, and graph_optimization_level to MaxLevel. "
                "The arena may preallocate. No byte bound for this model is stated."
            ),
            "authoritative",
            "onnxruntime v1.31.1 CPU session defaults, not this graph",
            "not-provided",
            "bytes",
            "none",
        ),
        _source(
            "ort-memory-page",
            "ONNX Runtime memory consumption page",
            "https://onnxruntime.ai/docs/performance/tune-performance/memory.html",
            "Microsoft",
            None,
            "retrieved-2026-11-12",
            (
                "The ONNX Runtime memory page describes a shared arena and optional "
                "mimalloc. It states no Linux resident byte bound for this FP32 model. "
                "Linux mimalloc is not given a special provision there."
            ),
            "authoritative",
            "General ONNX Runtime allocator guidance",
            "not-provided",
            "bytes",
            "none",
        ),
        _source(
            "ort-graph-opt",
            "ONNX Runtime graph optimizations page",
            "https://onnxruntime.ai/docs/performance/model-optimizations/graph-optimizations.html",
            "Microsoft",
            None,
            "retrieved-2026-11-12",
            (
                "The graph optimization page says all optimization levels are enabled by "
                "default and describes constant folding and fusions. It states no resident "
                "byte bound for this FP32 CPU session."
            ),
            "authoritative",
            "General ONNX Runtime graph optimizations",
            "not-provided",
            "bytes",
            "none",
        ),
        _source(
            "onnx-external-data",
            "ONNX external data specification",
            "https://onnx.ai/onnx/repo-docs/ExternalData.html",
            "ONNX",
            None,
            "1.24.0",
            (
                "The ONNX external-data page says large initializer bytes may live in a "
                "separate file and that offsets should be page aligned to enable mmap. It "
                "does not require a runtime to map those bytes or state a resident size."
            ),
            "authoritative",
            "ONNX external-data layout, not ONNX Runtime resident use",
            "not-provided",
            "bytes",
            "restrictive-reading",
        ),
        _source(
            "fp32-logical-product",
            "Logical FP32 parameter product",
            _CARD,
            "Liquid AI",
            LFM_SOURCE_REVISION,
            None,
            (
                "Multiplying the committed parameter count 1170340608 by 4 gives "
                "4681362432 logical FP32 bytes. Weight tying is not stated, so this "
                "product is not a resident upper bound."
            ),
            "authoritative",
            "Logical FP32 width for the committed parameter count",
            "calculated",
            "bytes",
            "restrictive-reading",
        ),
        _source(
            "margin-not-applied",
            "Safety margin absence",
            "https://onnxruntime.ai/docs/performance/tune-performance/memory.html",
            "Microsoft",
            None,
            "retrieved-2026-11-12",
            (
                "No official page states a safety-margin percentage or byte allowance for "
                "this FP32 CPU session. The margin stays unset while any required upper "
                "bound is unknown."
            ),
            "unresolved",
            "No applicable safety-margin bound for this FP32 session",
            "not-provided",
            "bytes",
            "unresolved",
        ),
    ]


def _category(category_id: str) -> dict[str, Any]:
    evidence_ids, uncertainty = _CATEGORY_EVIDENCE[category_id]
    logical = LOGICAL_PARAMETER_BYTES if category_id == "static_parameter_memory" else None
    return {
        "categoryId": category_id,
        "evidenceStatus": "unresolved",
        "valueType": "not-provided",
        "unit": "bytes",
        "lowerBoundBytes": None,
        "upperBoundBytes": None,
        "logicalBytes": logical,
        "logicalBytesIncludedInPeak": False,
        "evidenceIds": evidence_ids,
        "uncertainty": uncertainty,
    }


_CATEGORY_EVIDENCE: dict[str, tuple[list[str], str]] = {
    "static_parameter_memory": (
        ["lfm-card-shape", "lfm-onnx-fp32", "fp32-logical-product"],
        (
            f"Weight tying is not stated. The logical product of {PARAMETER_COUNT} "
            "parameters at 4 bytes is not a resident upper bound."
        ),
    ),
    "graph_and_initializer_overhead": (
        ["lfm-onnx-fp32", "onnx-external-data", "ort-session-defaults"],
        "External-data layout and optional mmap do not establish resident initializer bytes.",
    ),
    "runtime_process_baseline": (
        ["ort-session-defaults", "ort-memory-page"],
        "No publisher states resident bytes for the CPU process, libraries, or session.",
    ),
    "allocator_and_optimization_overhead": (
        ["ort-session-defaults", "ort-graph-opt", "ort-memory-page"],
        "Default arena, memory pattern, and MaxLevel optimizations have no byte bound here.",
    ),
    "activation_memory": (
        ["lfm-card-shape"],
        "Hidden size and activation width are not stated, so the sequence formula has no bytes.",
    ),
    "architecture_state_memory": (
        ["lfm-card-shape", "lfm-onnx-state"],
        "Attention and convolution state are named, but their byte sizes are not stated.",
    ),
    "input_output_tensor_memory": (
        ["lfm-card-shape", "lfm-onnx-state"],
        "Vocabulary size is stated, but FP32 logits shape and dtype are not stated.",
    ),
    "tokenizer_and_configuration_memory": (
        ["lfm-card-shape"],
        "Logical tokenizer and configuration file sizes are storage, not resident bytes.",
    ),
    "hardened_execution_overhead": (
        ["ort-memory-page"],
        "Launcher, IPC, and attestation resident bytes are unpublished. Address space is excluded.",
    ),
    "safety_margin": (
        ["margin-not-applied"],
        "The margin stays unset while any required upper bound is unknown.",
    ),
}
