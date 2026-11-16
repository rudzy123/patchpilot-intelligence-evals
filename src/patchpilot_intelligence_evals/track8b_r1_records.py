"""Durable Track 8B-R1 records. They do not launch a model or call Run."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_plan import (
    MeasurementError,
    authority,
    digest_document,
)
from patchpilot_intelligence_evals.measurement_retry_closeout import context_memory_conclusion
from patchpilot_intelligence_evals.measurement_retry_plan import SESSION_ID, load_retry_plan
from patchpilot_intelligence_evals.runtime_dependency_closure import (
    PROVIDER_LIBRARY,
    approved_public_closure,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

SMOKE_PEAK_BYTES = 46_288_896
_ATTEMPT = "candidates/authorization/track8b-r1-stopped-attempt.json"
_DEPENDENCY = "candidates/authorization/track8b-r1-dependency-mount-defect.json"
_MEMORY = "candidates/authorization/track8b-r1-memory-conclusion-defect.json"
_CLOSEOUT = "candidates/authorization/track8b-r1-corrected-closeout.json"
_DISPOSITION = "candidates/authorization/track8b-r1-plan-disposition.json"
_TRACK9 = "candidates/authorization/track8b-r1-stopped-track9-readiness.json"
_REVIEW = "candidates/authorization/track8b-r1-implementation-review.json"
_NOT_READY = "TRACK 9 EVALUATION REVIEW NOT READY"
_COMPONENTS = (
    (
        "stopped-attempt",
        "accepted",
        "The stopped retry attempt is accepted as fail-closed infrastructure evidence. "
        "It ended with inference-failure before CreateSession and before Run. "
        "Later phases stayed withheld.",
    ),
    (
        "dependency-mount",
        "corrected-before-commit",
        "Load proof and inference now share one dependency closure. Approved standard "
        "libraries mount read-only and individually. The ELF interpreter stays in the "
        "existing hardened execution policy. Provider libraries and broad host "
        "directories stay unmounted.",
    ),
    (
        "memory-conclusion",
        "corrected-before-commit",
        "within-ceiling now requires every required context phase, complete "
        "noncontradictory peaks at or below 12884901888 bytes, no OOM, and successful "
        "isolation and cleanup. An empty phase set is unavailable. The smoke peak "
        "stays smoke evidence.",
    ),
    (
        "plan-disposition",
        "recorded",
        "The retry plan is consumed and is not reusable. No replacement plan digest is "
        "issued. Another real execution needs a new session or reviewed retry "
        "authority, a new plan digest, a fresh result root, and a new operator "
        "checkpoint.",
    ),
)
_NOT_AUTHORIZED = (
    "another Run on the consumed retry plan",
    "a replacement plan digest",
    "candidate selection",
    "calibration approval",
    "production use",
)


def build_stopped_attempt() -> dict[str, Any]:
    """The accepted stopped attempt. The external result root stays unchanged."""
    return digest_document(
        {**_attempt_facts(), "measurementPerformed": False},
        "track8b-r1-stopped-attempt",
        "identityDigest",
    )


def build_dependency_defect() -> dict[str, Any]:
    """The missing read-only dependency mount. No host path is recorded."""
    return digest_document(
        {
            **_locked(),
            "approvedClosure": approved_public_closure(),
            "broadDirectoryMounted": False,
            "defectId": "missing-runtime-dependency-mount",
            "failureBeforeSession": "before-create-session",
            "fallbackRetrieval": False,
            "interpreterPolicy": "existing-hardened-execution-policy",
            "modelSessionCreated": False,
            "networkUsed": False,
            "planDigest": _plan_digest(),
            "providerLibrary": PROVIDER_LIBRARY,
            "providerMounted": False,
            "realModelExecuted": False,
            "runInvoked": False,
            "sessionId": SESSION_ID,
            "status": "corrected-before-commit",
        },
        "track8b-r1-dependency-mount-defect",
        "identityDigest",
    )


def build_memory_defect() -> dict[str, Any]:
    """The vacuous within-ceiling label. Smoke evidence does not feed the conclusion."""
    return digest_document(
        {
            **_locked(),
            "candidateMetrics": "not-produced",
            "ceilingBytes": 12_884_901_888,
            "correctedConclusion": _context_conclusion(),
            "defectId": "vacuous-memory-conclusion",
            "emptyPhaseSetWasWithinCeiling": True,
            "modelSessionCreated": False,
            "planDigest": _plan_digest(),
            "realModelExecuted": False,
            "runInvoked": False,
            "sessionId": SESSION_ID,
            "smokeEstablishesContextEligibility": False,
            "smokeEvidenceRole": "smoke-only",
            "smokePeakBytes": SMOKE_PEAK_BYTES,
            "status": "corrected-before-commit",
        },
        "track8b-r1-memory-conclusion-defect",
        "identityDigest",
    )


def build_corrected_closeout() -> dict[str, Any]:
    """Corrected interpretation. The immutable external closeout is not rewritten."""
    return digest_document(
        {
            **_attempt_facts(),
            "closeoutState": "stopped",
            "measurementPerformed": False,
            "memoryConclusion": _context_conclusion(),
            "smokeEstablishesContextEligibility": False,
            "smokeEvidenceRole": "smoke-only",
            "smokePeakBytes": SMOKE_PEAK_BYTES,
        },
        "track8b-r1-corrected-closeout",
        "identityDigest",
    )


def build_retry_disposition() -> dict[str, Any]:
    """The retry plan is consumed. This record does not issue a replacement digest."""
    return digest_document(
        {
            **_locked(),
            "approvalStatus": "not-approved",
            "executionStatus": "not-executed",
            "modelSessionCreated": False,
            "nextRunRequiresFreshResultRoot": True,
            "nextRunRequiresNewPlan": True,
            "nextRunRequiresNewSession": True,
            "nextRunRequiresOperatorApproval": True,
            "planDigest": _plan_digest(),
            "planDisposition": "consumed",
            "realModelExecuted": False,
            "replacementPlanDigest": "not-issued",
            "reusable": False,
            "runInvoked": False,
            "sessionId": SESSION_ID,
        },
        "track8b-r1-plan-disposition",
        "identityDigest",
    )


def build_stopped_track9() -> dict[str, Any]:
    """Advisory Track 9 record for the stopped attempt. It stays not-ready."""
    plan = load_retry_plan()
    return digest_document(
        {
            **_locked(),
            "measurementPerformed": False,
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "readinessOutcome": "not-ready",
            "realModelExecuted": False,
            "reason": "inference-failure",
            "sessionId": plan["sessionId"],
            "verdict": _NOT_READY,
        },
        "retry-track9-readiness",
        "identityDigest",
    )


def build_track8b_r1_review() -> dict[str, Any]:
    """Implementation review. The digest covers every field except itself."""
    document: dict[str, Any] = {
        **_attempt_facts(),
        "authorizedScope": (
            "This record accepts the stopped Track 8B-R1 attempt as fail-closed "
            "infrastructure evidence and records the dependency-mount and "
            "memory-conclusion corrections. It does not authorize another Run, "
            "candidate selection, calibration, or production use."
        ),
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "decision": (
            "stopped retry accepted as fail-closed evidence and bounded defects "
            "corrected for review before commit"
        ),
        "measurementPerformed": False,
        "memoryConclusion": _context_conclusion(),
        "notAuthorized": list(_NOT_AUTHORIZED),
        "planDisposition": "consumed",
        "replacementPlanDigest": "not-issued",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-16",
        "reviewStatus": "stopped-attempt-accepted-defects-corrected",
    }
    document["reviewDigest"] = review_digest(document)
    reject_sensitive(document)
    validate("track8b-r1-implementation-review", document)
    return document


def load_stopped_attempt() -> dict[str, Any]:
    """Load the stopped-attempt record."""
    return _load(_ATTEMPT, build_stopped_attempt)


def load_dependency_defect() -> dict[str, Any]:
    """Load the dependency-mount defect."""
    return _load(_DEPENDENCY, build_dependency_defect)


def load_memory_defect() -> dict[str, Any]:
    """Load the memory-conclusion defect."""
    return _load(_MEMORY, build_memory_defect)


def load_corrected_closeout() -> dict[str, Any]:
    """Load the corrected closeout interpretation."""
    return _load(_CLOSEOUT, build_corrected_closeout)


def load_retry_disposition() -> dict[str, Any]:
    """Load the consumed retry-plan disposition."""
    return _load(_DISPOSITION, build_retry_disposition)


def load_stopped_track9() -> dict[str, Any]:
    """Load the stopped-attempt Track 9 recommendation."""
    return _load(_TRACK9, build_stopped_track9)


def load_track8b_r1_review() -> dict[str, Any]:
    """Load the implementation review."""
    return _load(_REVIEW, build_track8b_r1_review)


def _attempt_facts() -> dict[str, Any]:
    plan = load_retry_plan()
    return {
        **_locked(),
        "attemptOutcome": "stopped",
        "candidateMetrics": "not-produced",
        "context4096": "withheld",
        "context8192": "withheld",
        "corpusEvaluation": "not-started",
        "failureAuthority": "measurement-infrastructure",
        "failureCategory": "inference-failure",
        "modelSessionCreated": False,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": plan["priorPlanDigest"],
        "realModelExecuted": False,
        "runInvoked": False,
        "sessionId": plan["sessionId"],
        "shortGeneration": "withheld",
        "track9Readiness": "not-ready",
    }


def _locked() -> dict[str, Any]:
    return authority()


def _context_conclusion() -> str:
    return context_memory_conclusion({"context-4096": None, "context-8192": None})


def _plan_digest() -> str:
    digest = str(load_retry_plan()["planDigest"])
    if load_retry_plan()["executionStatus"] != "not-executed":
        raise MeasurementError("record-drift")
    return digest


def _load(relative: str, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
