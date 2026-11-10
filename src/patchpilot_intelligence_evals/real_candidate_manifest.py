"""Closed manifests for one offline local model.

Deterministic test doubles stay on the fixture manifest. This module does not
download weights, contact a model hub, or execute a model. Before Track 6 the
only valid state is not acquired, not executed, and not production ready.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_manifest import ManifestError
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.network_guard import BoundaryError, assert_inside_repository
from patchpilot_intelligence_evals.schemas import repo_root, validate

_SHELL_CHARACTERS = frozenset(" \t\r\n;&|$`<>*?\\'\"!(){}[]")
_SIBLING_PARTS = frozenset({"patchpilot", "neural-from-scratch"})
_PROHIBITED_USE = frozenset(
    {
        "hosted-inference",
        "model-training",
        "production-decision",
        "provider-execution",
        "state-mutation",
        "tenant-analysis",
        "trust-remote-code",
        "weight-redistribution",
    }
)
_BANNED_KEYS = frozenset({"apikey", "credential", "hostname", "password", "secret", "username"})
_MAX_ARTIFACT_BYTES = 8589934592
_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_RUNTIME_RECORD = Path("candidates/authorization/runtime-authorization.json")


def manifest_digest(document: dict[str, Any]) -> str:
    """SHA-256 of the canonical manifest with the digest field removed."""
    payload = {key: value for key, value in document.items() if key != "manifestDigest"}
    return sha256_text(canonical_dumps(payload))


def seal_offline_manifest(
    document: dict[str, Any],
    *,
    authorized_runtime_ids: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Return a copy whose manifest digest matches the other fields."""
    sealed = deepcopy(document)
    sealed.pop("manifestDigest", None)
    sealed["manifestDigest"] = manifest_digest(sealed)
    return validate_offline_manifest(sealed, authorized_runtime_ids=authorized_runtime_ids)


def validate_offline_manifest(
    document: dict[str, Any],
    *,
    authorized_runtime_ids: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Validate one not-acquired offline-local-model manifest."""
    validate("offline-local-model-manifest", document)
    if document["candidateKind"] != "offline-local-model":
        raise ManifestError("candidate-kind")
    if document["manifestDigest"] != manifest_digest(document):
        raise ManifestError("manifest-digest")
    _reject_sensitive(document)
    if document["sourceCodeLicenseApplies"] is not isinstance(
        document["sourceCodeLicenseUrl"], str
    ):
        raise ManifestError("missing-provenance")
    if not document["weightLicenseUrl"] or not document["tokenizerLicenseUrl"]:
        raise ManifestError("missing-provenance")
    if not document["tokenizerSourceUrl"] or not document["officialSourceUrl"]:
        raise ManifestError("missing-provenance")
    names = _expected_names(document["expectedArtifacts"])
    if len(names) != len(document["expectedArtifacts"]):
        raise ManifestError("duplicate-artifact")
    total = sum(int(item["expectedBytes"]) for item in document["expectedArtifacts"])
    if total > _MAX_ARTIFACT_BYTES:
        raise ManifestError("resource-envelope")
    if document["observedArtifacts"] or document["locallyVerifiedArtifactIdentities"]:
        raise ManifestError("fabricated-digest")
    if document["acquisitionStatus"] != "not-acquired":
        raise ManifestError("acquisition-status")
    if document["executionStatus"] != "not-executed":
        raise ManifestError("execution-status")
    if document["productionReady"] is not False:
        raise ManifestError("production-ready")
    if document["remoteCodePolicy"] != "prohibited":
        raise ManifestError("remote-code")
    if document["telemetryPolicy"] != "disabled":
        raise ManifestError("telemetry")
    if document["quantization"] != "none":
        raise ManifestError("quantization")
    _check_runtime(str(document["runtimeId"]), authorized_runtime_ids)
    return document


def load_offline_manifest(
    relative_path: str,
    *,
    root: Path | None = None,
    authorized_runtime_ids: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Load a repository-relative offline manifest and validate it."""
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
    return validate_offline_manifest(loaded, authorized_runtime_ids=authorized_runtime_ids)


def _expected_names(artifacts: list[dict[str, Any]]) -> set[str]:
    names: set[str] = set()
    for item in artifacts:
        name = str(item["fileName"])
        if "/" in name or "\\" in name or ".." in Path(name).parts:
            raise ManifestError("path-traversal")
        names.add(name)
    return names


def _check_runtime(runtime_id: str, authorized_runtime_ids: frozenset[str] | None) -> None:
    """Allow the not-authorized illustration id, and no other unapproved runtime."""
    if runtime_id == "none":
        return
    authorized = (
        authorized_runtime_ids if authorized_runtime_ids is not None else _authorized_runtime_ids()
    )
    if runtime_id not in authorized:
        raise ManifestError("unauthorized-runtime")


def _authorized_runtime_ids() -> frozenset[str]:
    path = repo_root() / _RUNTIME_RECORD
    if not path.is_file():
        return frozenset({"none"})
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ManifestError("runtime-authorization")
    outcome = loaded.get("authorizationOutcome")
    if outcome == "no-runtime":
        return frozenset({"none"})
    if outcome == "authorized":
        runtime_id = loaded.get("runtimeId")
        if isinstance(runtime_id, str) and runtime_id not in {"", "none"}:
            return frozenset({runtime_id})
    raise ManifestError("runtime-authorization")


def _reject_sensitive(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in _BANNED_KEYS:
                raise ManifestError("prohibited-identifier")
            _reject_sensitive(item)
        return
    if isinstance(value, list):
        for item in value:
            _reject_sensitive(item)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if "/home/" in lowered or "/users/" in lowered:
            raise ManifestError("identity-bearing-path")
        if "-----begin " in lowered or _IPV4.search(value):
            raise ManifestError("prohibited-identifier")


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
