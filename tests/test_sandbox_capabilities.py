"""Capability probes distinguish command presence from proven behavior."""

from __future__ import annotations

import pytest

from patchpilot_intelligence_evals.sandbox_capabilities import (
    SandboxCapabilityError,
    classify_probe,
    load_capability_report,
    probe_capabilities,
    validate_capability_report,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError


def test_command_presence_is_not_enforcement() -> None:
    disposition, evidence = classify_probe(present=True, behavior="unproven")
    assert disposition == "unsupported"
    assert evidence == "command-present-unproven"
    missing = classify_probe(present=False, behavior="unproven")
    assert missing == ("unavailable", "command-missing")
    failed = classify_probe(present=True, behavior="failed")
    assert failed == ("failed", "probe-failed")
    per_user = classify_probe(present=True, behavior="per-user")
    assert per_user == ("unsupported", "per-user-not-private")


def test_enforced_claim_requires_behavior_evidence() -> None:
    report = load_capability_report()
    report["probes"][0]["evidence"] = "command-present-unproven"
    with pytest.raises(SchemaValidationError):
        validate_capability_report(report)
    drifted = load_capability_report()
    drifted["probes"][0]["disposition"] = "unsupported"
    drifted["probes"][0]["evidence"] = "behavior-proven"
    with pytest.raises(SandboxCapabilityError) as caught:
        validate_capability_report(drifted)
    assert caught.value.code == "evidence-mismatch"


def test_committed_report_separates_presence_from_enforcement() -> None:
    report = load_capability_report()
    assert report["realModelExecuted"] is False
    assert report["productionReady"] is False
    identifiers = [item["probeId"] for item in report["probes"]]
    assert len(identifiers) == len(set(identifiers))
    for item in report["probes"]:
        if item["disposition"] == "enforced":
            assert item["evidence"] == "behavior-proven"
        if item["evidence"] == "command-missing":
            assert item["commandPresent"] is False
            assert item["disposition"] == "unavailable"
        assert "/home/" not in str(item)


def test_live_probe_records_proven_controls_only() -> None:
    report = probe_capabilities()
    by_id = {item["probeId"]: item for item in report["probes"]}
    if by_id["bubblewrap"]["disposition"] != "enforced":
        pytest.skip("unsupported-capability")
    if by_id["systemd-user-scope"]["disposition"] != "enforced":
        pytest.skip("unsupported-capability")
    assert by_id["bubblewrap"]["evidence"] == "behavior-proven"
    assert by_id["network-namespace"]["evidence"] == "behavior-proven"
    assert by_id["systemd-user-scope"]["evidence"] == "behavior-proven"
    assert by_id["seccomp"]["disposition"] != "enforced"
    for item in report["probes"]:
        if item["disposition"] == "enforced":
            assert item["evidence"] == "behavior-proven"


def test_non_linux_probe_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    import platform
    import sys

    probe_capabilities.cache_clear()
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(platform, "machine", lambda: "aarch64")
    try:
        report = probe_capabilities()
    finally:
        probe_capabilities.cache_clear()
    assert report["operatingSystemFamily"] == "darwin"
    assert report["architecture"] == "aarch64"
    assert all(item["disposition"] == "unavailable" for item in report["probes"])
    assert all(item["evidence"] == "command-missing" for item in report["probes"])
