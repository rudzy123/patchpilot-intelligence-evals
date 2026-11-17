"""Retry launches. Template compatibility finishes before a model session exists."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_inference import (
    Launcher,
    classify_execution,
    launch_child,
    measurement_limits,
)
from patchpilot_intelligence_evals.cgroup_memory import (
    ScopeSampler,
    contradictory_resident,
    parse_memory_events,
    retry_window,
)
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult, execute_hardened
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.measurement_retry_plan import empty_retry_memory
from patchpilot_intelligence_evals.template_compatibility import (
    CHAT_TEMPLATE_SHA256,
    TemplateCompatibilityError,
    render_checked,
)


class RetrySampler(ScopeSampler):
    """Sample resident counters and keep ``memory.events`` on the same row."""

    def __call__(self, pid: int, unit: str, results: Path) -> None:
        before = len(self.samples)
        super().__call__(pid, unit, results)
        if len(self.samples) == before or self.directory is None:
            return
        path = self.directory / "memory.events"
        try:
            if not path.is_file():
                return
            events = parse_memory_events(path.read_text(encoding="utf-8"))
        except OSError:
            return
        self.samples[-1]["memoryEvents"] = events


def render_phase_prompt(template: str, content: str) -> str:
    """Render one bounded prompt. This does not create a session or call Run."""
    if not content:
        raise MeasurementError("compatibility-failure")
    try:
        return render_checked(template, expected_digest=CHAT_TEMPLATE_SHA256, content=content)
    except TemplateCompatibilityError as exc:
        if exc.code == "identity-mismatch":
            raise MeasurementError("digest-mismatch") from exc
        raise MeasurementError("compatibility-failure") from exc


def launch_retry(
    config: dict[str, Any],
    *,
    approval: str,
    runtime_dir: Path,
    model_dir: Path,
    limits: Any,
    launcher: Launcher,
    executed: bool,
    inference_retry: bool = False,
    result_root: Path | None = None,
) -> tuple[dict[str, Any], bool, bool]:
    """Launch one child after the caller has rendered any chat prompt."""
    if executed and inference_retry:
        from patchpilot_intelligence_evals.inference_retry_plan import (
            require_inference_retry_approval,
        )
        from patchpilot_intelligence_evals.inference_retry_preflight import require_passed_precheck

        require_inference_retry_approval(approval)
        if launcher is execute_hardened:
            if result_root is None:
                raise MeasurementError("missing-root")
            require_passed_precheck(result_root)
    sampler: ScopeSampler = RetrySampler()
    result, observer = launch_child(
        config,
        runtime_dir=runtime_dir,
        model_dir=model_dir,
        limits=limits,
        launcher=launcher,
        sampler=sampler,
        retry_approval=None if inference_retry or not executed else approval,
        inference_retry_approval=approval if executed and inference_retry else None,
    )
    cold_warm = bool(config.get("coldWarm"))
    classified = classify_execution(result, observer, cold_warm=cold_warm)
    classified["coldMemory"] = retry_window(observer.samples, frozenset({"cold", "unmarked"}))
    if cold_warm:
        classified["warmMemory"] = retry_window(observer.samples, frozenset({"warm"}))
    else:
        classified["warmMemory"] = empty_retry_memory()
    _apply_memory_gate(classified, cold_warm=cold_warm)
    run_invoked, session_created = _flags(result)
    if not executed:
        run_invoked = False
        session_created = False
    return classified, run_invoked, session_created


def phase_limits(phase: dict[str, Any]) -> Any:
    """Use the approved resident ceiling. Address space stays a separate limit."""
    return measurement_limits(phase)


def _apply_memory_gate(classified: dict[str, Any], *, cold_warm: bool) -> None:
    if classified["exitClassification"] != "success":
        return
    required = [classified["coldMemory"]]
    if cold_warm:
        required.append(classified["warmMemory"])
    for memory in required:
        telemetry = str(memory.get("telemetry"))
        if telemetry == "oom":
            code = "oom"
        elif telemetry == "exceeded":
            code = "memory-ceiling"
        elif telemetry != "complete" or contradictory_resident(memory):
            code = "telemetry-unresolved"
        else:
            continue
        classified["exitClassification"] = code
        classified["stopCause"] = code
        classified["outputDigest"] = None
        return


def _flags(result: ExecutionResult) -> tuple[bool, bool]:
    if not result.report:
        return False, False
    try:
        loaded = json.loads(result.report.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return False, False
    if not isinstance(loaded, dict):
        return False, False
    return bool(loaded.get("runInvoked")), bool(loaded.get("modelSessionCreated"))


def repeated_token_ids(token: int, count: int) -> list[int]:
    """Build one exact repeated-token input. The count is the measurement contract."""
    if token != 574 or count not in {4096, 8192}:
        raise MeasurementError("inference-failure")
    return [token] * count
