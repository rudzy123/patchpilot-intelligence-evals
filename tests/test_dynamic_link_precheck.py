"""Dynamic-link precheck stays inside the closure and does not call Run."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.dynamic_link_precheck import (
    _individual,
    load_precheck_template,
)
from patchpilot_intelligence_evals.filesystem_policy import Mount
from patchpilot_intelligence_evals.inference_retry_cli import handle
from patchpilot_intelligence_evals.runtime_dependency_closure import (
    LIBRARY_NAME,
    PROVIDER_LIBRARY,
    approved_public_closure,
)


def test_precheck_template_does_not_create_a_session() -> None:
    document = load_precheck_template()
    assert document["status"] == "not-executed"
    assert document["createSessionCalled"] is False
    assert document["getApiCalled"] is False
    assert document["runInvoked"] is False
    assert document["modelSessionCreated"] is False
    assert document["providerLoaded"] is False
    assert document["dependencies"] == approved_public_closure()


def test_precheck_child_does_not_name_session_or_run() -> None:
    source = Path("src/patchpilot_intelligence_evals/dynamic_link_precheck_main.py").read_text(
        encoding="utf-8"
    )
    assert "CreateSession" not in source
    assert "Run(" not in source
    assert "OrtGetApiBase" in source
    assert LIBRARY_NAME in source
    assert PROVIDER_LIBRARY not in source


def test_broad_directory_mount_is_rejected(tmp_path: Path) -> None:
    directory = tmp_path / "usr-lib"
    directory.mkdir()
    library = tmp_path / "libc.so.6"
    library.write_bytes(b"synthetic")
    assert _individual((Mount(str(directory), "/usr/lib", True),)) is False
    assert _individual((Mount(str(library), "/usr/lib/libc.so.6", False),)) is False
    assert _individual((Mount(str(library), "/usr/lib/libc.so.6", True),)) is True


def test_passed_precheck_command_stays_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    def passed(*_args: object, **_kwargs: object) -> dict[str, object]:
        return {
            "createSessionCalled": False,
            "planDigest": "a" * 64,
            "runInvoked": False,
            "status": "passed",
        }

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.inference_retry_cli.run_dynamic_link_precheck",
        passed,
    )
    payload = handle(
        "inference-retry-precheck",
        argparse.Namespace(
            model_cache="/var/tmp/model",
            result_root="/var/tmp/result",
            runtime_cache="/var/tmp/runtime",
        ),
    )
    assert payload["status"] == "ok"
    assert payload["precheckStatus"] == "passed"
    assert payload["runInvoked"] is False


def test_provider_library_is_outside_the_public_closure() -> None:
    names = {row["basename"] for row in approved_public_closure()}
    assert PROVIDER_LIBRARY not in names
    assert all("providers" not in name for name in names)
