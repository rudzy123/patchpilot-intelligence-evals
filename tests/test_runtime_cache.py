"""External runtime cache controls. Temporary synthetic bytes only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.runtime_artifact_verification import (
    RuntimeVerificationError,
    assert_verified_runtime_identity,
)
from patchpilot_intelligence_evals.runtime_cache import (
    RuntimeCacheError,
    assert_may_consider_for_execution,
    cleanup_rejected,
    load_runtime_policy,
    place_quarantine,
    promote_attempt,
    reject_attempt,
    validate_runtime_root,
)
from patchpilot_intelligence_evals.schemas import repo_root

_LIBRARY = "libonnxruntime.so.1.31.1"
_ELF = b"\x7fELFsynthetic-runtime"
_LICENSE = b"synthetic-mit\n"
_NOTICE = b"synthetic-notice\n"
_IDENTITY = b'{"runtimeId":"onnxruntime","telemetry":"disabled","versionTag":"v1.31.1"}'


def _runtime(tmp_path: Path) -> Path:
    root = tmp_path / "runtime"
    root.mkdir()
    return root


def _files() -> dict[str, bytes]:
    return {
        _LIBRARY: _ELF,
        "LICENSE": _LICENSE,
        "ThirdPartyNotices.txt": _NOTICE,
        "runtime-identity.json": _IDENTITY,
    }


def _expected(files: dict[str, bytes]) -> list[dict[str, object]]:
    roles = {
        _LIBRARY: ("shared-library", "elf"),
        "LICENSE": ("license", "not-executable"),
        "ThirdPartyNotices.txt": ("notice", "not-executable"),
        "runtime-identity.json": ("configuration", "not-executable"),
    }
    expected: list[dict[str, object]] = []
    for name, payload in files.items():
        role, executable_format = roles[name]
        expected.append(
            {
                "fileName": name,
                "role": role,
                "expectedBytes": len(payload),
                "upstreamSha256": hashlib.sha256(payload).hexdigest(),
                "executableFormat": executable_format,
            }
        )
    return expected


def test_runtime_policy_is_closed_and_path_free(capsys: pytest.CaptureFixture[str]) -> None:
    policy = load_runtime_policy()
    assert policy["productionReady"] is False
    assert policy["runtimeInstalled"] is False
    assert policy["installationAuthorized"] is False
    assert policy["states"] == ["quarantine", "verified", "rejected"]
    assert policy["packageFileName"] == "onnxruntime-linux-x64-1.31.1.tgz"
    text = json.dumps(policy)
    assert "/home/" not in text
    workflow = (repo_root() / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "upload-artifact" not in workflow
    assert "actions/cache" not in workflow
    ignore = (repo_root() / ".gitignore").read_text(encoding="utf-8")
    assert "runtime-cache/" in ignore
    assert main(["external-runtime-cache-policy-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["cacheLocation"] == "repository-external"
    assert summary["runtimeInstalled"] is False


def test_repository_sibling_and_traversal_roots_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(RuntimeCacheError) as caught:
        validate_runtime_root(repo_root())
    assert caught.value.code == "repository-root"
    sibling = repo_root().parent / "patchpilot" / "track6b-runtime-probe"
    with pytest.raises(RuntimeCacheError) as caught:
        validate_runtime_root(sibling)
    assert caught.value.code == "sibling-root"
    assert not sibling.exists()
    with pytest.raises(RuntimeCacheError) as caught:
        validate_runtime_root(tmp_path / ".." / "runtime")
    assert caught.value.code == "path-traversal"


def test_symlink_and_changed_root_are_rejected(tmp_path: Path) -> None:
    root = _runtime(tmp_path)
    link = tmp_path / "linked"
    link.symlink_to(root, target_is_directory=True)
    with pytest.raises(RuntimeCacheError) as caught:
        validate_runtime_root(link)
    assert caught.value.code == "symlink-escape"

    def _replace() -> None:
        root.rename(tmp_path / "moved")
        link_root = tmp_path / "runtime"
        link_root.symlink_to(tmp_path / "moved", target_is_directory=True)

    with pytest.raises(RuntimeCacheError) as caught:
        validate_runtime_root(root, probe=_replace)
    assert caught.value.code == "root-changed"


def test_model_cache_and_output_overlap_are_rejected(tmp_path: Path) -> None:
    root = _runtime(tmp_path)
    cache = tmp_path / "models"
    cache.mkdir()
    output = tmp_path / "output"
    output.mkdir()
    with pytest.raises(RuntimeCacheError) as caught:
        validate_runtime_root(root, model_cache_root=root)
    assert caught.value.code == "model-cache-root"
    nested = root / "output"
    nested.mkdir()
    with pytest.raises(RuntimeCacheError) as caught:
        validate_runtime_root(root, output_root=nested)
    assert caught.value.code == "output-root"
    validate_runtime_root(root, model_cache_root=cache, output_root=output)


def test_quarantine_cannot_execute_and_promotion_is_immutable(tmp_path: Path) -> None:
    root = _runtime(tmp_path)
    files = _files()
    place_quarantine(root, "runtime-ok", files)
    with pytest.raises(RuntimeCacheError) as caught:
        assert_may_consider_for_execution(root, "runtime-ok")
    assert caught.value.code == "quarantine-execution"
    manifest = promote_attempt(root, "runtime-ok", _expected(files))
    assert manifest["verificationState"] == "verified"
    assert manifest["runtimeInstalled"] is False
    verified = root / "verified" / "runtime-ok"
    assert_may_consider_for_execution(root, "runtime-ok")
    library = verified / _LIBRARY
    library.chmod(0o644)
    library.write_bytes(_ELF + b"x")
    library.chmod(0o444)
    with pytest.raises(RuntimeVerificationError) as identity_error:
        assert_verified_runtime_identity(verified, manifest)
    assert identity_error.value.code == "identity-changed"


def test_digest_size_and_rejection_persistence(tmp_path: Path) -> None:
    root = _runtime(tmp_path)
    files = _files()
    expected = _expected(files)
    for item in expected:
        if item["fileName"] == _LIBRARY:
            item["upstreamSha256"] = "b" * 64
    place_quarantine(root, "runtime-digest", files)
    with pytest.raises(RuntimeCacheError) as caught:
        promote_attempt(root, "runtime-digest", expected)
    assert caught.value.code == "digest-mismatch"
    with pytest.raises(RuntimeCacheError) as caught:
        place_quarantine(root, "runtime-digest", files)
    assert caught.value.code == "rejected-attempt"
    record = json.loads((root / "rejected" / "runtime-digest" / "rejection.json").read_text())
    assert "digest-mismatch" in record["reasons"]
    assert _ELF not in (root / "rejected" / "runtime-digest" / "rejection.json").read_bytes()
    cleanup_rejected(root, "runtime-digest")
    assert not (root / "rejected" / "runtime-digest" / _LIBRARY).exists()
    assert (root / "rejected" / "runtime-digest" / "rejection.json").is_file()
    place_quarantine(root, "runtime-size", files)
    sized = _expected(files)
    for item in sized:
        if item["fileName"] == "LICENSE":
            item["expectedBytes"] = 1
    with pytest.raises(RuntimeCacheError) as caught:
        promote_attempt(root, "runtime-size", sized)
    assert caught.value.code == "size-mismatch"


def test_explicit_rejection_and_symlink_payload(tmp_path: Path) -> None:
    root = _runtime(tmp_path)
    place_quarantine(root, "runtime-reject", _files())
    reject_attempt(root, "runtime-reject", ["telemetry-enabled"])
    with pytest.raises(RuntimeCacheError) as caught:
        assert_may_consider_for_execution(root, "runtime-reject")
    assert caught.value.code == "rejected-execution"
    place_quarantine(root, "runtime-link", _files())
    quarantine = root / "quarantine" / "runtime-link"
    license_path = quarantine / "LICENSE"
    license_path.chmod(0o644)
    license_path.unlink()
    outside = tmp_path / "outside"
    outside.write_bytes(b"outside")
    license_path.symlink_to(outside)
    with pytest.raises(RuntimeCacheError) as caught:
        promote_attempt(root, "runtime-link", _expected(_files()))
    assert caught.value.code == "symlink-escape"
