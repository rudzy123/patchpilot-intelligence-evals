"""Track 7 discovery universe. At most eight families, and at most four finalists.

Listing facts are upstream statements. They are not local observations.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP
from patchpilot_intelligence_evals.candidate_eligibility import (
    MODEL_IDS,
    RETRIEVED_ON,
    decide_candidate_eligibility,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/candidate-discovery.json")
_PRIVATE = re.compile(r"(?:/home/|(?:\d{1,3}\.){3}\d{1,3}|ip-26-0-174-36)")
DISCOVERY_LIMIT = 8
FINALIST_LIMIT = 4
PARAMETER_MIN = 500_000_000
PARAMETER_MAX = 3_200_000_000
CONTEXT_FLOOR = 4096
DENIED_FAMILIES = frozenset({"gemma-3", "olmo-2", "qwen2.5", "smollm2"})
PRIOR_PREFIXES = (
    "Qwen/Qwen2.5-",
    "HuggingFaceTB/SmolLM2-",
    "allenai/OLMo-2-",
    "google/gemma-3-",
)
LFM_MODEL_ID = "LiquidAI/LFM2.5-1.2B-Instruct"
LFM_FAMILY_ID = "lfm2.5"
LFM_SOURCE_REVISION = "b9d816ab510f9a28dca37cb182e9da8b0226e13c"
LFM_ONNX_REVISION = "10f72e70abf67ac0fd7ebf15bc5854726891d864"
_REASONS = (
    "artifact-cap",
    "artifact-unknown",
    "automatic-retrieval",
    "context-floor",
    "context-unknown",
    "conversion-required",
    "cpu-not-plausible",
    "direct-onnx",
    "hosted-api",
    "instruction-or-card",
    "parameter-band",
    "parameter-unknown",
    "prior-checkpoint",
    "quantization-required",
    "remote-code",
    "telemetry",
    "weight-terms-absent",
)


class DiscoveryError(ValueError):
    """A discovery record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def contains_private_marker(document: dict[str, Any]) -> bool:
    """True when a document carries a home path, IPv4 address, or known host token."""
    return _PRIVATE.search(json.dumps(document)) is not None


def evidence(
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
    """One quote-free evidence row. The revision is the retrieved immutable pin."""
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


def parameter_in_band(count: int) -> bool:
    """The session reading of approximately 0.5B to 3B parameters, inclusive."""
    return PARAMETER_MIN <= count <= PARAMETER_MAX


def exclusion_reasons(
    item: Mapping[str, Any],
    prior_ids: set[str],
    prior_revisions: set[str],
) -> list[str]:
    """Return sorted pre-screen failures. An empty list advances the family."""
    reasons: list[str] = []
    model_id = str(item["modelId"])
    family_id = str(item["familyId"])
    revision = str(item["revision"])
    if _prior(model_id, family_id, revision, prior_ids, prior_revisions):
        reasons.append("prior-checkpoint")
    count = item["parameterCount"]
    if count is None:
        reasons.append("parameter-unknown")
    elif not parameter_in_band(int(count)):
        reasons.append("parameter-band")
    context = item["contextTokens"]
    if context is None:
        reasons.append("context-unknown")
    elif int(context) < CONTEXT_FLOOR:
        reasons.append("context-floor")
    if not item["instructionCapable"] or not item["officialCard"]:
        reasons.append("instruction-or-card")
    if item["directOnnxInitial"] != "official-nonquantized":
        reasons.append("direct-onnx")
    listed = item["listedArtifactBytes"]
    if listed is None:
        reasons.append("artifact-unknown")
    elif int(listed) > ARTIFACT_CAP:
        reasons.append("artifact-cap")
    if item["conversionRequired"]:
        reasons.append("conversion-required")
    if item["quantizationRequired"]:
        reasons.append("quantization-required")
    if item["remoteCodeRequired"]:
        reasons.append("remote-code")
    if item["automaticRetrievalIndication"]:
        reasons.append("automatic-retrieval")
    if item["hostedApiRequired"]:
        reasons.append("hosted-api")
    if item["telemetryRequired"]:
        reasons.append("telemetry")
    if not item["cpuOnlyPlausible"]:
        reasons.append("cpu-not-plausible")
    if item["weightLicenseInitial"] == "absent":
        reasons.append("weight-terms-absent")
    unknown = set(reasons) - set(_REASONS)
    if unknown:
        raise DiscoveryError("reason-code")
    return sorted(reasons)


def decide_candidate_discovery() -> dict[str, Any]:
    """Build the eight-family universe and advance only families with no screen failure."""
    prior = _prior_checkpoints()
    prior_ids = {item["modelId"] for item in prior}
    prior_revisions = {item["revision"] for item in prior}
    candidates = [_screened(item, prior_ids, prior_revisions) for item in _inputs()]
    finalists = [item["modelId"] for item in candidates if item["preScreenOutcome"] == "advance"]
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "discoveryLimit": DISCOVERY_LIMIT,
        "finalistLimit": FINALIST_LIMIT,
        "parameterMinimum": PARAMETER_MIN,
        "parameterMaximum": PARAMETER_MAX,
        "contextFloorTokens": CONTEXT_FLOOR,
        "artifactCapBytes": ARTIFACT_CAP,
        "priorCheckpoints": prior,
        "deniedFamilyIds": sorted(DENIED_FAMILIES),
        "discoveryCandidateCount": len(candidates),
        "finalistCount": len(finalists),
        "finalistModelIds": finalists,
        "locallyObservedArtifactDigests": [],
        "candidates": candidates,
    }
    return validate_candidate_discovery(document)


def validate_candidate_discovery(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one discovery universe."""
    validate("candidate-discovery", document)
    if contains_private_marker(document):
        raise DiscoveryError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise DiscoveryError("local-digest")
    if document["priorCheckpoints"] != _prior_checkpoints():
        raise DiscoveryError("prior-checkpoints")
    prior_ids = {item["modelId"] for item in document["priorCheckpoints"]}
    prior_revisions = {item["revision"] for item in document["priorCheckpoints"]}
    candidates = document["candidates"]
    if len(candidates) > DISCOVERY_LIMIT or document["discoveryCandidateCount"] != len(candidates):
        raise DiscoveryError("discovery-limit")
    model_ids = [item["modelId"] for item in candidates]
    family_ids = [item["familyId"] for item in candidates]
    if len(set(model_ids)) != len(model_ids):
        raise DiscoveryError("duplicate-model")
    if len(set(family_ids)) != len(family_ids):
        raise DiscoveryError("duplicate-family")
    finalists: list[str] = []
    for item in candidates:
        reasons = exclusion_reasons(item, prior_ids, prior_revisions)
        if item["exclusionReasons"] != reasons:
            raise DiscoveryError("exclusion-reasons")
        outcome = "exclude" if reasons else "advance"
        if item["preScreenOutcome"] != outcome:
            raise DiscoveryError("pre-screen")
        if outcome == "advance":
            finalists.append(item["modelId"])
        if "prior-checkpoint" in reasons and item["priorFamilyStatus"] == "distinct":
            raise DiscoveryError("prior-status")
        if "prior-checkpoint" not in reasons and item["priorFamilyStatus"] != "distinct":
            raise DiscoveryError("prior-status")
        if not _evidence_ok(item):
            raise DiscoveryError("evidence")
    if len(finalists) > FINALIST_LIMIT:
        raise DiscoveryError("finalist-limit")
    if document["finalistModelIds"] != finalists or document["finalistCount"] != len(finalists):
        raise DiscoveryError("finalists")
    return document


def load_candidate_discovery(root: Path | None = None) -> dict[str, Any]:
    """Load the committed universe and require it to match the decision function."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise DiscoveryError("record-type")
    document = validate_candidate_discovery(loaded)
    if document != decide_candidate_discovery():
        raise DiscoveryError("discovery-drift")
    return document


def _bounded_stem(text: str, stem: str) -> bool:
    """True when the family token is present and not a prefix of a longer token."""
    start = 0
    while True:
        index = text.find(stem, start)
        if index < 0:
            return False
        end = index + len(stem)
        before = index == 0 or not text[index - 1].isalnum()
        after = end == len(text) or not text[end].isalnum()
        if before and after:
            return True
        start = index + 1


def _prior_identity(model_id: str, family_id: str) -> bool:
    """A renamed org, other size, or quantized suffix of a prior family stays excluded."""
    leaf = model_id.rsplit("/", 1)[-1].casefold()
    family = family_id.casefold()
    if any(_bounded_stem(leaf, stem) or _bounded_stem(family, stem) for stem in DENIED_FAMILIES):
        return True
    for prior in MODEL_IDS:
        name = prior.rsplit("/", 1)[-1].casefold()
        if leaf == name or leaf.startswith(f"{name}-") or leaf.startswith(f"{name}."):
            return True
    return False


def _prior(
    model_id: str, family_id: str, revision: str, prior_ids: set[str], prior_revisions: set[str]
) -> bool:
    if model_id in prior_ids or revision in prior_revisions or family_id in DENIED_FAMILIES:
        return True
    if any(model_id.startswith(prefix) for prefix in PRIOR_PREFIXES):
        return True
    if any(model_id.startswith(prior) for prior in prior_ids):
        return True
    return _prior_identity(model_id, family_id)


def _prior_checkpoints() -> list[dict[str, str]]:
    closure = decide_candidate_eligibility()
    checkpoints = [
        {"modelId": item["modelId"], "revision": item["revision"]} for item in closure["candidates"]
    ]
    if [item["modelId"] for item in checkpoints] != list(MODEL_IDS):
        raise DiscoveryError("prior-checkpoints")
    return checkpoints


def _screened(
    item: dict[str, Any], prior_ids: set[str], prior_revisions: set[str]
) -> dict[str, Any]:
    reasons = exclusion_reasons(item, prior_ids, prior_revisions)
    screened = dict(item)
    screened["exclusionReasons"] = reasons
    screened["preScreenOutcome"] = "exclude" if reasons else "advance"
    return screened


def _evidence_ok(item: dict[str, Any]) -> bool:
    allowed = {item["revision"]}
    if item["onnxRevision"] is not None:
        allowed.add(item["onnxRevision"])
    classes = set()
    for entry in item["evidence"]:
        classes.add(entry["evidenceClass"])
        if entry["applicability"] != item["modelId"]:
            return False
        if entry["retrievedOn"] != RETRIEVED_ON:
            return False
        if '"' in entry["claim"] or "'" in entry["claim"]:
            return False
        revision = entry["immutableRevision"]
        if revision is not None and revision not in allowed:
            return False
    return "authoritative" in classes


def _inputs() -> tuple[dict[str, Any], ...]:
    return (_lfm(), _smollm3(), _qwen3(), _granite(), _ministral(), _phi(), _falcon(), _apertus())


def _lfm() -> dict[str, Any]:
    model_id = LFM_MODEL_ID
    card = (
        f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/{LFM_SOURCE_REVISION}/README.md"
    )
    onnx_card = (
        "https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/"
        f"{LFM_ONNX_REVISION}/README.md"
    )
    return {
        "modelId": model_id,
        "familyId": LFM_FAMILY_ID,
        "publisher": "Liquid AI",
        "parameterCount": 1_170_340_608,
        "contextTokens": 32768,
        "instructionCapable": True,
        "officialCard": True,
        "revision": LFM_SOURCE_REVISION,
        "onnxRevision": LFM_ONNX_REVISION,
        "weightLicenseInitial": "revision-instrument",
        "tokenizerEvidenceInitial": "revision-file",
        "directOnnxInitial": "official-nonquantized",
        "listedArtifactBytes": 4_714_268_170,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": False,
        "quantizationRequired": False,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "LFM2.5 is a Liquid AI family with its own card, LFM Open License v1.0, "
            "and ONNX revision. It is not one of the five excluded checkpoints."
        ),
        "evidence": [
            evidence(
                "lfm25-card",
                "LFM2.5-1.2B-Instruct model card",
                card,
                "Liquid AI",
                LFM_SOURCE_REVISION,
                (
                    "The pinned card identifies a 1.17B instruction model with 32768 tokens "
                    "of context and names LFM Open License v1.0."
                ),
                "authoritative",
                model_id,
                "none",
            ),
            evidence(
                "lfm25-onnx-card",
                "LFM2.5-1.2B-Instruct-ONNX model card",
                onnx_card,
                "Liquid AI",
                LFM_ONNX_REVISION,
                (
                    "The publisher ONNX card maps the FP32 graph and three external-data "
                    "files. Their listed graph plus data size is 4714268170 bytes."
                ),
                "authoritative",
                model_id,
                "none",
            ),
        ],
    }


def _smollm3() -> dict[str, Any]:
    model_id = "HuggingFaceTB/SmolLM3-3B"
    revision = "a07cc9a04f16550a088caea529712d1d335b0ac1"
    onnx_revision = "583cadea149c60c0a737786f61ace5775e165d99"
    return {
        "modelId": model_id,
        "familyId": "smollm3",
        "publisher": "Hugging Face",
        "parameterCount": 3_075_098_624,
        "contextTokens": 65536,
        "instructionCapable": True,
        "officialCard": True,
        "revision": revision,
        "onnxRevision": onnx_revision,
        "weightLicenseInitial": "card-name-only",
        "tokenizerEvidenceInitial": "card-named",
        "directOnnxInitial": "official-nonquantized",
        "listedArtifactBytes": 12_334_174_552,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": False,
        "quantizationRequired": False,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "SmolLM3 is a later family with its own card, revision, and architecture name. "
            "It is not a size or quantized form of the excluded SmolLM2 checkpoint."
        ),
        "evidence": [
            evidence(
                "smollm3-card",
                "SmolLM3-3B model card",
                f"https://huggingface.co/HuggingFaceTB/SmolLM3-3B/blob/{revision}/README.md",
                "Hugging Face",
                revision,
                (
                    "The pinned card is an official SmolLM3 card. The configured context "
                    "used here is 65536 tokens. The card names Apache-2.0 without a LICENSE "
                    "file in the pinned sibling listing."
                ),
                "authoritative",
                model_id,
                "none",
            ),
            evidence(
                "smollm3-onnx-tree",
                "SmolLM3-3B-ONNX tree listing",
                (
                    "https://huggingface.co/api/models/HuggingFaceTB/SmolLM3-3B-ONNX/tree/"
                    f"{onnx_revision}/onnx"
                ),
                "Hugging Face",
                onnx_revision,
                (
                    "The pinned ONNX tree lists onnx/model.onnx_data at 12333948928 bytes. "
                    "With the graph, the non-quantized pair is 12334174552 bytes."
                ),
                "authoritative",
                model_id,
                "none",
            ),
        ],
    }


def _qwen3() -> dict[str, Any]:
    model_id = "Qwen/Qwen3-1.7B"
    revision = "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"
    return {
        "modelId": model_id,
        "familyId": "qwen3",
        "publisher": "Qwen",
        "parameterCount": 2_031_739_904,
        "contextTokens": 32768,
        "instructionCapable": True,
        "officialCard": True,
        "revision": revision,
        "onnxRevision": None,
        "weightLicenseInitial": "revision-instrument",
        "tokenizerEvidenceInitial": "revision-file",
        "directOnnxInitial": "third-party",
        "listedArtifactBytes": None,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": True,
        "quantizationRequired": False,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "Qwen3 is a later generation with its own card, LICENSE file, and revision. "
            "It is not a Qwen2.5 checkpoint."
        ),
        "evidence": [
            evidence(
                "qwen3-card",
                "Qwen3-1.7B model card",
                f"https://huggingface.co/Qwen/Qwen3-1.7B/blob/{revision}/README.md",
                "Qwen",
                revision,
                (
                    "The pinned card names a 1.7B model with 32768 tokens of context. "
                    "The safetensors listing reports 2031739904 parameters, and that higher "
                    "figure is used for the parameter screen."
                ),
                "conflicting",
                model_id,
                "restrictive-reading",
            ),
            evidence(
                "qwen3-onnx-community",
                "onnx-community Qwen3-1.7B-ONNX repository",
                "https://huggingface.co/onnx-community/Qwen3-1.7B-ONNX",
                "onnx-community",
                None,
                (
                    "The published ONNX repository is an onnx-community conversion. "
                    "The Qwen tree for this revision does not publish the ONNX graph."
                ),
                "authoritative",
                model_id,
                "rejected-unofficial",
            ),
        ],
    }


def _granite() -> dict[str, Any]:
    model_id = "ibm-granite/granite-3.3-2b-instruct"
    revision = "707f574c62054322f6b5b04b6d075f0a8f05e0f0"
    return {
        "modelId": model_id,
        "familyId": "granite-3.3",
        "publisher": "IBM",
        "parameterCount": 2_533_539_840,
        "contextTokens": 131072,
        "instructionCapable": True,
        "officialCard": True,
        "revision": revision,
        "onnxRevision": None,
        "weightLicenseInitial": "card-name-only",
        "tokenizerEvidenceInitial": "card-named",
        "directOnnxInitial": "absent",
        "listedArtifactBytes": None,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": True,
        "quantizationRequired": False,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "Granite 3.3 is an IBM family with its own card and revision. "
            "It is not one of the five excluded checkpoints."
        ),
        "evidence": [
            evidence(
                "granite-card",
                "granite-3.3-2b-instruct model card",
                (
                    "https://huggingface.co/ibm-granite/granite-3.3-2b-instruct/blob/"
                    f"{revision}/README.md"
                ),
                "IBM",
                revision,
                (
                    "The pinned card documents a 2B-class instruct model and 131072 tokens "
                    "of context. The safetensors listing reports 2533539840 parameters. "
                    "The pinned tree has no ONNX graph and no LICENSE file."
                ),
                "authoritative",
                model_id,
                "restrictive-reading",
            )
        ],
    }


def _ministral() -> dict[str, Any]:
    model_id = "mistralai/Ministral-3-3B-Instruct-2512"
    revision = "b35d4dfe56c142746f54dbd64f579faab2744308"
    onnx_revision = "e1128d389145f96bb1c3c2625cb8ca255ffa7034"
    return {
        "modelId": model_id,
        "familyId": "ministral-3",
        "publisher": "Mistral AI",
        "parameterCount": 3_849_090_048,
        "contextTokens": None,
        "instructionCapable": True,
        "officialCard": True,
        "revision": revision,
        "onnxRevision": onnx_revision,
        "weightLicenseInitial": "card-name-only",
        "tokenizerEvidenceInitial": "card-named",
        "directOnnxInitial": "official-nonquantized",
        "listedArtifactBytes": None,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": False,
        "quantizationRequired": True,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "Ministral 3 is a Mistral family with its own card and revision. "
            "The source checkpoint is a distinct multimodal release, not an excluded family."
        ),
        "evidence": [
            evidence(
                "ministral-card",
                "Ministral-3-3B-Instruct-2512 model card",
                (
                    "https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512/blob/"
                    f"{revision}/README.md"
                ),
                "Mistral AI",
                revision,
                (
                    "The pinned safetensors listing reports 3849090048 parameters, including "
                    "FP8 weights. That count is outside the approximate 3B band. Context "
                    "length was not established from the card body."
                ),
                "authoritative",
                model_id,
                "restrictive-reading",
            )
        ],
    }


def _phi() -> dict[str, Any]:
    model_id = "microsoft/Phi-4-mini-instruct"
    revision = "cfbefacb99257ffa30c83adab238a50856ac3083"
    return {
        "modelId": model_id,
        "familyId": "phi-4-mini",
        "publisher": "Microsoft",
        "parameterCount": 3_836_021_760,
        "contextTokens": 131072,
        "instructionCapable": True,
        "officialCard": True,
        "revision": revision,
        "onnxRevision": None,
        "weightLicenseInitial": "revision-instrument",
        "tokenizerEvidenceInitial": "remote-code",
        "directOnnxInitial": "official-quantized-only",
        "listedArtifactBytes": None,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": True,
        "automaticRetrievalIndication": True,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": False,
        "quantizationRequired": True,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "Phi-4-mini is a Microsoft family with its own card, MIT license, and revision. "
            "It is not one of the five excluded checkpoints."
        ),
        "evidence": [
            evidence(
                "phi-card",
                "Phi-4-mini-instruct model card",
                f"https://huggingface.co/microsoft/Phi-4-mini-instruct/blob/{revision}/README.md",
                "Microsoft",
                revision,
                (
                    "The pinned card states 3.8B parameters and 128K context. The listing "
                    "reports 3836021760 parameters. The tree contains custom modeling code "
                    "and an auto map."
                ),
                "authoritative",
                model_id,
                "none",
            ),
            evidence(
                "phi-onnx-card",
                "Phi-4-mini-instruct-onnx model card",
                "https://huggingface.co/microsoft/Phi-4-mini-instruct-onnx",
                "Microsoft",
                None,
                (
                    "The official ONNX card describes int4 CPU and GPU variants and does "
                    "not publish an unquantized graph."
                ),
                "authoritative",
                model_id,
                "none",
            ),
        ],
    }


def _falcon() -> dict[str, Any]:
    model_id = "tiiuae/Falcon3-1B-Instruct"
    revision = "28ba2251970a01dd1edc7ba7dad2eb71216ccfdf"
    return {
        "modelId": model_id,
        "familyId": "falcon3",
        "publisher": "Technology Innovation Institute",
        "parameterCount": 1_669_408_768,
        "contextTokens": None,
        "instructionCapable": True,
        "officialCard": True,
        "revision": revision,
        "onnxRevision": None,
        "weightLicenseInitial": "card-name-only",
        "tokenizerEvidenceInitial": "card-named",
        "directOnnxInitial": "third-party",
        "listedArtifactBytes": None,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": True,
        "quantizationRequired": False,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "Falcon3 is a TII family with its own card and revision. "
            "It is not one of the five excluded checkpoints."
        ),
        "evidence": [
            evidence(
                "falcon-card",
                "Falcon3-1B-Instruct model card",
                f"https://huggingface.co/tiiuae/Falcon3-1B-Instruct/blob/{revision}/README.md",
                "Technology Innovation Institute",
                revision,
                (
                    "The pinned card identifies Falcon3-1B-Instruct. Context length was not "
                    "established. The license is named through an external terms page, and "
                    "the pinned tree has no LICENSE file."
                ),
                "authoritative",
                model_id,
                "none",
            ),
            evidence(
                "falcon-onnx-community",
                "onnx-community Falcon3-1B-Instruct repository",
                "https://huggingface.co/onnx-community/Falcon3-1B-Instruct",
                "onnx-community",
                None,
                "The ONNX repository is an onnx-community conversion of the TII checkpoint.",
                "authoritative",
                model_id,
                "rejected-unofficial",
            ),
        ],
    }


def _apertus() -> dict[str, Any]:
    model_id = "swiss-ai/Apertus-v1.1-0.5B-Instruct"
    revision = "a140fd61fb57422c36a26301caea17edee799874"
    return {
        "modelId": model_id,
        "familyId": "apertus-v1.1",
        "publisher": "Swiss AI",
        "parameterCount": 572_567_080,
        "contextTokens": None,
        "instructionCapable": True,
        "officialCard": True,
        "revision": revision,
        "onnxRevision": None,
        "weightLicenseInitial": "card-name-only",
        "tokenizerEvidenceInitial": "card-named",
        "directOnnxInitial": "third-party",
        "listedArtifactBytes": None,
        "cpuOnlyPlausible": True,
        "remoteCodeRequired": False,
        "automaticRetrievalIndication": True,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "conversionRequired": True,
        "quantizationRequired": False,
        "priorFamilyStatus": "distinct",
        "materialDifference": (
            "Apertus v1.1 is a Swiss AI family with its own card and revision. "
            "It is not one of the five excluded checkpoints."
        ),
        "evidence": [
            evidence(
                "apertus-card",
                "Apertus-v1.1-0.5B-Instruct model card",
                (
                    "https://huggingface.co/swiss-ai/Apertus-v1.1-0.5B-Instruct/blob/"
                    f"{revision}/README.md"
                ),
                "Swiss AI",
                revision,
                (
                    "The safetensors listing reports 572567080 parameters. The card names "
                    "Apache-2.0 without a LICENSE file in the sibling listing. Acceptable-use "
                    "text calls for periodic retrieval of an external filter."
                ),
                "authoritative",
                model_id,
                "restrictive-reading",
            ),
            evidence(
                "apertus-onnx-community",
                "onnx-community Apertus ONNX repository",
                "https://huggingface.co/onnx-community/Apertus-v1.1-0.5B-Instruct-ONNX",
                "onnx-community",
                None,
                "The ONNX repository is an onnx-community conversion.",
                "authoritative",
                model_id,
                "rejected-unofficial",
            ),
        ],
    }
