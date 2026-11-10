"""Repository-external artifact cache.

Quarantine cannot be executed, loaded, or promoted until every inventory check
passes. Rejected attempts stay rejected. This module does not download a model
or create a persistent cache inside the Git repository.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_verification import (
    VerificationError,
    assert_verified_identity,
    inspect_attempt,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_ATTEMPT_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
_SIBLING_NAMES = ("neural-from-scratch", "patchpilot")
_ROOT_REQUIREMENTS = frozenset(
    {
        "explicit-root",
        "outside-git-repository",
        "outside-sibling-repositories",
        "reject-traversal",
        "reject-symlink-escape",
        "reject-repository-contained-root",
        "stable-root-during-validation",
    }
)
_POLICY = Path("candidates/authorization/external-artifact-cache-policy.json")


class CacheError(ValueError):
    """A cache root or attempt failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_cache_policy(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the closed cache policy. It stores no filesystem path."""
    validate("external-artifact-cache-policy", document)
    if document["siblingRepositoryNames"] != list(_SIBLING_NAMES):
        raise CacheError("sibling-names")
    if set(document["rootRequirements"]) != _ROOT_REQUIREMENTS:
        raise CacheError("root-requirements")
    if document["productionReady"] is not False:
        raise CacheError("production-ready")
    if document["acquisitionStatus"] != "not-acquired":
        raise CacheError("acquisition-status")
    if document["executionStatus"] != "not-executed":
        raise CacheError("execution-status")
    return document


def load_cache_policy(root: Path | None = None) -> dict[str, Any]:
    """Load the committed cache policy."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _POLICY).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise CacheError("policy-type")
    return validate_cache_policy(loaded)


def validate_cache_root(
    root: Path,
    *,
    repository: Path | None = None,
    sibling_roots: tuple[Path, ...] | None = None,
    probe: Callable[[], None] | None = None,
) -> Path:
    """Resolve an explicit cache root or reject containment, traversal, and links."""
    repository_path = repository if repository is not None else repo_root()
    if not root.is_absolute():
        raise CacheError("relative-root")
    if ".." in root.parts:
        raise CacheError("path-traversal")
    lexical = Path(os.path.abspath(root))
    if ".." in lexical.parts:
        raise CacheError("path-traversal")
    repository_lexical = Path(os.path.abspath(repository_path))
    repository_resolved = repository_path.resolve()
    prefixes = sibling_roots
    if prefixes is None:
        prefixes = tuple(repository_resolved.parent / name for name in _SIBLING_NAMES)
    for prefix in prefixes:
        absolute = Path(os.path.abspath(prefix))
        if _under(lexical, absolute):
            raise CacheError("sibling-root")
    if _under(lexical, repository_lexical) or _under(lexical, repository_resolved):
        raise CacheError("repository-root")
    if not root.exists() or not root.is_dir():
        raise CacheError("missing-root")
    if root.is_symlink():
        raise CacheError("symlink-escape")
    resolved = root.resolve(strict=True)
    for prefix in prefixes:
        if _under(resolved, Path(os.path.abspath(prefix))):
            raise CacheError("sibling-root")
    if _under(resolved, repository_resolved):
        raise CacheError("repository-root")
    before = root.stat()
    resolved_before = root.resolve()
    if probe is not None:
        probe()
    if not root.exists():
        raise CacheError("root-changed")
    after = root.stat()
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        raise CacheError("root-changed")
    if root.resolve() != resolved_before:
        raise CacheError("root-changed")
    return resolved


def place_quarantine(
    root: Path,
    attempt_id: str,
    files: Mapping[str, bytes],
    *,
    repository: Path | None = None,
) -> Path:
    """Write synthetic bytes into a new quarantine attempt."""
    resolved = validate_cache_root(root, repository=repository)
    _check_attempt_id(attempt_id)
    if _attempt(resolved, "rejected", attempt_id).exists():
        raise CacheError("rejected-attempt")
    if _attempt(resolved, "verified", attempt_id).exists():
        raise CacheError("already-verified")
    destination = _attempt(resolved, "quarantine", attempt_id)
    if destination.exists():
        raise CacheError("attempt-exists")
    destination.mkdir(parents=True)
    for name, payload in files.items():
        if not isinstance(payload, bytes):
            raise CacheError("payload-type")
        target = destination / name
        if target.parent != destination or target.is_symlink():
            raise CacheError("path-traversal")
        target.write_bytes(payload)
    return destination


def promote_attempt(
    root: Path,
    attempt_id: str,
    expected: list[dict[str, Any]],
    *,
    repository: Path | None = None,
) -> dict[str, Any]:
    """Verify quarantine and publish it only when every check passes."""
    resolved = validate_cache_root(root, repository=repository)
    _check_attempt_id(attempt_id)
    if _attempt(resolved, "rejected", attempt_id).exists():
        raise CacheError("rejected-attempt")
    source = _attempt(resolved, "quarantine", attempt_id)
    if not source.is_dir() or source.is_symlink():
        raise CacheError("missing-quarantine")
    try:
        manifest = inspect_attempt(
            source,
            expected,
            attempt_id=attempt_id,
            remote_code_required=False,
            tokenizer_provenance_recorded=True,
            license_reference_recorded=True,
        )
    except VerificationError as exc:
        _move_rejected(resolved, attempt_id, [exc.code])
        raise CacheError(exc.code) from exc
    if manifest["verificationState"] != "verified":
        _move_rejected(resolved, attempt_id, list(manifest["reasonCodes"]))
        raise CacheError(str(manifest["reasonCodes"][0]))
    destination = _attempt(resolved, "verified", attempt_id)
    destination.mkdir(parents=True)
    for item in manifest["observedFiles"]:
        name = str(item["fileName"])
        file_path = source / name
        if file_path.is_symlink() or not file_path.is_file():
            shutil.rmtree(destination)
            _move_rejected(resolved, attempt_id, ["symlink-escape"])
            raise CacheError("symlink-escape")
        (destination / name).write_bytes(file_path.read_bytes())
    record = resolved / "verified" / f"{attempt_id}.verification.json"
    record.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(source)
    validate_cache_root(root, repository=repository)
    assert_verified_identity(destination, manifest)
    return manifest


def reject_attempt(
    root: Path,
    attempt_id: str,
    reasons: list[str],
    *,
    repository: Path | None = None,
) -> None:
    """Mark an attempt rejected and retain the reason codes."""
    resolved = validate_cache_root(root, repository=repository)
    _check_attempt_id(attempt_id)
    if not reasons:
        raise CacheError("missing-reason")
    source = _attempt(resolved, "quarantine", attempt_id)
    if not source.is_dir():
        raise CacheError("missing-quarantine")
    _move_rejected(resolved, attempt_id, reasons)


def assert_may_consider_for_execution(
    root: Path,
    attempt_id: str,
    *,
    repository: Path | None = None,
) -> None:
    """Allow consideration of a verified attempt only. This does not execute it."""
    resolved = validate_cache_root(root, repository=repository)
    _check_attempt_id(attempt_id)
    if _attempt(resolved, "quarantine", attempt_id).exists():
        raise CacheError("quarantine-execution")
    if _attempt(resolved, "rejected", attempt_id).exists():
        raise CacheError("rejected-execution")
    verified = _attempt(resolved, "verified", attempt_id)
    if not verified.is_dir() or verified.is_symlink():
        raise CacheError("not-verified")


def cleanup_rejected(
    root: Path,
    attempt_id: str,
    *,
    repository: Path | None = None,
) -> None:
    """Delete rejected payload bytes and keep the reason record."""
    resolved = validate_cache_root(root, repository=repository)
    _check_attempt_id(attempt_id)
    rejected = _attempt(resolved, "rejected", attempt_id)
    if not rejected.is_dir() or rejected.is_symlink():
        raise CacheError("missing-rejected")
    record = rejected / "rejection.json"
    if not record.is_file() or record.is_symlink():
        raise CacheError("missing-reason")
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
        raise CacheError("rejected-attempt")
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
        raise CacheError("path-traversal")


def _under(path: Path, prefix: Path) -> bool:
    return path == prefix or prefix in path.parents
