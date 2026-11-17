"""Closed Track 8B-R2 corrections. They do not call Run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.inference_behavioral_measurement import record_sealed_or_orphan
from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan
from patchpilot_intelligence_evals.result_store import ResultStoreError
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track8b_r2_records import (
    HEADROOM_BYTES,
    PLAN_DIGEST,
    confirm_completed_runs,
    load_behavioral_interpretation,
    load_memory_conclusion,
    load_plan_disposition,
    load_schema_forensics,
)

_RESULT_ROOT = Path("/var/tmp/patchpilot-evals-track8b-r2")


def test_forensic_authority_is_unresolved_without_stdout() -> None:
    document = load_schema_forensics()
    assert document["authorityCounts"] == {
        "adapter": 0,
        "candidate-output": 0,
        "evaluator": 0,
        "protocol": 0,
        "unresolved": 15,
    }
    assert document["schemaErrorCounts"] == {"unavailable": 15}
    assert document["repetitionsAgree"] is True
    assert document["sameMalformedShape"] == "unresolved"
    assert document["anyCandidateOutputValid"] is False
    assert document["candidateCharacterizedAsSchemaNoncompliant"] is False
    assert document["correctableWithoutContractChange"] is False
    assert document["correctionBlocker"] == "raw-output-not-retained"
    assert len(document["runs"]) == 15
    assert {row["failureAuthority"] for row in document["runs"]} == {"unresolved"}
    assert {row["rawOutputDigest"] for row in document["runs"]} == {None}
    if _RESULT_ROOT.is_dir():
        confirm_completed_runs(_RESULT_ROOT)


def test_behavioral_interpretation_is_partial() -> None:
    document = load_behavioral_interpretation()
    assert document["behavioralMeasurementAttempted"] is True
    assert document["behavioralMeasurementCompleted"] is False
    assert document["behavioralConclusion"] == "partial-inconclusive"
    assert document["candidateMetricsProduced"] is False
    assert document["candidateEvaluatedCompletely"] is False
    assert document["completedRunRecords"] == 15
    assert document["casesWithoutResults"] == 19
    assert document["summaryStop"] == "telemetry-unresolved"
    assert document["comparisonWinner"] is None
    assert document["comparisonStatus"] == "not-executed"
    assert document["percentageGatesCalibrated"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["productionReady"] is False


def test_memory_headroom_is_exact() -> None:
    document = load_memory_conclusion()
    assert document["ceilingBytes"] - document["warm8192PeakBytes"] == HEADROOM_BYTES
    assert document["minimumHeadroomBytes"] == HEADROOM_BYTES
    assert document["cold4096PeakBytes"] == 7_284_371_456
    assert document["warm4096PeakBytes"] == 8_511_131_648
    assert document["cold8192PeakBytes"] == 9_816_231_936
    assert document["warm8192PeakBytes"] == 12_271_669_248
    assert document["memoryConclusion"] == "within-ceiling"
    assert document["headroomAssessment"] == "limited"
    assert document["oom"] is False
    assert document["cgroupPeakEvidence"] == "complete"
    assert document["warmRss"] == "unavailable"
    assert document["oneCandidateProcess"] == "mandatory"
    assert document["productionCapacityEvidence"] is False


def test_r2_plan_is_consumed_without_an_r3_digest() -> None:
    document = load_plan_disposition()
    assert document["planDigest"] == PLAN_DIGEST
    assert document["planDisposition"] == "consumed"
    assert document["reusable"] is False
    assert document["replacementPlanDigest"] == "not-issued"
    assert document["r3Plan"] == "not-issued"
    names = [path.name for path in (repo_root() / "candidates" / "authorization").glob("*r3*")]
    assert names == []


def test_unsealed_output_is_retained_and_not_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = load_inference_plan()
    (tmp_path / "dynamic-link-precheck.json").write_text(
        json.dumps({"identityDigest": "ab" * 32}),
        encoding="utf-8",
    )

    def fail(*_args: object, **_kwargs: object) -> None:
        raise ResultStoreError("overwrite")

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.inference_behavioral_measurement.seal_launch",
        fail,
    )
    first = b'{"status":"success"}'
    second = b'{"status":"success","extra":1}'
    assert _record(tmp_path, plan, repetition=1, stdout=first) == "unclassified"
    assert _record(tmp_path, plan, repetition=2, stdout=second) == "unclassified"
    names = sorted(path.name for path in (tmp_path / "runs").iterdir())
    assert names == [
        "case-contra-001-r1-unclassified.json",
        "case-contra-001-r2-unclassified.json",
    ]
    saved = json.loads((tmp_path / "runs" / names[0]).read_text(encoding="utf-8"))
    assert saved["outputByteCount"] == len(first)
    assert saved["outputDigest"] == hashlib.sha256(first).hexdigest()
    assert saved["recordKind"] == "unclassified-launch"
    assert first.decode("utf-8") not in (tmp_path / "runs" / names[0]).read_text(encoding="utf-8")


def test_empty_output_is_not_invented(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plan = load_inference_plan()

    def fail(*_args: object, **_kwargs: object) -> None:
        raise ResultStoreError("overwrite")

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.inference_behavioral_measurement.seal_launch",
        fail,
    )
    with pytest.raises(ResultStoreError):
        _record(tmp_path, plan, repetition=1, stdout=b"")
    assert not (tmp_path / "runs").exists()


def _record(root: Path, plan: dict[str, Any], *, repetition: int, stdout: bytes) -> str:
    return record_sealed_or_orphan(
        root=root,
        relative=f"runs/case-contra-001-r{repetition}.json",
        record={"schemaVersion": "1.0.0"},
        schema_name="inference-retry-behavioral-run",
        stdout=stdout,
        plan=plan,
        case_id="case-contra-001",
        repetition=repetition,
        executed=False,
        run_invoked=False,
        session_created=False,
    )
