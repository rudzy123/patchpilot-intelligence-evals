"""Direct official ONNX evidence. Listing hashes are upstream identities only."""

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

_RECORD = Path("candidates/authorization/direct-onnx-artifacts.json")
_SMOL = "31b70e2e869a7173562077fd711b654946d38674"

SMOL_ONNX_FILES: tuple[tuple[str, int, str, str, str, bool], ...] = (
    (
        "onnx/model.onnx",
        165580,
        "c538daa78f811830dc9028aa228a63a218147ab478c0c65ef6e2d8cab532380a",
        "b69ac087826fbedefba1dbe97b9d17cf48675792",
        "graph",
        False,
    ),
    (
        "onnx/model.onnx_data",
        6847602688,
        "023686a59a534e45af70bc5f99ae70e592481701680591f9844fc140a3db220a",
        "aed3bffe07e9e2a2fc68503e0425f830ddc87a3b",
        "external-data",
        False,
    ),
    (
        "onnx/model_bnb4.onnx",
        1311307655,
        "ac7400ca170e6644d95d26394846d2cce8083298e8519b1df7ac1eaa0ab2b5b6",
        "c3ab9a75c21b830771d5b924b250c5dc724c87b4",
        "reduced-precision",
        True,
    ),
    (
        "onnx/model_fp16.onnx",
        1326807956,
        "3d891d77661f6339f727b3188f1c21b1429a1e4e55c40d1f60f85048b00a4348",
        "07b5ef0888039365fe64cd30a0d4bedcf1ccbc84",
        "reduced-precision",
        False,
    ),
    (
        "onnx/model_fp16.onnx_data",
        2097152000,
        "5f48c05c14ed97738f8dc5854c20c229ddc8661f43fa914085843901a4ba8740",
        "187b37c4f0b643f43e2c2b120fa6374e5265b163",
        "reduced-precision",
        False,
    ),
    (
        "onnx/model_int8.onnx",
        1714119778,
        "db5cb9057f4e7014f00c38fd9764f0103e60bb4d145ad600b7144625f0d56930",
        "4ea45ed05b995911304345e9d5dde087f7a7c148",
        "reduced-precision",
        True,
    ),
    (
        "onnx/model_q4.onnx",
        1411969607,
        "467b7b8f62d99f184d3628d24b8d65c151e331695f6e9ea997616c4e279e9a51",
        "cecf443db34b2f4b3df139036fbb4543845dcf55",
        "reduced-precision",
        True,
    ),
    (
        "onnx/model_q4f16.onnx",
        1108730338,
        "d94946187fb5f27579f3db4ba21fb7f7466c7cbd18956bd420d3981f75282f9c",
        "369e89655598bf48287847b0e90b4e780f6a14e2",
        "reduced-precision",
        True,
    ),
    (
        "onnx/model_quantized.onnx",
        1714119846,
        "b1110061268f161512c234c4d43cd9dbe61eeb1454e9b94b652edf4de55ae51c",
        "e06dd6dc1f43a3e2a750286d4d45846125588314",
        "reduced-precision",
        True,
    ),
    (
        "onnx/model_uint8.onnx",
        1714119846,
        "b1110061268f161512c234c4d43cd9dbe61eeb1454e9b94b652edf4de55ae51c",
        "e06dd6dc1f43a3e2a750286d4d45846125588314",
        "reduced-precision",
        True,
    ),
)


class OnnxEvidenceError(ValueError):
    """An ONNX evidence record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def published_directory_bytes() -> int:
    """Sum the upstream listing sizes. This is not a qualified footprint."""
    return sum(item[1] for item in SMOL_ONNX_FILES)


def nonquantized_pair_bytes() -> int:
    """Sum the adjacent non-quantized names. Adjacency is not a relationship."""
    return SMOL_ONNX_FILES[0][1] + SMOL_ONNX_FILES[1][1]


def direct_path_eligible(
    publisher_class: str,
    *,
    external_data_complete: bool,
    graph_parsed: bool,
    quantized_present: bool,
    pair_qualifies: bool,
) -> bool:
    """Official direct publication is required. Conversions and guesses fail."""
    return (
        publisher_class == "official-direct"
        and external_data_complete
        and not graph_parsed
        and not quantized_present
        and pair_qualifies
    )


def decide_direct_onnx_evidence() -> dict[str, Any]:
    """Build the committed direct-ONNX decisions."""
    families = [_family(item) for item in _INPUTS]
    document = _shell(families)
    return validate_direct_onnx_evidence(document)


def validate_direct_onnx_evidence(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one direct-ONNX record."""
    validate("direct-onnx-artifact", document)
    try:
        reject_private_markers(document, EligibilityError)
    except EligibilityError as exc:
        raise OnnxEvidenceError(exc.code) from exc
    if document["graphParsed"] is not False:
        raise OnnxEvidenceError("graph-parsed")
    if document["locallyObservedArtifactDigests"] != []:
        raise OnnxEvidenceError("local-digest")
    families = document["families"]
    if [item["modelId"] for item in families] != list(MODEL_IDS):
        raise OnnxEvidenceError("candidate-boundary")
    for item in families:
        quantized = any(entry["quantized"] for entry in item["files"])
        expected = direct_path_eligible(
            str(item["publisherClass"]),
            external_data_complete=bool(item["externalDataComplete"]),
            graph_parsed=False,
            quantized_present=quantized,
            pair_qualifies=bool(item["pairQualifies"]),
        )
        if item["directPathEligible"] is not expected:
            raise OnnxEvidenceError("direct-path")
        if item["publisherClass"] != "official-direct" and item["directPathEligible"]:
            raise OnnxEvidenceError("unofficial-publisher")
        if item["files"] and not item["externalDataComplete"] and item["pairQualifies"]:
            raise OnnxEvidenceError("external-data")
    return document


def load_direct_onnx_evidence(root: Path | None = None) -> dict[str, Any]:
    """Load the committed record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise OnnxEvidenceError("record-type")
    document = validate_direct_onnx_evidence(loaded)
    if document != decide_direct_onnx_evidence():
        raise OnnxEvidenceError("onnx-drift")
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
        "graphParsed": False,
        "retrievedOn": RETRIEVED_ON,
        "locallyObservedArtifactDigests": [],
        "families": families,
    }


def _files(rows: tuple[tuple[str, int, str, str, str, bool], ...]) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "role": role,
            "byteCount": size,
            "upstreamListingSha256": digest,
            "gitOid": git_oid,
            "quantized": quantized,
            "approved": False,
        }
        for path, size, digest, git_oid, role, quantized in rows
    ]


def _rejected(publisher: str, url: str, reason: str) -> dict[str, str]:
    return {"publisher": publisher, "url": url, "reason": reason}


def _evidence(
    evidence_id: str,
    source_name: str,
    url: str,
    publisher: str,
    revision: str | None,
    claim: str,
    evidence_class: str,
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
        "conflictDisposition": disposition,
    }


def _family(item: dict[str, Any]) -> dict[str, Any]:
    files = _files(item["files"])
    quantized = any(entry["quantized"] for entry in files)
    pair = bool(item["pairQualifies"])
    external = bool(item["externalDataComplete"])
    publisher = str(item["publisherClass"])
    return {
        "modelId": item["modelId"],
        "revision": item["revision"],
        "publisherClass": publisher,
        "directPathEligible": direct_path_eligible(
            publisher,
            external_data_complete=external,
            graph_parsed=False,
            quantized_present=quantized,
            pair_qualifies=pair,
        ),
        "externalDataComplete": external,
        "pairQualifies": pair,
        "directoryBytes": item["directoryBytes"],
        "nonquantizedPairBytes": item["nonquantizedPairBytes"],
        "files": files,
        "rejectedSources": list(item["rejectedSources"]),
        "evidence": list(item["evidence"]),
    }


_REVISIONS = (
    "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    "aa8e72537993ba99e69dfaafa59ed015b17504d1",
    _SMOL,
    "48d788eca847d4d7548f375ad03d3c9312f6139e",
    "dcc83ea841ab6100d6b47a070329e1ba4cf78752",
)

_INPUTS: tuple[dict[str, Any], ...] = (
    {
        "modelId": MODEL_IDS[0],
        "revision": _REVISIONS[0],
        "publisherClass": "absent",
        "externalDataComplete": False,
        "pairQualifies": False,
        "directoryBytes": None,
        "nonquantizedPairBytes": None,
        "files": (),
        "rejectedSources": (
            _rejected(
                "onnx-community",
                "https://huggingface.co/onnx-community/Qwen2.5-1.5B-Instruct",
                "Community conversion, not a Qwen publication.",
            ),
            _rejected(
                "tonythethompson",
                "https://huggingface.co/tonythethompson/Qwen2.5-1.5B-Instruct-ONNX",
                "Community conversion, not a Qwen publication.",
            ),
        ),
        "evidence": (
            _evidence(
                "qwen15-onnx-listing",
                "Qwen2.5-1.5B-Instruct revision listing",
                "https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B-Instruct/revision/"
                + _REVISIONS[0],
                "Qwen Team",
                _REVISIONS[0],
                "The official revision lists no ONNX file.",
                "authoritative",
                "none",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[1],
        "revision": _REVISIONS[1],
        "publisherClass": "absent",
        "externalDataComplete": False,
        "pairQualifies": False,
        "directoryBytes": None,
        "nonquantizedPairBytes": None,
        "files": (),
        "rejectedSources": (),
        "evidence": (
            _evidence(
                "qwen3-onnx-listing",
                "Qwen2.5-3B-Instruct revision listing",
                "https://huggingface.co/api/models/Qwen/Qwen2.5-3B-Instruct/revision/"
                + _REVISIONS[1],
                "Qwen Team",
                _REVISIONS[1],
                "The official revision lists no ONNX file. A GGUF repository is not ONNX.",
                "authoritative",
                "none",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[2],
        "revision": _SMOL,
        "publisherClass": "hosted-conversion",
        "externalDataComplete": False,
        "pairQualifies": False,
        "directoryBytes": published_directory_bytes(),
        "nonquantizedPairBytes": nonquantized_pair_bytes(),
        "files": SMOL_ONNX_FILES,
        "rejectedSources": (),
        "evidence": (
            _evidence(
                "smol-onnx-tree",
                "SmolLM2-1.7B-Instruct ONNX tree",
                "https://huggingface.co/api/models/HuggingFaceTB/"
                "SmolLM2-1.7B-Instruct/tree/" + _SMOL + "/onnx",
                "HuggingFaceTB",
                _SMOL,
                "The onnx tree is a hosted conversion. Filename adjacency is not external data.",
                "authoritative",
                "restrictive-reading",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[3],
        "revision": _REVISIONS[3],
        "publisherClass": "absent",
        "externalDataComplete": False,
        "pairQualifies": False,
        "directoryBytes": None,
        "nonquantizedPairBytes": None,
        "files": (),
        "rejectedSources": (),
        "evidence": (
            _evidence(
                "olmo-onnx-listing",
                "OLMo-2-0425-1B-Instruct revision listing",
                "https://huggingface.co/api/models/allenai/"
                "OLMo-2-0425-1B-Instruct/revision/" + _REVISIONS[3],
                "Allen Institute for AI",
                _REVISIONS[3],
                "The official revision lists no ONNX file. The GGUF repository is quantized.",
                "authoritative",
                "rejected-unofficial",
            ),
        ),
    },
    {
        "modelId": MODEL_IDS[4],
        "revision": _REVISIONS[4],
        "publisherClass": "absent",
        "externalDataComplete": False,
        "pairQualifies": False,
        "directoryBytes": None,
        "nonquantizedPairBytes": None,
        "files": (),
        "rejectedSources": (
            _rejected(
                "onnx-community",
                "https://huggingface.co/onnx-community/gemma-3-1b-it-ONNX",
                "Not a Google publication of this text checkpoint.",
            ),
            _rejected(
                "onnxruntime",
                "https://huggingface.co/onnxruntime/Gemma-3-ONNX",
                "Not a Google publication of this text checkpoint.",
            ),
        ),
        "evidence": (
            _evidence(
                "gemma-onnx-listing",
                "gemma-3-1b-it revision listing",
                "https://huggingface.co/api/models/google/gemma-3-1b-it/revision/" + _REVISIONS[4],
                "Google",
                _REVISIONS[4],
                "The official revision lists no ONNX file.",
                "authoritative",
                "none",
            ),
        ),
    },
)
