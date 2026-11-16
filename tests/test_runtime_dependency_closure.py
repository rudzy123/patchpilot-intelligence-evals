"""Shared runtime dependency closure. These tests do not create a session."""

from __future__ import annotations

import ast
import ctypes
import json
from collections.abc import Callable
from pathlib import Path

import pytest

import patchpilot_intelligence_evals.candidate_inference as candidate_inference
import patchpilot_intelligence_evals.measurement_retry_plan as measurement_retry_plan
import patchpilot_intelligence_evals.runtime_dependency_closure as runtime_dependency_closure
from patchpilot_intelligence_evals.candidate_inference import launch_child, measurement_limits
from patchpilot_intelligence_evals.filesystem_policy import Mount, dependency_mounts
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult, execute_hardened
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.measurement_retry_plan import load_retry_plan, phase_by_name
from patchpilot_intelligence_evals.runtime_dependency_closure import (
    APPROVED_BASENAMES,
    INTERPRETER_NAME,
    LIBRARY_NAME,
    PROVIDER_LIBRARY,
    ClosureError,
    approved_public_closure,
    approved_runtime_mounts,
    inspect_dependency,
    public_dependency,
    resolve_runtime_dependencies,
)
from patchpilot_intelligence_evals.schemas import repo_root


def test_approved_closure_mounts_are_individual_and_read_only(tmp_path: Path) -> None:
    binary, text, roots = _closure(tmp_path)
    resolved = resolve_runtime_dependencies(binary, ldd_text=text, roots=roots)
    mounts = approved_runtime_mounts(binary, ldd_text=text, roots=roots)
    public = [public_dependency(item) for item in resolved]
    assert {item.basename for item in resolved} == APPROVED_BASENAMES | {INTERPRETER_NAME}
    assert "/" not in json.dumps(public)
    assert all(mount.read_only for mount in mounts)
    assert all(Path(mount.source).is_file() for mount in mounts)
    assert {Path(mount.destination).name for mount in mounts} == APPROVED_BASENAMES
    assert INTERPRETER_NAME not in {Path(mount.destination).name for mount in mounts}
    assert PROVIDER_LIBRARY not in {Path(mount.destination).name for mount in mounts}
    assert len(mounts) == len(APPROVED_BASENAMES)


def test_launcher_passes_those_mounts_read_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected = (Mount("/tmp/copy-libc.so.6", "/usr/lib/libc.so.6", True),)
    monkeypatch.setattr(candidate_inference, "approved_runtime_mounts", lambda _binary: expected)
    monkeypatch.setattr(measurement_retry_plan, "require_retry_approval", lambda _supplied: {})
    monkeypatch.setattr(measurement_retry_plan, "require_open_retry_plan", lambda: None)
    captured: dict[str, object] = {}

    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        captured["mounts"] = kwargs["extra_mounts"]
        return _result()

    monkeypatch.setattr(candidate_inference, "execute_hardened", launcher)
    phase = phase_by_name(load_retry_plan(), "one-token-smoke")
    launch_child(
        {"phase": "one-token-smoke"},
        runtime_dir=tmp_path,
        model_dir=tmp_path,
        limits=measurement_limits(phase),
        launcher=launcher,
        retry_approval="synthetic",
    )
    mounts = captured["mounts"]
    assert isinstance(mounts, tuple)
    assert expected[0] in mounts
    assert all(isinstance(mount, Mount) and mount.read_only for mount in mounts)
    assert all(
        isinstance(mount, Mount) and Path(mount.destination).name != PROVIDER_LIBRARY
        for mount in mounts
    )


def test_unresolved_dependency_fails_before_session_and_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ctypes, "CDLL", _unexpected("session"))
    binary, _text, roots = _closure(tmp_path)
    unresolved = "\tlibc.so.6 => not found\n"
    with pytest.raises(ClosureError) as caught:
        resolve_runtime_dependencies(binary, ldd_text=unresolved, roots=roots)
    assert caught.value.code == "unresolved-dependency"
    monkeypatch.setattr(measurement_retry_plan, "require_retry_approval", lambda _supplied: {})
    monkeypatch.setattr(measurement_retry_plan, "require_open_retry_plan", lambda: None)
    monkeypatch.setattr(runtime_dependency_closure, "read_ldd", lambda _binary: unresolved)

    def launched(*_args: object, **_kwargs: object) -> ExecutionResult:
        raise AssertionError("launched")

    monkeypatch.setattr(candidate_inference, "execute_hardened", launched)
    phase = phase_by_name(load_retry_plan(), "one-token-smoke")
    with pytest.raises(MeasurementError) as measurement:
        launch_child(
            {"phase": "one-token-smoke"},
            runtime_dir=tmp_path,
            model_dir=tmp_path,
            limits=measurement_limits(phase),
            launcher=launched,
            retry_approval="synthetic",
        )
    assert measurement.value.code == "unverified-dependency"


def test_unapproved_provider_and_closure_mismatch_fail(tmp_path: Path) -> None:
    binary, text, roots = _closure(tmp_path)
    provider = _library(tmp_path / "sys", f"lib/{PROVIDER_LIBRARY}")
    with pytest.raises(ClosureError) as provider_error:
        resolve_runtime_dependencies(
            binary,
            ldd_text=f"{text}\t{PROVIDER_LIBRARY} => {provider} (0x1)\n",
            roots=roots,
        )
    assert provider_error.value.code == "unapproved-provider"
    extra = _library(tmp_path / "sys", "lib/libextra.so.1")
    with pytest.raises(ClosureError) as mismatch:
        resolve_runtime_dependencies(
            binary,
            ldd_text=f"{text}\tlibextra.so.1 => {extra} (0x1)\n",
            roots=roots,
        )
    assert mismatch.value.code == "closure-mismatch"


def test_dependency_outside_approved_roots_fails(tmp_path: Path) -> None:
    binary, text, roots = _closure(tmp_path)
    outside = text.replace(str(_path(tmp_path, "libc.so.6")), "/opt/vendor/libc.so.6")
    with pytest.raises(ClosureError) as caught:
        resolve_runtime_dependencies(binary, ldd_text=outside, roots=roots)
    assert caught.value.code == "unapproved-root"


def test_writable_dependency_fails(tmp_path: Path) -> None:
    binary, text, roots = _closure(tmp_path)
    _path(tmp_path, "libm.so.6").chmod(0o666)
    with pytest.raises(ClosureError) as caught:
        resolve_runtime_dependencies(binary, ldd_text=text, roots=roots)
    assert caught.value.code == "writable-dependency"


def test_symlink_escaping_dependency_fails(tmp_path: Path) -> None:
    binary, text, roots = _closure(tmp_path)
    outside = tmp_path / "outside" / "libc.so.6"
    outside.parent.mkdir()
    outside.write_bytes(b"escaped")
    link = _path(tmp_path, "libc.so.6")
    link.unlink()
    link.symlink_to(outside)
    with pytest.raises(ClosureError) as caught:
        resolve_runtime_dependencies(binary, ldd_text=text, roots=roots)
    assert caught.value.code == "symlink-escape"


def test_transport_attempt_dependency_fails(tmp_path: Path) -> None:
    root = tmp_path / "sys"
    moved = _library(root, "duplicate-transport/libc.so.6")
    binary, text, roots = _closure(tmp_path)
    replaced = text.replace(str(_path(tmp_path, "libc.so.6")), str(moved))
    with pytest.raises(ClosureError) as caught:
        resolve_runtime_dependencies(binary, ldd_text=replaced, roots=roots)
    assert caught.value.code == "transport-attempt"


@pytest.mark.parametrize(
    ("relative", "code"),
    [
        ("quarantine/libc.so.6", "quarantine-dependency"),
        (".venv/libc.so.6", "project-environment"),
        ("site-packages/libc.so.6", "project-environment"),
    ],
)
def test_rejected_dependency_sources(tmp_path: Path, relative: str, code: str) -> None:
    path = _library(tmp_path / "sys", relative)
    with pytest.raises(ClosureError) as caught:
        inspect_dependency("libc.so.6", str(path), roots=(f"{tmp_path / 'sys'}/",))
    assert caught.value.code == code


def test_home_dependency_fails() -> None:
    with pytest.raises(ClosureError) as caught:
        inspect_dependency("libc.so.6", "/home/example/libc.so.6")
    assert caught.value.code == "home-dependency"


def test_broad_library_directory_is_prohibited(tmp_path: Path) -> None:
    binary, text, roots = _closure(tmp_path)
    directory = tmp_path / "sys" / "lib"
    with pytest.raises(ClosureError) as caught:
        inspect_dependency("libc.so.6", str(directory), roots=roots)
    assert caught.value.code == "broad-directory"
    mounts = approved_runtime_mounts(binary, ldd_text=text, roots=roots)
    broad = {"/lib", "/lib64", "/usr/lib", "/usr/lib64", "/usr/lib/x86_64-linux-gnu"}
    assert all(mount.destination.rstrip("/") not in broad for mount in mounts)
    assert all(not Path(mount.source).is_dir() for mount in mounts)


def test_committed_records_omit_absolute_host_paths() -> None:
    text = Path("candidates/authorization/track8b-r1-dependency-mount-defect.json").read_text(
        encoding="utf-8"
    )
    assert "/" not in text
    assert json.loads(text)["approvedClosure"] == approved_public_closure()
    assert all("/" not in json.dumps(row) for row in approved_public_closure())


def test_validation_does_not_create_a_session_or_call_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ctypes, "CDLL", _unexpected("session"))
    binary, text, roots = _closure(tmp_path)
    approved_runtime_mounts(binary, ldd_text=text, roots=roots)
    source = (
        repo_root() / "src/patchpilot_intelligence_evals/runtime_dependency_closure.py"
    ).read_text(encoding="utf-8")
    assert "CreateSession" not in source
    assert "Run(" not in source
    assert "import onnxruntime" not in source
    for banned in ("urllib", "requests", "socket", "http://", "https://"):
        assert banned not in source


def test_load_proof_and_inference_share_the_closure(monkeypatch: pytest.MonkeyPatch) -> None:
    root = repo_root() / "src" / "patchpilot_intelligence_evals"
    proof = _calls(root / "hardened_load_proof.py", "launch_offline_load")
    inference = _calls(root / "candidate_inference.py", "launch_child")
    wrapper = _calls(root / "filesystem_policy.py", "dependency_mounts")
    assert "approved_runtime_mounts" in proof
    assert "approved_runtime_mounts" in inference
    assert "dependency_mounts" not in proof
    assert "approved_runtime_mounts" in wrapper
    seen: list[str] = []

    def fake(binary: Path, **_kwargs: object) -> tuple[Mount, ...]:
        seen.append(binary.name)
        return ()

    monkeypatch.setattr(runtime_dependency_closure, "approved_runtime_mounts", fake)
    assert dependency_mounts(Path(LIBRARY_NAME)) == ()
    assert seen == [LIBRARY_NAME]


def test_consumed_retry_does_not_mount_or_launch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(candidate_inference, "approved_runtime_mounts", _unexpected("mounted"))
    phase = phase_by_name(load_retry_plan(), "one-token-smoke")
    with pytest.raises(MeasurementError) as caught:
        launch_child(
            {"phase": "one-token-smoke"},
            runtime_dir=Path("/tmp/runtime"),
            model_dir=Path("/tmp/model"),
            limits=measurement_limits(phase),
            launcher=execute_hardened,
            retry_approval=load_retry_plan()["planDigest"],
        )
    assert caught.value.code == "plan-consumed"


def _closure(tmp_path: Path) -> tuple[Path, str, tuple[str, ...]]:
    root = tmp_path / "sys"
    files = {name: _library(root, f"lib/{name}") for name in sorted(APPROVED_BASENAMES)}
    interpreter = _library(root, f"lib64/{INTERPRETER_NAME}")
    lines = [f"\t{name} => {files[name]} (0x1)" for name in sorted(APPROVED_BASENAMES)]
    lines.append(f"\t{interpreter} (0x1)")
    binary = root / LIBRARY_NAME
    binary.write_bytes(b"runtime")
    return binary, "\n".join(lines) + "\n", (f"{root}/",)


def _library(root: Path, relative: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"synthetic-library")
    path.chmod(0o644)
    return path


def _path(tmp_path: Path, name: str) -> Path:
    return tmp_path / "sys" / "lib" / name


def _result() -> ExecutionResult:
    return ExecutionResult(
        exit_classification="success",
        return_code=0,
        stdout=b"",
        stderr=b"",
        cleanup="reaped",
        attempts=1,
        report=b"",
        argv=(),
    )


def _unexpected(label: str) -> Callable[..., object]:
    def fail(*_args: object, **_kwargs: object) -> object:
        raise AssertionError(label)

    return fail


def _calls(path: Path, function: str) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name != function:
            continue
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            func = call.func
            if isinstance(func, ast.Name):
                names.append(func.id)
            elif isinstance(func, ast.Attribute):
                names.append(func.attr)
    return names
