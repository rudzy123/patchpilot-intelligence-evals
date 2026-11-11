"""Direct ONNX evidence rejects unofficial conversions."""

from __future__ import annotations

import json
from typing import Any

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.direct_onnx_evidence import (
    OnnxEvidenceError,
    decide_direct_onnx_evidence,
    direct_path_eligible,
    load_direct_onnx_evidence,
    nonquantized_pair_bytes,
    published_directory_bytes,
)


def test_committed_onnx_evidence(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_direct_onnx_evidence()
    assert document == decide_direct_onnx_evidence()
    assert document["graphParsed"] is False
    assert all(item["directPathEligible"] is False for item in document["families"])
    smol = document["families"][2]
    assert smol["publisherClass"] == "hosted-conversion"
    assert smol["directoryBytes"] == 19246095294
    assert published_directory_bytes() == 19246095294
    assert smol["nonquantizedPairBytes"] == 6847768268
    assert nonquantized_pair_bytes() == 6847768268
    assert smol["pairQualifies"] is False
    assert smol["externalDataComplete"] is False
    quantized = [item for item in smol["files"] if item["path"].endswith("model_quantized.onnx")]
    uint8 = [item for item in smol["files"] if item["path"].endswith("model_uint8.onnx")]
    assert quantized[0]["upstreamListingSha256"] == uint8[0]["upstreamListingSha256"]
    assert quantized[0]["byteCount"] == uint8[0]["byteCount"]
    qwen = document["families"][0]
    assert qwen["rejectedSources"][0]["publisher"] == "onnx-community"
    assert document["locallyObservedArtifactDigests"] == []
    assert main(["direct-onnx-evidence-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["directPathCount"] == 0
    assert summary["productionReady"] is False


def test_unofficial_and_incomplete_paths_fail() -> None:
    assert (
        direct_path_eligible(
            "rejected-unofficial",
            external_data_complete=True,
            graph_parsed=False,
            quantized_present=False,
            pair_qualifies=True,
        )
        is False
    )
    assert (
        direct_path_eligible(
            "hosted-conversion",
            external_data_complete=False,
            graph_parsed=False,
            quantized_present=True,
            pair_qualifies=False,
        )
        is False
    )
    assert (
        direct_path_eligible(
            "official-direct",
            external_data_complete=False,
            graph_parsed=False,
            quantized_present=False,
            pair_qualifies=False,
        )
        is False
    )
    assert (
        direct_path_eligible(
            "official-direct",
            external_data_complete=True,
            graph_parsed=True,
            quantized_present=False,
            pair_qualifies=True,
        )
        is False
    )
    document = decide_direct_onnx_evidence()
    document["families"][0]["publisherClass"] = "rejected-unofficial"
    document["families"][0]["directPathEligible"] = True
    with pytest.raises(OnnxEvidenceError) as caught:
        load_checked(document)
    assert caught.value.code == "direct-path"


def load_checked(document: dict[str, Any]) -> dict[str, Any]:
    from patchpilot_intelligence_evals.direct_onnx_evidence import validate_direct_onnx_evidence

    return validate_direct_onnx_evidence(document)
