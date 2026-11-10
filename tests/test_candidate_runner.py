"""Bounded subprocess execution. These tests do not describe an OS sandbox."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.candidate_boundary import classify_candidate_path
from patchpilot_intelligence_evals.candidate_manifest import seal_manifest
from patchpilot_intelligence_evals.candidate_runner import (
    CHILD_ENV_KEYS,
    invoke_candidate,
)
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases
from patchpilot_intelligence_evals.protocol import build_request
from patchpilot_intelligence_evals.schemas import repo_root


def _case(case_id: str = "case-ground-001") -> dict[str, Any]:
    return next(item for item in load_cases() if item["caseId"] == case_id)


def _manifest(script: str) -> dict[str, Any]:
    document: dict[str, Any] = {
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
    return seal_manifest(document, repo_root())


def _invoke(script: str, *, timeout: float = 15, case_id: str = "case-ground-001") -> Any:
    case = _case(case_id)
    before_case = canonical_dumps(case)
    request = build_request(case, _manifest(script)["manifestDigest"])
    before_request = canonical_dumps(request)
    invocation = invoke_candidate(
        _manifest(script),
        request,
        timeout_seconds=timeout,
    )
    assert canonical_dumps(case) == before_case
    assert canonical_dumps(request) == before_request
    assert invocation.attempts == 1
    return invocation


def test_successful_invocation() -> None:
    invocation = _invoke("tests/candidate_scripts/success_case.py")
    assert invocation.outcome == "success"
    assert invocation.exit_code == 0
    assert invocation.parsed is not None
    assert invocation.parsed["status"] == "success"


def test_timeout_nonzero_malformed_multiple_and_limits() -> None:
    started = time.monotonic()
    timed_out = _invoke("tests/candidate_scripts/timeout_case.py", timeout=0.8)
    assert timed_out.outcome == "timeout"
    assert time.monotonic() - started < 8
    assert _invoke("tests/candidate_scripts/nonzero_case.py").outcome == "nonzero-exit"
    assert _invoke("tests/candidate_scripts/malformed_case.py").outcome == "malformed-output"
    assert _invoke("tests/candidate_scripts/multiple_case.py").outcome == "multiple-outputs"
    assert _invoke("tests/candidate_scripts/oversized_stdout.py").outcome == "output-limit-exceeded"
    assert _invoke("tests/candidate_scripts/oversized_stderr.py").outcome == "stderr-limit-exceeded"


def test_protocol_request_identity_and_schema_failures() -> None:
    assert _invoke("tests/candidate_scripts/protocol_mismatch.py").outcome == "protocol-mismatch"
    assert (
        _invoke("tests/candidate_scripts/request_id_mismatch.py").outcome == "request-id-mismatch"
    )
    assert (
        _invoke("tests/candidate_scripts/identity_mismatch.py").outcome
        == "candidate-identity-mismatch"
    )
    assert _invoke("tests/candidate_scripts/schema_invalid.py").outcome == "schema-invalid-output"


def test_environment_is_minimal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-provider-secret")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "synthetic-cloud-secret")
    invocation = _invoke("tests/candidate_scripts/env_keys.py")
    keys = set(json.loads(invocation.captured_stdout.decode("utf-8")))
    assert keys <= CHILD_ENV_KEYS
    assert "OPENAI_API_KEY" not in keys
    assert "AWS_SECRET_ACCESS_KEY" not in keys
    assert b"synthetic-provider-secret" not in invocation.captured_stdout
    assert b"synthetic-cloud-secret" not in invocation.captured_stdout


def test_shell_metacharacters_stay_in_the_argument_array(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[Any, dict[str, Any]]] = []
    real_popen = subprocess.Popen

    def spy(*args: Any, **kwargs: Any) -> Any:
        calls.append((args, kwargs))
        return real_popen(*args, **kwargs)

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.candidate_runner.subprocess.Popen",
        spy,
    )
    invocation = _invoke("tests/candidate_scripts/argv_case.py")
    assert len(calls) == 1
    argv = calls[0][0][0]
    assert calls[0][1]["shell"] is False
    assert isinstance(argv, list)
    assert argv[1:] == [
        "-m",
        "patchpilot_intelligence_evals.candidate_child",
        "tests/candidate_scripts/argv_case.py",
    ]
    reported = json.loads(invocation.captured_stdout.decode("utf-8"))
    assert len(reported) == 1
    assert reported[0].endswith("tests/candidate_scripts/argv_case.py")
    assert ";" not in reported[0]
    echo = _invoke("tests/candidate_scripts/echo_stdin.py", case_id="case-inject-002")
    assert b"$(echo pwn)" not in echo.captured_stdout
    assert b"INJECT-NORTH-0002" in echo.captured_stdout
    assert "INJECT-NORTH-0002" not in canonical_dumps(echo.public_record())


def test_working_directory_is_a_restricted_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[Path] = []
    real_popen = subprocess.Popen

    def spy(*args: Any, **kwargs: Any) -> Any:
        cwd = Path(kwargs["cwd"])
        script = cwd / "tests" / "candidate_scripts" / "cwd_case.py"
        assert script.is_file()
        assert not (cwd / "corpus").exists()
        assert not (cwd / "build").exists()
        seen.append(cwd)
        return real_popen(*args, **kwargs)

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.candidate_runner.subprocess.Popen",
        spy,
    )
    invocation = _invoke("tests/candidate_scripts/cwd_case.py")
    reported = Path(invocation.captured_stdout.decode("utf-8"))
    assert seen == [reported]
    assert reported != repo_root()


def test_candidate_boundary_hides_corpus_results_and_siblings(tmp_path: Path) -> None:
    repo = repo_root()
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    assert (
        classify_candidate_path(repo / "corpus" / "cases" / "case-ground-001.json", runtime=runtime)
        == "deny"
    )
    assert (
        classify_candidate_path(
            repo / "build" / "candidate-execution-result.json",
            runtime=runtime,
        )
        == "deny"
    )
    assert classify_candidate_path(repo.parent / "patchpilot" / "README.md", runtime=runtime) == (
        "deny"
    )
    assert (
        classify_candidate_path(
            repo.parent / "neural-from-scratch" / "README.md",
            runtime=runtime,
        )
        == "deny"
    )
    assert classify_candidate_path(runtime / "main.py", runtime=runtime) == "allow"
    invocation = _invoke("tests/candidate_scripts/boundary_probe.py")
    report = json.loads(invocation.captured_stdout.decode("utf-8"))
    for key in (
        "corpus",
        "build",
        "sibling-patchpilot",
        "sibling-neural-from-scratch",
        "load-cases",
    ):
        assert report[key] == "denied"
    assert report["relative-corpus"] == "absent"
    assert "corpus" not in report["cwd-entries"]
    assert "build" not in report["cwd-entries"]


def test_observable_network_attempt_fails() -> None:
    invocation = _invoke("tests/candidate_scripts/network_case.py")
    assert invocation.outcome == "network-policy-failure"
    assert invocation.exit_code == 86
    assert "INJECT-NORTH-0002" not in canonical_dumps(invocation.public_record())
