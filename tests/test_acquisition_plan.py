"""Track 8A plan, allowlist, and preflight. These tests do not transfer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.acquisition_plan import (
    PlanError,
    build_acquisition_allowlist,
    build_acquisition_plan,
    chosen_files,
    command_templates,
    free_space_minimum_bytes,
    load_acquisition_allowlist,
    load_acquisition_plan,
    preflight_report,
    redirect_allowed,
    reject_sensitive,
    require_operator_approval,
    transfer_allowed,
    validate_external_root,
)
from patchpilot_intelligence_evals.cli import main

_PLAN_DIGEST = "349c1d666bb4106e284cd0b41f6bac6b4ea65b9d2c5edee8eb358dfc006aec92"


def test_committed_plan_matches_the_builder() -> None:
    plan = load_acquisition_plan()
    assert plan == build_acquisition_plan()
    assert plan["planDigest"] == _PLAN_DIGEST
    assert plan["acquisitionStatus"] == "not-acquired"
    assert plan["selectionOutcome"] == "no-selection"
    assert plan["productionReady"] is False
    assert plan["installationAuthorized"] is False
    assert plan["measurementPerformed"] is False
    assert plan["candidateNoticeFileName"] is None
    assert len(plan["candidateFiles"]) == 11
    assert len(chosen_files()) == 11
    assert free_space_minimum_bytes() == 4_998_666_888
    assert plan["candidateFilesystemMinimumBytes"] == 6_442_450_944
    assert plan["logicalArtifactCeilingBytes"] == 8_589_934_592
    assert plan["artifactBytesSaved"] == 0
    assert plan["redirectDiscovery"] == "metadata-only"
    assert sum(item["expectedBytes"] for item in plan["candidateFiles"]) == 4_717_588_977


def test_allowlist_is_closed_and_scopes_observed_delivery_hosts() -> None:
    plan = load_acquisition_plan()
    allowlist = load_acquisition_allowlist()
    assert allowlist == build_acquisition_allowlist(plan)
    assert allowlist["allowedHosts"] == ["github.com", "huggingface.co"]
    assert allowlist["followRedirects"] == "plan-scoped-delivery-hosts"
    assert allowlist["prohibitedRedirectHosts"] == [
        "cas-bridge.xethub.hf.co",
        "cdn-lfs.huggingface.co",
        "objects.githubusercontent.com",
    ]
    hosts = {row["host"]: row for row in allowlist["planScopedDeliveryHosts"]}
    assert hosts["release-assets.githubusercontent.com"]["artifacts"] == [
        "onnxruntime-linux-x64-1.31.1.tgz"
    ]
    assert hosts["us.aws.cdn.hf.co"]["artifacts"] == [
        "onnx/model.onnx",
        "onnx/model.onnx_data",
        "onnx/model.onnx_data_1",
        "onnx/model.onnx_data_2",
    ]
    assert all(row["scope"] == "track8a-acquisition-plan" for row in hosts.values())
    assert len(allowlist["allowedUrls"]) == 12
    assert len(allowlist["redirectObservations"]) == 12
    assert all(row["bodyBytesSaved"] == 0 for row in allowlist["redirectObservations"])
    assert all(row["identityPreserved"] is True for row in allowlist["redirectObservations"])
    runtime = str(plan["runtimeTransferUrl"])
    assert transfer_allowed(runtime, allowlist)
    assert not transfer_allowed("https://example.com/archive.tgz", allowlist)
    assert not transfer_allowed(str(plan["runtimeReleasePageUrl"]), allowlist)
    assert not transfer_allowed("https://us.aws.cdn.hf.co/object", allowlist)
    assert not transfer_allowed(
        "https://release-assets.githubusercontent.com/object",
        allowlist,
    )


def test_approval_is_the_plan_digest() -> None:
    plan = load_acquisition_plan()
    require_operator_approval(plan["planDigest"], plan)
    with pytest.raises(PlanError) as caught:
        require_operator_approval("nope", plan)
    assert caught.value.code == "approval-required"


def test_redirect_policy_preserves_artifact_identity() -> None:
    plan = load_acquisition_plan()
    allowlist = load_acquisition_allowlist()
    runtime = str(plan["runtimeTransferUrl"])
    revision = plan["onnxRevision"]
    repository = plan["onnxRepository"]
    model = f"https://huggingface.co/{repository}/resolve/{revision}/onnx/model.onnx"
    license_url = f"https://huggingface.co/{repository}/resolve/{revision}/LICENSE"
    cached = f"https://huggingface.co/api/resolve-cache/models/{repository}/{revision}/LICENSE"
    assert redirect_allowed(
        runtime,
        "https://release-assets.githubusercontent.com/object",
        allowlist,
    )
    assert redirect_allowed(model, "https://us.aws.cdn.hf.co/xet-bridge-us/object", allowlist)
    assert redirect_allowed(license_url, cached, allowlist)
    assert not redirect_allowed(
        license_url,
        "https://us.aws.cdn.hf.co/xet-bridge-us/object",
        allowlist,
    )
    assert not redirect_allowed(
        runtime,
        "https://cdn-lfs.huggingface.co/object",
        allowlist,
    )
    assert not redirect_allowed(
        model,
        "https://cas-bridge.xethub.hf.co/object",
        allowlist,
    )
    assert not redirect_allowed(
        model,
        "https://objects.githubusercontent.com/object",
        allowlist,
    )
    assert not redirect_allowed(
        runtime, "http://release-assets.githubusercontent.com/object", allowlist
    )
    assert not redirect_allowed(
        runtime,
        "https://user:secret@release-assets.githubusercontent.com/object",
        allowlist,
    )
    assert not redirect_allowed(
        model,
        f"https://huggingface.co/{repository}/resolve/{revision}/README.md",
        allowlist,
    )
    assert "cdn-lfs.huggingface.co" not in json.dumps(allowlist["planScopedDeliveryHosts"])


def test_preflight_does_not_transfer_or_record_a_host_path(tmp_path: Path) -> None:
    report = preflight_report()
    assert report["transfer"] == "not-started"
    assert report["networkPhase"] == "preflight"
    assert report["availableBytes"] is None
    assert report["rootsSupplied"] is False
    assert report["planDigest"] == _PLAN_DIGEST
    encoded = json.dumps(report)
    assert "/home/" not in encoded
    assert "<runtime-root>" in report["commandTemplates"][0]
    root = tmp_path / "runtime"
    model = tmp_path / "model"
    root.mkdir()
    model.mkdir()
    supplied = preflight_report(root, model)
    assert supplied["rootsSupplied"] is True
    assert isinstance(supplied["availableBytes"], int)
    assert "/tmp/" not in json.dumps(
        {key: value for key, value in supplied.items() if key != "availableBytes"}
    )
    with pytest.raises(PlanError) as caught:
        preflight_report(root, root)
    assert caught.value.code == "root-collision"


def test_external_roots_reject_home_and_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / ".venv"
    workspace.mkdir()
    with pytest.raises(PlanError) as caught:
        validate_external_root(workspace)
    assert caught.value.code == "workspace-root"
    home = Path("/home")
    if home.is_dir() and not home.is_symlink():
        with pytest.raises(PlanError) as home_caught:
            validate_external_root(home)
        assert home_caught.value.code == "home-root"


def test_sensitive_markers_are_rejected() -> None:
    with pytest.raises(PlanError) as caught:
        reject_sensitive({"note": "AKIAEXAMPLE"})
    assert caught.value.code == "identity"
    with pytest.raises(PlanError):
        reject_sensitive({"address": "10.1.2.3"})


def test_command_templates_use_placeholders() -> None:
    commands = command_templates(_PLAN_DIGEST)
    assert all("<runtime-root>" in command for command in commands)
    assert all("/home/" not in command for command in commands)
    assert _PLAN_DIGEST in commands[1]


def test_plan_validation_command() -> None:
    from contextlib import redirect_stdout
    from io import StringIO

    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["acquisition-plan-validation"])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["status"] == "ok"
    assert summary["planDigest"] == _PLAN_DIGEST
    assert summary["productionReady"] is False
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["acquisition-preflight"])
    assert code == 0
    preflight = json.loads(buffer.getvalue())
    assert preflight["transfer"] == "not-started"
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(
            [
                "acquire-runtime",
                "--runtime-cache",
                "/tmp",
                "--operator-approval",
                "nope",
            ]
        )
    assert code == 1
