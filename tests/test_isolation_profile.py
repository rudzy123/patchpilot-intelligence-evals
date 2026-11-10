"""Isolation profile and harmless Linux limit probes. No model is executed."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.isolation_profile import (
    has_acquisition_blocker,
    load_profile,
    probe_linux_limit,
)
from patchpilot_intelligence_evals.protocol import TIMEOUT_SECONDS

_BLOCKING = {
    "no-cloud-credentials",
    "no-gold-label-access",
    "no-home-directory-access",
    "no-outbound-network",
    "no-prior-result-access",
    "no-sibling-repository-access",
    "no-ssh-configuration-access",
    "read-only-candidate-configuration",
    "read-only-verified-artifacts",
}
_LIMITS = {
    "cpu-time-limit",
    "file-size-limit",
    "memory-limit",
    "open-file-limit",
    "process-count-limit",
}


def test_profile_records_acquisition_blockers(capsys: pytest.CaptureFixture[str]) -> None:
    profile = load_profile()
    assert profile["operatingSystemSandboxClaimed"] is False
    assert profile["fixtureTimeoutSeconds"] == TIMEOUT_SECONDS == 15
    assert profile["budgets"]["maxStderrBytes"] == 65536
    assert profile["budgets"]["startupAndLoadSeconds"] == 180
    assert profile["budgets"]["warmPerCaseSeconds"] == 120
    assert profile["budgets"]["completeCorpusSeconds"] == 5400
    assert profile["acquisitionStatus"] == "not-acquired"
    assert profile["executionStatus"] == "not-executed"
    assert profile["productionReady"] is False
    assert has_acquisition_blocker(profile) is True
    by_id = {item["controlId"]: item for item in profile["controls"]}
    assert set(by_id) >= _BLOCKING | _LIMITS
    for control_id in _BLOCKING:
        assert by_id[control_id]["enforcement"] == "namespace-or-container"
        assert by_id[control_id]["disposition"] == "deferred-blocker"
    for control_id in _LIMITS:
        assert by_id[control_id]["enforcement"] == "linux-resource-limit"
        assert by_id[control_id]["acquisitionBlocking"] is False
    assert by_id["no-shell"]["enforcement"] == "current-harness"
    assert main(["isolation-profile-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["acquisitionBlocked"] is True
    assert summary["productionReady"] is False


@pytest.mark.parametrize("kind", ["file-size", "open-files", "memory", "nproc", "cpu"])
def test_harmless_linux_limit_fires(kind: str) -> None:
    assert probe_linux_limit(kind) == "enforced"
