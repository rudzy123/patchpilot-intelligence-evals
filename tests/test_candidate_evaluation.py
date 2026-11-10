"""Complete evaluation, durable results, and comparison."""

from __future__ import annotations

import json
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.candidate_evaluation import evaluate_candidate
from patchpilot_intelligence_evals.candidate_manifest import seal_manifest
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.comparison import compare_results
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases
from patchpilot_intelligence_evals.result_store import (
    ResultStoreError,
    read_execution_result,
    write_canonical,
    write_execution_result,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate

_QUALITY = (
    "conforming",
    "unsupported-claim",
    "prompt-injection-following",
    "cross-tenant-leaking",
)
_OPERATIONAL = (
    "timeout",
    "malformed-output",
    "excessive-output",
    "nonzero-exit",
)


def _strip_volatile(result: dict[str, Any]) -> dict[str, Any]:
    import copy

    cloned = copy.deepcopy(result)
    cloned["executedAt"] = "stable"
    cloned["operatingSystem"] = "stable"
    cloned["pythonVersion"] = "stable"
    cloned["repositoryCommit"] = "stable"

    def walk(metrics: dict[str, Any]) -> None:
        for name in ("latency", "peakProcessMemory"):
            metrics[name] = {
                "numerator": 0,
                "denominator": 0,
                "status": "unmeasured",
                "value": None,
            }

    for item in cloned["perCase"]:
        walk(item["metrics"])
    for block in cloned["byCategory"].values():
        walk(block)
    walk(cloned["global"])
    return cloned


@pytest.fixture(scope="module")
def evaluation_dir(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    yield tmp_path_factory.mktemp("candidate-evaluation")


@pytest.fixture(scope="module")
def quality_results(evaluation_dir: Path) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for folder in _QUALITY:
        from patchpilot_intelligence_evals.candidate_manifest import load_manifest

        manifest = load_manifest(f"candidates/fixtures/{folder}/manifest.json")
        results[folder] = evaluate_candidate(
            manifest,
            output_dir=folder,
            output_root=evaluation_dir,
        )
    return results


@pytest.fixture(scope="module")
def operational_results(evaluation_dir: Path) -> dict[str, dict[str, Any]]:
    from patchpilot_intelligence_evals.candidate_manifest import load_manifest

    results: dict[str, dict[str, Any]] = {}
    for folder in _OPERATIONAL:
        manifest = load_manifest(f"candidates/fixtures/{folder}/manifest.json")
        timeout = 0.8 if folder == "timeout" else 15
        results[folder] = evaluate_candidate(
            manifest,
            output_dir=folder,
            output_root=evaluation_dir,
            timeout_seconds=timeout,
        )
    return results


def _failing_gates(result: dict[str, Any]) -> set[str]:
    return {name for name, gate in result["gates"].items() if gate["status"] == "fail"}


def test_conforming_complete_evaluation_uses_authorized_input(
    quality_results: dict[str, dict[str, Any]],
) -> None:
    result = quality_results["conforming"]
    assert result["complete"] is True
    assert result["caseCount"] == 24
    assert result["productionReady"] is False
    assert result["executionFailureCategories"] == []
    assert all(item["executionOutcome"] == "success" for item in result["perCase"])
    for name in (
        "affectednessOrPriorityChange",
        "citationValidity",
        "crossTenantDisclosure",
        "outputSchemaValidity",
        "promptInjectionResistance",
        "secretDisclosure",
        "unauthorizedStateMutation",
        "unsupportedFactualClaims",
    ):
        assert result["gates"][name]["status"] == "pass"
    validate("candidate-execution-result", result)


def test_faulty_fixtures_fail_only_their_added_gate(
    quality_results: dict[str, dict[str, Any]],
) -> None:
    base = _failing_gates(quality_results["conforming"])
    assert "unsupportedFactualClaims" not in base
    assert "promptInjectionResistance" not in base
    assert "crossTenantDisclosure" not in base
    unsupported = _failing_gates(quality_results["unsupported-claim"])
    injection = _failing_gates(quality_results["prompt-injection-following"])
    leaking = _failing_gates(quality_results["cross-tenant-leaking"])
    assert unsupported == base | {"unsupportedFactualClaims"}
    assert injection == base | {"promptInjectionResistance"}
    assert leaking == base | {"crossTenantDisclosure"}
    assert (
        quality_results["cross-tenant-leaking"]["gates"]["unauthorizedStateMutation"]["status"]
        == "pass"
    )


def test_operational_fixtures_are_execution_failures(
    operational_results: dict[str, dict[str, Any]],
) -> None:
    expected = {
        "timeout": "timeout",
        "malformed-output": "malformed-output",
        "excessive-output": "output-limit-exceeded",
        "nonzero-exit": "nonzero-exit",
    }
    for folder, outcome in expected.items():
        result = operational_results[folder]
        assert result["executionFailureCategories"] == [outcome]
        assert all(item["qualityScored"] is False for item in result["perCase"])
        assert result["gates"]["unauthorizedStateMutation"]["status"] == "unmeasured"
        assert result["gates"]["outputSchemaValidity"]["status"] == "unmeasured"
        assert result["productionReady"] is False


def test_results_are_stable_and_omit_prompts(
    quality_results: dict[str, dict[str, Any]],
    evaluation_dir: Path,
) -> None:
    from patchpilot_intelligence_evals.candidate_manifest import load_manifest

    manifest = load_manifest("candidates/fixtures/conforming/manifest.json")
    again = evaluate_candidate(manifest)
    first = quality_results["conforming"]
    assert first["experimentId"] == again["experimentId"]
    assert _strip_volatile(first) == _strip_volatile(again)
    stored = read_execution_result(
        f"conforming/{first['experimentId']}/candidate-execution-result.json",
        root=evaluation_dir,
    )
    text = canonical_dumps(stored)
    prompt = next(
        str(case["assistanceRequest"])
        for case in load_cases()
        if case["caseId"] == "case-inject-002"
    )
    assert prompt not in text
    assert "explanationText" not in text
    assert "assistanceRequest" not in text
    manifest_doc = (
        evaluation_dir / "conforming" / str(first["experimentId"]) / "experiment-manifest.json"
    ).read_text(encoding="utf-8")
    assert '"productionReady":false' in manifest_doc.replace(" ", "")


def test_overwrite_is_rejected_and_bytes_stay(
    quality_results: dict[str, dict[str, Any]],
    evaluation_dir: Path,
) -> None:
    result = quality_results["conforming"]
    relative = f"conforming/{result['experimentId']}/candidate-execution-result.json"
    before = (evaluation_dir / relative).read_bytes()
    with pytest.raises(ResultStoreError) as caught:
        write_execution_result("conforming", result, root=evaluation_dir)
    assert caught.value.code == "overwrite"
    assert (evaluation_dir / relative).read_bytes() == before


def test_concurrent_evaluations_keep_separate_artifacts(tmp_path: Path) -> None:
    from patchpilot_intelligence_evals.candidate_manifest import load_manifest

    manifest = load_manifest("candidates/fixtures/conforming/manifest.json")
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "marker.txt").write_text("left-marker", encoding="utf-8")
    (right / "marker.txt").write_text("right-marker", encoding="utf-8")

    def run(root: Path) -> dict[str, Any]:
        return evaluate_candidate(
            manifest,
            output_dir="evaluation",
            output_root=root,
            case_ids=("case-ground-001",),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        left_future = pool.submit(run, left)
        right_future = pool.submit(run, right)
        left_result = left_future.result()
        right_result = right_future.result()
    assert left_result["experimentId"] == right_result["experimentId"]
    assert left_result["productionReady"] is False
    assert (left / "marker.txt").read_text(encoding="utf-8") == "left-marker"
    assert (right / "marker.txt").read_text(encoding="utf-8") == "right-marker"
    left_result_path = (
        left / "evaluation" / str(left_result["experimentId"]) / "candidate-execution-result.json"
    )
    right_result_path = (
        right / "evaluation" / str(right_result["experimentId"]) / "candidate-execution-result.json"
    )
    assert left_result_path.is_file()
    assert right_result_path.is_file()
    left_bytes = left_result_path.read_bytes()
    right_bytes = right_result_path.read_bytes()
    assert b"left-marker" not in right_bytes
    assert b"right-marker" not in left_bytes
    assert b"left-marker" not in left_bytes
    assert b"right-marker" not in right_bytes
    with pytest.raises(ResultStoreError) as caught:
        evaluate_candidate(
            manifest,
            output_dir="evaluation",
            output_root=left,
            case_ids=("case-ground-001",),
        )
    assert caught.value.code == "overwrite"
    assert left_result_path.read_bytes() == left_bytes


def test_partial_execution_keeps_later_cases() -> None:
    script = "tests/candidate_scripts/partial_case.py"
    manifest = seal_manifest(
        {
            "schemaVersion": "1.0.0",
            "protocolVersion": "1.0.0",
            "candidateId": "fixture-conforming",
            "candidateVersion": "1",
            "candidateKind": "deterministic-test-double",
            "implementation": {
                "interpreter": "current-python",
                "entryPoint": script,
                "implementationPaths": [script],
            },
            "source": "original-synthetic",
            "license": "Apache-2.0",
            "permittedUse": ["offline-harness-evaluation"],
            "prohibitedUse": [
                "model-training",
                "production-decision",
                "provider-execution",
                "state-mutation",
                "tenant-analysis",
            ],
            "executionRequirements": {
                "network": "prohibited",
                "determinism": "deterministic",
                "timeoutSeconds": 15,
                "maxStdoutBytes": 65536,
                "maxStderrBytes": 16384,
                "retries": 0,
            },
            "expectedDeterminism": "deterministic",
            "networkPolicy": "prohibited",
            "dataRetention": "no-retention",
            "reviewStatus": "accepted-by-principal-systems-architect",
        }
    )
    result = evaluate_candidate(
        manifest,
        case_ids=("case-ground-001", "case-ground-002"),
        timeout_seconds=0.8,
    )
    outcomes = {item["caseId"]: item["executionOutcome"] for item in result["perCase"]}
    assert outcomes == {"case-ground-001": "success", "case-ground-002": "timeout"}
    assert result["complete"] is False
    assert result["executionFailureCategories"] == ["timeout"]


def test_invalid_manifest_and_escaped_output_are_rejected() -> None:
    from patchpilot_intelligence_evals.candidate_manifest import load_manifest

    manifest = dict(load_manifest("candidates/fixtures/conforming/manifest.json"))
    manifest["candidateKind"] = "hosted-provider"
    with pytest.raises(SchemaValidationError):
        evaluate_candidate(manifest, case_ids=("case-ground-001",))
    manifest = load_manifest("candidates/fixtures/conforming/manifest.json")
    with pytest.raises(ResultStoreError):
        evaluate_candidate(
            manifest,
            output_dir="../patchpilot/out",
            case_ids=("case-ground-001",),
        )


def test_execution_and_comparison_commands_validate_their_own_artifacts(
    quality_results: dict[str, dict[str, Any]],
    evaluation_dir: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    experiment = str(quality_results["conforming"]["experimentId"])
    execution = f"conforming/{experiment}/candidate-execution-result.json"
    comparison = compare_results(
        quality_results["conforming"],
        quality_results["unsupported-claim"],
    )
    write_canonical("comparison.json", comparison, schema_name="comparison-result", root=tmp_path)
    monkeypatch.setattr("patchpilot_intelligence_evals.cli.repo_root", lambda: evaluation_dir)
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["result-validation", "--result", execution])
    assert code == 0
    assert json.loads(buffer.getvalue())["productionReady"] is False
    assert main(["comparison-validation", "--result", execution]) == 1
    monkeypatch.setattr("patchpilot_intelligence_evals.cli.repo_root", lambda: tmp_path)
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["comparison-validation", "--result", "comparison.json"])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["artifact"] == "comparison-result"
    assert summary["productionReady"] is False
    assert main(["result-validation", "--result", "comparison.json"]) == 1
    assert main(["calibration-validation", "--result", "comparison.json"]) == 1


def test_comparison_is_deterministic_and_has_no_winner(
    quality_results: dict[str, dict[str, Any]],
) -> None:
    left = quality_results["conforming"]
    right = quality_results["unsupported-claim"]
    comparison = compare_results(left, right)
    assert comparison == compare_results(left, right)
    assert comparison["status"] == "comparable"
    assert comparison["winner"] is None
    assert comparison["productionReady"] is False
    assert comparison["gateComparison"][0]["gate"] == "crossTenantDisclosure"
    unsupported = next(
        item["rightStatus"]
        for item in comparison["gateComparison"]
        if item["gate"] == "unsupportedFactualClaims"
    )
    assert unsupported == "fail"
    changed = dict(right)
    changed["corpusDigest"] = "b" * 64
    rejected = compare_results(left, changed)
    assert rejected["status"] == "incomparable"
    assert rejected["reason"] == "corpus-digest"
    assert rejected["gateComparison"] == []
    assert rejected["winner"] is None
    missing = compare_results(left, None)
    assert missing["status"] == "missing-result"
    assert missing["reason"] == "missing-right"
    assert missing["gateComparison"] == []
