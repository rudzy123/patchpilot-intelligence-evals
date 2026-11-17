"""Durable Track 9A corrections. They do not launch a model or call Run."""

from __future__ import annotations

import hashlib
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

PLAN_DIGEST = "6c4a9e6c64a3afe3c1cbb36d19985880beb067fdb9b5634752e8c4d1482560f1"
TRACK9_AUTHORIZATION_DIGEST = "e7325c76745505e533afaf12b108470fb6a2a2c765e5f7335b3b1ce1ef6c7477"
STDOUT_DIGEST = "b28e9aa7f5db74d23040d9b3045b5fc927bc2289378bb6bf676e4568ec20b0b9"
STDERR_DIGEST = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
EXTRACTED_DIGEST = "8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d"
_NOT_READY = "TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY"
_ATTEMPT = "candidates/authorization/track9a-stopped-attempt.json"
_DEFECT = "candidates/authorization/track9a-telemetry-finalization-defect.json"
_FORENSICS = "candidates/authorization/track9a-schema-forensics.json"
_INTERPRETATION = "candidates/authorization/track9a-corrected-interpretation.json"
_DISPOSITION = "candidates/authorization/track9a-plan-disposition.json"
_PROPORTIONALITY = "candidates/authorization/track9a-proportionality-review.json"
_TRACK10 = "candidates/authorization/track9a-track10-not-ready.json"
_REVIEW = "candidates/authorization/track9a-implementation-review.json"
_MISSING_REQUIRED = (
    "schemaVersion",
    "candidate",
    "authorizedOrganizationId",
    "findingId",
    "refused",
    "refusalReason",
    "preservedDeterministicFacts",
    "sourceFacts",
    "supportedClaims",
    "remediationSuggestions",
    "uncertainty",
    "citations",
    "safetyWarnings",
    "explanationText",
    "nonAuthoritative",
)
_UNEXPECTED = ("deterministicFacts", "findingExplanation")
_RETAINED = (
    ("closeout.json", "a1c8832b8a85316806817ecf59c4ce1878c3653015b890beb5de6517508a571b"),
    ("preflight.json", "d44d1440b4273d7ae606f4cdc327c0eb2dc422f11985de4d3161622eb30bd94f"),
    (
        "runs/case-ground-001-r1/diagnostics.json",
        "2375f466b41e1e49111663806ab50cd2c93323a830bbbc52cd21f06eed8ad659",
    ),
    (
        "runs/case-ground-001-r1/extracted.bin",
        "8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d",
    ),
    (
        "runs/case-ground-001-r1/raw-output.json",
        "488b8b9f3daf8163de8da3cd252383d39c8c6f52a814bd58af6c0f067a8e815f",
    ),
    (
        "runs/case-ground-001-r1/run.json",
        "086d9789a849a04ffd994b3200f8de1ac8b322300a6705dbc57038a0098dca4c",
    ),
    (
        "runs/case-ground-001-r1/stderr.bin",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
    (
        "runs/case-ground-001-r1/stdout.bin",
        "b28e9aa7f5db74d23040d9b3045b5fc927bc2289378bb6bf676e4568ec20b0b9",
    ),
    ("summary.json", "3dc8481a7d2fea67457e59627423b2d8ba7311a742a422afa7a486825ab4faf7"),
    (
        "track10-readiness.json",
        "9963c549d4eca60584fdbf6e5c3c57dc3c000701304d7a3a6722344487db18ad",
    ),
)
_COMPONENTS = (
    (
        "stopped-attempt",
        "recorded",
        "The corpus stopped after one sealed run. Seventy-one runs were withheld.",
    ),
    (
        "telemetry-finalization",
        "corrected-before-commit",
        "A sealed complete cgroup window stays complete. A later read is diagnostic.",
    ),
    (
        "schema-forensics",
        "recorded",
        "The retained explanation object is schema-invalid. Stop authority stays separate.",
    ),
    (
        "corrected-interpretation",
        "corrected-before-commit",
        "Behavioral measurement was attempted and did not complete.",
    ),
    (
        "plan-disposition",
        "recorded",
        "The Track 9A plan digest is consumed. No replacement digest is issued.",
    ),
    (
        "proportionality",
        "recorded",
        "The stopped evidence is accepted. The correction does not authorize another Run.",
    ),
    (
        "track10",
        "recorded",
        "Track 10 stays not ready because the corpus did not complete.",
    ),
    (
        "external-evidence",
        "recorded",
        "The external result files stay immutable. This correction does not rewrite them.",
    ),
)
_NOT_AUTHORIZED = (
    "another Run",
    "a replacement corpus plan",
    "the remaining 71 runs",
    "candidate selection",
    "calibration approval",
    "production use",
)


def build_stopped_attempt() -> dict[str, Any]:
    """Stopped attempt. One run was sealed and the corpus did not finish."""
    return digest_document(
        {
            **_pins(),
            "attemptOutcome": "stopped",
            "behavioralConclusion": "partial-inconclusive",
            "behavioralMeasurementAttempted": True,
            "behavioralMeasurementCompleted": False,
            "candidateEvaluatedCompletely": False,
            "candidateMetricsProduced": False,
            "completedRuns": 1,
            "corpusCompleted": False,
            "executionStopAuthority": "measurement-infrastructure",
            "externalEvidenceRewritten": False,
            "measurementCompleted": False,
            "measurementPerformed": True,
            "missingRuns": 71,
            "modelSessionCreated": True,
            "plannedRuns": 72,
            "realModelExecuted": True,
            "retainedFiles": _files(),
            "runInvoked": True,
            "stopCause": "telemetry-unresolved",
        },
        "track9a-stopped-attempt",
        "identityDigest",
    )


def build_telemetry_defect() -> dict[str, Any]:
    """The exited-child read that replaced a complete window is corrected."""
    return digest_document(
        {
            **_pins(),
            "aggregatedWindowTelemetry": "complete",
            "cgroupCurrentBytes": 3129344,
            "cgroupPeakBytes": 5709541376,
            "childState": "exited",
            "cleanup": "reaped",
            "correctedDisposition": "sealed-complete-window",
            "defect": "post-exit-read-downgrade",
            "observedExitClassification": "telemetry-unresolved",
            "downgradeRequiresContradiction": True,
            "incompleteTelemetryFailClosed": True,
            "networkResult": "denied",
            "oomEvents": 0,
            "postExitScope": "retained",
            "sealedLaunchOmission": False,
        },
        "track9a-telemetry-finalization-defect",
        "identityDigest",
    )


def build_schema_forensics() -> dict[str, Any]:
    """Read-only attribution of the one sealed schema-invalid explanation."""
    return digest_document(
        {
            **_pins(),
            "adapterAddedInnerFields": False,
            "adapterFallback": False,
            "adapterRemovedFields": False,
            "adapterRenamedFields": False,
            "adapterTruncated": False,
            "adapterWrappedEnvelope": True,
            "diagnosticIdentityDigest": (
                "f1aaa2a2288d04de90d5777e8fc5e87c1c74e8373d95f9a3b79202480233b6f9"
            ),
            "executionStopAuthority": "measurement-infrastructure",
            "fallbackShape": False,
            "executionStopCause": "telemetry-unresolved",
            "extractedBytes": 264,
            "extractedDigest": EXTRACTED_DIGEST,
            "extractionPreservedObject": True,
            "generationObserved": True,
            "innerObjectUnchanged": True,
            "jsonKeysPreserved": True,
            "missingRequiredFields": list(_MISSING_REQUIRED),
            "outputLimitStatus": "within-limit",
            "promptContainsFindingExplanation": False,
            "promptContractPresent": True,
            "responseSchemaDigest": (
                "15955301d2cd0e2f835b851e19d7f48a2664eb9df6f1f7f99d658926e8b46b91"
            ),
            "rawContainsDeterministicFacts": True,
            "rawContainsFindingExplanation": True,
            "responseFailureAuthority": "candidate-output",
            "responseSchemaVersion": "1.0.0",
            "runId": "case-ground-001-r1",
            "stderrBytes": 0,
            "stderrDigest": STDERR_DIGEST,
            "stderrTruncated": False,
            "stdoutBytes": 542,
            "stdoutDigest": STDOUT_DIGEST,
            "stdoutTruncated": False,
            "unexpectedFields": list(_UNEXPECTED),
        },
        "track9a-schema-forensics",
        "identityDigest",
    )


def build_corrected_interpretation() -> dict[str, Any]:
    """Corrected corpus reading. The external summary file stays untouched."""
    return digest_document(
        {
            **_pins(),
            "behavioralConclusion": "partial-inconclusive",
            "behavioralMeasurementAttempted": True,
            "behavioralMeasurementCompleted": False,
            "candidateEvaluatedCompletely": False,
            "candidateMetricsProduced": False,
            "comparisonStatus": "not-executed",
            "completedRuns": 1,
            "missingRuns": 71,
            "percentageGatesCalibrated": False,
            "summaryStop": "telemetry-unresolved",
        },
        "track9a-corrected-interpretation",
        "identityDigest",
    )


def build_plan_disposition() -> dict[str, Any]:
    """Consume the Track 9A digest. No replacement digest is issued."""
    return digest_document(
        {
            **_pins(),
            "executionStatus": "stopped",
            "furtherPlanAssumed": False,
            "modelSessionCreated": True,
            "planDisposition": "consumed",
            "realModelExecuted": True,
            "reusable": False,
            "runInvoked": True,
        },
        "track9a-plan-disposition",
        "identityDigest",
    )


def build_proportionality_review() -> dict[str, Any]:
    """The stopped evidence is accepted. Another Run stays unauthorized."""
    return digest_document(
        {
            **_pins(),
            "authorizesAnotherRun": False,
            "authorizesReplacementPlan": False,
            "proportionalityRecommendation": "review-required",
            "rationale": "stopped-evidence-accepted-without-another-run",
        },
        "track9a-proportionality-review",
        "identityDigest",
    )


def build_track10_not_ready() -> dict[str, Any]:
    """Track 10 stays not ready. The committed snapshot is not rewritten."""
    return digest_document(
        {
            **_pins(),
            "candidateMetricsProduced": False,
            "completedRuns": 1,
            "missingRuns": 71,
            "readinessOutcome": "not-ready",
            "reason": "telemetry-unresolved",
            "verdict": _NOT_READY,
        },
        "track9a-track10-not-ready",
        "identityDigest",
    )


def build_track9a_review() -> dict[str, Any]:
    """Implementation review. The digest covers every field except itself."""
    document: dict[str, Any] = {
        **_pins(),
        "attemptOutcome": "stopped",
        "authorizedScope": (
            "This record accepts the stopped corpus as fail-closed evidence and records the "
            "telemetry and forensic corrections. It does not authorize another Run, a replacement "
            "plan, the remaining runs, candidate selection, calibration, or production use."
        ),
        "behavioralConclusion": "partial-inconclusive",
        "candidateMetrics": "not-produced",
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "decision": (
            "stopped attempt accepted and bounded corrections recorded for review before commit"
        ),
        "measurementCompleted": False,
        "measurementPerformed": True,
        "modelSessionCreated": True,
        "notAuthorized": list(_NOT_AUTHORIZED),
        "planDisposition": "consumed",
        "realModelExecuted": True,
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-17",
        "reviewStatus": "stopped-attempt-accepted-corrections-pending-commit",
        "runInvoked": True,
        "stopCause": "telemetry-unresolved",
        "track10Readiness": "not-ready",
    }
    document["reviewDigest"] = review_digest(document)
    reject_sensitive(document)
    validate("track9a-implementation-review", document)
    return document


def confirm_retained_files(root: Path) -> None:
    """Check external file bytes against the sealed digests. This does not write."""
    if root.is_symlink() or not root.is_dir():
        raise MeasurementError("result-root-reuse")
    for relative, digest in _RETAINED:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise MeasurementError("record-drift")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise MeasurementError("digest-mismatch")
        if path.stat().st_mode & 0o777 != 0o400:
            raise MeasurementError("record-drift")


def load_stopped_attempt() -> dict[str, Any]:
    """Load the stopped-attempt record."""
    return _load(_ATTEMPT, build_stopped_attempt)


def load_telemetry_defect() -> dict[str, Any]:
    """Load the telemetry-finalization defect."""
    return _load(_DEFECT, build_telemetry_defect)


def load_schema_forensics() -> dict[str, Any]:
    """Load the first-run schema forensics."""
    return _load(_FORENSICS, build_schema_forensics)


def load_corrected_interpretation() -> dict[str, Any]:
    """Load the corrected corpus interpretation."""
    return _load(_INTERPRETATION, build_corrected_interpretation)


def load_plan_disposition() -> dict[str, Any]:
    """Load the consumed Track 9A plan disposition."""
    return _load(_DISPOSITION, build_plan_disposition)


def load_proportionality_review() -> dict[str, Any]:
    """Load the proportionality review."""
    return _load(_PROPORTIONALITY, build_proportionality_review)


def load_track10_not_ready() -> dict[str, Any]:
    """Load the Track 10 not-ready record."""
    return _load(_TRACK10, build_track10_not_ready)


def load_track9a_review() -> dict[str, Any]:
    """Load the Track 9A implementation review."""
    return _load(_REVIEW, build_track9a_review)


def _pins() -> dict[str, Any]:
    plan = _plan()
    return {
        **authority(),
        "comparisonWinner": None,
        "planDigest": plan["planDigest"],
        "replacementPlanDigest": "not-issued",
        "sessionId": plan["sessionId"],
        "track9AuthorizationDigest": plan["track9AuthorizationDigest"],
    }


def _files() -> list[dict[str, str]]:
    return [{"path": path, "sha256": digest} for path, digest in _RETAINED]


def _plan() -> dict[str, Any]:
    from patchpilot_intelligence_evals.corpus_continuation_plan import load_corpus_plan

    plan = load_corpus_plan()
    if plan["planDigest"] != PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    if plan["track9AuthorizationDigest"] != TRACK9_AUTHORIZATION_DIGEST:
        raise MeasurementError("digest-mismatch")
    if plan["plannedRuns"] != 72 or plan["executionStatus"] != "not-executed":
        raise MeasurementError("record-drift")
    if plan["runInvoked"] is not False:
        raise MeasurementError("record-drift")
    return plan


def _load(relative: str, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
