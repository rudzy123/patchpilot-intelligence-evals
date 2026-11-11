"""Synthetic runtime adapter execution.

The launcher is the hardened Track 6A boundary. The only fixture name accepted
here is the synthetic runtime adapter.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps
from patchpilot_intelligence_evals.hardened_execution import (
    HardenedExecutionError,
    allowlisted_environment,
    build_argv,
    command_uses_shell,
    execute_hardened,
)
from patchpilot_intelligence_evals.protocol import (
    ProtocolError,
    parse_candidate_stdout,
    validate_request,
)
from patchpilot_intelligence_evals.resource_controls import DEFAULT_LIMITS
from patchpilot_intelligence_evals.runtime_adapter_contract import AdapterError, require_execution
from patchpilot_intelligence_evals.runtime_artifact_verification import (
    RuntimeVerificationError,
    assert_verified_runtime_identity,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate

_FIXTURE_NAME = "synthetic_runtime_adapter.py"


def adapter_environment() -> tuple[tuple[str, str], ...]:
    """Return the only extra environment pair the launcher may set."""
    return allowlisted_environment((("ORT_DISABLE_TELEMETRY", "1"),))


def adapter_argv(arguments: tuple[str, ...] = ()) -> list[str]:
    """Build the hardened argument vector for the synthetic fixture."""
    if command_uses_shell(arguments):
        raise AdapterError("shell-rejected")
    return build_argv(
        unit="patchpilot-hadapter",
        mounts=(),
        limits=DEFAULT_LIMITS,
        arguments=arguments,
        environment=adapter_environment(),
    )


def validate_invocation(
    *,
    fixture: Path,
    request: dict[str, Any],
    execution: dict[str, Any],
    runtime_directory: Path,
    runtime_manifest: dict[str, Any],
    arguments: tuple[str, ...] = (),
) -> None:
    """Reject a protocol invocation that leaves the hardened contract.

    This path launches the synthetic fixture only. It does not accept a model
    artifact, including a verified safetensors source.
    """
    if fixture.name != _FIXTURE_NAME:
        raise AdapterError("fallback-execution")
    if command_uses_shell(arguments):
        raise AdapterError("shell-rejected")
    require_execution(execution)
    try:
        validate_request(request)
    except (ProtocolError, SchemaValidationError) as exc:
        raise AdapterError("protocol-malformed") from exc
    try:
        assert_verified_runtime_identity(runtime_directory, runtime_manifest)
    except RuntimeVerificationError as exc:
        raise AdapterError("unverified-runtime") from exc


def invoke_synthetic(
    *,
    fixture: Path,
    request: dict[str, Any],
    execution: dict[str, Any],
    runtime_directory: Path,
    runtime_manifest: dict[str, Any],
    config_dir: Path,
    arguments: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Launch the synthetic fixture once. No model directory is mounted."""
    validate_invocation(
        fixture=fixture,
        request=request,
        execution=execution,
        runtime_directory=runtime_directory,
        runtime_manifest=runtime_manifest,
        arguments=arguments,
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "execution.json").write_text(
        canonical_dumps(execution) + "\n",
        encoding="utf-8",
    )
    (config_dir / "request.json").write_text(canonical_dumps(request), encoding="utf-8")
    try:
        result = execute_hardened(
            fixture,
            arguments,
            config_dir=config_dir,
            environment=adapter_environment(),
        )
    except HardenedExecutionError as exc:
        code = (
            exc.code
            if exc.code in {"timeout", "output-limit-exceeded"}
            else "internal-harness-failure"
        )
        if exc.code == "shell":
            code = "shell-rejected"
        raise AdapterError(code) from exc
    return _interpret(result)


def _interpret(result: Any) -> dict[str, Any]:
    classification = str(result.exit_classification)
    if classification in {"timeout", "output-limit-exceeded", "internal-harness-failure"}:
        raise AdapterError(classification)
    if classification != "success":
        raise AdapterError("nonzero")
    outcome, parsed = parse_candidate_stdout(result.stdout)
    if outcome != "parsed" or parsed is None:
        raise AdapterError("protocol-malformed")
    try:
        validate("candidate-response", parsed)
    except SchemaValidationError as exc:
        raise AdapterError("protocol-malformed") from exc
    if parsed.get("status") != "unavailable":
        raise AdapterError("fallback-execution")
    return {
        "status": "ok",
        "adapterId": "patchpilot-onnxruntime-adapter",
        "adapterVersion": "1.0.0",
        "runtimeId": "onnxruntime",
        "versionTag": "v1.31.1",
        "responseStatus": parsed["status"],
        "realModelExecuted": False,
        "productionReady": False,
        "argvUsesShell": command_uses_shell(result.argv),
    }
