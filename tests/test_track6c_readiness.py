"""Track 6C stays not-ready. An in-memory ready path does not change the record."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest

from patchpilot_intelligence_evals.candidate_format_resolution import decide_format_resolution
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.conversion_plan import decide_conversion_plan
from patchpilot_intelligence_evals.runtime_adapter_contract import load_adapter_contract
from patchpilot_intelligence_evals.runtime_cache import load_runtime_policy
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track6c_readiness import (
    Track6CReadinessError,
    decide_track6c,
    load_track6c_readiness,
)

_RECORD = Path("candidates/authorization/track6c-readiness.json")
_NOT_READY = "TRACK 6C CONTROLLED STAGING NOT READY"
_READY = "TRACK 6C CONTROLLED STAGING READY"


def _inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        decide_format_resolution(),
        decide_conversion_plan(),
        load_adapter_contract(),
        load_runtime_policy(),
    )


def _direct_format() -> dict[str, Any]:
    document = cast(dict[str, Any], json.loads(json.dumps(decide_format_resolution())))
    family = document["families"][0]
    family["officialOnnxPresent"] = True
    family["qualifies"] = True
    family["blockers"] = []
    family["listingDigestDisposition"] = "listing-only"
    family["listingFiles"] = [
        {
            "fileName": "model.onnx",
            "byteCount": 32,
            "upstreamListingSha256": "a" * 64,
        }
    ]
    family["onnxDirectoryBytes"] = 32
    document["resolutionOutcome"] = "direct-onnx"
    document["directOnnxQualified"] = True
    return document


def test_committed_track6c_is_not_ready(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_track6c_readiness()
    assert document == decide_track6c(*_inputs())
    assert document["readinessOutcome"] == "not-ready"
    assert document["verdict"] == _NOT_READY
    assert document["selectionOutcome"] == "no-selection"
    assert document["runtimeInstallationStatus"] == "not-installed"
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["conversionStatus"] == "not-performed"
    assert document["executionStatus"] == "not-executed"
    assert document["installationAuthorized"] is False
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["locallyObservedRuntimeDigests"] == []
    assert document["locallyObservedModelArtifactDigests"] == []
    assert document["blockers"] == [
        "bounded-subprocess-compatibility",
        "conversion-not-authorized",
        "equivalence-not-measured",
        "explicit-weight-use-license",
        "no-qualifying-direct-onnx",
        "onnx-directory-exceeds-artifact-cap",
        "sources-not-independently-eligible",
        "tokenizer-provenance",
        "toolchain-not-offline-closed",
    ]
    text = json.dumps(document)
    assert "/home/" not in text
    assert "https://" not in text
    assert main(["track6c-readiness-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["readinessOutcome"] == "not-ready"
    assert summary["verdict"] == _NOT_READY
    assert summary["installationAuthorized"] is False


def test_ready_requires_every_prerequisite_and_does_not_rewrite_the_record() -> None:
    root = repo_root()
    before = (root / _RECORD).read_text(encoding="utf-8")
    _format, plan, adapter, runtime = _inputs()
    ready = decide_track6c(_direct_format(), plan, adapter, runtime)
    assert ready["readinessOutcome"] == "ready"
    assert ready["verdict"] == _READY
    assert ready["blockers"] == []
    assert ready["installationAuthorized"] is False
    assert ready["productionReady"] is False
    assert ready["realModelExecuted"] is False
    assert "conversion-not-authorized" not in ready["blockers"]
    assert (root / _RECORD).read_text(encoding="utf-8") == before
    blocked = json.loads(json.dumps(_direct_format()))
    blocked["families"][0]["blockers"] = ["tokenizer-provenance"]
    blocked["families"][0]["qualifies"] = False
    blocked["resolutionOutcome"] = "no-path"
    blocked["directOnnxQualified"] = False
    withheld = decide_track6c(blocked, plan, adapter, runtime)
    assert withheld["readinessOutcome"] == "not-ready"
    assert "tokenizer-provenance" in withheld["blockers"]
    assert "conversion-not-authorized" in withheld["blockers"]
    duplicate = _direct_format()
    second = duplicate["families"][1]
    second["officialOnnxPresent"] = True
    second["qualifies"] = True
    second["blockers"] = []
    second["listingFiles"] = [
        {
            "fileName": "model.onnx",
            "byteCount": 16,
            "upstreamListingSha256": "b" * 64,
        }
    ]
    second["onnxDirectoryBytes"] = 16
    with pytest.raises(Track6CReadinessError) as caught:
        decide_track6c(duplicate, plan, adapter, runtime)
    assert caught.value.code == "resolution-outcome"
