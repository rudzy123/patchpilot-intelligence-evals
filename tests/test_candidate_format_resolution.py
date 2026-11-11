"""Direct ONNX resolution. Listing digests are not local observations."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.candidate_format_resolution import (
    FormatResolutionError,
    decide_format_resolution,
    family_qualifies,
    load_format_resolution,
    resolution_outcome,
    validate_format_resolution,
)
from patchpilot_intelligence_evals.cli import main

_CAP = 8589934592


def test_committed_resolution_has_no_qualifying_path(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_format_resolution()
    assert document == decide_format_resolution()
    assert document["resolutionOutcome"] == "no-path"
    assert document["directOnnxQualified"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["locallyObservedArtifactDigests"] == []
    assert document["installationAuthorized"] is False
    assert document["productionReady"] is False
    text = json.dumps(document)
    assert "https://" not in text
    assert "*" not in text
    assert "/home/" not in text
    families = {item["modelId"]: item for item in document["families"]}
    assert set(families) == {
        "HuggingFaceTB/SmolLM2-1.7B-Instruct",
        "Qwen/Qwen2.5-1.5B-Instruct",
        "Qwen/Qwen2.5-3B-Instruct",
        "allenai/OLMo-2-0425-1B-Instruct",
        "google/gemma-3-1b-it",
    }
    for item in families.values():
        assert item["qualifies"] is False
        assert "bounded-subprocess-compatibility" in item["blockers"]
    assert families["Qwen/Qwen2.5-1.5B-Instruct"]["officialOnnxPresent"] is False
    assert families["Qwen/Qwen2.5-3B-Instruct"]["officialOnnxPresent"] is False
    assert families["google/gemma-3-1b-it"]["listingDigestDisposition"] == "redacted"
    assert families["google/gemma-3-1b-it"]["listingFiles"] == []
    smol = families["HuggingFaceTB/SmolLM2-1.7B-Instruct"]
    sizes = {item["fileName"]: item["byteCount"] for item in smol["listingFiles"]}
    assert sizes["onnx/model.onnx"] == 165580
    assert sizes["onnx/model.onnx_data"] + sizes["onnx/model_fp16.onnx_data"] == 8944754688
    assert smol["onnxDirectoryBytes"] == 19246095294
    assert smol["onnxDirectoryBytes"] > _CAP
    assert "converted-onnx-not-qualifying" in smol["blockers"]
    assert main(["candidate-format-resolution-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["resolutionOutcome"] == "no-path"
    assert summary["directOnnxQualified"] is False
    assert summary["productionReady"] is False


def test_one_qualifying_family_is_required() -> None:
    assert family_qualifies(official_onnx=True, blockers=[]) is True
    assert family_qualifies(official_onnx=True, blockers=["tokenizer-provenance"]) is False
    assert family_qualifies(official_onnx=False, blockers=[]) is False
    assert resolution_outcome(0) == "no-path"
    assert resolution_outcome(1) == "direct-onnx"
    assert resolution_outcome(2) == "no-path"
    document = json.loads(json.dumps(decide_format_resolution()))
    document["families"][0]["qualifies"] = True
    with pytest.raises(FormatResolutionError) as caught:
        validate_format_resolution(document)
    assert caught.value.code == "family-qualifies"
