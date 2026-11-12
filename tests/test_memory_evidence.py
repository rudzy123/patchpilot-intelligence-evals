"""Memory-evidence authority tests."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
)
from patchpilot_intelligence_evals.memory_evidence import (
    MemoryEvidenceError,
    decide_memory_evidence,
    load_memory_evidence,
    validate_memory_evidence,
)
from patchpilot_intelligence_evals.memory_model import (
    CATEGORY_IDS,
    LOGICAL_PARAMETER_BYTES,
)


def test_catalog_covers_every_category_and_rejects_edge_memory() -> None:
    document = load_memory_evidence()
    assert document["sourceRevision"] == LFM_SOURCE_REVISION
    assert document["onnxRevision"] == LFM_ONNX_REVISION
    assert document["graphParsed"] is False
    assert document["realModelExecuted"] is False
    assert [row["categoryId"] for row in document["categories"]] == list(CATEGORY_IDS)
    memory = next(item for item in document["evidence"] if item["evidenceId"] == "lfm-card-memory")
    assert memory["evidenceClass"] == "conflicting"
    assert memory["units"] == "decimal-gigabytes"
    assert memory["byteBoundPermitted"] is False
    assert memory["conflictDisposition"] == "restrictive-reading"
    static = document["categories"][0]
    assert static["logicalBytes"] == LOGICAL_PARAMETER_BYTES
    assert static["upperBoundBytes"] is None
    assert static["evidenceStatus"] == "unresolved"
    assert all(row["upperBoundBytes"] is None for row in document["categories"])
    assert document == decide_memory_evidence()


def test_revision_unit_and_inapplicable_bound_fail() -> None:
    drifted = json.loads(json.dumps(decide_memory_evidence()))
    drifted["categories"][0]["upperBoundBytes"] = LOGICAL_PARAMETER_BYTES
    drifted["categories"][0]["evidenceIds"] = ["lfm-card-memory"]
    with pytest.raises(MemoryEvidenceError) as inapplicable:
        validate_memory_evidence(drifted)
    assert inapplicable.value.code == "inapplicable-bound"
    zeroed = json.loads(json.dumps(decide_memory_evidence()))
    zeroed["categories"][2]["upperBoundBytes"] = 0
    with pytest.raises(MemoryEvidenceError) as unresolved:
        validate_memory_evidence(zeroed)
    assert unresolved.value.code == "unresolved-bound"
    stored = json.loads(json.dumps(decide_memory_evidence()))
    stored["categories"][1]["logicalBytes"] = 4_714_127_360
    with pytest.raises(MemoryEvidenceError) as storage:
        validate_memory_evidence(stored)
    assert storage.value.code == "storage-as-resident"
