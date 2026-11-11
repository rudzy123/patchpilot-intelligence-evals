"""Track 7 artifact budget. Unknown sizes fail, and one byte over either cap fails.

Verification overhead is one extra copy of the selected inventory because promotion
copies quarantine to verified. The runtime allowance is the published package size.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import (
    ARTIFACT_CAP,
    CONTEXT_CAP,
    MEMORY_CAP,
    budget_fits,
)
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    contains_private_marker,
    decide_candidate_discovery,
    evidence,
)
from patchpilot_intelligence_evals.candidate_eligibility import RETRIEVED_ON
from patchpilot_intelligence_evals.finalist_onnx import (
    SELECTED_FILES,
    component_bytes,
    decide_finalist_onnx,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.subprocess_compatibility import PROPERTIES

_RECORD = Path("candidates/authorization/finalist-artifact-budget.json")
_ADAPTER = Path("candidates/authorization/runtime-adapter-contract.json")
_PROFILE = Path("candidates/authorization/evaluation-hardware-profile.json")
RUNTIME_ID = "onnxruntime"
RUNTIME_TAG = "v1.31.1"
RUNTIME_REVISION = "6af1a932e2286d5c58166085d24c68783033edee"
RUNTIME_PACKAGE = "onnxruntime-linux-x64-1.31.1.tgz"
RUNTIME_LISTED_BYTES = 11413655
RUNTIME_LISTED_SHA256 = "c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9"
ADAPTER_ID = "patchpilot-onnxruntime-adapter"
ADAPTER_VERSION = "1.0.0"
PROFILE_ID = "linux-bwrap-systemd-v1"
PROFILE_VERSION = "1.0.0"
_STORAGE = 1403456720896
TRACK7_PROPERTIES = PROPERTIES + ("bounded-output", "no-quantization")


class FinalistBudgetError(ValueError):
    """A budget record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def track7_footprint(
    graph_bytes: int | None,
    external_data_bytes: Sequence[int | None],
    tokenizer_bytes: int | None,
    configuration_bytes: int | None,
    metadata_bytes: int | None,
    runtime_staging_bytes: int | None,
) -> int | None:
    """Inventory plus one verification copy plus the runtime package. Unknown fails."""
    parts: list[int | None] = [
        graph_bytes,
        tokenizer_bytes,
        configuration_bytes,
        metadata_bytes,
        runtime_staging_bytes,
        *external_data_bytes,
    ]
    if any(part is None for part in parts):
        return None
    inventory = sum(
        part
        for part in (
            graph_bytes,
            tokenizer_bytes,
            configuration_bytes,
            metadata_bytes,
            *external_data_bytes,
        )
        if part is not None
    )
    if runtime_staging_bytes is None:
        return None
    return inventory + inventory + runtime_staging_bytes


def execution_compatible(properties: dict[str, str], direct_onnx: bool) -> bool:
    """Every planned-contract property must pass, and the official ONNX path must qualify."""
    if set(properties) != set(TRACK7_PROPERTIES):
        raise FinalistBudgetError("property-set")
    return direct_onnx and all(properties[name] == "pass" for name in TRACK7_PROPERTIES)


def decide_finalist_budget() -> dict[str, Any]:
    """Build the committed fail-closed budget for the discovery finalist."""
    _require_identities()
    _require_finalist()
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
        "contextCapTokens": CONTEXT_CAP,
        "availableStorageBytes": _STORAGE,
        "runtimeId": RUNTIME_ID,
        "runtimeVersionTag": RUNTIME_TAG,
        "runtimeRevision": RUNTIME_REVISION,
        "runtimePackageFileName": RUNTIME_PACKAGE,
        "runtimeStagingListedBytes": RUNTIME_LISTED_BYTES,
        "runtimePackagePublishedSha256": RUNTIME_LISTED_SHA256,
        "adapterId": ADAPTER_ID,
        "adapterVersion": ADAPTER_VERSION,
        "profileId": PROFILE_ID,
        "profileVersion": PROFILE_VERSION,
        "safetensorsExecution": "prohibited",
        "quantizationApproved": False,
        "verificationPerformed": False,
        "finalistCount": 1,
        "finalistModelIds": [LFM_MODEL_ID],
        "locallyObservedArtifactDigests": [],
        "finalists": [_lfm()],
    }
    return validate_finalist_budget(document)


def validate_finalist_budget(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one budget record."""
    validate("finalist-artifact-budget", document)
    if contains_private_marker(document):
        raise FinalistBudgetError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise FinalistBudgetError("local-digest")
    if document["artifactCapBytes"] != ARTIFACT_CAP or document["memoryCapBytes"] != MEMORY_CAP:
        raise FinalistBudgetError("cap")
    if document["contextCapTokens"] != CONTEXT_CAP:
        raise FinalistBudgetError("cap")
    if document["verificationPerformed"] is not False:
        raise FinalistBudgetError("disabled-state")
    if document["quantizationApproved"] is not False:
        raise FinalistBudgetError("disabled-state")
    _require_identities()
    _require_finalist(document["finalistModelIds"])
    if document["runtimeStagingListedBytes"] != RUNTIME_LISTED_BYTES:
        raise FinalistBudgetError("runtime-size")
    if document["runtimeRevision"] != RUNTIME_REVISION:
        raise FinalistBudgetError("runtime-revision")
    finalists = document["finalists"]
    if [item["modelId"] for item in finalists] != document["finalistModelIds"]:
        raise FinalistBudgetError("finalist-boundary")
    if document["finalistCount"] != len(finalists):
        raise FinalistBudgetError("finalist-count")
    direct = decide_finalist_onnx()["finalists"][0]["directPathEligible"]
    for item in finalists:
        if not _budget_matches(item, direct_onnx=bool(direct)):
            raise FinalistBudgetError("arithmetic")
        if not _evidence_ok(item):
            raise FinalistBudgetError("evidence")
    return document


def load_finalist_budget(root: Path | None = None) -> dict[str, Any]:
    """Load the committed budget and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise FinalistBudgetError("record-type")
    document = validate_finalist_budget(loaded)
    if document != decide_finalist_budget():
        raise FinalistBudgetError("budget-drift")
    return document


def _budget_matches(item: dict[str, Any], *, direct_onnx: bool) -> bool:
    parts = component_bytes()
    external = [
        listed.listed_byte_count
        for listed in SELECTED_FILES
        if listed.selected and listed.role == "external-data"
    ]
    footprint = track7_footprint(
        parts["graphBytes"],
        external,
        parts["tokenizerBytes"],
        parts["configurationBytes"],
        parts["metadataBytes"],
        RUNTIME_LISTED_BYTES,
    )
    fits = budget_fits(
        footprint,
        item["peakMemoryBytes"],
        item["contextTokens"],
        quantization_present=item["quantizationPresent"],
    )
    properties = {entry["name"]: entry["result"] for entry in item["properties"]}
    compatible = execution_compatible(properties, direct_onnx)
    expected_outcome = "pass" if compatible else "fail"
    if item["footprintBytes"] != footprint or item["inventoryBytes"] != parts["inventoryBytes"]:
        return False
    if item["verificationOverheadBytes"] != parts["inventoryBytes"]:
        return False
    if item["runtimeStagingListedBytes"] != RUNTIME_LISTED_BYTES:
        return False
    if item["peakMemoryBasis"] == "unknown-fp32" and item["peakMemoryBytes"] is not None:
        return False
    for name in (
        "graphBytes",
        "externalDataBytes",
        "tokenizerBytes",
        "configurationBytes",
        "metadataBytes",
    ):
        if item[name] != parts[name]:
            return False
    for name, result in fits.items():
        if item[name] != result:
            return False
    outcome_matches: bool = item["executionOutcome"] == expected_outcome
    return outcome_matches


def _require_identities() -> None:
    root = repo_root()
    adapter = json.loads((root / _ADAPTER).read_text(encoding="utf-8"))
    profile = json.loads((root / _PROFILE).read_text(encoding="utf-8"))
    envelope = profile["resourceEnvelope"]
    if adapter["adapterId"] != ADAPTER_ID or adapter["adapterVersion"] != ADAPTER_VERSION:
        raise FinalistBudgetError("adapter")
    if adapter["immutableRevision"] != RUNTIME_REVISION or adapter["versionTag"] != RUNTIME_TAG:
        raise FinalistBudgetError("adapter")
    if adapter["sourceModel"]["execution"] != "prohibited":
        raise FinalistBudgetError("safetensors")
    if adapter["profileId"] != PROFILE_ID or adapter["profileVersion"] != PROFILE_VERSION:
        raise FinalistBudgetError("profile")
    if envelope["maximumArtifactBytes"] != ARTIFACT_CAP:
        raise FinalistBudgetError("cap")
    if envelope["maximumPeakProcessMemoryBytes"] != MEMORY_CAP:
        raise FinalistBudgetError("cap")
    if envelope["maximumContextTokens"] != CONTEXT_CAP:
        raise FinalistBudgetError("cap")
    if profile["availableStorageBytes"] != _STORAGE:
        raise FinalistBudgetError("cap")


def _require_finalist(model_ids: list[str] | None = None) -> None:
    expected = decide_candidate_discovery()["finalistModelIds"]
    if expected != [LFM_MODEL_ID]:
        raise FinalistBudgetError("finalist-boundary")
    if model_ids is not None and model_ids != expected:
        raise FinalistBudgetError("finalist-boundary")


def _evidence_ok(item: dict[str, Any]) -> bool:
    classes = {entry["evidenceClass"] for entry in item["evidence"]}
    if "authoritative" not in classes:
        return False
    for entry in item["evidence"]:
        if '"' in entry["claim"] or "'" in entry["claim"]:
            return False
        if entry["applicability"] not in {item["modelId"], RUNTIME_ID}:
            return False
    return True


def _lfm() -> dict[str, Any]:
    parts = component_bytes()
    external = [
        item.listed_byte_count
        for item in SELECTED_FILES
        if item.selected and item.role == "external-data"
    ]
    footprint = track7_footprint(
        parts["graphBytes"],
        external,
        parts["tokenizerBytes"],
        parts["configurationBytes"],
        parts["metadataBytes"],
        RUNTIME_LISTED_BYTES,
    )
    context = 32768
    fits = budget_fits(footprint, None, context, quantization_present=False)
    direct = bool(decide_finalist_onnx()["finalists"][0]["directPathEligible"])
    properties = [{"name": name, "result": "pass"} for name in TRACK7_PROPERTIES]
    mapped = {entry["name"]: entry["result"] for entry in properties}
    row: dict[str, Any] = {
        "modelId": LFM_MODEL_ID,
        "onnxRevision": LFM_ONNX_REVISION,
        "contextTokens": context,
        "peakMemoryBytes": None,
        "peakMemoryBasis": "unknown-fp32",
        "quantizationPresent": False,
        "cpuOnlyViability": "pass",
        "verificationOverheadEqualsInventory": True,
        "properties": properties,
        "evidence": [
            evidence(
                "ort-v1-31-1-release",
                "ONNX Runtime v1.31.1 release",
                "https://github.com/microsoft/onnxruntime/releases/tag/v1.31.1",
                "Microsoft",
                RUNTIME_REVISION,
                (
                    "Release v1.31.1 is commit 6af1a932e2286d5c58166085d24c68783033edee. "
                    "The asset onnxruntime-linux-x64-1.31.1.tgz is listed at 11413655 bytes."
                ),
                "authoritative",
                RUNTIME_ID,
                "none",
            ),
            evidence(
                "lfm-memory-card",
                "LFM2.5-1.2B-Instruct model card",
                (
                    "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/"
                    "b9d816ab510f9a28dca37cb182e9da8b0226e13c/README.md"
                ),
                "Liquid AI",
                "b9d816ab510f9a28dca37cb182e9da8b0226e13c",
                (
                    "The card states sub-1GB figures for NPU and Q4_0 rows. Those figures "
                    "do not establish FP32 ONNX peak memory, so peak memory stays unknown."
                ),
                "conflicting",
                LFM_MODEL_ID,
                "restrictive-reading",
            ),
        ],
    }
    row.update(parts)
    row["verificationOverheadBytes"] = parts["inventoryBytes"]
    row["runtimeStagingListedBytes"] = RUNTIME_LISTED_BYTES
    row["footprintBytes"] = footprint
    row.update(fits)
    row["executionOutcome"] = "pass" if execution_compatible(mapped, direct) else "fail"
    return row
