"""Accepted review of the Track 6A hardened boundary.

Acceptance records the evaluated host. It does not authorize installation,
acquisition, selection, or inference.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_authorization import load_track6_authorization
from patchpilot_intelligence_evals.evidence_closure import load_closure
from patchpilot_intelligence_evals.execution_attestation import (
    RESIDUALS,
    load_attestation,
    load_profile,
    load_readiness,
)
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.runtime_security import load_assessment, load_authorization
from patchpilot_intelligence_evals.sandbox_capabilities import load_capability_report
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/track6a-implementation-review.json")
_DECISION = "hardened execution boundary approved with documented residuals"
_SCOPE = (
    "This approval accepts the Track 6A hardened execution boundary with documented "
    "residuals for the next controlled architectural Session only."
)
_READINESS_MEANING = (
    "Track 6B readiness means the hardened execution boundary is ready for the next "
    "controlled architectural Session."
)
_ACCEPTED_CONTROLS: tuple[tuple[str, str, str], ...] = (
    (
        "user-namespace",
        "capability-probe",
        "User namespace isolation was accepted as enforced on the evaluated host.",
    ),
    (
        "mount-namespace",
        "capability-probe",
        "Mount namespace isolation was accepted as enforced on the evaluated host.",
    ),
    (
        "pid-namespace",
        "capability-probe",
        "PID namespace isolation was accepted as enforced on the evaluated host.",
    ),
    (
        "network-namespace",
        "capability-probe",
        "Network namespace isolation was accepted as enforced on the evaluated host.",
    ),
    (
        "ipc-namespace",
        "capability-probe",
        "IPC namespace isolation was accepted as enforced on the evaluated host.",
    ),
    (
        "uts-namespace",
        "capability-probe",
        "UTS namespace isolation was accepted as enforced on the evaluated host.",
    ),
    (
        "cgroup-namespace",
        "capability-probe",
        "Cgroup namespace isolation was accepted as enforced on the evaluated host.",
    ),
    (
        "minimal-environment",
        "execution-profile",
        "The minimal constructed environment was accepted as enforced on the evaluated host.",
    ),
    (
        "read-only-verified-artifacts",
        "execution-profile",
        "Read-only synthetic artifacts were accepted as enforced on the evaluated host.",
    ),
    (
        "read-only-candidate-configuration",
        "execution-profile",
        "Read-only synthetic configuration was accepted as enforced on the evaluated host.",
    ),
    (
        "isolated-writable-results",
        "execution-profile",
        "Isolated writable results were accepted as enforced on the evaluated host.",
    ),
    (
        "no-gold-label-access",
        "execution-profile",
        "Hidden gold labels were accepted as enforced on the evaluated host.",
    ),
    (
        "no-prior-result-access",
        "execution-profile",
        "Hidden prior results were accepted as enforced on the evaluated host.",
    ),
    (
        "no-sibling-repository-access",
        "execution-profile",
        "Hidden sibling repositories were accepted as enforced on the evaluated host.",
    ),
    (
        "no-home-directory-access",
        "execution-profile",
        "Hidden home material was accepted as enforced on the evaluated host.",
    ),
    (
        "no-ssh-configuration-access",
        "execution-profile",
        "Hidden SSH material was accepted as enforced on the evaluated host.",
    ),
    (
        "no-cloud-credentials",
        "execution-profile",
        "Hidden cloud credentials were accepted as enforced on the evaluated host.",
    ),
    (
        "no-outbound-network",
        "execution-profile",
        "Host-network denial was accepted as enforced on the evaluated host.",
    ),
    (
        "dns-denial",
        "execution-profile",
        "DNS denial was accepted as enforced on the evaluated host.",
    ),
    (
        "ipv4-denial",
        "execution-profile",
        "IPv4 denial was accepted as enforced on the evaluated host.",
    ),
    (
        "ipv6-denial",
        "execution-profile",
        "IPv6 denial was accepted as enforced on the evaluated host.",
    ),
    (
        "host-loopback-denial",
        "execution-profile",
        "Host-loopback-service denial was accepted as enforced on the evaluated host.",
    ),
    (
        "external-unix-socket-denial",
        "execution-profile",
        "External Unix-socket denial was accepted as enforced on the evaluated host.",
    ),
    (
        "memory-limit",
        "execution-profile",
        "Cgroup MemoryMax was accepted as enforced on the evaluated host.",
    ),
    (
        "process-count-limit",
        "execution-profile",
        "Cgroup TasksMax was accepted as enforced on the evaluated host.",
    ),
    (
        "cpu-time-limit",
        "execution-profile",
        "The CPU-time limit was accepted as enforced on the evaluated host.",
    ),
    (
        "address-space-limit",
        "execution-profile",
        "The address-space limit was accepted as enforced on the evaluated host.",
    ),
    (
        "wall-clock-limit",
        "execution-profile",
        "The wall-clock limit was accepted as enforced on the evaluated host.",
    ),
    (
        "file-size-limit",
        "execution-profile",
        "The file-size limit was accepted as enforced on the evaluated host.",
    ),
    (
        "open-file-limit",
        "execution-profile",
        "The open-file limit was accepted as enforced on the evaluated host.",
    ),
    (
        "stdout-limit",
        "execution-profile",
        "The stdout limit was accepted as enforced on the evaluated host.",
    ),
    (
        "stderr-limit",
        "execution-profile",
        "The stderr limit was accepted as enforced on the evaluated host.",
    ),
    (
        "process-tree-termination",
        "execution-profile",
        "Complete process-tree cleanup was accepted as enforced on the evaluated host.",
    ),
    (
        "no-shell",
        "execution-profile",
        "Direct argument execution with no shell was accepted as enforced on the evaluated host.",
    ),
)
_ACCEPTED_RESIDUALS: tuple[tuple[str, str], ...] = (
    (
        "sandbox-local-loopback",
        "Sandbox-local loopback remains available inside the isolated namespace.",
    ),
    (
        "seccomp-unsupported",
        "Seccomp is unsupported because enforcement was not proven.",
    ),
    ("unshare-failed", "Direct unshare failed."),
    ("podman-unavailable", "Rootless Podman is unavailable."),
    ("docker-unavailable", "Rootless Docker is unavailable."),
    ("direct-cgroup-delegation-failed", "Direct cgroup delegation failed."),
    (
        "single-uid-user-namespace",
        "The user namespace uses a single UID map.",
    ),
    ("numeric-uid-in-mount-options", "Numeric UID mount options remain."),
    (
        "candidate-format-gap",
        (
            "The authorized runtime supports ONNX while the current candidate contract "
            "remains safetensors."
        ),
    ),
    (
        "rlimit-nproc-not-private",
        "RLIMIT_NPROC is not a private process-count boundary.",
    ),
    (
        "acquisition-remains-not-authorized",
        "Track 6 acquisition remains not authorized.",
    ),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "runtime installation",
    "model or tokenizer acquisition",
    "model conversion",
    "candidate selection",
    "real inference",
    "evaluation-gate changes",
    "shadow mode",
    "PatchPilot production composition",
)


class Track6AReviewError(ValueError):
    """A Track 6A review check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def build_review() -> dict[str, Any]:
    """Build the accepted Track 6A review and seal it with the shared digest function."""
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "reviewStatus": "accepted-by-principal-systems-architect",
        "reviewDate": "2026-11-10",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "decision": _DECISION,
        "authorizedScope": _SCOPE,
        "readinessMeaning": _READINESS_MEANING,
        "profileId": "linux-bwrap-systemd-v1",
        "profileVersion": "1.0.0",
        "mechanism": "bubblewrap+systemd-user-scope",
        "runtimeId": "onnxruntime",
        "versionTag": "v1.31.1",
        "immutableRevision": "6af1a932e2286d5c58166085d24c68783033edee",
        "artifactFormat": "onnx",
        "installationAuthorized": False,
        "installedDuringSession": False,
        "candidateFormatGap": True,
        "candidateDecision": "no-selection",
        "track6Authorization": "not-authorized",
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
        "acceptedControls": [
            {"controlId": control_id, "source": source, "statement": statement}
            for control_id, source, statement in _ACCEPTED_CONTROLS
        ],
        "acceptedResiduals": [
            {"residualId": residual_id, "statement": statement}
            for residual_id, statement in _ACCEPTED_RESIDUALS
        ],
        "notAuthorized": list(_NOT_AUTHORIZED),
    }
    document["reviewDigest"] = review_digest(document)
    return validate_review(document)


def validate_review(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the review against its schema, digest, and the live closed records."""
    validate("track6a-implementation-review", document)
    _reject_identity(document)
    if document["reviewDigest"] != review_digest(document):
        raise Track6AReviewError("review-digest")
    if document["readinessMeaning"] != _READINESS_MEANING:
        raise Track6AReviewError("readiness-meaning")
    if list(document["notAuthorized"]) != list(_NOT_AUTHORIZED):
        raise Track6AReviewError("not-authorized")
    if document["locallyObservedArtifactDigests"]:
        raise Track6AReviewError("local-digest")
    _require_controls(document["acceptedControls"])
    _require_residuals(document["acceptedResiduals"])
    _require_live_outcomes(document)
    return document


def load_review(root: Path | None = None) -> dict[str, Any]:
    """Load the committed Track 6A review and require it to match the sealed record."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track6AReviewError("record-type")
    document = validate_review(loaded)
    if document != build_review():
        raise Track6AReviewError("review-drift")
    return document


def _require_controls(items: list[dict[str, Any]]) -> None:
    observed = [
        (str(item["controlId"]), str(item["source"]), str(item["statement"])) for item in items
    ]
    if tuple(observed) != _ACCEPTED_CONTROLS:
        raise Track6AReviewError("control-set")


def _require_residuals(items: list[dict[str, Any]]) -> None:
    observed = [(str(item["residualId"]), str(item["statement"])) for item in items]
    if tuple(observed) != _ACCEPTED_RESIDUALS:
        raise Track6AReviewError("residual-set")
    if tuple(item[0] for item in observed) != RESIDUALS:
        raise Track6AReviewError("residual-set")


def _require_live_outcomes(document: dict[str, Any]) -> None:
    profile = load_profile()
    report = load_capability_report()
    authorized = load_authorization()
    assessment = load_assessment()
    readiness = load_readiness()
    attestation = load_attestation()
    track6 = load_track6_authorization()
    closure = load_closure()
    if (
        profile["profileId"] != document["profileId"]
        or profile["profileVersion"] != document["profileVersion"]
        or profile["mechanism"] != document["mechanism"]
    ):
        raise Track6AReviewError("profile-outcome")
    if profile["productionReady"] is not False or profile["realModelExecuted"] is not False:
        raise Track6AReviewError("execution-claim")
    probes = {str(item["probeId"]): item for item in report["probes"]}
    controls = {str(item["controlId"]): item for item in profile["controls"]}
    for control_id, source, _statement in _ACCEPTED_CONTROLS:
        if source == "capability-probe":
            probe = probes[control_id]
            proven = probe["disposition"] == "enforced" and probe["evidence"] == "behavior-proven"
            if not proven:
                raise Track6AReviewError("control-outcome")
        elif controls[control_id]["disposition"] != "enforced":
            raise Track6AReviewError("control-outcome")
    if authorized["runtimeId"] != document["runtimeId"]:
        raise Track6AReviewError("runtime-outcome")
    if authorized["versionTag"] != document["versionTag"]:
        raise Track6AReviewError("runtime-outcome")
    if authorized["immutableRevision"] != document["immutableRevision"]:
        raise Track6AReviewError("runtime-outcome")
    if authorized["artifactFormat"] != document["artifactFormat"]:
        raise Track6AReviewError("runtime-outcome")
    if authorized["authorizationOutcome"] != "authorized":
        raise Track6AReviewError("runtime-outcome")
    if (
        authorized["installationAuthorized"] is not False
        or authorized["installedDuringSession"] is not False
        or assessment["installedDuringSession"] is not False
    ):
        raise Track6AReviewError("installation")
    if authorized["candidateFormatGap"] is not True or authorized["candidateSelected"] is not False:
        raise Track6AReviewError("format-gap")
    if authorized["locallyObservedArtifactDigests"] or authorized["realModelExecuted"] is not False:
        raise Track6AReviewError("execution-claim")
    if authorized["productionReady"] is not False:
        raise Track6AReviewError("production-ready")
    if (
        authorized["acquisitionStatus"] != "not-acquired"
        or authorized["executionStatus"] != "not-executed"
    ):
        raise Track6AReviewError("acquisition-status")
    if readiness["residualIds"] != [residual_id for residual_id, _statement in _ACCEPTED_RESIDUALS]:
        raise Track6AReviewError("residual-outcome")
    if readiness["readiness"] != "ready" or readiness["blockers"]:
        raise Track6AReviewError("readiness-outcome")
    if (
        readiness["selectionOutcome"] != document["candidateDecision"]
        or closure["selectionOutcome"] != document["candidateDecision"]
    ):
        raise Track6AReviewError("candidate-outcome")
    if closure["qualifyingCandidateCount"] != 0:
        raise Track6AReviewError("candidate-outcome")
    if (
        readiness["installationAuthorized"] is not False
        or readiness["candidateSelected"] is not False
        or readiness["localModelArtifactDigests"]
    ):
        raise Track6AReviewError("readiness-outcome")
    if track6["authorizationOutcome"] != document["track6Authorization"]:
        raise Track6AReviewError("track6-outcome")
    runtime_identity = f"{document['runtimeId']}@{document['versionTag']}"
    if attestation["runtimeAuthorizationId"] != runtime_identity:
        raise Track6AReviewError("attestation-outcome")
    for record in (readiness, attestation, report, track6, closure):
        if record["productionReady"] is not False:
            raise Track6AReviewError("production-ready")
        if record.get("realModelExecuted", False) is not False:
            raise Track6AReviewError("execution-claim")
        if (
            record["acquisitionStatus"] != "not-acquired"
            or record["executionStatus"] != "not-executed"
        ):
            raise Track6AReviewError("acquisition-status")


def _reject_identity(document: dict[str, Any]) -> None:
    text = json.dumps(document)
    if "/home/" in text or "/Users/" in text or "AWS_SECRET" in text or "PRIVATE KEY" in text:
        raise Track6AReviewError("identity")
