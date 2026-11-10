"""Accepted review of the Track 5 boundary. Acceptance does not authorize acquisition."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_authorization import load_track6_authorization
from patchpilot_intelligence_evals.artifact_verification import load_verification_template
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.evidence_closure import load_closure
from patchpilot_intelligence_evals.isolation_profile import load_profile
from patchpilot_intelligence_evals.real_candidate_manifest import load_offline_manifest
from patchpilot_intelligence_evals.runtime_authorization import load_authorization
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/track5-implementation-review.json")
_ILLUSTRATION = "candidates/templates/offline-local-model-manifest.json"
_COMPONENTS: tuple[tuple[str, str, str], ...] = (
    (
        "real-candidate-boundary",
        "approved",
        "The real-candidate boundary is approved. The offline illustration stays not-authorized.",
    ),
    (
        "external-artifact-cache-boundary",
        "approved",
        "The external artifact-cache boundary is approved.",
    ),
    (
        "synthetic-artifact-verification",
        "approved-with-documented-limitations",
        (
            "Synthetic artifact-verification controls are approved. "
            "Executable sniffing is not malware detection."
        ),
    ),
)
_UNMET: tuple[tuple[str, str], ...] = (
    ("one-qualifying-candidate", "One qualifying candidate."),
    ("one-authorized-runtime", "One authorized runtime."),
    (
        "isolation-without-acquisition-blocker",
        "Isolation without an acquisition blocker.",
    ),
    (
        "immutable-revision-and-source",
        "Immutable revision and source satisfying the selected-candidate contract.",
    ),
    (
        "tokenizer-provenance",
        "Resolved tokenizer provenance and licensing.",
    ),
    (
        "weight-license-and-commercial-use",
        "Resolved weight licensing and commercial-use terms.",
    ),
    (
        "redistribution-unnecessary",
        "Confirmation that redistribution is unnecessary or explicitly authorized.",
    ),
)
_PASSING: tuple[tuple[str, str], ...] = (
    ("cache-and-verification", "Cache and verification boundary."),
    ("hardware-fit", "Hardware fit."),
    ("no-gate-change", "No evaluation-gate change."),
)
_RESIDUALS: tuple[tuple[str, str], ...] = (
    (
        "namespace-or-container-controls",
        "Nine isolation controls still require namespace or container enforcement.",
    ),
    (
        "executable-sniffing-not-malware-detection",
        "Executable-content sniffing is not malware detection.",
    ),
    (
        "python-hooks-not-os-network-isolation",
        "Python network hooks are not operating-system network isolation.",
    ),
    (
        "rlimit-as-address-space",
        "RLIMIT_AS limits address space rather than resident memory.",
    ),
    ("rlimit-nproc-per-user", "RLIMIT_NPROC is a per-user control."),
    (
        "sandbox-process-group-timeout",
        (
            "A restricted verification sandbox that cannot signal a process group may "
            "classify an intended timeout as internal-harness-failure."
        ),
    ),
    (
        "clean-evaluation-output-root",
        (
            "Ignored pre-existing build output must be removed or an empty explicit "
            "output root must be used before reproducible evaluation commands."
        ),
    ),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "Track 6 acquisition",
    "a candidate",
    "a runtime",
    "model or tokenizer download",
    "model execution",
    "quantization",
    "gate changes",
    "shadow mode",
    "PatchPilot production composition",
)


class ReviewError(ValueError):
    """A Track 5 review check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def review_digest(document: dict[str, Any]) -> str:
    """SHA-256 of the canonical review with the digest field removed."""
    payload = {key: value for key, value in document.items() if key != "reviewDigest"}
    return sha256_text(canonical_dumps(payload))


def build_review() -> dict[str, Any]:
    """Build the accepted fail-closed review and seal its digest."""
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "reviewStatus": "accepted-by-principal-systems-architect",
        "reviewDate": "2026-11-10",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "decision": "track 5 boundary approved and acquisition withheld",
        "authorizedScope": (
            "This approval accepts the Track 5 fail-closed implementation record only."
        ),
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "runtimeDecision": "no-runtime",
        "candidateDecision": "no-selection",
        "track6Authorization": "not-authorized",
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
        "unmetPrerequisites": [
            {"prerequisiteId": prerequisite_id, "statement": statement}
            for prerequisite_id, statement in _UNMET
        ],
        "passingPrerequisites": [
            {"prerequisiteId": prerequisite_id, "statement": statement}
            for prerequisite_id, statement in _PASSING
        ],
        "acceptedResiduals": [
            {"residualId": residual_id, "statement": statement}
            for residual_id, statement in _RESIDUALS
        ],
        "notAuthorized": list(_NOT_AUTHORIZED),
    }
    document["reviewDigest"] = review_digest(document)
    return validate_review(document)


def validate_review(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the review and require the live fail-closed outcomes."""
    validate("track5-implementation-review", document)
    if document["reviewDigest"] != review_digest(document):
        raise ReviewError("review-digest")
    if document["locallyObservedArtifactDigests"]:
        raise ReviewError("local-digest")
    _require_components(document["componentReviews"])
    _require_pairs(document["unmetPrerequisites"], _UNMET, "unmet-prerequisites")
    _require_pairs(document["passingPrerequisites"], _PASSING, "passing-prerequisites")
    _require_pairs(document["acceptedResiduals"], _RESIDUALS, "residuals", "residualId")
    if list(document["notAuthorized"]) != list(_NOT_AUTHORIZED):
        raise ReviewError("not-authorized")
    _require_live_outcomes(document)
    return document


def load_review(root: Path | None = None) -> dict[str, Any]:
    """Load the committed review and require it to match the sealed record."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ReviewError("record-type")
    document = validate_review(loaded)
    if document != build_review():
        raise ReviewError("review-drift")
    return document


def _require_components(reviews: list[dict[str, Any]]) -> None:
    observed = [
        (str(item["componentId"]), str(item["disposition"]), str(item["statement"]))
        for item in reviews
    ]
    if tuple(observed) != _COMPONENTS:
        raise ReviewError("component-reviews")


def _require_pairs(
    items: list[dict[str, Any]],
    expected: tuple[tuple[str, str], ...],
    code: str,
    identifier: str = "prerequisiteId",
) -> None:
    observed = [(str(item[identifier]), str(item["statement"])) for item in items]
    if tuple(observed) != expected:
        raise ReviewError(code)


def _require_live_outcomes(document: dict[str, Any]) -> None:
    runtime = load_authorization()
    closure = load_closure()
    track6 = load_track6_authorization()
    profile = load_profile()
    template = load_verification_template()
    illustration = load_offline_manifest(_ILLUSTRATION)
    if runtime["authorizationOutcome"] != document["runtimeDecision"]:
        raise ReviewError("runtime-outcome")
    if runtime["runtimeId"] is not None or runtime["locallyObservedArtifactDigests"]:
        raise ReviewError("runtime-outcome")
    if closure["selectionOutcome"] != document["candidateDecision"]:
        raise ReviewError("candidate-outcome")
    if closure["qualifyingCandidateCount"] != 0 or closure["locallyObservedArtifactDigests"]:
        raise ReviewError("candidate-outcome")
    if track6["authorizationOutcome"] != document["track6Authorization"]:
        raise ReviewError("track6-outcome")
    unmet = [str(item["prerequisiteId"]) for item in document["unmetPrerequisites"]]
    if unmet != [str(item["prerequisiteId"]) for item in track6["blockers"]]:
        raise ReviewError("track6-blockers")
    passing = [str(item["prerequisiteId"]) for item in document["passingPrerequisites"]]
    live_passing = [
        str(item["prerequisiteId"]) for item in track6["prerequisites"] if item["status"] == "pass"
    ]
    if passing != live_passing:
        raise ReviewError("track6-passes")
    blockers = [item for item in profile["controls"] if item["acquisitionBlocking"] is True]
    if len(blockers) != 9 or profile["acquisitionBlocked"] is not True:
        raise ReviewError("isolation-residuals")
    if template["malwareDetectionClaimed"] is not False:
        raise ReviewError("verification-limitation")
    if (
        template["locallyObservedArtifactDigests"]
        or illustration["locallyVerifiedArtifactIdentities"]
    ):
        raise ReviewError("local-digest")
    if illustration["reviewStatus"] != "not-authorized":
        raise ReviewError("illustration-status")
    for record in (runtime, closure, track6, illustration, template):
        if (
            record["acquisitionStatus"] != "not-acquired"
            or record["executionStatus"] != "not-executed"
        ):
            raise ReviewError("acquisition-status")
        if record["productionReady"] is not False:
            raise ReviewError("production-ready")
