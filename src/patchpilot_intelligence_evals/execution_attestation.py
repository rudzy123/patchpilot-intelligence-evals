"""Closed execution attestations and the Track 6B readiness decision."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from patchpilot_intelligence_evals.resource_controls import DEFAULT_LIMITS
from patchpilot_intelligence_evals.runtime_security import (
    RuntimeSecurityError,
    load_authorization,
    validate_authorization,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

PROFILE_ID = "linux-bwrap-systemd-v1"
PROFILE_VERSION = "1.0.0"
MECHANISM = "bubblewrap+systemd-user-scope"
BUBBLEWRAP_VERSION = "0.11.1"
SYSTEMD_VERSION = "259"
REQUIRED_CONTROLS: tuple[str, ...] = (
    "unprivileged-execution",
    "minimal-environment",
    "read-only-verified-artifacts",
    "read-only-candidate-configuration",
    "isolated-writable-results",
    "no-gold-label-access",
    "no-prior-result-access",
    "no-sibling-repository-access",
    "no-home-directory-access",
    "no-ssh-configuration-access",
    "no-cloud-credentials",
    "no-outbound-network",
    "host-loopback-denial",
    "dns-denial",
    "ipv4-denial",
    "ipv6-denial",
    "external-unix-socket-denial",
    "process-count-limit",
    "cpu-time-limit",
    "memory-limit",
    "address-space-limit",
    "wall-clock-limit",
    "file-size-limit",
    "open-file-limit",
    "stdout-limit",
    "stderr-limit",
    "process-tree-termination",
    "no-shell",
    "explicit-working-directory",
)
RESIDUALS: tuple[str, ...] = (
    "sandbox-local-loopback",
    "seccomp-unsupported",
    "unshare-failed",
    "podman-unavailable",
    "docker-unavailable",
    "direct-cgroup-delegation-failed",
    "single-uid-user-namespace",
    "numeric-uid-in-mount-options",
    "candidate-format-gap",
    "rlimit-nproc-not-private",
    "acquisition-remains-not-authorized",
)
_PROFILE = Path("candidates/authorization/hardened-execution-profile.json")
_READINESS = Path("candidates/authorization/track6b-readiness.json")
_ATTESTATION = Path("candidates/authorization/hardened-execution-attestation.json")
_VERDICT_READY = "TRACK 6B HARDENED ACQUISITION READY WITH DOCUMENTED RESIDUALS"
_VERDICT_NOT_READY = "TRACK 6B HARDENED ACQUISITION NOT READY"


class AttestationError(ValueError):
    """An attestation or readiness record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_profile(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the hardened profile and its limit identity."""
    validate("hardened-execution-profile", document)
    _reject_identity(document)
    if document["realModelExecuted"] is not False or document["productionReady"] is not False:
        raise AttestationError("execution-claim")
    if document["memoryMechanism"] != "cgroup-memory-max":
        raise AttestationError("memory-mechanism")
    if document["addressSpaceMechanism"] != "rlimit-as":
        raise AttestationError("address-space-mechanism")
    if document["processCountMechanism"] != "cgroup-tasks-max":
        raise AttestationError("process-count-mechanism")
    identifiers = [str(item["controlId"]) for item in document["controls"]]
    if len(identifiers) != len(set(identifiers)):
        raise AttestationError("duplicate-control")
    limits = document["limits"]
    expected = {
        "memoryMaxBytes": DEFAULT_LIMITS.memory_max_bytes,
        "tasksMax": DEFAULT_LIMITS.tasks_max,
        "cpuSeconds": DEFAULT_LIMITS.cpu_seconds,
        "addressSpaceBytes": DEFAULT_LIMITS.address_space_bytes,
        "fileSizeBytes": DEFAULT_LIMITS.file_size_bytes,
        "openFiles": DEFAULT_LIMITS.open_files,
        "wallClockSeconds": DEFAULT_LIMITS.wall_clock_seconds,
        "stdoutBytes": DEFAULT_LIMITS.stdout_bytes,
        "stderrBytes": DEFAULT_LIMITS.stderr_bytes,
        "retries": 0,
    }
    if limits != expected:
        raise AttestationError("limit-drift")
    return document


def validate_attestation(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one attestation. It cannot claim a real model ran."""
    validate("hardened-execution-attestation", document)
    _reject_identity(document)
    if document["realModelExecuted"] is not False or document["productionReady"] is not False:
        raise AttestationError("execution-claim")
    if document["attempts"] != 1:
        raise AttestationError("retry")
    return document


def validate_readiness(document: dict[str, Any]) -> dict[str, Any]:
    """Validate a readiness record without treating residuals as enforcement."""
    validate("track6b-readiness", document)
    _reject_identity(document)
    if document["selectionOutcome"] != "no-selection":
        raise AttestationError("selection")
    if document["localModelArtifactDigests"]:
        raise AttestationError("model-digest")
    if document["readiness"] == "ready" and document["blockers"]:
        raise AttestationError("ready-blocker")
    if document["readiness"] == "not-ready" and not document["blockers"]:
        raise AttestationError("missing-blocker")
    return document


def decide_readiness(
    profile: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any]:
    """Return not-ready unless every required control and one runtime are proven."""
    checked = validate_profile(profile)
    try:
        authorized = validate_authorization(authorization)
    except RuntimeSecurityError as exc:
        raise AttestationError(exc.code) from None
    enforced = {
        str(item["controlId"]) for item in checked["controls"] if item["disposition"] == "enforced"
    }
    blockers = [control for control in REQUIRED_CONTROLS if control not in enforced]
    if authorized["authorizationOutcome"] != "authorized":
        blockers.append("runtime-authorization")
    readiness = "ready" if not blockers else "not-ready"
    verdict = _VERDICT_READY if readiness == "ready" else _VERDICT_NOT_READY
    return validate_readiness(
        {
            "schemaVersion": "1.0.0",
            "productionReady": False,
            "realModelExecuted": False,
            "selectionOutcome": "no-selection",
            "acquisitionStatus": "not-acquired",
            "executionStatus": "not-executed",
            "readiness": readiness,
            "verdict": verdict,
            "profileId": checked["profileId"],
            "profileVersion": checked["profileVersion"],
            "runtimeAuthorizationOutcome": authorized["authorizationOutcome"],
            "runtimeId": authorized["runtimeId"],
            "blockers": blockers,
            "residualIds": list(RESIDUALS),
            "localModelArtifactDigests": [],
            "candidateSelected": False,
            "installationAuthorized": False,
        }
    )


def build_attestation(
    *,
    profile: dict[str, Any],
    authorization: dict[str, Any],
    fixture_name: str,
    fixture_bytes: bytes,
    input_bytes: bytes,
    stdout: bytes,
    exit_classification: str,
    network_result: str,
    filesystem_result: str,
    cleanup_result: str,
    executed_at: datetime,
    repository_commit: str,
) -> dict[str, Any]:
    """Build one attestation. Digests replace stream contents and paths."""
    checked = validate_profile(profile)
    authorized = validate_authorization(authorization)
    grouped = _grouped(checked["controls"])
    runtime_id = authorized["runtimeId"]
    version = authorized["versionTag"]
    authorization_id = None if runtime_id is None else f"{runtime_id}@{version}"
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "profileId": checked["profileId"],
        "profileVersion": checked["profileVersion"],
        "mechanism": checked["mechanism"],
        "mechanismVersion": checked["bubblewrapVersion"],
        "operatingSystemFamily": checked["operatingSystemFamily"],
        "architecture": checked["architecture"],
        "enforcedControlIds": grouped["enforced"],
        "unavailableControlIds": grouped["unavailable"],
        "failedControlIds": grouped["failed"],
        "unsupportedControlIds": grouped["unsupported"],
        "runtimeAuthorizationId": authorization_id,
        "fixtureIdentity": fixture_name,
        "fixtureDigest": _sha256(fixture_bytes),
        "inputDigest": _sha256(input_bytes),
        "outputDigest": _sha256(stdout),
        "exitClassification": exit_classification,
        "attempts": 1,
        "resourceLimits": checked["limits"],
        "networkTestResult": network_result,
        "filesystemVisibilityResult": filesystem_result,
        "processTreeCleanupResult": cleanup_result,
        "executedAt": executed_at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repositoryCommit": repository_commit,
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
    }
    return validate_attestation(document)


def repository_commit(root: Path | None = None) -> str:
    """Return the current commit hash without reading git identity configuration."""
    base = root if root is not None else repo_root()
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        shell=False,
        capture_output=True,
        text=True,
        cwd=base,
    )
    if completed.returncode != 0:
        raise AttestationError("commit")
    commit = completed.stdout.strip()
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        raise AttestationError("commit")
    return commit


def load_profile(root: Path | None = None) -> dict[str, Any]:
    """Load the committed hardened profile."""
    return _load(root, _PROFILE, validate_profile)


def load_readiness(root: Path | None = None) -> dict[str, Any]:
    """Load the readiness record and require it to match the profile and runtime."""
    base = root if root is not None else repo_root()
    document = _load(base, _READINESS, validate_readiness)
    if document != decide_readiness(load_profile(base), load_authorization(base)):
        raise AttestationError("readiness-drift")
    return document


def load_attestation(root: Path | None = None) -> dict[str, Any]:
    """Load the committed synthetic attestation."""
    return _load(root, _ATTESTATION, validate_attestation)


def _grouped(controls: list[dict[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {
        "enforced": [],
        "unavailable": [],
        "failed": [],
        "unsupported": [],
    }
    for item in controls:
        disposition = str(item["disposition"])
        if disposition not in grouped:
            raise AttestationError("disposition")
        grouped[disposition].append(str(item["controlId"]))
    return grouped


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _reject_identity(document: dict[str, Any]) -> None:
    text = json.dumps(document)
    if "/home/" in text or "/Users/" in text or "AWS_SECRET" in text or "PRIVATE KEY" in text:
        raise AttestationError("identity")


def _load(root: Path | None, relative: Path, checker: Any) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AttestationError("record-type")
    return cast(dict[str, Any], checker(cast(dict[str, Any], loaded)))
