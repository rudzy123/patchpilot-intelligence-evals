"""Adapter contract checks. No runtime is installed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.corpus import load_cases
from patchpilot_intelligence_evals.hardened_execution import (
    HardenedExecutionError,
    build_argv,
)
from patchpilot_intelligence_evals.protocol import build_request
from patchpilot_intelligence_evals.resource_controls import DEFAULT_LIMITS
from patchpilot_intelligence_evals.runtime_adapter_contract import (
    AdapterError,
    execution_configuration,
    format_unavailable_response,
    load_adapter_contract,
    require_executable_onnx,
)
from patchpilot_intelligence_evals.runtime_artifact_verification import not_staged_verification
from patchpilot_intelligence_evals.synthetic_runtime_adapter import (
    adapter_argv,
    validate_invocation,
)

_DIGEST = "a" * 64


def _request() -> dict[str, object]:
    return build_request(load_cases()[0], _DIGEST)


def test_contract_stays_closed(capsys: pytest.CaptureFixture[str]) -> None:
    contract = load_adapter_contract()
    assert contract["adapterId"] == "patchpilot-onnxruntime-adapter"
    assert contract["profileId"] == "linux-bwrap-systemd-v1"
    assert contract["shell"] == "prohibited"
    assert contract["telemetry"] == "disabled"
    assert contract["automaticConversion"] == "prohibited"
    assert contract["fallbackExecution"] == "prohibited"
    assert contract["sourceModel"]["format"] == "safetensors"
    assert contract["sourceModel"]["execution"] == "prohibited"
    assert contract["executableRuntimeModel"]["format"] == "onnx"
    assert contract["executableRuntimeModel"]["state"] == "unavailable"
    assert contract["syntheticFixture"]["modelArtifact"] is False
    assert contract["realCandidateOutcome"] == "format-unavailable"
    assert "approvedModelFormat" not in contract
    assert contract["runtimeInstalled"] is False
    assert contract["productionReady"] is False
    assert "/home/" not in json.dumps(contract)
    assert main(["runtime-adapter-contract-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["adapterId"] == "patchpilot-onnxruntime-adapter"
    assert summary["executableModelFormat"] == "onnx"
    assert summary["realCandidateOutcome"] == "format-unavailable"
    assert summary["realModelExecuted"] is False


def test_adapter_argv_disables_telemetry_without_a_shell() -> None:
    argv = adapter_argv()
    assert "ORT_DISABLE_TELEMETRY" in argv
    assert argv[argv.index("ORT_DISABLE_TELEMETRY") + 1] == "1"
    assert "--clearenv" in argv
    assert "bash" not in argv
    plain = build_argv(
        unit="patchpilot-h0123456789abcdef",
        mounts=(),
        limits=DEFAULT_LIMITS,
        arguments=("ok",),
    )
    assert "ORT_DISABLE_TELEMETRY" not in plain
    with pytest.raises(HardenedExecutionError) as caught:
        build_argv(
            unit="patchpilot-h0123456789abcdef",
            mounts=(),
            limits=DEFAULT_LIMITS,
            arguments=(),
            environment=(("HOME", "/tmp"),),
        )
    assert caught.value.code == "environment"


def test_invocation_fails_closed_before_launch(tmp_path: Path) -> None:
    execution = execution_configuration()
    request = _request()
    runtime = not_staged_verification()
    with pytest.raises(AdapterError) as caught:
        validate_invocation(
            fixture=Path("other.py"),
            request=request,
            execution=execution,
            runtime_directory=tmp_path,
            runtime_manifest=runtime,
        )
    assert caught.value.code == "fallback-execution"
    with pytest.raises(AdapterError) as caught:
        validate_invocation(
            fixture=Path("synthetic_runtime_adapter.py"),
            request=request,
            execution=execution,
            runtime_directory=tmp_path,
            runtime_manifest=runtime,
            arguments=("bash", "-c", "true"),
        )
    assert caught.value.code == "shell-rejected"
    online = dict(execution)
    online["offline"] = False
    with pytest.raises(AdapterError) as caught:
        validate_invocation(
            fixture=Path("synthetic_runtime_adapter.py"),
            request=request,
            execution=online,
            runtime_directory=tmp_path,
            runtime_manifest=runtime,
        )
    assert caught.value.code == "offline-required"
    with pytest.raises(AdapterError) as caught:
        validate_invocation(
            fixture=Path("synthetic_runtime_adapter.py"),
            request=request,
            execution=execution,
            runtime_directory=tmp_path,
            runtime_manifest=runtime,
        )
    assert caught.value.code == "unverified-runtime"
    converting = dict(execution)
    converting["automaticConversion"] = True
    with pytest.raises(AdapterError) as caught:
        validate_invocation(
            fixture=Path("synthetic_runtime_adapter.py"),
            request=request,
            execution=converting,
            runtime_directory=tmp_path,
            runtime_manifest=runtime,
        )
    assert caught.value.code == "conversion-attempt"
    fallback = dict(execution)
    fallback["fallbackExecution"] = True
    with pytest.raises(AdapterError) as caught:
        validate_invocation(
            fixture=Path("synthetic_runtime_adapter.py"),
            request=request,
            execution=fallback,
            runtime_directory=tmp_path,
            runtime_manifest=runtime,
        )
    assert caught.value.code == "fallback-execution"


def test_safetensors_source_is_rejected_as_an_executable_input(tmp_path: Path) -> None:
    payload = b"synthetic-track6b-source"
    directory = tmp_path / "source"
    directory.mkdir()
    (directory / "model.safetensors").write_bytes(payload)
    manifest = {
        "artifactClass": "source-model",
        "format": "safetensors",
        "approvedFormat": "safetensors",
        "verificationState": "verified",
        "files": [
            {
                "fileName": "model.safetensors",
                "role": "source-weights",
                "expectedBytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    with pytest.raises(AdapterError) as caught:
        require_executable_onnx(directory, manifest)
    assert caught.value.code == "source-model-rejected"


def test_unverified_onnx_artifact_is_rejected(tmp_path: Path) -> None:
    graph = b"synthetic-onnx-graph\n"
    directory = tmp_path / "onnx"
    directory.mkdir()
    (directory / "model.onnx").write_bytes(graph)
    manifest = _onnx_manifest(graph, external=None)
    manifest["verificationState"] = "not-staged"
    with pytest.raises(AdapterError) as caught:
        require_executable_onnx(directory, manifest)
    assert caught.value.code == "unverified-model"


def test_missing_onnx_external_data_is_rejected(tmp_path: Path) -> None:
    graph = b"synthetic-onnx-graph\n"
    external = b"synthetic-onnx-data\n"
    directory = tmp_path / "onnx"
    directory.mkdir()
    (directory / "model.onnx").write_bytes(graph)
    with pytest.raises(AdapterError) as caught:
        require_executable_onnx(directory, _onnx_manifest(graph, external))
    assert caught.value.code == "missing-external-data"


def test_unexpected_onnx_external_data_is_rejected(tmp_path: Path) -> None:
    graph = b"synthetic-onnx-graph\n"
    directory = tmp_path / "onnx"
    directory.mkdir()
    (directory / "model.onnx").write_bytes(graph)
    (directory / "extra.onnx_data").write_bytes(b"synthetic-extra\n")
    with pytest.raises(AdapterError) as caught:
        require_executable_onnx(directory, _onnx_manifest(graph, external=None))
    assert caught.value.code == "unexpected-external-data"


def test_format_unavailable_response_is_stable_and_schema_valid() -> None:
    request_id = str(_request()["requestId"])
    first = format_unavailable_response(request_id)
    second = format_unavailable_response(request_id)
    assert first == second
    assert first["status"] == "unavailable"
    assert first["failure"]["category"] == "unavailable"
    assert first["candidateId"] == "fixture-format-unavailable"
    text = json.dumps(first)
    assert "safetensors" not in text
    assert "/home/" not in text


def _onnx_manifest(graph: bytes, external: bytes | None) -> dict[str, object]:
    files: list[dict[str, object]] = [_onnx_file("model.onnx", "onnx-graph", graph)]
    external_names: list[str] = []
    if external is not None:
        files.append(_onnx_file("model.onnx_data", "onnx-external-data", external))
        external_names.append("model.onnx_data")
    return {
        "artifactClass": "executable-runtime-model",
        "format": "onnx",
        "verificationState": "verified",
        "externalDataFiles": external_names,
        "files": files,
    }


def _onnx_file(name: str, role: str, payload: bytes) -> dict[str, object]:
    return {
        "fileName": name,
        "role": role,
        "expectedBytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
