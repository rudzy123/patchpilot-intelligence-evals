"""Repository-external runtime staging.

Quarantine cannot be executed or promoted until every runtime inventory check
passes. Rejected attempts stay rejected. This module does not download a
runtime or create a persistent cache inside the Git repository.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.runtime_artifact_verification import (
    RuntimeVerificationError,
    assert_verified_runtime_identity,
    inspect_runtime,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_ATTEMPT_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
_SIBLING_NAMES = ("neural-from-scratch", "patchpilot")
_ROOT_REQUIREMENTS = frozenset(
    {
        "distinct-from-model-artifact-cache",
        "distinct-from-output-directory",
        "explicit-root",
        "outside-git-repository",
        "outside-sibling-repositories",
        "reject-repository-contained-root",
        "reject-symlink-escape",
        "reject-traversal",
        "stable-root-during-validation",
    }
)
_POLICY = Path("candidates/authorization/external-runtime-cache-policy.json")


class RuntimeCacheError(ValueError):
    """A runtime root or attempt failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_runtime_policy(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the closed runtime-cache policy. It stores no filesystem path."""
    validate("external-runtime-cache-policy", document)
    if document["siblingRepositoryNames"] != list(_SIBLING_NAMES):
        raise RuntimeCacheError("sibling-names")
    if set(document["rootRequirements"]) != _ROOT_REQUIREMENTS:
        raise RuntimeCacheError("root-requirements")
    if document["productionReady"] is not False:
        raise RuntimeCacheError("production-ready")
    if document["runtimeInstalled"] is not False or document["installationAuthorized"] is not False:
        raise RuntimeCacheError("installation-authorized")
    if document["acquisitionStatus"] != "not-acquired":
        raise RuntimeCacheError("acquisition-status")
    if document["executionStatus"] != "not-executed":
        raise RuntimeCacheError("execution-status")
    if document["conversionStatus"] != "not-performed":
        raise RuntimeCacheError("conversion-status")
    text = json.dumps(document)
    if "/home/" in text or "/Users/" in text:
        raise RuntimeCacheError("identity")
    return document


def load_runtime_policy(root: Path | None = None) -> dict[str, Any]:
    """Load the committed runtime-cache policy."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _POLICY).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeCacheError("policy-type")
    return validate_runtime_policy(loaded)


def validate_runtime_root(
    root: Path,
    *,
    repository: Path | None = None,
    sibling_roots: tuple[Path, ...] | None = None,
    model_cache_root: Path | None = None,
    output_root: Path | None = None,
    probe: Callable[[], None] | None = None,
) -> Path:
    """Resolve an explicit runtime root or reject containment, traversal, and links."""
    repository_path = repository if repository is not None else repo_root()
    if not root.is_absolute():
        raise RuntimeCacheError("relative-root")
    if ".." in root.parts:
        raise RuntimeCacheError("path-traversal")
    lexical = Path(os.path.abspath(root))
    if ".." in lexical.parts:
        raise RuntimeCacheError("path-traversal")
    repository_lexical = Path(os.path.abspath(repository_path))
    repository_resolved = repository_path.resolve()
    prefixes = sibling_roots
    if prefixes is None:
        prefixes = tuple(repository_resolved.parent / name for name in _SIBLING_NAMES)
    for prefix in prefixes:
        absolute = Path(os.path.abspath(prefix))
        if _under(lexical, absolute):
            raise RuntimeCacheError("sibling-root")
    if _under(lexical, repository_lexical) or _under(lexical, repository_resolved):
        raise RuntimeCacheError("repository-root")
    _distinct(lexical, model_cache_root, "model-cache-root")
    _distinct(lexical, output_root, "output-root")
    if not root.exists() or not root.is_dir():
        raise RuntimeCacheError("missing-root")
    if root.is_symlink():
        raise RuntimeCacheError("symlink-escape")
    resolved = root.resolve(strict=True)
    for prefix in prefixes:
        if _under(resolved, Path(os.path.abspath(prefix))):
            raise RuntimeCacheError("sibling-root")
    if _under(resolved, repository_resolved):
        raise RuntimeCacheError("repository-root")
    if (
        model_cache_root is not None
        and model_cache_root.exists()
        and not model_cache_root.is_symlink()
    ):
        if _same_identity(root, model_cache_root) or _under(resolved, model_cache_root.resolve()):
            raise RuntimeCacheError("model-cache-root")
    if output_root is not None and output_root.exists() and not output_root.is_symlink():
        if _same_identity(root, output_root) or _under(resolved, output_root.resolve()):
            raise RuntimeCacheError("output-root")
    before = root.stat()
    resolved_before = root.resolve()
    if probe is not None:
        probe()
    if not root.exists():
        raise RuntimeCacheError("root-changed")
    after = root.stat()
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        raise RuntimeCacheError("root-changed")
    if root.resolve() != resolved_before:
        raise RuntimeCacheError("root-changed")
    return resolved


def place_quarantine(
    root: Path,
    attempt_id: str,
    files: Mapping[str, bytes],
    *,
    repository: Path | None = None,
    model_cache_root: Path | None = None,
    output_root: Path | None = None,
) -> Path:
    """Write synthetic bytes into a new quarantine attempt and clear write bits."""
    resolved = validate_runtime_root(
        root,
        repository=repository,
        model_cache_root=model_cache_root,
        output_root=output_root,
    )
    _check_attempt_id(attempt_id)
    if _attempt(resolved, "rejected", attempt_id).exists():
        raise RuntimeCacheError("rejected-attempt")
    if _attempt(resolved, "verified", attempt_id).exists():
        raise RuntimeCacheError("already-verified")
    destination = _attempt(resolved, "quarantine", attempt_id)
    if destination.exists():
        raise RuntimeCacheError("attempt-exists")
    destination.mkdir(parents=True)
    for name, payload in files.items():
        if not isinstance(payload, bytes):
            raise RuntimeCacheError("payload-type")
        target = destination / name
        if target.parent != destination or target.is_symlink():
            raise RuntimeCacheError("path-traversal")
        target.write_bytes(payload)
        target.chmod(0o444)
    return destination


def promote_attempt(
    root: Path,
    attempt_id: str,
    expected: list[dict[str, Any]],
    *,
    repository: Path | None = None,
    model_cache_root: Path | None = None,
    output_root: Path | None = None,
) -> dict[str, Any]:
    """Verify quarantine and publish it only when every runtime check passes."""
    resolved = validate_runtime_root(
        root,
        repository=repository,
        model_cache_root=model_cache_root,
        output_root=output_root,
    )
    _check_attempt_id(attempt_id)
    if _attempt(resolved, "rejected", attempt_id).exists():
        raise RuntimeCacheError("rejected-attempt")
    source = _attempt(resolved, "quarantine", attempt_id)
    if not source.is_dir() or source.is_symlink():
        raise RuntimeCacheError("missing-quarantine")
    try:
        manifest = inspect_runtime(source, expected, attempt_id=attempt_id)
    except RuntimeVerificationError as exc:
        _move_rejected(resolved, attempt_id, [exc.code])
        raise RuntimeCacheError(exc.code) from exc
    if manifest["verificationState"] != "verified":
        _move_rejected(resolved, attempt_id, list(manifest["reasonCodes"]))
        raise RuntimeCacheError(str(manifest["reasonCodes"][0]))
    destination = _attempt(resolved, "verified", attempt_id)
    destination.mkdir(parents=True)
    for item in manifest["observedFiles"]:
        name = str(item["fileName"])
        file_path = source / name
        if file_path.is_symlink() or not file_path.is_file():
            shutil.rmtree(destination)
            _move_rejected(resolved, attempt_id, ["symlink-escape"])
            raise RuntimeCacheError("symlink-escape")
        target = destination / name
        target.write_bytes(file_path.read_bytes())
        target.chmod(0o444)
    record = resolved / "verified" / f"{attempt_id}.verification.json"
    record.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(source)
    validate_runtime_root(
        root,
        repository=repository,
        model_cache_root=model_cache_root,
        output_root=output_root,
    )
    assert_verified_runtime_identity(destination, manifest)
    return manifest


def reject_attempt(
    root: Path,
    attempt_id: str,
    reasons: list[str],
    *,
    repository: Path | None = None,
    model_cache_root: Path | None = None,
    output_root: Path | None = None,
) -> None:
    """Mark an attempt rejected and retain the reason codes."""
    resolved = validate_runtime_root(
        root,
        repository=repository,
        model_cache_root=model_cache_root,
        output_root=output_root,
    )
    _check_attempt_id(attempt_id)
    if not reasons:
        raise RuntimeCacheError("missing-reason")
    source = _attempt(resolved, "quarantine", attempt_id)
    if not source.is_dir():
        raise RuntimeCacheError("missing-quarantine")
    _move_rejected(resolved, attempt_id, reasons)


def assert_may_consider_for_execution(
    root: Path,
    attempt_id: str,
    *,
    repository: Path | None = None,
    model_cache_root: Path | None = None,
    output_root: Path | None = None,
) -> None:
    """Allow consideration of a verified runtime only. This does not execute it."""
    resolved = validate_runtime_root(
        root,
        repository=repository,
        model_cache_root=model_cache_root,
        output_root=output_root,
    )
    _check_attempt_id(attempt_id)
    if _attempt(resolved, "quarantine", attempt_id).exists():
        raise RuntimeCacheError("quarantine-execution")
    if _attempt(resolved, "rejected", attempt_id).exists():
        raise RuntimeCacheError("rejected-execution")
    verified = _attempt(resolved, "verified", attempt_id)
    if not verified.is_dir() or verified.is_symlink():
        raise RuntimeCacheError("not-verified")


def cleanup_rejected(
    root: Path,
    attempt_id: str,
    *,
    repository: Path | None = None,
    model_cache_root: Path | None = None,
    output_root: Path | None = None,
) -> None:
    """Delete rejected payload bytes and keep the reason record."""
    resolved = validate_runtime_root(
        root,
        repository=repository,
        model_cache_root=model_cache_root,
        output_root=output_root,
    )
    _check_attempt_id(attempt_id)
    rejected = _attempt(resolved, "rejected", attempt_id)
    if not rejected.is_dir() or rejected.is_symlink():
        raise RuntimeCacheError("missing-rejected")
    record = rejected / "rejection.json"
    if not record.is_file() or record.is_symlink():
        raise RuntimeCacheError("missing-reason")
    for child in list(rejected.iterdir()):
        if child.name == "rejection.json":
            continue
        if child.is_symlink() or child.is_file():
            child.unlink()
            continue
        if child.is_dir():
            shutil.rmtree(child)


def _move_rejected(resolved: Path, attempt_id: str, reasons: list[str]) -> None:
    source = _attempt(resolved, "quarantine", attempt_id)
    destination = _attempt(resolved, "rejected", attempt_id)
    if destination.exists():
        raise RuntimeCacheError("rejected-attempt")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        os.rename(source, destination)
    else:
        destination.mkdir(parents=True)
    payload = {
        "schemaVersion": "1.0.0",
        "attemptId": attempt_id,
        "reasons": list(dict.fromkeys(reasons)),
    }
    (destination / "rejection.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _attempt(root: Path, state: str, attempt_id: str) -> Path:
    return root / state / attempt_id


def _check_attempt_id(attempt_id: str) -> None:
    if not _ATTEMPT_ID.fullmatch(attempt_id) or ".." in Path(attempt_id).parts:
        raise RuntimeCacheError("path-traversal")


def _under(path: Path, prefix: Path) -> bool:
    return path == prefix or prefix in path.parents


def _distinct(lexical: Path, other: Path | None, code: str) -> None:
    if other is None:
        return
    if not other.is_absolute() or ".." in other.parts:
        raise RuntimeCacheError(code)
    absolute = Path(os.path.abspath(other))
    if _under(lexical, absolute) or _under(absolute, lexical):
        raise RuntimeCacheError(code)


def _same_identity(left: Path, right: Path) -> bool:
    left_stat = left.stat()
    right_stat = right.stat()
    return (left_stat.st_dev, left_stat.st_ino) == (right_stat.st_dev, right_stat.st_ino)
