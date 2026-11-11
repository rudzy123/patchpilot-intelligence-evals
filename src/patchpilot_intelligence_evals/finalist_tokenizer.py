"""Tokenizer eligibility for Track 7 finalists.

The license conclusion uses the instrument in the pinned revision. Co-location is
not treated as proof unless that instrument applies to the whole revision.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
    decide_candidate_discovery,
    evidence,
)
from patchpilot_intelligence_evals.candidate_eligibility import RETRIEVED_ON
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/finalist-tokenizer.json")
_CLEAR = frozenset({"granted", "restricted", "not-granted"})
_INSTRUMENTS = frozenset({"revision-license-file", "separate-instrument"})
_LICENSE = (
    f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/{LFM_ONNX_REVISION}/LICENSE"
)


class FinalistTokenizerError(ValueError):
    """A tokenizer record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def tokenizer_eligible(item: dict[str, Any]) -> bool:
    """Unknown or inferred licensing fails. Restricted-but-explicit terms can pass."""
    grants = (item["commercialUse"], item["redistribution"], item["modification"])
    inventory = item["inventory"]
    return (
        item["sourceKind"] == "model-revision"
        and item["licenseInstrument"] in _INSTRUMENTS
        and all(grant in _CLEAR for grant in grants)
        and item["offlineOperation"] is True
        and item["automaticRetrievalRequired"] is False
        and item["remoteCodeRequired"] is False
        and item["inventoryComplete"] is True
        and any(entry["role"] == "tokenizer" for entry in inventory)
    )


def decide_finalist_tokenizer() -> dict[str, Any]:
    """Build the committed tokenizer decision for the discovery finalist."""
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
        "finalistCount": 1,
        "finalistModelIds": [LFM_MODEL_ID],
        "locallyObservedArtifactDigests": [],
        "finalists": [_lfm()],
    }
    return validate_finalist_tokenizer(document)


def validate_finalist_tokenizer(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one tokenizer record."""
    validate("finalist-tokenizer", document)
    if contains_private_marker(document):
        raise FinalistTokenizerError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise FinalistTokenizerError("local-digest")
    _require_finalist(document["finalistModelIds"])
    finalists = document["finalists"]
    if [item["modelId"] for item in finalists] != document["finalistModelIds"]:
        raise FinalistTokenizerError("finalist-boundary")
    if document["finalistCount"] != len(finalists):
        raise FinalistTokenizerError("finalist-count")
    for item in finalists:
        if item["eligibilityOutcome"] != ("pass" if tokenizer_eligible(item) else "fail"):
            raise FinalistTokenizerError("eligibility")
        if item["revision"] != LFM_ONNX_REVISION or item["modelRevision"] != LFM_SOURCE_REVISION:
            raise FinalistTokenizerError("revision")
        if not _evidence_ok(item):
            raise FinalistTokenizerError("evidence")
    return document


def load_finalist_tokenizer(root: Path | None = None) -> dict[str, Any]:
    """Load the committed tokenizer record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise FinalistTokenizerError("record-type")
    document = validate_finalist_tokenizer(loaded)
    if document != decide_finalist_tokenizer():
        raise FinalistTokenizerError("tokenizer-drift")
    return document


def _require_finalist(model_ids: list[str] | None = None) -> None:
    expected = decide_candidate_discovery()["finalistModelIds"]
    if expected != [LFM_MODEL_ID]:
        raise FinalistTokenizerError("finalist-boundary")
    if model_ids is not None and model_ids != expected:
        raise FinalistTokenizerError("finalist-boundary")


def _evidence_ok(item: dict[str, Any]) -> bool:
    classes = set()
    instruments = set()
    for entry in item["evidence"]:
        classes.add(entry["evidenceClass"])
        instruments.add(entry["evidenceId"])
        if entry["applicability"] != item["modelId"]:
            return False
        if '"' in entry["claim"] or "'" in entry["claim"]:
            return False
        revision = entry["immutableRevision"]
        if revision not in {None, LFM_ONNX_REVISION, LFM_SOURCE_REVISION}:
            return False
    return "authoritative" in classes and "lfm-tokenizer-license" in instruments


def _lfm() -> dict[str, Any]:
    row: dict[str, Any] = {
        "modelId": LFM_MODEL_ID,
        "modelRevision": LFM_SOURCE_REVISION,
        "revision": LFM_ONNX_REVISION,
        "sourceKind": "model-revision",
        "sourceRepository": "LiquidAI/LFM2.5-1.2B-Instruct-ONNX",
        "licenseInstrument": "revision-license-file",
        "licenseName": "LFM Open License v1.0",
        "commercialUse": "restricted",
        "redistribution": "granted",
        "modification": "granted",
        "attributionRequired": True,
        "offlineOperation": True,
        "automaticRetrievalRequired": False,
        "remoteCodeRequired": False,
        "inventoryComplete": True,
        "inventory": [
            {
                "fileName": "tokenizer.json",
                "role": "tokenizer",
                "listedByteCount": 3297799,
                "localDigestRequired": True,
            },
            {
                "fileName": "tokenizer_config.json",
                "role": "tokenizer",
                "listedByteCount": 2391,
                "localDigestRequired": True,
            },
        ],
        "evidence": [
            evidence(
                "lfm-tokenizer-license",
                "LFM2.5 ONNX LICENSE file",
                _LICENSE,
                "Liquid AI",
                LFM_ONNX_REVISION,
                (
                    "The pinned ONNX LICENSE is LFM Open License v1.0 and applies to the "
                    "Work in that revision, including tokenizer.json. Commercial use is "
                    "conditioned on annual revenue not exceeding 10000000 USD."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "none",
            ),
            evidence(
                "lfm-tokenizer-offline",
                "LFM2.5 ONNX model card",
                (
                    "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/"
                    f"{LFM_ONNX_REVISION}/README.md"
                ),
                "Liquid AI",
                LFM_ONNX_REVISION,
                (
                    "The quickstart sets trust_remote_code, and the pinned trees contain "
                    "no custom Python module. Local tokenizer files do not require a "
                    "hosted tokenizer API. The flag is not a load requirement."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "restrictive-reading",
            ),
        ],
    }
    row["eligibilityOutcome"] = "pass" if tokenizer_eligible(row) else "fail"
    return row
