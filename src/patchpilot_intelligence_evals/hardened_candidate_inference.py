"""Inference-retry launches. A passing dynamic-link precheck precedes any session."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_inference import Launcher
from patchpilot_intelligence_evals.corrected_candidate_inference import launch_retry


def launch_inference(
    config: dict[str, Any],
    *,
    approval: str,
    runtime_dir: Path,
    model_dir: Path,
    result_root: Path,
    limits: Any,
    launcher: Launcher,
    executed: bool,
) -> tuple[dict[str, Any], bool, bool]:
    """Launch one verified child after the no-session precheck has passed."""
    return launch_retry(
        config,
        approval=approval,
        runtime_dir=runtime_dir,
        model_dir=model_dir,
        limits=limits,
        launcher=launcher,
        executed=executed,
        inference_retry=True,
        result_root=result_root,
    )
