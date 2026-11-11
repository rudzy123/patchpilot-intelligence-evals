"""Tokenizer eligibility for the five pinned families.

A model-card license does not license a tokenizer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_eligibility import (
    MODEL_IDS,
    RETRIEVED_ON,
    EligibilityError,
    reject_private_markers,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/tokenizer-eligibility.json")
_PASSING_INSTRUMENTS = frozenset({"revision-license-file", "separate-instrument"})


class TokenizerError(ValueError):
    """A tokenizer record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def tokenizer_eligible(license_instrument: str) -> bool:
    """Same-revision or separate instruments can pass. Assumptions cannot."""
    return license_instrument in _PASSING_INSTRUMENTS


def decide_tokenizer_eligibility() -> dict[str, Any]:
    """Build the committed tokenizer decisions."""
    families = [_family(item) for item in _INPUTS]
    document = _shell(families)
    return validate_tokenizer_eligibility(document)


def validate_tokenizer_eligibility(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one tokenizer record."""
    validate("tokenizer-eligibility", document)
    try:
        reject_private_markers(document, EligibilityError)
    except EligibilityError as exc:
        raise TokenizerError(exc.code) from exc
    if document["locallyObservedArtifactDigests"] != []:
        raise TokenizerError("local-digest")
    families = document["families"]
    if [item["modelId"] for item in families] != list(MODEL_IDS):
        raise TokenizerError("candidate-boundary")
    for item in families:
        expected = "pass" if tokenizer_eligible(str(item["licenseInstrument"])) else "fail"
        if item["eligibilityOutcome"] != expected:
            raise TokenizerError("tokenizer-eligibility")
        if item["remoteCodeRequired"] is True and item["eligibilityOutcome"] == "pass":
            raise TokenizerError("remote-code")
        if item["automaticRetrievalRequired"] is True and item["eligibilityOutcome"] == "pass":
            raise TokenizerError("automatic-retrieval")
        if any(entry["byteCount"] is not None for entry in item["fileInventory"]):
            raise TokenizerError("local-size")
    return document


def load_tokenizer_eligibility(root: Path | None = None) -> dict[str, Any]:
    """Load the committed record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TokenizerError("record-type")
    document = validate_tokenizer_eligibility(loaded)
    if document != decide_tokenizer_eligibility():
        raise TokenizerError("tokenizer-drift")
    return document


def _shell(families: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "locallyObservedArtifactDigests": [],
        "families": families,
    }


def _files(*names: str) -> list[dict[str, Any]]:
    return [{"fileName": name, "byteCount": None} for name in names]


def _family(item: dict[str, Any]) -> dict[str, Any]:
    instrument = str(item["licenseInstrument"])
    return {
        "modelId": item["modelId"],
        "revision": item["revision"],
        "tokenizerIdentity": item["tokenizerIdentity"],
        "sourceKind": item["sourceKind"],
        "immutableRevision": item["immutableRevision"],
        "fileInventory": _files(*item["files"]),
        "licenseInstrument": instrument,
        "commercialUse": item["commercialUse"],
        "redistribution": item["redistribution"],
        "modification": item["modification"],
        "offlineLoading": item["offlineLoading"],
        "remoteCodeRequired": False,
        "automaticRetrievalRequired": False,
        "eligibilityOutcome": "pass" if tokenizer_eligible(instrument) else "fail",
        "conflicts": list(item["conflicts"]),
        "evidence": list(item["evidence"]),
    }


def _evidence(
    evidence_id: str,
    source_name: str,
    url: str,
    publisher: str,
    revision: str | None,
    claim: str,
    evidence_class: str,
    applicability: str,
    disposition: str,
) -> dict[str, Any]:
    return {
        "evidenceId": evidence_id,
        "sourceName": source_name,
        "url": url,
        "publisher": publisher,
        "retrievedOn": RETRIEVED_ON,
        "immutableRevision": revision,
        "claim": claim,
        "evidenceClass": evidence_class,
        "applicability": applicability,
        "conflictDisposition": disposition,
    }


def _conflict(topic: str, status: str, text: str) -> dict[str, str]:
    return {"topic": topic, "status": status, "restrictiveInterpretation": text}


_QWEN15 = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
_QWEN3 = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
_SMOL = "31b70e2e869a7173562077fd711b654946d38674"
_OLMO = "48d788eca847d4d7548f375ad03d3c9312f6139e"
_GEMMA = "dcc83ea841ab6100d6b47a070329e1ba4cf78752"
_COSMO = "4ce2318a3628e77279c939ed6a9f3f03034402de"
_DOLMA = "5292e5d6c0f40b67cc765fe41bec991cf4345b5c"
_TOKEN_FILES = ("merges.txt", "tokenizer.json", "tokenizer_config.json", "vocab.json")

_INPUTS: tuple[dict[str, Any], ...] = (
    {
        "modelId": MODEL_IDS[0],
        "revision": _QWEN15,
        "tokenizerIdentity": "Qwen2.5-1.5B-Instruct tokenizer",
        "sourceKind": "model-revision",
        "immutableRevision": _QWEN15,
        "files": _TOKEN_FILES,
        "licenseInstrument": "terms-do-not-name-tokenizer",
        "commercialUse": "unresolved",
        "redistribution": "unresolved",
        "modification": "unresolved",
        "offlineLoading": "pass",
        "conflicts": (
            _conflict(
                "tokenizer-applicability",
                "unresolved",
                "Apache-2.0 covers a Work with an attached notice. This file names no tokenizer.",
            ),
        ),
        "evidence": (
            _evidence(
                "qwen15-tokenizer-license",
                "Qwen2.5-1.5B-Instruct license file",
                "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/" + _QWEN15 + "/LICENSE",
                "Qwen Team",
                _QWEN15,
                "Apache-2.0 names none of the four tokenizer files listed for this revision.",
                "authoritative",
                MODEL_IDS[0],
                "unresolved",
            ),
            _evidence(
                "qwen15-tokenizer-listing",
                "Qwen2.5-1.5B-Instruct revision listing",
                "https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B-Instruct/revision/" + _QWEN15,
                "Qwen Team",
                _QWEN15,
                "Listing files: merges.txt, vocab.json, tokenizer.json, tokenizer_config.json.",
                "authoritative",
                MODEL_IDS[0],
                "none",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[1],
        "revision": _QWEN3,
        "tokenizerIdentity": "Qwen2.5-3B-Instruct tokenizer",
        "sourceKind": "model-revision",
        "immutableRevision": _QWEN3,
        "files": _TOKEN_FILES,
        "licenseInstrument": "terms-do-not-name-tokenizer",
        "commercialUse": "unresolved",
        "redistribution": "unresolved",
        "modification": "unresolved",
        "offlineLoading": "pass",
        "conflicts": (
            _conflict(
                "tokenizer-applicability",
                "unresolved",
                "The research license names weights and code. It does not name tokenizer files.",
            ),
            _conflict(
                "separate-instrument",
                "resolved",
                "This research LICENSE is not the 1.5B Apache-2.0 file. The grants stay separate.",
            ),
        ),
        "evidence": (
            _evidence(
                "qwen3-tokenizer-license",
                "Qwen2.5-3B-Instruct research license",
                "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/" + _QWEN3 + "/LICENSE",
                "Alibaba Cloud",
                _QWEN3,
                "Materials include weights and code. The text does not name tokenizer files.",
                "authoritative",
                MODEL_IDS[1],
                "unresolved",
            ),
            _evidence(
                "qwen3-tokenizer-listing",
                "Qwen2.5-3B-Instruct revision listing",
                "https://huggingface.co/api/models/Qwen/Qwen2.5-3B-Instruct/revision/" + _QWEN3,
                "Qwen Team",
                _QWEN3,
                "Listing files: merges.txt, vocab.json, tokenizer.json, tokenizer_config.json.",
                "authoritative",
                MODEL_IDS[1],
                "none",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[2],
        "revision": _SMOL,
        "tokenizerIdentity": "SmolLM2-1.7B-Instruct tokenizer",
        "sourceKind": "model-revision",
        "immutableRevision": _SMOL,
        "files": _TOKEN_FILES + ("special_tokens_map.json",),
        "licenseInstrument": "absent",
        "commercialUse": "unresolved",
        "redistribution": "unresolved",
        "modification": "unresolved",
        "offlineLoading": "pass",
        "conflicts": (
            _conflict(
                "tokenizer-license",
                "unresolved",
                "The model card is not a tokenizer license. cosmo2 publishes no license file.",
            ),
        ),
        "evidence": (
            _evidence(
                "smol-tokenizer-listing",
                "SmolLM2-1.7B-Instruct revision listing",
                "https://huggingface.co/api/models/HuggingFaceTB/SmolLM2-1.7B-Instruct",
                "HuggingFaceTB",
                _SMOL,
                "Tokenizer files are in the revision. That revision has no LICENSE file.",
                "authoritative",
                MODEL_IDS[2],
                "unresolved",
            ),
            _evidence(
                "smol-cosmo2-tokenizer",
                "cosmo2 tokenizer card",
                "https://huggingface.co/api/models/HuggingFaceTB/cosmo2-tokenizer",
                "HuggingFaceTB",
                _COSMO,
                "cosmo2 at this revision has no license field and no LICENSE file.",
                "authoritative",
                MODEL_IDS[2],
                "unresolved",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[3],
        "revision": _OLMO,
        "tokenizerIdentity": "OLMo-2-0425-1B-Instruct tokenizer",
        "sourceKind": "model-revision",
        "immutableRevision": _OLMO,
        "files": _TOKEN_FILES + ("special_tokens_map.json",),
        "licenseInstrument": "absent",
        "commercialUse": "unresolved",
        "redistribution": "unresolved",
        "modification": "unresolved",
        "offlineLoading": "pass",
        "conflicts": (
            _conflict(
                "tokenizer-license",
                "unresolved",
                "The instruct card does not state a tokenizer license. dolma2 has no license file.",
            ),
        ),
        "evidence": (
            _evidence(
                "olmo-tokenizer-listing",
                "OLMo-2-0425-1B-Instruct revision listing",
                "https://huggingface.co/api/models/allenai/"
                "OLMo-2-0425-1B-Instruct/revision/" + _OLMO,
                "Allen Institute for AI",
                _OLMO,
                "Tokenizer files are in the revision. That revision has no LICENSE file.",
                "authoritative",
                MODEL_IDS[3],
                "unresolved",
            ),
            _evidence(
                "olmo-dolma2-tokenizer",
                "dolma2 tokenizer card",
                "https://huggingface.co/api/models/allenai/dolma2-tokenizer",
                "Allen Institute for AI",
                _DOLMA,
                "dolma2 at this revision has no license field and no LICENSE file.",
                "authoritative",
                MODEL_IDS[3],
                "unresolved",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[4],
        "revision": _GEMMA,
        "tokenizerIdentity": "gemma-3-1b-it tokenizer",
        "sourceKind": "model-revision",
        "immutableRevision": _GEMMA,
        "files": (
            "added_tokens.json",
            "special_tokens_map.json",
            "tokenizer.json",
            "tokenizer.model",
            "tokenizer_config.json",
        ),
        "licenseInstrument": "terms-do-not-name-tokenizer",
        "commercialUse": "unresolved",
        "redistribution": "unresolved",
        "modification": "unresolved",
        "offlineLoading": "pass",
        "conflicts": (
            _conflict(
                "tokenizer-grant",
                "unresolved",
                "The Gemma terms cover weights and parameters. They do not name the tokenizer.",
            ),
        ),
        "evidence": (
            _evidence(
                "gemma-tokenizer-terms",
                "Gemma terms of use",
                "https://ai.google.dev/gemma/terms",
                "Google",
                None,
                "The terms define Gemma as weights and parameters and do not name a tokenizer.",
                "authoritative",
                MODEL_IDS[4],
                "restrictive-reading",
            ),
            _evidence(
                "gemma-tokenizer-listing",
                "gemma-3-1b-it revision listing",
                "https://huggingface.co/api/models/google/gemma-3-1b-it/revision/" + _GEMMA,
                "Google",
                _GEMMA,
                "The revision lists tokenizer.json and tokenizer.model. Terms omit them.",
                "authoritative",
                MODEL_IDS[4],
                "unresolved",
            ),
        ),
    },
)
