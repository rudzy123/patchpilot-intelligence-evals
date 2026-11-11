"""Artifact-budget arithmetic. Unknown required inputs fail closed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_eligibility import (
    MODEL_IDS,
    EligibilityError,
    reject_private_markers,
)
from patchpilot_intelligence_evals.direct_onnx_evidence import (
    nonquantized_pair_bytes,
    published_directory_bytes,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/candidate-artifact-budget.json")
_PROFILE = Path("candidates/authorization/evaluation-hardware-profile.json")
ARTIFACT_CAP = 8589934592
MEMORY_CAP = 12884901888
CONTEXT_CAP = 8192
_STORAGE = 1403456720896
_STORAGE_MULTIPLE = 2


class BudgetError(ValueError):
    """A budget record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def artifact_footprint(
    graph_bytes: int | None,
    external_data_bytes: list[int | None],
    tokenizer_configuration_bytes: int | None,
    verification_overhead_bytes: int | None,
    runtime_staging_allowance_bytes: int | None,
) -> int | None:
    """Sum one graph, every external file, tokenizer bytes, and both allowances."""
    parts: list[int | None] = [
        graph_bytes,
        tokenizer_configuration_bytes,
        verification_overhead_bytes,
        runtime_staging_allowance_bytes,
        *external_data_bytes,
    ]
    if any(part is None for part in parts):
        return None
    return sum(part for part in parts if part is not None)


def budget_fits(
    footprint_bytes: int | None,
    peak_memory_bytes: int | None,
    context_tokens: int | None,
    *,
    quantization_present: bool,
    artifact_cap: int = ARTIFACT_CAP,
    memory_cap: int = MEMORY_CAP,
    context_cap: int = CONTEXT_CAP,
) -> dict[str, str]:
    """Equality with either cap passes. One byte over, or any unknown, fails."""
    artifact = _fit(footprint_bytes is not None and footprint_bytes <= artifact_cap)
    memory = _fit(peak_memory_bytes is not None and peak_memory_bytes <= memory_cap)
    context = _fit(context_tokens is not None and context_tokens >= context_cap)
    storage = _fit(footprint_bytes is not None and footprint_bytes * _STORAGE_MULTIPLE <= _STORAGE)
    if quantization_present:
        artifact = "fail"
    hardware = _fit(artifact == "pass" and memory == "pass" and storage == "pass")
    return {
        "artifactFit": artifact,
        "memoryFit": memory,
        "contextFit": context,
        "storageHeadroom": storage,
        "hardwareFit": hardware,
    }


def decide_artifact_budget() -> dict[str, Any]:
    """Build the committed fail-closed budgets."""
    _require_profile_caps()
    families = [_family(item) for item in _INPUTS]
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": "2026-11-11",
        "artifactCapBytes": ARTIFACT_CAP,
        "memoryCapBytes": MEMORY_CAP,
        "contextCapTokens": CONTEXT_CAP,
        "availableStorageBytes": _STORAGE,
        "minimumFreeStorageMultiple": _STORAGE_MULTIPLE,
        "quantizationApproved": False,
        "locallyObservedArtifactDigests": [],
        "families": families,
    }
    return validate_artifact_budget(document)


def validate_artifact_budget(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one budget record."""
    validate("candidate-artifact-budget", document)
    try:
        reject_private_markers(document, EligibilityError)
    except EligibilityError as exc:
        raise BudgetError(exc.code) from exc
    if document["artifactCapBytes"] != ARTIFACT_CAP or document["memoryCapBytes"] != MEMORY_CAP:
        raise BudgetError("cap")
    families = document["families"]
    if [item["modelId"] for item in families] != list(MODEL_IDS):
        raise BudgetError("candidate-boundary")
    for item in families:
        footprint = artifact_footprint(
            item["graphBytes"],
            list(item["externalDataBytes"]),
            item["tokenizerConfigurationBytes"],
            item["verificationOverheadBytes"],
            item["runtimeStagingAllowanceBytes"],
        )
        if item["footprintBytes"] != footprint:
            raise BudgetError("footprint")
        fits = budget_fits(
            footprint,
            item["peakMemoryBytes"],
            item["contextTokens"],
            quantization_present=bool(item["quantizationPresent"]),
        )
        for key in ("artifactFit", "memoryFit", "contextFit", "storageHeadroom", "hardwareFit"):
            if item[key] != fits[key]:
                raise BudgetError("fit")
        directory = item["directoryBytes"]
        exceeds = directory is not None and directory > ARTIFACT_CAP
        if item["directoryExceedsCap"] is not exceeds:
            raise BudgetError("directory")
    return document


def load_artifact_budget(root: Path | None = None) -> dict[str, Any]:
    """Load the committed record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise BudgetError("record-type")
    document = validate_artifact_budget(loaded)
    if document != decide_artifact_budget():
        raise BudgetError("budget-drift")
    return document


def _require_profile_caps() -> None:
    profile = json.loads((repo_root() / _PROFILE).read_text(encoding="utf-8"))
    envelope = profile["resourceEnvelope"]
    if envelope["maximumArtifactBytes"] != ARTIFACT_CAP:
        raise BudgetError("artifact-cap")
    if envelope["maximumPeakProcessMemoryBytes"] != MEMORY_CAP:
        raise BudgetError("memory-cap")
    if envelope["maximumContextTokens"] != CONTEXT_CAP:
        raise BudgetError("context-cap")
    if profile["availableStorageBytes"] != _STORAGE:
        raise BudgetError("storage")
    if envelope["quantizationApproved"] is not False:
        raise BudgetError("quantization")


def _fit(passed: bool) -> str:
    return "pass" if passed else "fail"


def _family(item: dict[str, Any]) -> dict[str, Any]:
    external = list(item["externalDataBytes"])
    footprint = artifact_footprint(
        item["graphBytes"],
        external,
        item["tokenizerConfigurationBytes"],
        item["verificationOverheadBytes"],
        item["runtimeStagingAllowanceBytes"],
    )
    fits = budget_fits(
        footprint,
        item["peakMemoryBytes"],
        item["contextTokens"],
        quantization_present=bool(item["quantizationPresent"]),
    )
    return {
        "modelId": item["modelId"],
        "contextTokens": item["contextTokens"],
        "contextFit": fits["contextFit"],
        "graphBytes": item["graphBytes"],
        "externalDataBytes": external,
        "tokenizerConfigurationBytes": item["tokenizerConfigurationBytes"],
        "verificationOverheadBytes": item["verificationOverheadBytes"],
        "runtimeStagingAllowanceBytes": item["runtimeStagingAllowanceBytes"],
        "peakMemoryBytes": item["peakMemoryBytes"],
        "quantizationPresent": item["quantizationPresent"],
        "footprintBytes": footprint,
        "artifactFit": fits["artifactFit"],
        "memoryFit": fits["memoryFit"],
        "storageHeadroom": fits["storageHeadroom"],
        "hardwareFit": fits["hardwareFit"],
        "directoryBytes": item["directoryBytes"],
        "directoryExceedsCap": bool(item["directoryExceedsCap"]),
        "nonquantizedPairBytes": item["nonquantizedPairBytes"],
        "pairQualifies": False,
    }


def _unknown(model_id: str, context: int | None) -> dict[str, Any]:
    return {
        "modelId": model_id,
        "contextTokens": context,
        "graphBytes": None,
        "externalDataBytes": [],
        "tokenizerConfigurationBytes": None,
        "verificationOverheadBytes": None,
        "runtimeStagingAllowanceBytes": None,
        "peakMemoryBytes": None,
        "quantizationPresent": False,
        "directoryBytes": None,
        "directoryExceedsCap": False,
        "nonquantizedPairBytes": None,
    }


_INPUTS: tuple[dict[str, Any], ...] = (
    _unknown(MODEL_IDS[0], 32768),
    _unknown(MODEL_IDS[1], 32768),
    {
        **_unknown(MODEL_IDS[2], None),
        "quantizationPresent": True,
        "directoryBytes": published_directory_bytes(),
        "directoryExceedsCap": True,
        "nonquantizedPairBytes": nonquantized_pair_bytes(),
    },
    _unknown(MODEL_IDS[3], None),
    _unknown(MODEL_IDS[4], 32768),
)
