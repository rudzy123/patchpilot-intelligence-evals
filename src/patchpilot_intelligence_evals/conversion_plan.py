"""ONNX conversion-plan decision.

Three official toolchains are assessed. None is authorized. No tool is installed
and no conversion is performed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.conversion_equivalence import (
    ATOL,
    COMPARISON,
    CONVERTED_PROVENANCE,
    RTOL,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/onnx-conversion-plan.json")
_TOOLCHAINS: tuple[dict[str, Any], ...] = (
    {
        "toolchainId": "optimum-onnx",
        "versionTag": "v0.1.0",
        "immutableRevision": "d2328e386a81b0970a458a7570a38b131414edc6",
        "licenseName": "Apache-2.0",
        "authorizationOutcome": "not-authorized",
        "disqualifiers": (
            "export-defaults-not-offline-closed",
            "runtime-pin-not-authorized",
            "sources-not-independently-eligible",
            "torch-pin-unresolved",
        ),
    },
    {
        "toolchainId": "onnxruntime-genai",
        "versionTag": "v0.19.0",
        "immutableRevision": "d01b2441a72d4e3223415b9b08474c6e65fbc028",
        "licenseName": "MIT",
        "authorizationOutcome": "not-authorized",
        "disqualifiers": (
            "architecture-support-unresolved",
            "sources-not-independently-eligible",
        ),
    },
    {
        "toolchainId": "pytorch-onnx-exporter",
        "versionTag": "unresolved",
        "immutableRevision": None,
        "licenseName": "unresolved",
        "authorizationOutcome": "not-authorized",
        "disqualifiers": (
            "not-a-closed-safetensors-toolchain",
            "sources-not-independently-eligible",
            "version-unresolved",
        ),
    },
)


class ConversionPlanError(ValueError):
    """A conversion plan failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_conversion_plan() -> dict[str, Any]:
    """Return the withheld conversion plan."""
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "runtimeInstalled": False,
        "modelAcquired": False,
        "realModelExecuted": False,
        "installationAuthorized": False,
        "authorizationOutcome": "not-authorized",
        "conversionStatus": "not-performed",
        "selectionOutcome": "no-selection",
        "retrievedOn": "2026-11-10",
        "toolchains": [
            {**item, "disqualifiers": sorted(item["disqualifiers"])} for item in _TOOLCHAINS
        ],
        "equivalence": {
            "comparison": COMPARISON,
            "atol": ATOL,
            "rtol": RTOL,
            "convertedProvenance": CONVERTED_PROVENANCE,
            "publisherProvided": False,
            "opsetDisposition": "unresolved",
            "precisionDisposition": "unresolved",
            "externalDataDisposition": "unresolved",
            "determinismDisposition": "variation-characterized",
        },
        "offlineClosed": False,
        "equivalenceMeasured": False,
        "locallyObservedArtifactDigests": [],
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
    }
    return validate_conversion_plan(document)


def validate_conversion_plan(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one conversion plan."""
    validate("onnx-conversion-plan", document)
    if document["equivalence"]["atol"] != ATOL or document["equivalence"]["rtol"] != RTOL:
        raise ConversionPlanError("tolerance")
    if document["equivalence"]["convertedProvenance"] != CONVERTED_PROVENANCE:
        raise ConversionPlanError("provenance")
    if document["equivalence"]["publisherProvided"] is not False:
        raise ConversionPlanError("publisher-provided")
    text = json.dumps(document)
    if "/home/" in text or "https://" in text or "http://" in text:
        raise ConversionPlanError("identity")
    if len(document["toolchains"]) > 3:
        raise ConversionPlanError("toolchain-count")
    return document


def load_conversion_plan(root: Path | None = None) -> dict[str, Any]:
    """Load the committed plan and require it to match the decision function."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ConversionPlanError("record-type")
    document = validate_conversion_plan(loaded)
    if document != decide_conversion_plan():
        raise ConversionPlanError("plan-drift")
    return document
