"""External cache controls. Temporary synthetic bytes only. No model is downloaded."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.artifact_cache import (
    CacheError,
    assert_may_consider_for_execution,
    cleanup_rejected,
    load_cache_policy,
    place_quarantine,
    promote_attempt,
    validate_cache_root,
)
from patchpilot_intelligence_evals.artifact_verification import (
    VerificationError,
    assert_verified_identity,
)
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.schemas import repo_root

_PAYLOAD = b"synthetic-track5"


def _cache(tmp_path: Path) -> Path:
    root = tmp_path / "cache"
    root.mkdir()
    return root


def _expected(
    payload: bytes = _PAYLOAD,
    *,
    size: int | None = None,
    upstream: str | None = None,
    name: str = "model.safetensors",
) -> list[dict[str, object]]:
    return [
        {
            "fileName": name,
            "expectedBytes": len(payload) if size is None else size,
            "upstreamSha256": upstream,
        }
    ]


def test_cache_policy_is_closed_and_path_free(capsys: pytest.CaptureFixture[str]) -> None:
    policy = load_cache_policy()
    assert policy["productionReady"] is False
    assert policy["acquisitionStatus"] == "not-acquired"
    assert policy["executionStatus"] == "not-executed"
    assert policy["states"] == ["quarantine", "verified", "rejected"]
    text = json.dumps(policy)
    assert "/home/" not in text
    assert "upload-artifact" not in (repo_root() / ".github/workflows/validate.yml").read_text()
    assert "actions/cache" not in (repo_root() / ".github/workflows/validate.yml").read_text()
    ignore = (repo_root() / ".gitignore").read_text(encoding="utf-8")
    assert "*.safetensors" in ignore
    assert "artifact-cache/" in ignore
    assert main(["artifact-cache-policy-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["cacheLocation"] == "repository-external"
    assert summary["productionReady"] is False


def test_repository_root_is_rejected() -> None:
    with pytest.raises(CacheError) as caught:
        validate_cache_root(repo_root())
    assert caught.value.code == "repository-root"
    with pytest.raises(CacheError) as caught:
        validate_cache_root(repo_root() / "candidates")
    assert caught.value.code == "repository-root"


def test_sibling_like_root_is_rejected_without_creating_it() -> None:
    sibling = repo_root().parent / "patchpilot" / "track5-cache-probe"
    with pytest.raises(CacheError) as caught:
        validate_cache_root(sibling)
    assert caught.value.code == "sibling-root"
    assert not sibling.exists()
    other = repo_root().parent / "neural-from-scratch"
    with pytest.raises(CacheError) as caught:
        validate_cache_root(other)
    assert caught.value.code == "sibling-root"


def test_traversal_is_rejected(tmp_path: Path) -> None:
    root = _cache(tmp_path)
    with pytest.raises(CacheError) as caught:
        validate_cache_root(root / ".." / "cache")
    assert caught.value.code == "path-traversal"


def test_symlink_root_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "link"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(CacheError) as caught:
        validate_cache_root(link)
    assert caught.value.code == "symlink-escape"


def test_changed_root_is_rejected(tmp_path: Path) -> None:
    root = _cache(tmp_path)

    def _replace() -> None:
        root.rmdir()
        root.mkdir()

    with pytest.raises(CacheError) as caught:
        validate_cache_root(root, probe=_replace)
    assert caught.value.code == "root-changed"


def test_quarantine_cannot_be_considered_for_execution(tmp_path: Path) -> None:
    root = _cache(tmp_path)
    place_quarantine(root, "attempt-a", {"model.safetensors": _PAYLOAD})
    with pytest.raises(CacheError) as caught:
        assert_may_consider_for_execution(root, "attempt-a")
    assert caught.value.code == "quarantine-execution"


def test_unexpected_and_missing_files_fail(tmp_path: Path) -> None:
    root = _cache(tmp_path)
    place_quarantine(
        root,
        "attempt-extra",
        {"model.safetensors": _PAYLOAD, "extra.safetensors": b"extra"},
    )
    with pytest.raises(CacheError) as caught:
        promote_attempt(root, "attempt-extra", _expected())
    assert caught.value.code == "unexpected-file"
    place_quarantine(root, "attempt-missing", {"model.safetensors": _PAYLOAD})
    expected = _expected() + _expected(name="weights.safetensors")
    with pytest.raises(CacheError) as caught:
        promote_attempt(root, "attempt-missing", expected)
    assert caught.value.code == "missing-file"


def test_digest_and_size_mismatches_fail(tmp_path: Path) -> None:
    root = _cache(tmp_path)
    place_quarantine(root, "attempt-digest", {"model.safetensors": _PAYLOAD})
    with pytest.raises(CacheError) as caught:
        promote_attempt(root, "attempt-digest", _expected(upstream="a" * 64))
    assert caught.value.code == "digest-mismatch"
    place_quarantine(root, "attempt-size", {"model.safetensors": _PAYLOAD})
    with pytest.raises(CacheError) as caught:
        promote_attempt(root, "attempt-size", _expected(size=1))
    assert caught.value.code == "size-mismatch"


def test_valid_synthetic_inventory_promotes_and_byte_change_invalidates(tmp_path: Path) -> None:
    root = _cache(tmp_path)
    place_quarantine(root, "attempt-ok", {"model.safetensors": _PAYLOAD})
    manifest = promote_attempt(root, "attempt-ok", _expected())
    assert manifest["verificationState"] == "verified"
    assert manifest["acquisitionStatus"] == "not-acquired"
    assert manifest["executionStatus"] == "not-executed"
    assert manifest["locallyObservedArtifactDigests"]
    assert_may_consider_for_execution(root, "attempt-ok")
    verified = root / "verified" / "attempt-ok" / "model.safetensors"
    verified.write_bytes(_PAYLOAD + b"x")
    with pytest.raises(VerificationError) as caught:
        assert_verified_identity(verified.parent, manifest)
    assert caught.value.code == "identity-changed"


def test_rejected_attempt_cannot_promote_without_a_new_attempt(tmp_path: Path) -> None:
    root = _cache(tmp_path)
    place_quarantine(root, "attempt-bad", {"model.safetensors": _PAYLOAD})
    with pytest.raises(CacheError):
        promote_attempt(root, "attempt-bad", _expected(upstream="b" * 64))
    record = (root / "rejected" / "attempt-bad" / "rejection.json").read_text(encoding="utf-8")
    assert "synthetic-track5" not in record
    with pytest.raises(CacheError) as caught:
        promote_attempt(root, "attempt-bad", _expected())
    assert caught.value.code == "rejected-attempt"
    cleanup_rejected(root, "attempt-bad")
    assert not (root / "rejected" / "attempt-bad" / "model.safetensors").exists()
    assert (root / "rejected" / "attempt-bad" / "rejection.json").is_file()
    place_quarantine(root, "attempt-new", {"model.safetensors": _PAYLOAD})
    manifest = promote_attempt(root, "attempt-new", _expected())
    assert manifest["verificationState"] == "verified"


def test_symlink_inside_quarantine_cannot_promote(tmp_path: Path) -> None:
    root = _cache(tmp_path)
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside")
    place_quarantine(root, "attempt-link", {"model.safetensors": _PAYLOAD})
    link = root / "quarantine" / "attempt-link" / "model.safetensors"
    link.unlink()
    link.symlink_to(outside)
    with pytest.raises(CacheError) as caught:
        promote_attempt(root, "attempt-link", _expected())
    assert caught.value.code == "symlink-escape"
