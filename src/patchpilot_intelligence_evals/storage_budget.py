"""Track 7A storage reservations. The 8 GiB ceiling stays the peak logical-byte cap.

Allocated blocks, sparse allocation, and compressed transport size do not reduce a
reservation. Transient acquisition bytes are not authorized and do not become zero.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP, MEMORY_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    contains_private_marker,
)
from patchpilot_intelligence_evals.candidate_eligibility import RETRIEVED_ON
from patchpilot_intelligence_evals.finalist_budget import (
    RUNTIME_LISTED_BYTES,
    decide_finalist_budget,
)
from patchpilot_intelligence_evals.finalist_onnx import SELECTED_FILES, component_bytes
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/artifact-storage-policy.json")
_DOMAIN_MAX = 2**63 - 1
_SELECTED_FILE_COUNT = 11
_JOURNAL_RESERVE = 65536
_MANIFEST_RESERVE = 1048576
_RECEIPT_RESERVE = 65536
_DIRECTORY_ENTRY_RESERVE = 4096
_DIRECTORY_RESERVE = _DIRECTORY_ENTRY_RESERVE * (_SELECTED_FILE_COUNT + 1)
_VERIFICATION_OVERHEAD = (
    _JOURNAL_RESERVE + _MANIFEST_RESERVE + _RECEIPT_RESERVE + _DIRECTORY_RESERVE
)
_LEGACY_FOOTPRINT = 9446591609
_COPY_PEAK = 9447820409
_ATOMIC_PEAK = 4730231432
_COPY_OVER = 857885817
_ATOMIC_UNDER = 3859703160
_STATES = (
    "quarantine-open",
    "quarantine-closed",
    "verifying",
    "sealed",
    "promoting",
    "verified",
    "rejected",
    "indeterminate",
)
ATOMIC_CONTRACT_REQUIREMENTS: tuple[str, ...] = (
    "same-filesystem-device",
    "rename-noreplace",
    "no-copy-fallback",
    "sealed-before-promotion",
    "destination-absent",
    "file-data-sync",
    "manifest-sync",
    "quarantine-directory-sync",
    "verified-parent-sync",
    "fail-closed-on-sync",
    "cross-device-rejection",
)
_COPY_FORMULA = "quarantine + verified + verification-working-overhead + runtime-staging"
_ATOMIC_FORMULA = "one-artifact-set + verification-working-overhead + runtime-staging"


class StorageBudgetError(ValueError):
    """A storage reservation failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def checked_int(value: object) -> int:
    """Accept a non-negative signed 64-bit integer. Booleans fail closed."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise StorageBudgetError("integer-overflow")
    if value < 0 or value > _DOMAIN_MAX:
        raise StorageBudgetError("integer-overflow")
    return value


def checked_add(left: int, right: int) -> int:
    """Add two in-domain sizes. A sum outside the domain fails closed."""
    left_i = checked_int(left)
    right_i = checked_int(right)
    if left_i > _DOMAIN_MAX - right_i:
        raise StorageBudgetError("integer-overflow")
    return left_i + right_i


def budget_size(*, logical: int, allocated: int) -> int:
    """Return the logical size. Allocated blocks are checked and then ignored."""
    logical_i = checked_int(logical)
    checked_int(allocated)
    return logical_i


def file_sizes(path: Path) -> dict[str, int]:
    """Read logical size and allocated bytes without following a link."""
    info = os.lstat(path)
    return {
        "logicalBytes": checked_int(info.st_size),
        "allocatedBytes": checked_int(info.st_blocks * 512),
    }


def ceiling_outcome(peak: int) -> str:
    """Equality with the artifact ceiling passes. One byte over fails."""
    peak_i = checked_int(peak)
    if peak_i <= ARTIFACT_CAP:
        return "pass"
    return "fail"


def peak_bytes(*, copies: int, logical: int, overhead: int, runtime: int) -> int:
    """Sum complete logical copies, verification overhead, and runtime staging."""
    copy_count = checked_int(copies)
    if copy_count not in (1, 2):
        raise StorageBudgetError("integer-overflow")
    total = checked_int(logical)
    for _ in range(copy_count - 1):
        total = checked_add(total, logical)
    total = checked_add(total, overhead)
    return checked_add(total, runtime)


def model_outcome(
    model: str,
    *,
    logical: int | None,
    overhead: int | None,
    runtime: int | None,
    contract_implemented: bool,
    transient_supplied: bool = False,
) -> str:
    """Classify one promotion model. Unknown inputs and acquisition bytes stay unresolved."""
    if model == "cross-filesystem":
        return "ineligible"
    if model not in {"copy", "atomic"}:
        raise StorageBudgetError("unknown-model")
    if transient_supplied:
        return "unresolved"
    if logical is None or overhead is None or runtime is None:
        return "unresolved"
    if model == "atomic" and not contract_implemented:
        return "unresolved"
    copies = 2 if model == "copy" else 1
    peak = peak_bytes(copies=copies, logical=logical, overhead=overhead, runtime=runtime)
    return ceiling_outcome(peak)


def verification_overhead_bytes(file_count: int) -> int:
    """Journal, manifest, receipt, and directory reservations for one attempt."""
    count = checked_int(file_count)
    directory = checked_int(_DIRECTORY_ENTRY_RESERVE * (count + 1))
    total = checked_add(_JOURNAL_RESERVE, _MANIFEST_RESERVE)
    total = checked_add(total, _RECEIPT_RESERVE)
    return checked_add(total, directory)


def contract_implemented() -> bool:
    """True when the atomic promoter covers every requirement and does not copy."""
    from patchpilot_intelligence_evals.atomic_promotion import covers_contract

    return covers_contract()


def decide_storage_policy() -> dict[str, Any]:
    """Build the committed storage policy from the Track 7 finalist inventory."""
    logical = _require_inventory()
    overhead = verification_overhead_bytes(_SELECTED_FILE_COUNT)
    if overhead != _VERIFICATION_OVERHEAD:
        raise StorageBudgetError("arithmetic")
    legacy = checked_add(checked_add(logical, logical), RUNTIME_LISTED_BYTES)
    copy_peak = peak_bytes(
        copies=2, logical=logical, overhead=overhead, runtime=RUNTIME_LISTED_BYTES
    )
    atomic_peak = peak_bytes(
        copies=1, logical=logical, overhead=overhead, runtime=RUNTIME_LISTED_BYTES
    )
    if legacy != _LEGACY_FOOTPRINT or copy_peak != _COPY_PEAK or atomic_peak != _ATOMIC_PEAK:
        raise StorageBudgetError("arithmetic")
    if copy_peak - ARTIFACT_CAP != _COPY_OVER or ARTIFACT_CAP - atomic_peak != _ATOMIC_UNDER:
        raise StorageBudgetError("arithmetic")
    implemented = contract_implemented()
    if not implemented:
        raise StorageBudgetError("contract")
    from patchpilot_intelligence_evals.verification_seal import (
        APPROVED_EXACT_NAMES,
        APPROVED_SUFFIXES,
    )

    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "artifactCapBytes": ARTIFACT_CAP,
        "memoryCapBytes": MEMORY_CAP,
        "logicalInventoryBytes": logical,
        "legacyCopyFootprintBytes": legacy,
        "selectedFileCount": _SELECTED_FILE_COUNT,
        "journalReserveBytes": _JOURNAL_RESERVE,
        "manifestReserveBytes": _MANIFEST_RESERVE,
        "receiptReserveBytes": _RECEIPT_RESERVE,
        "directoryMetadataReserveBytes": _DIRECTORY_RESERVE,
        "verificationWorkingOverheadBytes": overhead,
        "hashBufferDiskBytes": 0,
        "hashBufferCountsTowardPeak": False,
        "runtimeStagingListedBytes": RUNTIME_LISTED_BYTES,
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "allocatedBytesGovernCeiling": False,
        "sparseAllocatedBytesGovernCeiling": False,
        "compressedTransportBytesGovernCeiling": False,
        "ceilingGovernsPeakReservation": True,
        "copyPromotionFormula": _COPY_FORMULA,
        "atomicPromotionFormula": _ATOMIC_FORMULA,
        "crossFilesystemFormula": "ineligible",
        "copyPromotionPeakBytes": copy_peak,
        "atomicPromotionPeakBytes": atomic_peak,
        "copyPromotionOverBytes": copy_peak - ARTIFACT_CAP,
        "atomicPromotionUnderBytes": ARTIFACT_CAP - atomic_peak,
        "copyPromotionStorageOutcome": model_outcome(
            "copy",
            logical=logical,
            overhead=overhead,
            runtime=RUNTIME_LISTED_BYTES,
            contract_implemented=True,
        ),
        "atomicPromotionStorageOutcome": model_outcome(
            "atomic",
            logical=logical,
            overhead=overhead,
            runtime=RUNTIME_LISTED_BYTES,
            contract_implemented=implemented,
        ),
        "crossFilesystemStorageOutcome": "ineligible",
        "copyFallback": "prohibited",
        "atomicContractStatus": "implemented",
        "atomicContractRequirements": list(ATOMIC_CONTRACT_REQUIREMENTS),
        "approvedSuffixes": list(APPROVED_SUFFIXES),
        "approvedExactNames": list(APPROVED_EXACT_NAMES),
        "states": list(_STATES),
        "sameFilesystemPersistence": "equality-only",
        "integerDomainMaximum": _DOMAIN_MAX,
        "locallyObservedArtifactDigests": [],
        "finalistModelId": LFM_MODEL_ID,
        "selectionOutcome": "no-selection",
        "authorizationOutcome": "not-authorized",
        "weightedScore": None,
        "qualifyingCandidateCount": 0,
        "peakMemoryBasis": "unknown-fp32",
        "explanationSuitability": "unresolved",
    }
    return validate_storage_policy(document)


def validate_storage_policy(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one storage policy and recompute its peaks."""
    validate("artifact-storage-policy", document)
    if contains_private_marker(document):
        raise StorageBudgetError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise StorageBudgetError("local-digest")
    if document["artifactCapBytes"] != ARTIFACT_CAP or document["memoryCapBytes"] != MEMORY_CAP:
        raise StorageBudgetError("cap")
    logical = _require_inventory()
    overhead = verification_overhead_bytes(document["selectedFileCount"])
    if document["logicalInventoryBytes"] != logical:
        raise StorageBudgetError("arithmetic")
    if document["verificationWorkingOverheadBytes"] != overhead:
        raise StorageBudgetError("arithmetic")
    if document["legacyCopyFootprintBytes"] != _LEGACY_FOOTPRINT:
        raise StorageBudgetError("arithmetic")
    if document["copyPromotionPeakBytes"] != _COPY_PEAK:
        raise StorageBudgetError("arithmetic")
    if document["atomicPromotionPeakBytes"] != _ATOMIC_PEAK:
        raise StorageBudgetError("arithmetic")
    if document["copyPromotionStorageOutcome"] != "fail":
        raise StorageBudgetError("outcome")
    if document["atomicPromotionStorageOutcome"] != "pass":
        raise StorageBudgetError("outcome")
    if document["crossFilesystemStorageOutcome"] != "ineligible":
        raise StorageBudgetError("outcome")
    if document["copyFallback"] != "prohibited":
        raise StorageBudgetError("copy-fallback")
    if tuple(document["atomicContractRequirements"]) != ATOMIC_CONTRACT_REQUIREMENTS:
        raise StorageBudgetError("contract")
    if document["atomicContractStatus"] != "implemented" or not contract_implemented():
        raise StorageBudgetError("contract")
    if document["selectionOutcome"] != "no-selection":
        raise StorageBudgetError("selection")
    if document["authorizationOutcome"] != "not-authorized":
        raise StorageBudgetError("authorization")
    if document["weightedScore"] is not None or document["qualifyingCandidateCount"] != 0:
        raise StorageBudgetError("selection")
    if document["peakMemoryBasis"] != "unknown-fp32":
        raise StorageBudgetError("memory")
    if document["explanationSuitability"] != "unresolved":
        raise StorageBudgetError("suitability")
    if document["transientAcquisitionOverheadBytes"] is not None:
        raise StorageBudgetError("acquisition")
    if document["hashBufferDiskBytes"] != 0:
        raise StorageBudgetError("arithmetic")
    return document


def load_storage_policy(root: Path | None = None) -> dict[str, Any]:
    """Load the committed policy and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise StorageBudgetError("record-type")
    document = validate_storage_policy(loaded)
    if document != decide_storage_policy():
        raise StorageBudgetError("policy-drift")
    return document


def _require_inventory() -> int:
    parts = component_bytes()
    logical = checked_int(parts["inventoryBytes"])
    selected = sum(1 for item in SELECTED_FILES if item.selected)
    if selected != _SELECTED_FILE_COUNT or logical != 4717588977:
        raise StorageBudgetError("inventory")
    finalist = decide_finalist_budget()["finalists"][0]
    if finalist["inventoryBytes"] != logical or finalist["footprintBytes"] != _LEGACY_FOOTPRINT:
        raise StorageBudgetError("inventory")
    if finalist["artifactFit"] != "fail" or finalist["peakMemoryBasis"] != "unknown-fp32":
        raise StorageBudgetError("inventory")
    return logical
