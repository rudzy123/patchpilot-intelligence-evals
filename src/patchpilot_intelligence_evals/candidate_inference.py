"""Parent side of one verified session. This module does not call session Run."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.cgroup_memory import ScopeSampler, window
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.filesystem_policy import Mount
from patchpilot_intelligence_evals.hardened_execution import (
    ExecutionResult,
    execute_hardened,
)
from patchpilot_intelligence_evals.measurement_plan import (
    ADDRESS_SPACE_BYTES,
    MeasurementError,
    empty_memory,
    empty_timing,
)
from patchpilot_intelligence_evals.resource_controls import ResourceLimits
from patchpilot_intelligence_evals.runtime_staging import (
    RuntimeStagingError,
    logging_level_error,
    ort_api_indices,
    ort_api_version,
)
from patchpilot_intelligence_evals.track8b_records import require_reusable_plan

_FIXTURE = Path(__file__).with_name("candidate_inference_main.py")
_TOKENIZER = Path(__file__).with_name("verified_tokenizer.py")
_TEMPLATE = Path(__file__).with_name("template_compatibility.py")
_INDEX_FIELDS = {
    "allocator": "GetAllocatorWithDefaultOptions",
    "allocator_free": "AllocatorFree",
    "cast_type": "CastTypeInfoToTensorInfo",
    "cpu_memory": "CreateCpuMemoryInfo",
    "create_env": "CreateEnv",
    "create_session": "CreateSession",
    "create_session_options": "CreateSessionOptions",
    "dimensions": "GetDimensions",
    "dimensions_count": "GetDimensionsCount",
    "disable_telemetry": "DisableTelemetryEvents",
    "element_count": "GetTensorShapeElementCount",
    "element_type": "GetTensorElementType",
    "get_error": "GetErrorMessage",
    "input_count": "SessionGetInputCount",
    "input_name": "SessionGetInputName",
    "input_type": "SessionGetInputTypeInfo",
    "mutable_data": "GetTensorMutableData",
    "output_count": "SessionGetOutputCount",
    "output_name": "SessionGetOutputName",
    "output_type": "SessionGetOutputTypeInfo",
    "release_env": "ReleaseEnv",
    "release_memory": "ReleaseMemoryInfo",
    "release_options": "ReleaseSessionOptions",
    "release_session": "ReleaseSession",
    "release_tensor_info": "ReleaseTensorTypeAndShapeInfo",
    "release_type": "ReleaseTypeInfo",
    "release_value": "ReleaseValue",
    "run": "Run",
    "set_inter_op": "SetInterOpNumThreads",
    "set_intra_op": "SetIntraOpNumThreads",
    "tensor": "CreateTensorWithDataAsOrtValue",
    "tensor_shape": "GetTensorTypeAndShape",
}
GOLD_KEYS = frozenset(
    {
        "category",
        "decisiveEvidenceIds",
        "expectedCitations",
        "expectedRefusal",
        "expectedRemediationSuggestions",
        "expectedSafetyWarnings",
        "expectedUncertainty",
        "goldSupportedClaims",
        "negativeControls",
        "prohibitedClaims",
        "promptInjection",
    }
)
Launcher = Callable[..., ExecutionResult]


def child_indexes(header: str) -> dict[str, int]:
    """Map the verified header onto the child config. The header is not mounted."""
    try:
        found = ort_api_indices(header)
        indexes = {key: found[name] for key, name in _INDEX_FIELDS.items()}
        indexes["api_version"] = ort_api_version(header)
        indexes["logging_level"] = logging_level_error(header)
    except (KeyError, RuntimeStagingError) as exc:
        raise MeasurementError("unverified-dependency") from exc
    return indexes


def assert_no_gold(document: dict[str, Any]) -> None:
    """Reject a child config that carries hidden evaluation fields."""
    if GOLD_KEYS.intersection(document):
        raise MeasurementError("gold-visible")
    text = canonical_dumps(document)
    for key in GOLD_KEYS:
        if f'"{key}"' in text:
            raise MeasurementError("gold-visible")


def measurement_limits(phase: dict[str, Any]) -> ResourceLimits:
    """Build limits. ``address_space_bytes`` is not the resident ceiling."""
    return ResourceLimits(
        memory_max_bytes=MEMORY_CAP,
        tasks_max=32,
        cpu_seconds=int(phase["cpuSeconds"]),
        address_space_bytes=ADDRESS_SPACE_BYTES,
        file_size_bytes=67_108_864,
        open_files=256,
        wall_clock_seconds=float(phase["wallClockSeconds"]),
        stdout_bytes=int(phase["stdoutBytes"]),
        stderr_bytes=int(phase["stderrBytes"]),
    )


def launch_child(
    config: dict[str, Any],
    *,
    runtime_dir: Path,
    model_dir: Path,
    limits: ResourceLimits,
    launcher: Launcher = execute_hardened,
    sampler: ScopeSampler | None = None,
) -> tuple[ExecutionResult, ScopeSampler]:
    """Stage one child. The callable is replaceable in synthetic tests."""
    if launcher is execute_hardened:
        require_reusable_plan()
    assert_no_gold(config)
    public = {
        key: value
        for key, value in config.items()
        if key not in {"prompt", "promptTemplate", "request"}
    }
    reject_sensitive(public)
    observer = sampler if sampler is not None else ScopeSampler()
    config_dir = Path("/tmp") / f"patchpilot-measurement-config-{id(config)}"
    config_dir.mkdir(parents=True)
    (config_dir / "request.json").write_text(
        json.dumps(config, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    mounts = (
        Mount(str(runtime_dir), "/verified-runtime", True),
        Mount(str(model_dir), "/verified-candidate", True),
    )
    try:
        result = launcher(
            _FIXTURE,
            (),
            limits=limits,
            config_dir=config_dir,
            environment=(("ORT_DISABLE_TELEMETRY", "1"),),
            extra_mounts=mounts,
            observer=observer,
            companions=(_TOKENIZER, _TEMPLATE),
        )
    finally:
        request = config_dir / "request.json"
        if request.exists():
            request.unlink()
        config_dir.rmdir()
    return result, observer


def _report(result: ExecutionResult) -> dict[str, Any]:
    if not result.report:
        return {}
    loaded = json.loads(result.report.decode("utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("malformed-response")
    return loaded


def _network_result(report: dict[str, Any]) -> str:
    network = report.get("network")
    if not isinstance(network, dict):
        return "not-performed"
    if network.get("ipv4") == "reached" or network.get("dns") == "reached":
        return "failed"
    return "denied"


def _timing_from(report: dict[str, Any], *, warm: bool) -> dict[str, Any]:
    timing = empty_timing()
    if warm:
        timing["generationSeconds"] = _number(report.get("warmGenerationSeconds"))
        timing["loadSeconds"] = None
    else:
        timing["generationSeconds"] = _number(report.get("coldGenerationSeconds"))
        if timing["generationSeconds"] is None:
            timing["generationSeconds"] = _number(report.get("generationSeconds"))
        timing["loadSeconds"] = _number(report.get("loadSeconds"))
        timing["firstTokenSeconds"] = _number(report.get("firstTokenSeconds"))
    timing["wallSeconds"] = _number(report.get("wallSeconds"))
    return timing


def _number(value: object) -> float | None:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return float(value)
    return None


def classify_execution(
    result: ExecutionResult,
    sampler: ScopeSampler,
    *,
    cold_warm: bool,
) -> dict[str, Any]:
    """Classify one launch. Resident peak is separate from virtual size."""
    report = _report(result) if result.report else {}
    cold = window(sampler.samples, frozenset({"cold", "unmarked"}))
    warm = window(sampler.samples, frozenset({"warm"})) if cold_warm else empty_memory()
    if not cold_warm:
        warm = empty_memory()
    network = _network_result(report)
    cleanup = "failed" if result.cleanup == "failed" else "reaped"
    if result.cleanup not in {"reaped", "failed"}:
        cleanup = "failed"
    classification = _classification(result, cold, warm, network, cleanup, cold_warm)
    stop = classification if classification != "success" else None
    return {
        "cleanup": cleanup,
        "coldMemory": cold,
        "coldTiming": _timing_from(report, warm=False),
        "exitClassification": classification,
        "inputTokens": report.get("inputTokenCount"),
        "networkResult": "failed" if network == "failed" else network,
        "newTokens": report.get("newTokenCount"),
        "outputDigest": report.get("outputDigest") if classification == "success" else None,
        "stdout": result.stdout,
        "stopCause": stop,
        "warmMemory": warm,
        "warmTiming": _timing_from(report, warm=True) if cold_warm else empty_timing(),
    }


def _classification(
    result: ExecutionResult,
    cold: dict[str, Any],
    warm: dict[str, Any],
    network: str,
    cleanup: str,
    cold_warm: bool,
) -> str:
    if cleanup == "failed":
        return "cleanup-failure"
    if network == "failed" or result.return_code == 5:
        return "network-violation"
    memories = [cold, warm] if cold_warm else [cold]
    if any(item.get("telemetry") == "oom" for item in memories):
        return "oom"
    if any(item.get("telemetry") == "exceeded" for item in memories):
        return "memory-ceiling"
    if any(item.get("telemetry") != "complete" for item in memories):
        return "telemetry-unresolved"
    if result.exit_classification in {"timeout", "output-limit-exceeded", "stderr-limit-exceeded"}:
        if result.exit_classification == "timeout":
            return "timeout"
        return "excessive-output"
    if result.return_code == 6:
        return "timeout"
    if result.return_code == 2:
        return "tokenizer-failure"
    if result.return_code == 3:
        return "model-load-failure"
    if result.return_code == 4:
        return "inference-failure"
    if result.return_code == 0 and result.exit_classification == "success":
        return "success"
    if result.exit_classification == "internal-harness-failure":
        return "isolation-failure"
    return "nonzero-exit"


def output_digest(stdout: bytes) -> str | None:
    """Digest canonical stdout. Empty output has no digest."""
    if not stdout:
        return None
    return sha256_text(stdout.decode("utf-8"))
