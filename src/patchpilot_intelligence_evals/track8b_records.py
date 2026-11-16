"""Durable Track 8B records for the stopped attempt. They do not launch a model."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_plan import (
    ARCHIVE_ATTEMPT,
    CANDIDATE_ATTEMPT,
    PHASE_ORDER,
    RUNTIME_ATTEMPT,
    MeasurementError,
    authority,
    digest_document,
    load_measurement_plan,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

APPROVED_PLAN_DIGEST = "8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2"
VERIFIED_TEMPLATE_DIGEST = "f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176"
_PREFLIGHT = "candidates/templates/measurement-preflight-template.json"
_ATTEMPT = "candidates/authorization/track8b-stopped-attempt.json"
_CLOSEOUT = "candidates/authorization/track8b-stopped-closeout.json"
_DISPOSITION = "candidates/authorization/track8b-plan-disposition.json"
_DEFECT = "candidates/authorization/track8b-template-compatibility-defect.json"
_REVIEW = "candidates/authorization/track8b-implementation-review.json"
_STOPPED_PHASES = (
    ("preflight", "passed"),
    ("one-token-smoke", "failed"),
    ("short-generation", "not-executed"),
    ("context-4096", "not-executed"),
    ("context-8192", "withheld"),
    ("corpus-evaluation", "not-executed"),
)
_COMPONENTS = (
    (
        "stopped-attempt",
        "accepted",
        "The 2026-11-16 attempt stopped with tokenizer-failure before a session and before Run. "
        "That fail-closed evidence is accepted. Later phases were not executed. "
        "The 8192-token phase stays withheld.",
    ),
    (
        "template-compatibility",
        "corrected-before-commit",
        "Compatibility checks the verified template digest and an explicit template subset. "
        "It does not require one operator spelling. The verified template bytes stay unchanged.",
    ),
    (
        "preflight-authority",
        "corrected-before-commit",
        "The historical preflight omitted calibrationStatus. Calibration remained not-approved "
        "in every authority-bearing record. No calibration decision changed. Future preflight "
        "records include the frozen authority fields.",
    ),
    (
        "plan-disposition",
        "recorded",
        "The approved plan is consumed and is not reusable. Another Run requires a new plan "
        "and a new operator approval. No replacement plan digest is issued.",
    ),
)
_NOT_AUTHORIZED = (
    "another Run on the consumed plan",
    "candidate selection",
    "calibration approval",
    "model or tokenizer acquisition",
    "production use",
)


def build_preflight_record(*, status: str) -> dict[str, Any]:
    """Future preflight record. It carries the frozen authority fields."""
    if status not in {"not-executed", "ok"}:
        raise MeasurementError("record-type")
    return digest_document(
        {
            **authority(),
            "archiveAttemptId": ARCHIVE_ATTEMPT,
            "candidateAttemptId": CANDIDATE_ATTEMPT,
            "candidateClass": "verified-candidate",
            "measurementPerformed": False,
            "planDigest": _plan_digest(),
            "realModelExecuted": False,
            "runInvoked": False,
            "runtimeAttemptId": RUNTIME_ATTEMPT,
            "runtimeClass": "verified-runtime",
            "status": status,
        },
        "measurement-preflight",
        "identityDigest",
    )


def build_preflight_template() -> dict[str, Any]:
    """Committed preflight shape. It has not been written to an external root."""
    return build_preflight_record(status="not-executed")


def build_stopped_attempt() -> dict[str, Any]:
    """The stopped attempt. The historical plan digest stays the approved digest."""
    return digest_document(
        {
            **authority(),
            "attemptStatus": "stopped",
            "calibrationDecisionChanged": False,
            "calibrationRemainedNotApproved": True,
            "candidateMetrics": "not-produced",
            "context4096": "not-executed",
            "context8192": "withheld",
            "corpusEvaluation": "not-executed",
            "futurePreflightIncludesCalibrationStatus": True,
            "historicalPreflightOmittedCalibrationStatus": True,
            "measurementPerformed": False,
            "planDigest": _plan_digest(),
            "realModelExecuted": False,
            "runInvoked": False,
            "sessionCreated": False,
            "shortGeneration": "not-executed",
            "stopCause": "tokenizer-failure",
            "track9Readiness": "not-ready",
        },
        "track8b-stopped-attempt",
        "identityDigest",
    )


def build_stopped_closeout() -> dict[str, Any]:
    """Observed closeout. The 8192-token phase stays withheld."""
    phases = [{"phase": phase, "status": status} for phase, status in _STOPPED_PHASES]
    if [item["phase"] for item in phases] != list(PHASE_ORDER):
        raise MeasurementError("record-type")
    return digest_document(
        {
            **authority(),
            "calibrationDecisionChanged": False,
            "calibrationRemainedNotApproved": True,
            "cleanup": "reaped",
            "closeoutState": "stopped",
            "historicalPreflightOmittedCalibrationStatus": True,
            "phases": phases,
            "planDigest": _plan_digest(),
            "realModelExecuted": False,
            "retainedResultClass": "measurement-result",
            "stopCause": "tokenizer-failure",
        },
        "measurement-closeout",
        "identityDigest",
    )


def build_plan_disposition() -> dict[str, Any]:
    """Mark the approved plan consumed. This correction issues no replacement digest."""
    return digest_document(
        {
            **authority(),
            "nextRunRequiresNewPlan": True,
            "nextRunRequiresOperatorApproval": True,
            "planDigest": _plan_digest(),
            "planDisposition": "consumed",
            "replacementPlanDigest": "not-issued",
            "reusable": False,
            "runInvoked": False,
        },
        "track8b-plan-disposition",
        "identityDigest",
    )


def build_template_defect() -> dict[str, Any]:
    """Record the spelling guard that stopped the attempt before a session."""
    return digest_document(
        {
            **authority(),
            "defectId": "template-compatibility-boundary",
            "failureBeforeSession": "tokenizer-failure",
            "rejectedSpellingProof": "messages | length",
            "runInvoked": False,
            "sessionCreated": False,
            "status": "corrected-before-commit",
            "templateBytesChanged": False,
            "verifiedTemplateDigest": VERIFIED_TEMPLATE_DIGEST,
        },
        "track8b-template-compatibility-defect",
        "identityDigest",
    )


def build_track8b_review() -> dict[str, Any]:
    """Seal the review with the repository review digest. It is prepared, not a new Run."""
    document: dict[str, Any] = {
        **authority(),
        "authorizedScope": (
            "This record accepts the stopped Track 8B attempt as fail-closed evidence and "
            "prepares the template and preflight corrections for review. It does not authorize "
            "another Run, candidate selection, calibration, or production use."
        ),
        "calibrationDecisionChanged": False,
        "calibrationRemainedNotApproved": True,
        "candidateMetrics": "not-produced",
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "context4096": "not-executed",
        "context8192": "withheld",
        "corpusEvaluation": "not-executed",
        "decision": (
            "stopped attempt accepted as fail-closed evidence and corrections prepared "
            "for review before commit"
        ),
        "historicalPreflightOmittedCalibrationStatus": True,
        "measurementPerformed": False,
        "notAuthorized": list(_NOT_AUTHORIZED),
        "planDigest": _plan_digest(),
        "planDisposition": "consumed",
        "realModelExecuted": False,
        "replacementPlanDigest": "not-issued",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-16",
        "reviewStatus": "stopped-attempt-accepted-corrections-prepared",
        "runInvoked": False,
        "sessionCreated": False,
        "shortGeneration": "not-executed",
        "stopCause": "tokenizer-failure",
        "track9Readiness": "not-ready",
    }
    document["reviewDigest"] = review_digest(document)
    reject_sensitive(document)
    validate("track8b-implementation-review", document)
    return document


def load_preflight_template() -> dict[str, Any]:
    """Load the committed future-preflight template."""
    return _load(_PREFLIGHT, build_preflight_template)


def load_stopped_attempt() -> dict[str, Any]:
    """Load the stopped-attempt record."""
    return _load(_ATTEMPT, build_stopped_attempt)


def load_stopped_closeout() -> dict[str, Any]:
    """Load the observed closeout."""
    return _load(_CLOSEOUT, build_stopped_closeout)


def load_plan_disposition() -> dict[str, Any]:
    """Load the consumed-plan disposition."""
    return _load(_DISPOSITION, build_plan_disposition)


def load_template_defect() -> dict[str, Any]:
    """Load the template-compatibility defect."""
    return _load(_DEFECT, build_template_defect)


def load_track8b_review() -> dict[str, Any]:
    """Load the prepared Track 8B review."""
    return _load(_REVIEW, build_track8b_review)


def require_reusable_plan() -> None:
    """Refuse the consumed plan before a real launch."""
    document = load_plan_disposition()
    if document["reusable"] is False and document["planDisposition"] == "consumed":
        raise MeasurementError("plan-consumed")
    raise MeasurementError("plan-consumed")


def _plan_digest() -> str:
    digest = str(load_measurement_plan()["planDigest"])
    if digest != APPROVED_PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    return digest


def _load(relative: str, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
