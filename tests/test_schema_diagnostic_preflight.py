"""Preflight stays short of Run and rejects an unsafe root."""

from __future__ import annotations

from pathlib import Path

from patchpilot_intelligence_evals.schema_diagnostic_plan import load_schema_diagnostic_plan
from patchpilot_intelligence_evals.schema_diagnostic_preflight import (
    load_preflight_template,
    run_schema_diagnostic_preflight,
)


def test_committed_preflight_has_not_executed() -> None:
    document = load_preflight_template()
    assert document["preflightStatus"] == "not-executed"
    assert document["runInvoked"] is False
    assert document["modelSessionCreated"] is False
    assert document["realModelExecuted"] is False
    assert document["resultRootValidated"] is False
    assert len(document["runs"]) == 6


def test_probe_failure_stops_before_a_case(tmp_path: Path) -> None:
    root = tmp_path / "preflight-root"
    root.mkdir(mode=0o700)
    failed = run_schema_diagnostic_preflight(
        tmp_path / "runtime",
        tmp_path / "model",
        root,
        bind=False,
        probe=lambda _path: "failed",
    )
    assert failed["preflightStatus"] == "failed"
    assert failed["dynamicLinkStatus"] == "failed"
    assert failed["runInvoked"] is False
    assert failed["modelSessionCreated"] is False
    assert failed["planDigest"] == load_schema_diagnostic_plan()["planDigest"]
    assert list(root.iterdir()) == []
