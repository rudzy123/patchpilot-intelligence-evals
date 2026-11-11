"""Track 6C candidate eligibility closure for the five pinned families.

Listing facts are upstream statements. They are not local observations.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/candidate-eligibility-closure.json")
RETRIEVED_ON = "2026-11-11"
MODEL_IDS: tuple[str, ...] = (
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "allenai/OLMo-2-0425-1B-Instruct",
    "google/gemma-3-1b-it",
)
MANDATORY: tuple[str, ...] = (
    "explicit-weight-use-license",
    "clear-commercial-use-position",
    "clear-redistribution-position",
    "immutable-official-revision",
    "no-remote-code-requirement",
    "fully-offline-runtime-support",
    "tokenizer-provenance",
    "artifact-digest-capability",
    "local-resource-fit",
    "bounded-subprocess-compatibility",
    "no-mandatory-telemetry",
    "no-tenant-data-requirement",
    "official-model-card",
    "documented-limitations",
    "no-production-dependency",
)
CATEGORY_WEIGHTS: dict[str, int] = {
    "license-provenance": 25,
    "security-offline": 20,
    "hardware-fit": 20,
    "evaluation-suitability": 20,
    "model-card": 10,
    "runtime-maturity": 5,
}
_RESULT_FIELDS: dict[str, str] = {
    "weightLicenseResult": "explicit-weight-use-license",
    "commercialUseResult": "clear-commercial-use-position",
    "redistributionResult": "clear-redistribution-position",
    "remoteCodeResult": "no-remote-code-requirement",
    "modelCardLimitationsResult": "documented-limitations",
}
_PRIVATE = re.compile(r"(?:/home/|(?:\d{1,3}\.){3}\d{1,3}|ip-26-0-174-36)")

_QWEN15 = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
_QWEN3 = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
_SMOL = "31b70e2e869a7173562077fd711b654946d38674"
_OLMO = "48d788eca847d4d7548f375ad03d3c9312f6139e"
_GEMMA = "dcc83ea841ab6100d6b47a070329e1ba4cf78752"


class EligibilityError(ValueError):
    """An eligibility record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def criteria_from_failures(failures: tuple[str, ...]) -> dict[str, str]:
    """Pass every Track 4 criterion except the named failures."""
    unknown = set(failures) - set(MANDATORY)
    if unknown:
        raise EligibilityError("unknown-criterion")
    return {name: "fail" if name in failures else "pass" for name in MANDATORY}


def weighted_score(
    mandatory: dict[str, str],
    categories: dict[str, int] | None,
) -> int | None:
    """Score only a candidate that passes every mandatory criterion."""
    if set(mandatory) != set(MANDATORY):
        raise EligibilityError("mandatory-shape")
    if any(mandatory[name] != "pass" for name in MANDATORY):
        return None
    if categories is None or set(categories) != set(CATEGORY_WEIGHTS):
        raise EligibilityError("score-categories")
    total = 0
    for name, weight in CATEGORY_WEIGHTS.items():
        points = categories[name]
        if points < 0 or points > weight:
            raise EligibilityError("score-range")
        total += points
    return total


def reject_private_markers(document: dict[str, Any], error: type[EligibilityError]) -> None:
    """Reject machine identities. Publisher URLs stay in the evidence locators."""
    if _PRIVATE.search(json.dumps(document)):
        raise error("identity")


def decide_candidate_eligibility() -> dict[str, Any]:
    """Build the committed no-selection closure from the 2026-11-11 retrieval."""
    candidates = [_candidate(item) for item in _INPUTS]
    qualifying = [item for item in candidates if item["mandatoryStatus"] == "pass"]
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "selectionOutcome": "selected" if len(qualifying) == 1 else "no-selection",
        "selectedModelId": qualifying[0]["modelId"] if len(qualifying) == 1 else None,
        "scoringApplied": bool(qualifying),
        "qualifyingCandidateCount": len(qualifying),
        "locallyObservedArtifactDigests": [],
        "candidates": candidates,
    }
    return validate_candidate_eligibility(document)


def validate_candidate_eligibility(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one eligibility closure."""
    validate("candidate-eligibility-closure", document)
    reject_private_markers(document, EligibilityError)
    if document["locallyObservedArtifactDigests"] != []:
        raise EligibilityError("local-digest")
    candidates = document["candidates"]
    if [item["modelId"] for item in candidates] != list(MODEL_IDS):
        raise EligibilityError("candidate-boundary")
    qualifying = []
    for item in candidates:
        failures = [name for name in MANDATORY if item["mandatoryCriteria"][name] != "pass"]
        if item["disqualifiers"] != sorted(failures):
            raise EligibilityError("disqualifiers")
        passed = not failures
        if item["mandatoryStatus"] != ("pass" if passed else "fail"):
            raise EligibilityError("mandatory-status")
        if item["scoringEligible"] is not passed:
            raise EligibilityError("scoring-eligibility")
        if passed and not isinstance(item["weightedScore"], int):
            raise EligibilityError("weighted-score")
        if not passed and item["weightedScore"] is not None:
            raise EligibilityError("weighted-score")
        for field, criterion in _RESULT_FIELDS.items():
            expected = "pass" if item[field] == "pass" else "fail"
            if item["mandatoryCriteria"][criterion] != expected:
                raise EligibilityError("result-criterion")
        classes = {entry["evidenceClass"] for entry in item["evidence"]}
        if "authoritative" not in classes:
            raise EligibilityError("evidence-authority")
        if passed:
            qualifying.append(item)
    count = len(qualifying)
    if document["qualifyingCandidateCount"] != count:
        raise EligibilityError("qualifying-count")
    if count == 1:
        if document["selectionOutcome"] != "selected":
            raise EligibilityError("selection")
        if document["selectedModelId"] != qualifying[0]["modelId"]:
            raise EligibilityError("selection")
        if document["scoringApplied"] is not True:
            raise EligibilityError("scoring-applied")
    else:
        if (
            document["selectionOutcome"] != "no-selection"
            or document["selectedModelId"] is not None
        ):
            raise EligibilityError("selection")
        if document["scoringApplied"] is not False:
            raise EligibilityError("scoring-applied")
    if count > 1:
        raise EligibilityError("selection")
    return document


def load_candidate_eligibility(root: Path | None = None) -> dict[str, Any]:
    """Load the committed closure and require it to match the decision function."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise EligibilityError("record-type")
    document = validate_candidate_eligibility(loaded)
    if document != decide_candidate_eligibility():
        raise EligibilityError("eligibility-drift")
    return document


def _candidate(item: dict[str, Any]) -> dict[str, Any]:
    mandatory = criteria_from_failures(tuple(item["failures"]))
    failures = [name for name in MANDATORY if mandatory[name] != "pass"]
    passed = not failures
    return {
        "modelId": item["modelId"],
        "revision": item["revision"],
        "priorBlockers": list(item["priorBlockers"]),
        "weightLicenseResult": item["weightLicenseResult"],
        "codeLicenseResult": item["codeLicenseResult"],
        "commercialUseResult": item["commercialUseResult"],
        "commercialGrant": item["commercialGrant"],
        "redistributionResult": item["redistributionResult"],
        "acceptableUseResult": item["acceptableUseResult"],
        "modelCardLimitationsResult": item["modelCardLimitationsResult"],
        "remoteCodeResult": item["remoteCodeResult"],
        "officialSourceResult": item["officialSourceResult"],
        "mandatoryCriteria": mandatory,
        "mandatoryStatus": "pass" if passed else "fail",
        "scoringEligible": passed,
        "weightedScore": None,
        "disqualifiers": sorted(failures),
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


def _apply(model_id: str, revision: str) -> str:
    return f"{model_id} at {revision}"


_QWEN15_ID = MODEL_IDS[0]
_QWEN3_ID = MODEL_IDS[1]
_SMOL_ID = MODEL_IDS[2]
_OLMO_ID = MODEL_IDS[3]
_GEMMA_ID = MODEL_IDS[4]

_INPUTS: tuple[dict[str, Any], ...] = (
    {
        "modelId": _QWEN15_ID,
        "revision": _QWEN15,
        "priorBlockers": (
            "bounded-subprocess-compatibility",
            "documented-limitations",
            "no-official-onnx",
            "tokenizer-provenance",
        ),
        "failures": (
            "bounded-subprocess-compatibility",
            "documented-limitations",
            "tokenizer-provenance",
        ),
        "weightLicenseResult": "pass",
        "codeLicenseResult": "pass",
        "commercialUseResult": "pass",
        "commercialGrant": "granted",
        "redistributionResult": "pass",
        "acceptableUseResult": "pass",
        "modelCardLimitationsResult": "fail",
        "remoteCodeResult": "pass",
        "officialSourceResult": "pass",
        "conflicts": (
            _conflict(
                "published-context-length",
                "resolved",
                "Series prose says 128K. The checkpoint says 32768. Use 32768.",
            ),
            _conflict(
                "tokenizer-applicability",
                "unresolved",
                "The Apache-2.0 notice does not name tokenizer files. Weight use stays separate.",
            ),
        ),
        "evidence": (
            _evidence(
                "qwen15-readme",
                "Qwen2.5-1.5B-Instruct model card",
                (
                    "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/"
                    "989aa7980e4cf806f80c7fef2b1adb7bc71aa306/README.md"
                ),
                "Qwen Team",
                _QWEN15,
                (
                    "The pinned card states 32768 context and 8192 generation. It has "
                    "no limitations section."
                ),
                "authoritative",
                _apply(_QWEN15_ID, _QWEN15),
                "restrictive-reading",
            ),
            _evidence(
                "qwen15-license",
                "Qwen2.5-1.5B-Instruct license file",
                (
                    "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/"
                    "989aa7980e4cf806f80c7fef2b1adb7bc71aa306/LICENSE"
                ),
                "Qwen Team",
                _QWEN15,
                "The pinned LICENSE file is Apache-2.0. It does not name the tokenizer files.",
                "authoritative",
                _apply(_QWEN15_ID, _QWEN15),
                "unresolved",
            ),
            _evidence(
                "qwen15-listing",
                "Qwen2.5-1.5B-Instruct revision listing",
                (
                    "https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B-Instruct/"
                    "revision/989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
                ),
                "Qwen Team",
                _QWEN15,
                "The listing has LICENSE and tokenizer files. It has no ONNX file.",
                "authoritative",
                _apply(_QWEN15_ID, _QWEN15),
                "none",
            ),
            _evidence(
                "qwen15-blog",
                "Qwen2.5 official blog",
                "https://qwenlm.github.io/blog/qwen2.5/",
                "Qwen Team",
                None,
                "The blog assigns Apache-2.0 to this size and adds no limitations section.",
                "authoritative",
                _apply(_QWEN15_ID, _QWEN15),
                "restrictive-reading",
            ),
            _evidence(
                "qwen15-onnx-community",
                "onnx-community Qwen2.5-1.5B-Instruct",
                "https://huggingface.co/onnx-community/Qwen2.5-1.5B-Instruct",
                "onnx-community",
                None,
                "This is a community ONNX conversion, not a Qwen publication.",
                "secondary",
                _apply(_QWEN15_ID, _QWEN15),
                "rejected-unofficial",
            ),
        ),
    },
    {
        "modelId": _QWEN3_ID,
        "revision": _QWEN3,
        "priorBlockers": (
            "bounded-subprocess-compatibility",
            "documented-limitations",
            "no-official-onnx",
            "tokenizer-provenance",
        ),
        "failures": (
            "bounded-subprocess-compatibility",
            "documented-limitations",
            "tokenizer-provenance",
        ),
        "weightLicenseResult": "pass",
        "codeLicenseResult": "pass",
        "commercialUseResult": "pass",
        "commercialGrant": "not-granted",
        "redistributionResult": "pass",
        "acceptableUseResult": "pass",
        "modelCardLimitationsResult": "fail",
        "remoteCodeResult": "pass",
        "officialSourceResult": "pass",
        "conflicts": (
            _conflict(
                "qwen-research-commercial-use",
                "resolved",
                "Weight commercial use is withheld and needs a separate license.",
            ),
            _conflict(
                "published-context-length",
                "resolved",
                "Series prose says 128K. This checkpoint says 32768. Use 32768.",
            ),
            _conflict(
                "tokenizer-applicability",
                "unresolved",
                "The research license names weights. It does not name tokenizer files.",
            ),
        ),
        "evidence": (
            _evidence(
                "qwen3-readme",
                "Qwen2.5-3B-Instruct model card",
                (
                    "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/"
                    "aa8e72537993ba99e69dfaafa59ed015b17504d1/README.md"
                ),
                "Qwen Team",
                _QWEN3,
                (
                    "The pinned card names qwen-research, states 32768 context, and "
                    "has no limitations section."
                ),
                "authoritative",
                _apply(_QWEN3_ID, _QWEN3),
                "restrictive-reading",
            ),
            _evidence(
                "qwen3-license",
                "Qwen2.5-3B-Instruct research license",
                (
                    "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/"
                    "aa8e72537993ba99e69dfaafa59ed015b17504d1/LICENSE"
                ),
                "Alibaba Cloud",
                _QWEN3,
                "The research LICENSE withholds commercial weight use and omits tokenizer names.",
                "authoritative",
                _apply(_QWEN3_ID, _QWEN3),
                "unresolved",
            ),
            _evidence(
                "qwen3-listing",
                "Qwen2.5-3B-Instruct revision listing",
                (
                    "https://huggingface.co/api/models/Qwen/Qwen2.5-3B-Instruct/"
                    "revision/aa8e72537993ba99e69dfaafa59ed015b17504d1"
                ),
                "Qwen Team",
                _QWEN3,
                (
                    "The listing has LICENSE, two safetensors shards, tokenizer "
                    "files, and no ONNX file."
                ),
                "authoritative",
                _apply(_QWEN3_ID, _QWEN3),
                "none",
            ),
            _evidence(
                "qwen3-blog",
                "Qwen2.5 official blog",
                "https://qwenlm.github.io/blog/qwen2.5/",
                "Qwen Team",
                None,
                "The blog assigns this size the Qwen Research License, not Apache-2.0.",
                "authoritative",
                _apply(_QWEN3_ID, _QWEN3),
                "restrictive-reading",
            ),
        ),
    },
    {
        "modelId": _SMOL_ID,
        "revision": _SMOL,
        "priorBlockers": (
            "bounded-subprocess-compatibility",
            "converted-onnx-not-qualifying",
            "explicit-weight-use-license",
            "onnx-directory-exceeds-artifact-cap",
            "quantization-not-approved",
            "tokenizer-provenance",
        ),
        "failures": (
            "bounded-subprocess-compatibility",
            "clear-commercial-use-position",
            "clear-redistribution-position",
            "explicit-weight-use-license",
            "local-resource-fit",
            "tokenizer-provenance",
        ),
        "weightLicenseResult": "fail",
        "codeLicenseResult": "fail",
        "commercialUseResult": "unresolved",
        "commercialGrant": "unresolved",
        "redistributionResult": "unresolved",
        "acceptableUseResult": "unresolved",
        "modelCardLimitationsResult": "pass",
        "remoteCodeResult": "pass",
        "officialSourceResult": "pass",
        "conflicts": (
            _conflict(
                "weight-license-instrument",
                "unresolved",
                (
                    "The card says Apache-2.0 and the pinned tree has no LICENSE "
                    "file. Weight use stays unresolved."
                ),
            ),
            _conflict(
                "remote-code-example",
                "resolved",
                "One sample sets trust_remote_code. The pinned tree lists no Python module.",
            ),
        ),
        "evidence": (
            _evidence(
                "smol-readme",
                "SmolLM2-1.7B-Instruct model card",
                (
                    "https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct/blob/"
                    "31b70e2e869a7173562077fd711b654946d38674/README.md"
                ),
                "HuggingFaceTB",
                _SMOL,
                "The card has a limitations section. Its Apache-2.0 line is not a LICENSE file.",
                "authoritative",
                _apply(_SMOL_ID, _SMOL),
                "restrictive-reading",
            ),
            _evidence(
                "smol-listing",
                "SmolLM2-1.7B-Instruct revision listing",
                "https://huggingface.co/api/models/HuggingFaceTB/SmolLM2-1.7B-Instruct",
                "HuggingFaceTB",
                _SMOL,
                (
                    "This revision is the repository head. It lists ONNX and "
                    "tokenizer files and no LICENSE file."
                ),
                "authoritative",
                _apply(_SMOL_ID, _SMOL),
                "none",
            ),
            _evidence(
                "smol-cosmo2",
                "cosmo2 tokenizer card",
                "https://huggingface.co/api/models/HuggingFaceTB/cosmo2-tokenizer",
                "HuggingFaceTB",
                "4ce2318a3628e77279c939ed6a9f3f03034402de",
                "The cosmo2 revision has no license field and no LICENSE file.",
                "authoritative",
                _apply(_SMOL_ID, _SMOL),
                "unresolved",
            ),
        ),
    },
    {
        "modelId": _OLMO_ID,
        "revision": _OLMO,
        "priorBlockers": (
            "bounded-subprocess-compatibility",
            "explicit-weight-use-license",
            "no-official-onnx",
            "tokenizer-provenance",
        ),
        "failures": (
            "bounded-subprocess-compatibility",
            "clear-redistribution-position",
            "explicit-weight-use-license",
            "tokenizer-provenance",
        ),
        "weightLicenseResult": "fail",
        "codeLicenseResult": "fail",
        "commercialUseResult": "pass",
        "commercialGrant": "restricted",
        "redistributionResult": "unresolved",
        "acceptableUseResult": "pass",
        "modelCardLimitationsResult": "pass",
        "remoteCodeResult": "pass",
        "officialSourceResult": "pass",
        "conflicts": (
            _conflict(
                "weight-license-instrument",
                "unresolved",
                (
                    "The card says Apache-2.0 and the pinned tree has no LICENSE "
                    "file. Redistribution stays unresolved."
                ),
            ),
            _conflict(
                "research-and-educational-use",
                "resolved",
                (
                    "The card limits use to research and education. That position "
                    "controls and supplies no LICENSE file."
                ),
            ),
        ),
        "evidence": (
            _evidence(
                "olmo-readme",
                "OLMo-2-0425-1B-Instruct model card",
                (
                    "https://huggingface.co/allenai/OLMo-2-0425-1B-Instruct/blob/"
                    "48d788eca847d4d7548f375ad03d3c9312f6139e/README.md"
                ),
                "Allen Institute for AI",
                _OLMO,
                (
                    "The card states research use and limited safety training. The "
                    "tree has no LICENSE file."
                ),
                "authoritative",
                _apply(_OLMO_ID, _OLMO),
                "restrictive-reading",
            ),
            _evidence(
                "olmo-listing",
                "OLMo-2-0425-1B-Instruct revision listing",
                (
                    "https://huggingface.co/api/models/allenai/"
                    "OLMo-2-0425-1B-Instruct/revision/"
                    "48d788eca847d4d7548f375ad03d3c9312f6139e"
                ),
                "Allen Institute for AI",
                _OLMO,
                (
                    "The listing has tokenizer files and safetensors. It has no "
                    "LICENSE file and no ONNX file."
                ),
                "authoritative",
                _apply(_OLMO_ID, _OLMO),
                "none",
            ),
            _evidence(
                "olmo-dolma2",
                "dolma2 tokenizer card",
                "https://huggingface.co/api/models/allenai/dolma2-tokenizer",
                "Allen Institute for AI",
                "5292e5d6c0f40b67cc765fe41bec991cf4345b5c",
                "The dolma2 revision has no license field and no LICENSE file.",
                "authoritative",
                _apply(_OLMO_ID, _OLMO),
                "unresolved",
            ),
            _evidence(
                "olmo-responsible-use",
                "Ai2 Responsible Use Guidelines",
                "https://allenai.org/responsible-use",
                "Allen Institute for AI",
                None,
                (
                    "The card points to this page. This retrieval returned no page "
                    "body, so it closes nothing."
                ),
                "unresolved",
                _apply(_OLMO_ID, _OLMO),
                "unresolved",
            ),
        ),
    },
    {
        "modelId": _GEMMA_ID,
        "revision": _GEMMA,
        "priorBlockers": (
            "artifact-digest-capability",
            "bounded-subprocess-compatibility",
            "fully-offline-runtime-support",
            "no-official-onnx",
            "tokenizer-provenance",
        ),
        "failures": (
            "artifact-digest-capability",
            "bounded-subprocess-compatibility",
            "fully-offline-runtime-support",
            "tokenizer-provenance",
        ),
        "weightLicenseResult": "pass",
        "codeLicenseResult": "unresolved",
        "commercialUseResult": "pass",
        "commercialGrant": "restricted",
        "redistributionResult": "pass",
        "acceptableUseResult": "pass",
        "modelCardLimitationsResult": "pass",
        "remoteCodeResult": "pass",
        "officialSourceResult": "pass",
        "conflicts": (
            _conflict(
                "remote-restriction",
                "unresolved",
                "Section 3.2 reserves remote restriction. Offline runtime support stays fail.",
            ),
            _conflict(
                "tokenizer-grant",
                "unresolved",
                "The terms cover weights and parameters. They do not name a tokenizer.",
            ),
            _conflict(
                "published-context-length",
                "resolved",
                "Family prose says 128K. The 1B size is 32K tokens. Use 32768.",
            ),
            _conflict(
                "upstream-digest",
                "conflicting",
                "The listing published no accepted safetensors digest. None is stored.",
            ),
        ),
        "evidence": (
            _evidence(
                "gemma-terms",
                "Gemma terms of use",
                "https://ai.google.dev/gemma/terms",
                "Google",
                None,
                "The terms dated 2026-04-01 cover Gemma 3 weights and reserve remote restriction.",
                "authoritative",
                _apply(_GEMMA_ID, _GEMMA),
                "restrictive-reading",
            ),
            _evidence(
                "gemma-model-card",
                "Gemma 3 model card",
                "https://ai.google.dev/gemma/docs/core/model_card_3",
                "Google DeepMind",
                None,
                "The card states limitations and assigns 32K context to the 1B size.",
                "authoritative",
                _apply(_GEMMA_ID, _GEMMA),
                "restrictive-reading",
            ),
            _evidence(
                "gemma-listing",
                "gemma-3-1b-it revision listing",
                (
                    "https://huggingface.co/api/models/google/gemma-3-1b-it/revision/"
                    "dcc83ea841ab6100d6b47a070329e1ba4cf78752"
                ),
                "Google",
                _GEMMA,
                (
                    "The listing has tokenizer.model and safetensors. It has no ONNX "
                    "file and no accepted digest."
                ),
                "authoritative",
                _apply(_GEMMA_ID, _GEMMA),
                "unresolved",
            ),
            _evidence(
                "gemma-unofficial-onnx",
                "Unofficial Gemma ONNX repositories",
                "https://huggingface.co/onnx-community/gemma-3-1b-it-ONNX",
                "onnx-community",
                None,
                (
                    "onnx-community and Microsoft Gemma-3-ONNX are not Google "
                    "publications of this checkpoint."
                ),
                "secondary",
                _apply(_GEMMA_ID, _GEMMA),
                "rejected-unofficial",
            ),
        ),
    },
)
