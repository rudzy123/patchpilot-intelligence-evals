"""Storage-budget arithmetic. No multi-gigabyte fixture is created."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP
from patchpilot_intelligence_evals.finalist_budget import load_finalist_budget
from patchpilot_intelligence_evals.storage_budget import (
    StorageBudgetError,
    budget_size,
    ceiling_outcome,
    checked_add,
    checked_int,
    file_sizes,
    load_storage_policy,
    model_outcome,
    peak_bytes,
)

_DOMAIN_MAX = 2**63 - 1


def test_exact_ceiling_passes_and_one_byte_over_fails() -> None:
    assert ceiling_outcome(ARTIFACT_CAP) == "pass"
    assert ceiling_outcome(ARTIFACT_CAP + 1) == "fail"
    assert peak_bytes(copies=1, logical=ARTIFACT_CAP, overhead=0, runtime=0) == ARTIFACT_CAP
    assert (
        ceiling_outcome(peak_bytes(copies=1, logical=ARTIFACT_CAP, overhead=1, runtime=0)) == "fail"
    )


def test_integer_overflow_is_rejected() -> None:
    with pytest.raises(StorageBudgetError) as caught:
        checked_add(_DOMAIN_MAX, 1)
    assert caught.value.code == "integer-overflow"
    for value in (True, False, -1, _DOMAIN_MAX + 1, 1.5, "8"):
        with pytest.raises(StorageBudgetError) as caught:
            checked_int(value)
        assert caught.value.code == "integer-overflow"


def test_unknown_and_transient_acquisition_stay_unresolved() -> None:
    assert (
        model_outcome(
            "copy",
            logical=None,
            overhead=1,
            runtime=1,
            contract_implemented=True,
        )
        == "unresolved"
    )
    assert (
        model_outcome(
            "atomic",
            logical=1,
            overhead=1,
            runtime=1,
            contract_implemented=True,
            transient_supplied=True,
        )
        == "unresolved"
    )


def test_sparse_logical_size_is_the_budget_input(tmp_path: Path) -> None:
    path = tmp_path / "hole"
    descriptor = os.open(path, os.O_CREAT | os.O_WRONLY, 0o644)
    os.truncate(descriptor, 1_048_576)
    os.close(descriptor)
    measured = file_sizes(path)
    assert measured["logicalBytes"] == 1_048_576
    assert (
        budget_size(logical=measured["logicalBytes"], allocated=measured["allocatedBytes"])
        == (measured["logicalBytes"])
    )
    assert ceiling_outcome(budget_size(logical=ARTIFACT_CAP + 1, allocated=0)) == "fail"


def test_finalist_models_keep_the_ceiling_and_track7_record() -> None:
    policy = load_storage_policy()
    assert policy["artifactCapBytes"] == ARTIFACT_CAP
    assert policy["copyPromotionPeakBytes"] == 9447820409
    assert policy["atomicPromotionPeakBytes"] == 4730231432
    assert policy["copyPromotionStorageOutcome"] == "fail"
    assert policy["atomicPromotionStorageOutcome"] == "pass"
    assert policy["crossFilesystemStorageOutcome"] == "ineligible"
    assert policy["copyFallback"] == "prohibited"
    assert policy["hashBufferDiskBytes"] == 0
    assert policy["transientAcquisitionOverheadBytes"] is None
    assert policy["selectionOutcome"] == "no-selection"
    assert policy["authorizationOutcome"] == "not-authorized"
    assert policy["weightedScore"] is None
    assert policy["qualifyingCandidateCount"] == 0
    assert policy["peakMemoryBasis"] == "unknown-fp32"
    assert policy["explanationSuitability"] == "unresolved"
    assert policy["productionReady"] is False
    assert policy["acquisitionStatus"] == "not-acquired"
    assert policy["executionStatus"] == "not-executed"
    finalist = load_finalist_budget()["finalists"][0]
    assert finalist["inventoryBytes"] == 4717588977
    assert finalist["footprintBytes"] == 9446591609
    assert finalist["artifactFit"] == "fail"
    assert (
        model_outcome(
            "cross-filesystem",
            logical=1,
            overhead=0,
            runtime=0,
            contract_implemented=True,
        )
        == "ineligible"
    )
