"""Durable Track 8B-R2 records. They do not launch a model or call Run."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_plan import (
    MeasurementError,
    authority,
    digest_document,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

PLAN_DIGEST = "2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350"
PRIOR_PLAN_DIGEST = "8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2"
PRECHECK_DIGEST = "ecb67d19b6ad0bfcdf5cd42724ebd8e0652790d79f00c6a149c4d8a49c772748"
CEILING_BYTES = 12_884_901_888
WARM_8192_PEAK_BYTES = 12_271_669_248
HEADROOM_BYTES = 613_232_640
_NOT_READY = "TRACK 9 EVALUATION REVIEW NOT READY"
_ATTEMPT = "candidates/authorization/track8b-r2-stopped-attempt.json"
_DEFECT = "candidates/authorization/track8b-r2-cgroup-sampling-defect.json"
_FORENSICS = "candidates/authorization/track8b-r2-schema-forensics.json"
_BEHAVIOR = "candidates/authorization/track8b-r2-behavioral-interpretation.json"
_MEMORY = "candidates/authorization/track8b-r2-memory-conclusion.json"
_DISPOSITION = "candidates/authorization/track8b-r2-plan-disposition.json"
_PROPORTIONALITY = "candidates/authorization/track8b-r2-proportionality-review.json"
_TRACK9 = "candidates/authorization/track8b-r2-stopped-track9-readiness.json"
_REVIEW = "candidates/authorization/track8b-r2-implementation-review.json"
_COMPLETED = (
    ("case-contra-001", 1),
    ("case-contra-001", 2),
    ("case-contra-001", 3),
    ("case-contra-002", 1),
    ("case-contra-002", 2),
    ("case-contra-002", 3),
    ("case-contra-003", 1),
    ("case-contra-003", 2),
    ("case-contra-003", 3),
    ("case-ground-001", 1),
    ("case-ground-001", 2),
    ("case-ground-001", 3),
    ("case-ground-002", 1),
    ("case-ground-002", 2),
    ("case-ground-002", 3),
)
_COMPONENTS = (
    (
        "stopped-attempt",
        "recorded",
        "The R2 attempt stopped after 15 sealed schema-failure runs. "
        "The sixteenth launch was not sealed. Metrics and gates were not produced.",
    ),
    (
        "cgroup-sampling",
        "corrected-before-commit",
        "Post-exit cgroup disappearance keeps the last complete sample. "
        "Scope loss while the child is active is an infrastructure failure. "
        "A context-memory pass still requires a complete cgroup peak.",
    ),
    (
        "schema-forensics",
        "recorded",
        "All 15 sealed runs have null output digests. Schema-error paths were not retained. "
        "Failure authority stays unresolved, so the candidate is not called schema-noncompliant.",
    ),
    (
        "behavioral-interpretation",
        "corrected-before-commit",
        "Behavioral measurement was attempted and did not complete. "
        "The conclusion is partial-inconclusive. Candidate metrics were not produced.",
    ),
    (
        "memory-conclusion",
        "accepted",
        "The measured peaks stay within the resident ceiling with 613232640 bytes of headroom. "
        "This is not production-capacity evidence. One candidate process at a time stays "
        "mandatory.",
    ),
    (
        "plan-disposition",
        "recorded",
        "The R2 plan digest is consumed and is not reusable. "
        "No replacement or R3 digest is issued.",
    ),
    (
        "proportionality",
        "recorded",
        "The infrastructure defect requires review. "
        "The recommendation does not authorize another Run or an R3 plan.",
    ),
    (
        "track9",
        "recorded",
        "Track 9 stays not ready because the corpus did not complete "
        "and the summary stop is telemetry-unresolved.",
    ),
)
_NOT_AUTHORIZED = (
    "another Run",
    "an R3 plan",
    "candidate selection",
    "calibration approval",
    "production use",
)


def build_stopped_attempt() -> dict[str, Any]:
    """Stopped attempt. Run occurred and the corpus did not finish."""
    plan = _plan()
    return digest_document(
        {
            **authority(),
            "attemptOutcome": "stopped",
            "behavioralConclusion": "partial-inconclusive",
            "candidateMetrics": "not-produced",
            "casesWithoutResults": 19,
            "completedRunRecords": 15,
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "corpusCompleted": False,
            "headroomAssessment": "limited",
            "measurementCompleted": False,
            "measurementPerformed": True,
            "memoryConclusion": "within-ceiling",
            "modelSessionCreated": True,
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "realModelExecuted": True,
            "runInvoked": True,
            "sessionId": plan["sessionId"],
            "stopCause": "telemetry-unresolved",
            "track9Readiness": "not-ready",
        },
        "track8b-r2-stopped-attempt",
        "identityDigest",
    )


def build_cgroup_defect() -> dict[str, Any]:
    """Post-exit sampling defect. The omitted child report is not a sealed run."""
    plan = _plan()
    return digest_document(
        {
            "childModelSessionCreated": True,
            "childRunInvoked": True,
            "childStatus": "ok",
            "completedRunRecords": 15,
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "contextPassRequiresCompletePeak": True,
            "correctedDisposition": "post-exit-scope-removed",
            "defect": "post-exit-scope-removal",
            "inputTokenCount": 796,
            "networkResult": "denied",
            "newTokenCount": 41,
            "observedErrno": 19,
            "observedRead": "memory.events",
            "omittedLaunch": True,
            "omittedLaunchSealed": False,
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "productionReady": False,
            "schemaVersion": "1.0.0",
            "sessionId": plan["sessionId"],
            "stdoutRetained": False,
            "tokenOutputDigest": "c5f4cd95ea0de4e7502580fee8363b9ad1b0ba38145ab514b7bc8893acd3a978",
        },
        "track8b-r2-cgroup-sampling-defect",
        "identityDigest",
    )


def build_schema_forensics() -> dict[str, Any]:
    """Closed attribution of the 15 sealed schema-failure runs."""
    plan = _plan()
    return digest_document(
        {
            "anyCandidateOutputValid": False,
            "authorityCounts": {
                "adapter": 0,
                "candidate-output": 0,
                "evaluator": 0,
                "protocol": 0,
                "unresolved": 15,
            },
            "candidateCharacterizedAsSchemaNoncompliant": False,
            "casesWithoutResults": 19,
            "completedRunCount": 15,
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "correctableWithoutContractChange": False,
            "correctionBlocker": "raw-output-not-retained",
            "evidenceBasis": "immutable-run-record-without-stdout",
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "productionReady": False,
            "repetitionsAgree": True,
            "runs": [_forensic_row(case_id, repetition) for case_id, repetition in _COMPLETED],
            "sameMalformedShape": "unresolved",
            "schemaErrorCounts": {"unavailable": 15},
            "schemaVersion": "1.0.0",
            "sessionId": plan["sessionId"],
        },
        "track8b-r2-schema-forensics",
        "identityDigest",
    )


def build_behavioral_interpretation() -> dict[str, Any]:
    """Corrected behavioral reading. The external closeout file stays untouched."""
    plan = _plan()
    return digest_document(
        {
            **authority(),
            "behavioralConclusion": "partial-inconclusive",
            "behavioralMeasurementAttempted": True,
            "behavioralMeasurementCompleted": False,
            "candidateEvaluatedCompletely": False,
            "candidateMetricsProduced": False,
            "casesWithoutResults": 19,
            "comparisonStatus": "not-executed",
            "comparisonWinner": None,
            "completedRunRecords": 15,
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "percentageGatesCalibrated": False,
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "sessionId": plan["sessionId"],
            "summaryStop": "telemetry-unresolved",
        },
        "track8b-r2-behavioral-interpretation",
        "identityDigest",
    )


def build_memory_conclusion() -> dict[str, Any]:
    """Accepted resident peaks. Headroom is exact and is not production capacity."""
    plan = _plan()
    if CEILING_BYTES - WARM_8192_PEAK_BYTES != HEADROOM_BYTES:
        raise MeasurementError("record-drift")
    return digest_document(
        {
            "ceilingBytes": CEILING_BYTES,
            "cgroupPeakEvidence": "complete",
            "cold4096PeakBytes": 7_284_371_456,
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "cold8192PeakBytes": 9_816_231_936,
            "headroomAssessment": "limited",
            "memoryConclusion": "within-ceiling",
            "minimumHeadroomBytes": HEADROOM_BYTES,
            "oneCandidateProcess": "mandatory",
            "oom": False,
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "productionCapacityEvidence": False,
            "productionReady": False,
            "schemaVersion": "1.0.0",
            "sessionId": plan["sessionId"],
            "warm4096PeakBytes": 8_511_131_648,
            "warm8192PeakBytes": WARM_8192_PEAK_BYTES,
            "warmRss": "unavailable",
        },
        "track8b-r2-memory-conclusion",
        "identityDigest",
    )


def build_plan_disposition() -> dict[str, Any]:
    """Consume the R2 digest. No replacement and no R3 digest is issued."""
    plan = _plan()
    return digest_document(
        {
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "executionStatus": "stopped",
            "furtherRetryAssumed": False,
            "modelSessionCreated": True,
            "planDigest": plan["planDigest"],
            "planDisposition": "consumed",
            "priorPlanDigest": plan["priorPlanDigest"],
            "productionReady": False,
            "r3Plan": "not-issued",
            "realModelExecuted": True,
            "replacementPlanDigest": "not-issued",
            "reusable": False,
            "runInvoked": True,
            "schemaVersion": "1.0.0",
            "sessionId": plan["sessionId"],
        },
        "track8b-r2-plan-disposition",
        "identityDigest",
    )


def build_proportionality_review() -> dict[str, Any]:
    """Review is required. That recommendation does not authorize another Run."""
    plan = _plan()
    return digest_document(
        {
            "authorizesR3": False,
            "authorizesRetry": False,
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "furtherRetryAssumed": False,
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "productionReady": False,
            "proportionalityRecommendation": "review-required",
            "rationale": "infrastructure-defect-requires-review",
            "schemaVersion": "1.0.0",
            "sessionId": plan["sessionId"],
        },
        "track8b-r2-proportionality-review",
        "identityDigest",
    )


def build_stopped_track9() -> dict[str, Any]:
    """Track 9 stays not ready. The corpus did not complete."""
    plan = _plan()
    return digest_document(
        {
            **authority(),
            "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
            "dependencyClosureDigest": plan["dependencyClosureDigest"],
            "dynamicLinkPrecheckDigest": PRECHECK_DIGEST,
            "measurementPerformed": True,
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "readinessOutcome": "not-ready",
            "realModelExecuted": True,
            "reason": "telemetry-unresolved",
            "sessionId": plan["sessionId"],
            "verdict": _NOT_READY,
        },
        "inference-retry-track9-readiness",
        "identityDigest",
    )


def build_track8b_r2_review() -> dict[str, Any]:
    """Implementation review. The digest covers every field except itself."""
    plan = _plan()
    document: dict[str, Any] = {
        **authority(),
        "attemptOutcome": "stopped",
        "authorizedScope": (
            "This record accepts the measured memory peaks and records the sampling, "
            "forensic, and interpretation corrections. It does not authorize another Run, "
            "an R3 plan, candidate selection, calibration, or production use."
        ),
        "behavioralConclusion": "partial-inconclusive",
        "candidateMetrics": "not-produced",
        "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "decision": (
            "memory measurements accepted and bounded corrections recorded for review before commit"
        ),
        "headroomAssessment": "limited",
        "measurementCompleted": False,
        "measurementPerformed": True,
        "memoryConclusion": "within-ceiling",
        "modelSessionCreated": True,
        "notAuthorized": list(_NOT_AUTHORIZED),
        "planDigest": plan["planDigest"],
        "planDisposition": "consumed",
        "priorPlanDigest": plan["priorPlanDigest"],
        "r3Plan": "not-issued",
        "realModelExecuted": True,
        "replacementPlanDigest": "not-issued",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-17",
        "reviewStatus": "memory-measurements-accepted-implementation-pending-commit",
        "runInvoked": True,
        "sessionId": plan["sessionId"],
        "stopCause": "telemetry-unresolved",
        "track9Readiness": "not-ready",
    }
    document["reviewDigest"] = review_digest(document)
    reject_sensitive(document)
    validate("track8b-r2-implementation-review", document)
    return document


def confirm_completed_runs(root: Path) -> None:
    """Check the immutable run files against the forensic rows. This does not write."""
    paths = sorted(path for path in (root / "runs").glob("*.json") if path.is_file())
    if len(paths) != len(_COMPLETED):
        raise MeasurementError("record-drift")
    for path, (case_id, repetition) in zip(paths, _COMPLETED, strict=True):
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise MeasurementError("record-type")
        if loaded.get("caseId") != case_id or loaded.get("repetition") != repetition:
            raise MeasurementError("record-drift")
        if loaded.get("exitClassification") != "schema-failure":
            raise MeasurementError("record-drift")
        if loaded.get("outputDigest") is not None:
            raise MeasurementError("record-drift")
        row = _forensic_row(case_id, repetition)
        if row["failureAuthority"] != "unresolved":
            raise MeasurementError("record-drift")


def load_stopped_attempt() -> dict[str, Any]:
    """Load the stopped-attempt record."""
    return _load(_ATTEMPT, build_stopped_attempt)


def load_cgroup_defect() -> dict[str, Any]:
    """Load the cgroup sampling defect."""
    return _load(_DEFECT, build_cgroup_defect)


def load_schema_forensics() -> dict[str, Any]:
    """Load the schema-failure forensic summary."""
    return _load(_FORENSICS, build_schema_forensics)


def load_behavioral_interpretation() -> dict[str, Any]:
    """Load the corrected behavioral interpretation."""
    return _load(_BEHAVIOR, build_behavioral_interpretation)


def load_memory_conclusion() -> dict[str, Any]:
    """Load the measured memory conclusion."""
    return _load(_MEMORY, build_memory_conclusion)


def load_plan_disposition() -> dict[str, Any]:
    """Load the consumed R2 plan disposition."""
    return _load(_DISPOSITION, build_plan_disposition)


def load_proportionality_review() -> dict[str, Any]:
    """Load the proportionality review."""
    return _load(_PROPORTIONALITY, build_proportionality_review)


def load_stopped_track9() -> dict[str, Any]:
    """Load the stopped-attempt Track 9 recommendation."""
    return _load(_TRACK9, build_stopped_track9)


def load_track8b_r2_review() -> dict[str, Any]:
    """Load the implementation review."""
    return _load(_REVIEW, build_track8b_r2_review)


def _forensic_row(case_id: str, repetition: int) -> dict[str, Any]:
    return {
        "caseId": case_id,
        "evidenceIdFormat": "not-retained",
        "failureAuthority": "unresolved",
        "jsonParseResult": "not-retained",
        "missingRequiredFields": [],
        "outputExtractionResult": "not-retained",
        "outputLimitStatus": "within-limit",
        "rawOutputByteCount": None,
        "rawOutputDigest": None,
        "repetition": repetition,
        "schemaErrors": [],
        "truncationStatus": "unresolved",
        "unexpectedFields": [],
    }


def _plan() -> dict[str, Any]:
    from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan

    plan = load_inference_plan()
    if plan["planDigest"] != PLAN_DIGEST or plan["priorPlanDigest"] != PRIOR_PLAN_DIGEST:
        raise MeasurementError("record-drift")
    if plan["executionStatus"] != "not-executed":
        raise MeasurementError("record-drift")
    return plan


def _load(relative: str, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
