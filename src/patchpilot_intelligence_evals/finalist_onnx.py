"""Direct official ONNX inventory for Track 7 finalists.

Byte counts and sha256 values are upstream listings. They are not local observations.
The graph is not parsed.
"""

from __future__ import annotations

import json
import posixpath
from pathlib import Path
from typing import Any, NamedTuple

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

_RECORD = Path("candidates/authorization/finalist-direct-onnx.json")
_ONNX_REPO = "LiquidAI/LFM2.5-1.2B-Instruct-ONNX"
ESTABLISHED_EXTERNAL = (
    "onnx/model.onnx_data",
    "onnx/model.onnx_data_1",
    "onnx/model.onnx_data_2",
)
_TREE = (
    "https://huggingface.co/api/models/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/tree/"
    f"{LFM_ONNX_REVISION}/onnx"
)
_CARD = (
    f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/{LFM_ONNX_REVISION}/README.md"
)
_LICENSE = (
    f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/{LFM_ONNX_REVISION}/LICENSE"
)


class ListedFile(NamedTuple):
    """One upstream file row from the pinned ONNX revision."""

    path: str
    role: str
    listed_byte_count: int
    published_sha256: str | None
    selected: bool
    quantized: bool
    reduced_precision: bool


class FinalistOnnxError(ValueError):
    """An ONNX record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


SELECTED_FILES: tuple[ListedFile, ...] = (
    ListedFile(
        "onnx/model.onnx",
        "graph",
        140810,
        "240b836266733940519db3893df325b4cfac8bb87222acbfa0f05dd8c87a6639",
        True,
        False,
        False,
    ),
    ListedFile(
        "onnx/model.onnx_data",
        "external-data",
        2063007744,
        "04339fb19070d30e0b5523dfecf21b5a469dd3056a43ccd050ce6e756f039ebe",
        True,
        False,
        False,
    ),
    ListedFile(
        "onnx/model.onnx_data_1",
        "external-data",
        2072240128,
        "cf2d2083fb09ebc8dfcdc46709ed1b9bc978dd7a08a83a6993f30c078b3e6fc5",
        True,
        False,
        False,
    ),
    ListedFile(
        "onnx/model.onnx_data_2",
        "external-data",
        578879488,
        "5817c9c46604164ef96aa9524e34422edc3ffa86e480bafbbcc80de38c0a7759",
        True,
        False,
        False,
    ),
    ListedFile("tokenizer.json", "tokenizer", 3297799, None, True, False, False),
    ListedFile("config.json", "configuration", 1599, None, True, False, False),
    ListedFile("generation_config.json", "configuration", 131, None, True, False, False),
    ListedFile("tokenizer_config.json", "configuration", 2391, None, True, False, False),
    ListedFile("chat_template.jinja", "configuration", 1783, None, True, False, False),
    ListedFile("LICENSE", "metadata", 10596, None, True, False, False),
    ListedFile("README.md", "metadata", 6508, None, True, False, False),
    ListedFile(
        "onnx/model_fp16.onnx",
        "graph",
        140027,
        "bc743b4b9ba1bbb4b2549d09045b2b78717712a72ec68ea33bee69c166610e25",
        False,
        False,
        True,
    ),
    ListedFile(
        "onnx/model_fp16.onnx_data",
        "external-data",
        2067623936,
        "dbc6b62ebc6547f80f5849d52f2e4511c0c1648984e46d71a7972534486bdeee",
        False,
        False,
        True,
    ),
    ListedFile(
        "onnx/model_fp16.onnx_data_1",
        "external-data",
        289439744,
        "3e320c36cdd1ed24e4af7f256151787128ff67a8fa36b1ff6b2c3f57edb5e6e4",
        False,
        False,
        True,
    ),
    ListedFile(
        "onnx/model_q4.onnx",
        "graph",
        183173,
        "c760a2d8be1d19c71c470ef294c1220ef85b5b3a0e31f12a363655ea7fab1d58",
        False,
        True,
        False,
    ),
    ListedFile(
        "onnx/model_q4.onnx_data",
        "external-data",
        850059264,
        "d9666c44e2acc32f06c9351f9e7c4fd66bc060d88ca8e7f954e836c6845f7488",
        False,
        True,
        False,
    ),
    ListedFile(
        "onnx/model_q4f16.onnx",
        "graph",
        182795,
        "a9986ad188200507342ac32f727aa4691edb5428b0aa8c4a9fbdf0c85a6fe667",
        False,
        True,
        True,
    ),
    ListedFile(
        "onnx/model_q4f16.onnx_data",
        "external-data",
        760279040,
        "46cfacc12941150620a3f644a5269e9baebd75d681cfa09cadeef71b8ed64ac2",
        False,
        True,
        True,
    ),
    ListedFile(
        "onnx/model_q8.onnx",
        "graph",
        188702,
        "4159fe2e86b581903f5bab107ae1f565581ffb0e0b0b88bbd37bdfb8e8147be7",
        False,
        True,
        False,
    ),
    ListedFile(
        "onnx/model_q8.onnx_data",
        "external-data",
        1768022016,
        "2f7ac1ece51cd846d36390c8eaba823bf55530ebefc0551585ae2b5afb86f779",
        False,
        True,
        False,
    ),
    ListedFile(
        "onnx/model_quantized.onnx",
        "graph",
        185703,
        "41f10dd256378c87406abda307aac9147d1a3e4f2df8d7cc15bdeac560382428",
        False,
        True,
        False,
    ),
    ListedFile(
        "onnx/model_quantized.onnx_data",
        "external-data",
        1520558080,
        "fe9d6c2ff3f8cf3383ea18e90c32e5bf1aedf68a0dfc2a0afb32ff24b4903d97",
        False,
        True,
        False,
    ),
)


def component_bytes(files: tuple[ListedFile, ...] = SELECTED_FILES) -> dict[str, int]:
    """Sum selected files by role. Unselected reduced-precision files stay out."""
    selected = [item for item in files if item.selected]

    def total(role: str) -> int:
        return sum(item.listed_byte_count for item in selected if item.role == role)

    graph = total("graph")
    external = total("external-data")
    tokenizer = total("tokenizer")
    configuration = total("configuration")
    metadata = total("metadata")
    return {
        "graphBytes": graph,
        "externalDataBytes": external,
        "tokenizerBytes": tokenizer,
        "configurationBytes": configuration,
        "metadataBytes": metadata,
        "inventoryBytes": graph + external + tokenizer + configuration + metadata,
    }


def safe_relative(path: str) -> bool:
    """Reject absolute paths, traversal, and non-normalized names."""
    if path != posixpath.normpath(path):
        return False
    if path.startswith("/") or "\\" in path:
        return False
    parts = path.split("/")
    return bool(parts) and all(part not in {"", ".", ".."} for part in parts)


def direct_path_eligible(item: dict[str, Any]) -> bool:
    """Official FP32 path only. Community, quantized, and incomplete inventories fail."""
    files = item["files"]
    selected = [entry for entry in files if entry["selected"]]
    graphs = [entry for entry in selected if entry["role"] == "graph"]
    external = [entry for entry in selected if entry["role"] == "external-data"]
    if item["publisherClass"] != "official-direct":
        return False
    if not item["externalDataComplete"] or not item["relationshipEstablished"]:
        return False
    if not item["licenseConsistent"] or item["remoteCodeRequired"]:
        return False
    if item["graphParsed"] is not False or item["runtimeCompatibility"] != "pass":
        return False
    if item["symlinkDependence"] or item["pathTraversal"]:
        return False
    if len(graphs) != 1 or {entry["path"] for entry in external} != set(ESTABLISHED_EXTERNAL):
        return False
    if any(entry["quantized"] or entry["reducedPrecision"] for entry in selected):
        return False
    if any(not safe_relative(entry["path"]) for entry in files):
        return False
    weights = graphs + external
    if any(entry["publishedSha256"] is None or entry["localDigestRequired"] for entry in weights):
        return False
    return True


def decide_finalist_onnx() -> dict[str, Any]:
    """Build the committed official-FP32 inventory for the discovery finalist."""
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
        "graphParsed": False,
        "finalists": [_lfm()],
    }
    return validate_finalist_onnx(document)


def validate_finalist_onnx(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one direct-ONNX record."""
    validate("finalist-direct-onnx", document)
    if contains_private_marker(document):
        raise FinalistOnnxError("identity")
    if document["locallyObservedArtifactDigests"] != [] or document["graphParsed"] is not False:
        raise FinalistOnnxError("local-observation")
    _require_finalist(document["finalistModelIds"])
    finalists = document["finalists"]
    if [item["modelId"] for item in finalists] != document["finalistModelIds"]:
        raise FinalistOnnxError("finalist-boundary")
    if document["finalistCount"] != len(finalists):
        raise FinalistOnnxError("finalist-count")
    for item in finalists:
        if item["graphParsed"] is not False:
            raise FinalistOnnxError("local-observation")
        if item["directPathEligible"] is not direct_path_eligible(item):
            raise FinalistOnnxError("direct-path")
        if not _files_consistent(item):
            raise FinalistOnnxError("inventory")
        if not _evidence_ok(item):
            raise FinalistOnnxError("evidence")
    return document


def load_finalist_onnx(root: Path | None = None) -> dict[str, Any]:
    """Load the committed ONNX record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise FinalistOnnxError("record-type")
    document = validate_finalist_onnx(loaded)
    if document != decide_finalist_onnx():
        raise FinalistOnnxError("onnx-drift")
    return document


def _require_finalist(model_ids: list[str] | None = None) -> None:
    expected = decide_candidate_discovery()["finalistModelIds"]
    if expected != [LFM_MODEL_ID]:
        raise FinalistOnnxError("finalist-boundary")
    if model_ids is not None and model_ids != expected:
        raise FinalistOnnxError("finalist-boundary")


def _files_consistent(item: dict[str, Any]) -> bool:
    files = item["files"]
    paths = [entry["path"] for entry in files]
    if len(paths) != len(set(paths)):
        return False
    selected_external = {
        entry["path"] for entry in files if entry["selected"] and entry["role"] == "external-data"
    }
    complete = selected_external == set(ESTABLISHED_EXTERNAL)
    if item["externalDataComplete"] is not complete:
        return False
    for entry in files:
        digest = entry["publishedSha256"]
        if digest is None and not entry["localDigestRequired"]:
            return False
        if digest is not None and entry["localDigestRequired"]:
            return False
        if digest is None and entry["transport"] != "git-blob":
            return False
        if digest is not None and entry["transport"] != "git-lfs":
            return False
        if not safe_relative(entry["path"]):
            return False
    return True


def _evidence_ok(item: dict[str, Any]) -> bool:
    allowed = {LFM_SOURCE_REVISION, LFM_ONNX_REVISION}
    ids = set()
    classes = set()
    for entry in item["evidence"]:
        ids.add(entry["evidenceId"])
        classes.add(entry["evidenceClass"])
        if entry["applicability"] != item["modelId"]:
            return False
        if '"' in entry["claim"] or "'" in entry["claim"]:
            return False
        revision = entry["immutableRevision"]
        if revision is not None and revision not in allowed:
            return False
    if "authoritative" not in classes or "lfm-onnx-readme" not in ids:
        return False
    return item["relationshipEstablished"] is True


def _file_row(item: ListedFile) -> dict[str, Any]:
    return {
        "path": item.path,
        "role": item.role,
        "listedByteCount": item.listed_byte_count,
        "publishedSha256": item.published_sha256,
        "localDigestRequired": item.published_sha256 is None,
        "selected": item.selected,
        "quantized": item.quantized,
        "reducedPrecision": item.reduced_precision,
        "transport": "git-lfs" if item.published_sha256 else "git-blob",
    }


def _lfm() -> dict[str, Any]:
    files = [_file_row(item) for item in SELECTED_FILES]
    row: dict[str, Any] = {
        "modelId": LFM_MODEL_ID,
        "sourceRevision": LFM_SOURCE_REVISION,
        "onnxRevision": LFM_ONNX_REVISION,
        "onnxRepository": _ONNX_REPO,
        "publisher": "Liquid AI",
        "publisherClass": "official-direct",
        "modelRelationship": "exact-family",
        "licenseName": "LFM Open License v1.0",
        "licenseConsistent": True,
        "remoteCodeRequired": False,
        "runtimeCompatibility": "pass",
        "opsetStated": False,
        "graphParsed": False,
        "symlinkDependence": False,
        "pathTraversal": False,
        "externalDataComplete": True,
        "relationshipEstablished": True,
        "verificationPerformed": False,
        "files": files,
        "evidence": [
            evidence(
                "lfm-onnx-readme",
                "LFM2.5 ONNX model card",
                _CARD,
                "Liquid AI",
                LFM_ONNX_REVISION,
                (
                    "The pinned card maps model.onnx to FP32 weights in model.onnx_data, "
                    "model.onnx_data_1, and model.onnx_data_2, and shows an ONNX Runtime "
                    "session example. It does not state an opset."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "restrictive-reading",
            ),
            evidence(
                "lfm-onnx-tree",
                "LFM2.5 ONNX tree listing",
                _TREE,
                "Liquid AI",
                LFM_ONNX_REVISION,
                (
                    "The pinned tree is the source for every recorded byte count and "
                    "published sha256. Files without a published sha256 require a future "
                    "local digest. Reduced-precision and quantized files are not selected."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "none",
            ),
            evidence(
                "lfm-onnx-license",
                "LFM2.5 ONNX LICENSE file",
                _LICENSE,
                "Liquid AI",
                LFM_ONNX_REVISION,
                (
                    "The pinned ONNX revision contains LFM Open License v1.0, the same "
                    "instrument as the source revision, including the 10000000 USD "
                    "commercial condition."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "none",
            ),
        ],
    }
    row["directPathEligible"] = direct_path_eligible(row)
    return row
