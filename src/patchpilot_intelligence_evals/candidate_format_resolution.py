"""Direct official ONNX resolution for the five existing candidate families.

Listing digests are upstream identities. They are not local observations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/candidate-format-resolution.json")
_CAP = 8589934592
_SMOL_FILES: tuple[tuple[str, int, str], ...] = (
    ("onnx/model.onnx", 165580, "c538daa78f811830dc9028aa228a63a218147ab478c0c65ef6e2d8cab532380a"),
    (
        "onnx/model.onnx_data",
        6847602688,
        "023686a59a534e45af70bc5f99ae70e592481701680591f9844fc140a3db220a",
    ),
    (
        "onnx/model_bnb4.onnx",
        1311307655,
        "ac7400ca170e6644d95d26394846d2cce8083298e8519b1df7ac1eaa0ab2b5b6",
    ),
    (
        "onnx/model_fp16.onnx",
        1326807956,
        "3d891d77661f6339f727b3188f1c21b1429a1e4e55c40d1f60f85048b00a4348",
    ),
    (
        "onnx/model_fp16.onnx_data",
        2097152000,
        "5f48c05c14ed97738f8dc5854c20c229ddc8661f43fa914085843901a4ba8740",
    ),
    (
        "onnx/model_int8.onnx",
        1714119778,
        "db5cb9057f4e7014f00c38fd9764f0103e60bb4d145ad600b7144625f0d56930",
    ),
    (
        "onnx/model_q4.onnx",
        1411969607,
        "467b7b8f62d99f184d3628d24b8d65c151e331695f6e9ea997616c4e279e9a51",
    ),
    (
        "onnx/model_q4f16.onnx",
        1108730338,
        "d94946187fb5f27579f3db4ba21fb7f7466c7cbd18956bd420d3981f75282f9c",
    ),
    (
        "onnx/model_quantized.onnx",
        1714119846,
        "b1110061268f161512c234c4d43cd9dbe61eeb1454e9b94b652edf4de55ae51c",
    ),
    (
        "onnx/model_uint8.onnx",
        1714119846,
        "b1110061268f161512c234c4d43cd9dbe61eeb1454e9b94b652edf4de55ae51c",
    ),
)


class FormatResolutionError(ValueError):
    """A format-resolution record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def family_qualifies(*, official_onnx: bool, blockers: list[str]) -> bool:
    """A family qualifies only when official ONNX exists and no blocker remains."""
    return official_onnx and not blockers


def resolution_outcome(qualified_count: int) -> str:
    """One qualifying family is a direct path. Every other count stays no-path."""
    if qualified_count == 1:
        return "direct-onnx"
    return "no-path"


def decide_format_resolution() -> dict[str, Any]:
    """Build the committed no-path decision from the pinned official listings."""
    families = [_family(item) for item in _FAMILY_INPUTS]
    qualified = sum(1 for item in families if item["qualifies"] is True)
    outcome = resolution_outcome(qualified)
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "runtimeInstalled": False,
        "modelAcquired": False,
        "realModelExecuted": False,
        "installationAuthorized": False,
        "selectionOutcome": "no-selection",
        "resolutionOutcome": outcome,
        "directOnnxQualified": outcome == "direct-onnx",
        "retrievedOn": "2026-11-10",
        "artifactCapBytes": _CAP,
        "families": families,
        "locallyObservedArtifactDigests": [],
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
        "conversionStatus": "not-performed",
    }
    return validate_format_resolution(document)


def validate_format_resolution(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one format-resolution record."""
    validate("candidate-format-resolution", document)
    if document["locallyObservedArtifactDigests"] != []:
        raise FormatResolutionError("local-digest")
    text = json.dumps(document)
    if "/home/" in text or "https://" in text or "http://" in text:
        raise FormatResolutionError("identity")
    cap = int(document["artifactCapBytes"])
    for item in document["families"]:
        blockers = list(item["blockers"])
        expected = bool(item["officialOnnxPresent"]) and not blockers
        if bool(item["qualifies"]) is not expected:
            raise FormatResolutionError("family-qualifies")
        listed = item["listingFiles"]
        total = sum(int(entry["byteCount"]) for entry in listed)
        if bool(item["officialOnnxPresent"]) is not bool(listed):
            raise FormatResolutionError("onnx-inventory")
        if listed and item["onnxDirectoryBytes"] != total:
            raise FormatResolutionError("onnx-inventory")
        if not listed and item["onnxDirectoryBytes"] is not None:
            raise FormatResolutionError("onnx-inventory")
        if bool(item["qualifies"]) and total > cap:
            raise FormatResolutionError("artifact-cap")
    qualified = [item for item in document["families"] if item["qualifies"] is True]
    if document["resolutionOutcome"] == "direct-onnx" and len(qualified) != 1:
        raise FormatResolutionError("resolution-outcome")
    if document["resolutionOutcome"] == "no-path" and qualified:
        raise FormatResolutionError("resolution-outcome")
    return document


def load_format_resolution(root: Path | None = None) -> dict[str, Any]:
    """Load the committed record and require it to match the decision function."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise FormatResolutionError("record-type")
    document = validate_format_resolution(loaded)
    if document != decide_format_resolution():
        raise FormatResolutionError("resolution-drift")
    return document


def _family(item: dict[str, Any]) -> dict[str, Any]:
    blockers = sorted(str(code) for code in item["blockers"])
    official = bool(item["officialOnnxPresent"])
    listing = [
        {
            "fileName": name,
            "byteCount": size,
            "upstreamListingSha256": digest,
        }
        for name, size, digest in item["listingFiles"]
    ]
    directory_bytes = sum(int(entry["byteCount"]) for entry in listing) if listing else None
    return {
        "modelId": item["modelId"],
        "revision": item["revision"],
        "officialOnnxPresent": official,
        "qualifies": family_qualifies(official_onnx=official, blockers=blockers),
        "onnxDirectoryBytes": directory_bytes,
        "listingDigestDisposition": item["listingDigestDisposition"],
        "listingFiles": listing,
        "blockers": blockers,
    }


_FAMILY_INPUTS: tuple[dict[str, Any], ...] = (
    {
        "modelId": "Qwen/Qwen2.5-1.5B-Instruct",
        "revision": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
        "officialOnnxPresent": False,
        "listingDigestDisposition": "not-applicable",
        "listingFiles": (),
        "blockers": (
            "bounded-subprocess-compatibility",
            "documented-limitations",
            "no-official-onnx",
        ),
    },
    {
        "modelId": "Qwen/Qwen2.5-3B-Instruct",
        "revision": "aa8e72537993ba99e69dfaafa59ed015b17504d1",
        "officialOnnxPresent": False,
        "listingDigestDisposition": "not-applicable",
        "listingFiles": (),
        "blockers": (
            "bounded-subprocess-compatibility",
            "documented-limitations",
            "no-official-onnx",
        ),
    },
    {
        "modelId": "HuggingFaceTB/SmolLM2-1.7B-Instruct",
        "revision": "31b70e2e869a7173562077fd711b654946d38674",
        "officialOnnxPresent": True,
        "listingDigestDisposition": "listing-only",
        "listingFiles": _SMOL_FILES,
        "blockers": (
            "bounded-subprocess-compatibility",
            "converted-onnx-not-qualifying",
            "explicit-weight-use-license",
            "onnx-directory-exceeds-artifact-cap",
            "onnx-graph-uninspected",
            "quantization-not-approved",
            "tokenizer-provenance",
        ),
    },
    {
        "modelId": "allenai/OLMo-2-0425-1B-Instruct",
        "revision": "48d788eca847d4d7548f375ad03d3c9312f6139e",
        "officialOnnxPresent": False,
        "listingDigestDisposition": "not-applicable",
        "listingFiles": (),
        "blockers": (
            "bounded-subprocess-compatibility",
            "explicit-weight-use-license",
            "no-official-onnx",
            "tokenizer-provenance",
        ),
    },
    {
        "modelId": "google/gemma-3-1b-it",
        "revision": "dcc83ea841ab6100d6b47a070329e1ba4cf78752",
        "officialOnnxPresent": False,
        "listingDigestDisposition": "redacted",
        "listingFiles": (),
        "blockers": (
            "artifact-digest-capability",
            "bounded-subprocess-compatibility",
            "fully-offline-runtime-support",
            "no-official-onnx",
            "tokenizer-provenance",
        ),
    },
)
