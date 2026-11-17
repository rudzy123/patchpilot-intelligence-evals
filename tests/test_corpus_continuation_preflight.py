"""Preflight recomputes identities and does not create a model session."""

from __future__ import annotations

from pathlib import Path

from patchpilot_intelligence_evals.corpus_continuation_plan import prepare_continuation_root
from patchpilot_intelligence_evals.corpus_continuation_preflight import (
    load_preflight_template,
    run_continuation_preflight,
)


def test_template_has_not_executed() -> None:
    document = load_preflight_template()
    assert document["preflightStatus"] == "not-executed"
    assert document["runInvoked"] is False
    assert document["modelSessionCreated"] is False
    assert document["realModelExecuted"] is False


def test_failed_probe_does_not_call_run(tmp_path: Path) -> None:
    root = prepare_continuation_root(tmp_path / "preflight-root")
    document = run_continuation_preflight(
        tmp_path / "runtime",
        tmp_path / "model",
        root,
        bind=False,
        probe=lambda _path: "failed",
    )
    assert document["preflightStatus"] == "failed"
    assert document["dynamicLinkStatus"] == "failed"
    assert document["runInvoked"] is False
    assert document["modelSessionCreated"] is False
    assert list(root.iterdir()) == []
