"""Official ONNX source, external-data inventory, and path checks."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.finalist_onnx import (
    ESTABLISHED_EXTERNAL,
    FinalistOnnxError,
    decide_finalist_onnx,
    direct_path_eligible,
    load_finalist_onnx,
    validate_finalist_onnx,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root

_RECORD = "candidates/authorization/finalist-direct-onnx.json"


def test_fp32_inventory_is_official_and_unparsed() -> None:
    document = load_finalist_onnx()
    finalist = document["finalists"][0]
    assert document["graphParsed"] is False
    assert finalist["directPathEligible"] is True
    assert finalist["publisherClass"] == "official-direct"
    assert finalist["verificationPerformed"] is False
    selected = {
        item["path"]
        for item in finalist["files"]
        if item["selected"] and item["role"] == "external-data"
    }
    assert selected == set(ESTABLISHED_EXTERNAL)
    assert all(not item["selected"] for item in finalist["files"] if item["quantized"])
    assert document["locallyObservedArtifactDigests"] == []


def test_unofficial_or_incomplete_graphs_fail() -> None:
    before = (repo_root() / _RECORD).read_bytes()
    community = json.loads(json.dumps(decide_finalist_onnx()))
    community["finalists"][0]["publisherClass"] = "community"
    assert direct_path_eligible(community["finalists"][0]) is False
    with pytest.raises(FinalistOnnxError) as community_error:
        validate_finalist_onnx(community)
    assert community_error.value.code == "direct-path"
    incomplete = json.loads(json.dumps(decide_finalist_onnx()))
    files = incomplete["finalists"][0]["files"]
    incomplete["finalists"][0]["files"] = [
        item for item in files if item["path"] != "onnx/model.onnx_data_2"
    ]
    with pytest.raises(FinalistOnnxError) as inventory_error:
        validate_finalist_onnx(incomplete)
    assert inventory_error.value.code == "direct-path"
    quantized = json.loads(json.dumps(decide_finalist_onnx()))
    quantized["finalists"][0]["files"][0]["quantized"] = True
    with pytest.raises(FinalistOnnxError) as quantized_error:
        validate_finalist_onnx(quantized)
    assert quantized_error.value.code == "direct-path"
    traversed = json.loads(json.dumps(decide_finalist_onnx()))
    traversed["finalists"][0]["files"][0]["path"] = "../model.onnx"
    with pytest.raises(FinalistOnnxError) as path_error:
        validate_finalist_onnx(traversed)
    assert path_error.value.code == "direct-path"
    parsed = json.loads(json.dumps(decide_finalist_onnx()))
    parsed["finalists"][0]["graphParsed"] = True
    parsed["finalists"][0]["directPathEligible"] = False
    with pytest.raises(SchemaValidationError):
        validate_finalist_onnx(parsed)
    assert (repo_root() / _RECORD).read_bytes() == before


def test_finalist_direct_onnx_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["finalist-direct-onnx-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["directPathEligible"] is True
    assert payload["graphParsed"] is False
    assert payload["productionReady"] is False
