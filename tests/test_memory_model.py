"""Memory-model contract tests. Synthetic bounds do not alter the committed record."""

from __future__ import annotations

import json
from typing import Any

import pytest

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.memory_model import (
    BYTES_PER_FP32,
    CATEGORY_IDS,
    DECIMAL_GIGABYTE,
    GIBIBYTE,
    LOGICAL_PARAMETER_BYTES,
    PARAMETER_COUNT,
    MemoryModelError,
    add_bytes,
    checked_int,
    classify_peak,
    decide_memory_model,
    fp32_parameter_product,
    load_memory_model,
    validate_memory_model,
)


def _row(
    category_id: str,
    upper: int | None,
    *,
    status: str = "deterministic-calculation",
    unit: str = "bytes",
    domain: str = "resident",
    included: bool = True,
    payload: bool | None = None,
    lower: int | None = None,
) -> dict[str, Any]:
    return {
        "categoryId": category_id,
        "unit": unit,
        "memoryDomain": domain,
        "includedInTotal": included,
        "countsParameterPayload": category_id == "static_parameter_memory"
        if payload is None
        else payload,
        "evidenceStatus": status,
        "lowerBoundBytes": upper if lower is None and upper is not None else lower,
        "upperBoundBytes": upper,
    }


def _complete(total: int) -> list[dict[str, Any]]:
    base, remainder = divmod(total, len(CATEGORY_IDS))
    rows = []
    for index, category_id in enumerate(CATEGORY_IDS):
        share = base + (remainder if index == len(CATEGORY_IDS) - 1 else 0)
        rows.append(_row(category_id, share))
    return rows


def test_committed_model_is_closed_and_logical_product_is_excluded() -> None:
    document = load_memory_model()
    assert document["ceilingBytes"] == MEMORY_CAP == 12_884_901_888
    assert document["gibibyteBytes"] == GIBIBYTE
    assert 12 * DECIMAL_GIGABYTE != MEMORY_CAP
    assert 12 * GIBIBYTE == MEMORY_CAP
    product = document["parameterRepresentation"]
    assert product["logicalProductBytes"] == LOGICAL_PARAMETER_BYTES
    assert product["logicalProductIncludedInPeak"] is False
    assert product["weightTyingStated"] is False
    assert fp32_parameter_product(PARAMETER_COUNT, BYTES_PER_FP32) == LOGICAL_PARAMETER_BYTES
    assert [row["categoryId"] for row in document["categories"]] == list(CATEGORY_IDS)
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["acquisitionStatus"] == "not-acquired"
    assert document == decide_memory_model()


def test_missing_duplicate_and_double_count_fail() -> None:
    rows = _complete(1024)
    with pytest.raises(MemoryModelError) as missing:
        classify_peak(rows[:-1])
    assert missing.value.code == "category-set"
    duplicated = [dict(rows[0]), *rows]
    with pytest.raises(MemoryModelError) as duplicate:
        classify_peak(duplicated)
    assert duplicate.value.code == "category-set"
    doubled = _complete(1024)
    doubled[1]["countsParameterPayload"] = True
    with pytest.raises(MemoryModelError) as counted:
        classify_peak(doubled)
    assert counted.value.code == "double-count"
    dropped = _complete(1024)
    dropped[0]["countsParameterPayload"] = False
    with pytest.raises(MemoryModelError) as owner:
        classify_peak(dropped)
    assert owner.value.code == "double-count"


def test_unit_domain_exclusion_and_integer_failures() -> None:
    decimal = _complete(1024)
    decimal[0]["unit"] = "GB"
    with pytest.raises(MemoryModelError) as unit:
        classify_peak(decimal)
    assert unit.value.code == "unit"
    virtual = _complete(1024)
    virtual[2]["memoryDomain"] = "virtual-address"
    with pytest.raises(MemoryModelError) as domain:
        classify_peak(virtual)
    assert domain.value.code == "domain"
    excluded = _complete(1024)
    excluded[-1]["includedInTotal"] = False
    with pytest.raises(MemoryModelError) as required:
        classify_peak(excluded)
    assert required.value.code == "required-exclusion"
    with pytest.raises(MemoryModelError) as boolean:
        checked_int(True)
    assert boolean.value.code == "integer"
    with pytest.raises(MemoryModelError) as overflow:
        add_bytes(2**62, 2**62)
    assert overflow.value.code == "overflow"
    wide = _complete(1024)
    wide[0]["upperBoundBytes"] = 2**62
    wide[0]["lowerBoundBytes"] = 2**62
    wide[1]["upperBoundBytes"] = 2**62
    wide[1]["lowerBoundBytes"] = 2**62
    with pytest.raises(MemoryModelError) as summed:
        classify_peak(wide)
    assert summed.value.code == "overflow"


def test_ceiling_and_unknown_upper_bound() -> None:
    exact = classify_peak(_complete(MEMORY_CAP))
    assert exact["classification"] == "proven-pass"
    assert exact["upperBoundBytes"] == MEMORY_CAP
    assert exact["ceilingComparison"] == "pass"
    over = classify_peak(_complete(MEMORY_CAP + 1))
    assert over["classification"] == "proven-fail"
    assert over["bytesRelativeToCeiling"] == 1
    unknown = _complete(MEMORY_CAP + 100)
    unknown[-1] = _row(
        "safety_margin",
        None,
        status="unresolved",
        lower=None,
    )
    unresolved = classify_peak(unknown)
    assert unresolved["classification"] == "unresolved"
    assert unresolved["upperBoundBytes"] is None
    assert unresolved["ceilingComparison"] == "unresolved"
    filled = _complete(1024)
    filled[-1]["evidenceStatus"] = "unresolved"
    filled[-1]["upperBoundBytes"] = 0
    filled[-1]["lowerBoundBytes"] = 0
    with pytest.raises(MemoryModelError) as zero_fill:
        classify_peak(filled)
    assert zero_fill.value.code == "zero-fill"


def test_contract_rejects_a_drifted_category_set() -> None:
    document = json.loads(json.dumps(decide_memory_model()))
    document["categories"][0]["countsParameterPayload"] = False
    document["categories"][1]["countsParameterPayload"] = True
    with pytest.raises(MemoryModelError) as drifted:
        validate_memory_model(document)
    assert drifted.value.code == "double-count"
