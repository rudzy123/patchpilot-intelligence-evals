"""Candidate manifest loading, digests, and entry-point checks.

Track 2 provenance for the synthetic corpus stays in the corpus manifest.
This module binds deterministic test doubles only. It does not authorize a
model, a hosted provider, or a network client.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.network_guard import BoundaryError, assert_inside_repository
from patchpilot_intelligence_evals.schemas import repo_root, validate

_SHELL_CHARACTERS = frozenset(" \t\r\n;&|$`<>*?\\'\"!(){}[]")
_SIBLING_PARTS = frozenset({"patchpilot", "neural-from-scratch"})
_PROHIBITED_USE = (
    "model-training",
    "production-decision",
    "provider-execution",
    "state-mutation",
    "tenant-analysis",
)


class ManifestError(ValueError):
    """A candidate manifest failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def check_relative_path(relative: str) -> None:
    """Reject shell strings, absolute paths, traversal, and sibling checkouts."""
    if relative.startswith(("/", "\\")):
        raise ManifestError("absolute-path")
    if any(character in _SHELL_CHARACTERS for character in relative):
        raise ManifestError("shell-metacharacter")
    parts = Path(relative).parts
    if ".." in parts:
        raise ManifestError("path-traversal")
    if any(part in _SIBLING_PARTS for part in parts):
        raise ManifestError("sibling-repository")
    if not relative.endswith(".py"):
        raise ManifestError("entry-point-suffix")


def implementation_digest(paths: list[str], root: Path) -> str:
    """SHA-256 of sorted relative paths and their file bytes."""
    hasher = hashlib.sha256()
    for relative in sorted(set(paths)):
        check_relative_path(relative)
        try:
            assert_inside_repository(relative, root)
        except BoundaryError as exc:
            raise ManifestError("path-traversal") from exc
        file_path = root.joinpath(*Path(relative).parts)
        if file_path.is_symlink() or not file_path.is_file():
            raise ManifestError("missing-implementation")
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(file_path.read_bytes())
    return hasher.hexdigest()


def configuration_digest(requirements: dict[str, Any]) -> str:
    """SHA-256 of the canonical execution-requirements object."""
    return sha256_text(canonical_dumps(requirements))


def manifest_digest(document: dict[str, Any]) -> str:
    """SHA-256 of the canonical manifest with the digest field removed."""
    payload = {key: value for key, value in document.items() if key != "manifestDigest"}
    return sha256_text(canonical_dumps(payload))


def seal_manifest(document: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    """Return a copy with implementation, configuration, and manifest digests."""
    base = root if root is not None else repo_root()
    sealed = deepcopy(document)
    sealed.pop("implementationDigest", None)
    sealed.pop("configurationDigest", None)
    sealed.pop("manifestDigest", None)
    implementation = sealed.get("implementation")
    requirements = sealed.get("executionRequirements")
    if not isinstance(implementation, dict) or not isinstance(requirements, dict):
        raise ManifestError("missing-provenance")
    paths = [str(item) for item in implementation.get("implementationPaths", [])]
    entry_point = str(implementation.get("entryPoint", ""))
    check_relative_path(entry_point)
    if entry_point not in paths:
        raise ManifestError("entry-point-not-listed")
    sealed["implementationDigest"] = implementation_digest(paths, base)
    sealed["configurationDigest"] = configuration_digest(requirements)
    sealed["manifestDigest"] = manifest_digest(sealed)
    return validate_manifest(sealed, root=base)


def validate_manifest(document: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    """Validate one sealed manifest. The returned object is the same mapping."""
    validate("candidate-manifest", document)
    if document["license"] != "Apache-2.0" or document["source"] != "original-synthetic":
        raise ManifestError("missing-provenance")
    if set(document["prohibitedUse"]) != set(_PROHIBITED_USE):
        raise ManifestError("prohibited-use")
    base = root if root is not None else repo_root()
    implementation = document["implementation"]
    if implementation["interpreter"] != "current-python":
        raise ManifestError("interpreter")
    paths = [str(item) for item in implementation["implementationPaths"]]
    entry_point = str(implementation["entryPoint"])
    check_relative_path(entry_point)
    if entry_point not in paths:
        raise ManifestError("entry-point-not-listed")
    for relative in paths:
        check_relative_path(relative)
    if document["implementationDigest"] != implementation_digest(paths, base):
        raise ManifestError("implementation-digest")
    if document["configurationDigest"] != configuration_digest(document["executionRequirements"]):
        raise ManifestError("configuration-digest")
    if document["manifestDigest"] != manifest_digest(document):
        raise ManifestError("manifest-digest")
    return document


def load_manifest(relative_path: str, root: Path | None = None) -> dict[str, Any]:
    """Load a repository-relative manifest file and validate it."""
    base = root if root is not None else repo_root()
    _check_manifest_path(relative_path)
    try:
        assert_inside_repository(relative_path, base)
    except BoundaryError as exc:
        raise ManifestError("path-traversal") from exc
    file_path = base.joinpath(*Path(relative_path).parts)
    if file_path.is_symlink() or not file_path.is_file():
        raise ManifestError("missing-manifest")
    loaded = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ManifestError("manifest-type")
    return validate_manifest(loaded, root=base)


def _check_manifest_path(relative: str) -> None:
    if relative.startswith(("/", "\\")):
        raise ManifestError("absolute-path")
    if any(character in _SHELL_CHARACTERS for character in relative):
        raise ManifestError("shell-metacharacter")
    parts = Path(relative).parts
    if ".." in parts:
        raise ManifestError("path-traversal")
    if any(part in _SIBLING_PARTS for part in parts):
        raise ManifestError("sibling-repository")
    if not relative.endswith(".json"):
        raise ManifestError("manifest-suffix")
