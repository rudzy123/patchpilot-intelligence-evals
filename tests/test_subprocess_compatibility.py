"""Bounded subprocess compatibility stays fail without an official graph."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.subprocess_compatibility import (
    PROPERTIES,
    SubprocessError,
    decide_subprocess_compatibility,
    load_subprocess_compatibility,
    subprocess_compatible,
)


def test_committed_subprocess_records(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_subprocess_compatibility()
    assert document == decide_subprocess_compatibility()
    assert document["adapterId"] == "patchpilot-onnxruntime-adapter"
    assert document["immutableRevision"] == "6af1a932e2286d5c58166085d24c68783033edee"
    assert document["runtimeNoteQualifiesCandidate"] is False
    assert all(item["compatibilityOutcome"] == "fail" for item in document["families"])
    assert document["evidence"][1]["url"].endswith("/v1.31.0")
    assert main(["bounded-subprocess-compatibility-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["compatibleCount"] == 0
    assert summary["realModelExecuted"] is False


def test_runtime_note_cannot_qualify_a_missing_graph() -> None:
    passing = dict.fromkeys(PROPERTIES, "pass")
    assert subprocess_compatible(passing, False) is False
    assert subprocess_compatible(passing, True) is True
    missing = dict(passing)
    missing["verified-onnx-graph"] = "fail"
    assert subprocess_compatible(missing, True) is False
    with pytest.raises(SubprocessError) as caught:
        subprocess_compatible({"verified-onnx-graph": "pass"}, True)
    assert caught.value.code == "property-set"
