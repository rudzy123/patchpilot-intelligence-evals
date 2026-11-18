"""Principal Architect review of Track 10. Approval does not start execution."""

from __future__ import annotations

import json
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.attributed_response_review import (
    MISSING_REQUIRED,
    UNEXPECTED,
    load_attributed_response,
)
from patchpilot_intelligence_evals.diagnostic_proportionality import (
    load_diagnostic_proportionality,
)
from patchpilot_intelligence_evals.evaluator import CATEGORIES
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.inference_retry_plan import CONSUMED_RETRY_PLAN_DIGEST
from patchpilot_intelligence_evals.investment_stop_decision import load_investment_stop
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schema_invariant_review import (
    INVARIANT_GATES,
    load_schema_invariant_review,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.six_run_diagnostic_authorization import (
    REPRESENTATIVE_RULE,
    REQUIRED_DIAGNOSTICS,
    THRESHOLD,
    load_six_run_authorization,
)
from patchpilot_intelligence_evals.track8b_r2_records import PLAN_DIGEST as R2_PLAN_DIGEST
from patchpilot_intelligence_evals.track8b_records import APPROVED_PLAN_DIGEST
from patchpilot_intelligence_evals.track9a_records import PLAN_DIGEST as TRACK9A_PLAN_DIGEST
from patchpilot_intelligence_evals.track10_candidate_disposition import load_track10_disposition
from patchpilot_intelligence_evals.track10_review import (
    SELECTED_ALTERNATIVE,
    SELECTED_CANDIDATE,
    SELECTED_TRACK,
    common,
    decision_for,
    reject_track10_text,
    require_session_decision,
)

SCHEMA_NAME = "track10-implementation-review"
_RECORD = "candidates/authorization/track10-implementation-review.json"
_SCOPE = (
    "This approval accepts the Track 10 candidate disposition and proportionality "
    "decision and authorizes one future six-run diagnostic Session in principle. "
    "It does not authorize current candidate execution, a diagnostic plan, an "
    "execution-plan digest, a result root, operator approval, candidate selection, "
    "calibration approval, PatchPilot integration, shadow mode, production use, "
    "release, or deployment."
)
_ALTERNATIVES: tuple[dict[str, Any], ...] = (
    {
        "alternativeId": "reject-now",
        "decision": "ineligible",
        "reason": "no-supported-mandatory-candidate-failure",
        "selected": False,
    },
    {
        "alternativeId": "six-run-diagnostic",
        "decision": "selected",
        "reason": "decision-grade-for-schema-behavior",
        "selected": True,
    },
    {
        "alternativeId": "full-72-run-continuation",
        "decision": "eligible",
        "reason": "disproportionate-to-narrow-uncertainty",
        "selected": False,
    },
    {
        "alternativeId": "protocol-forensics",
        "decision": "ineligible",
        "reason": "adapter-prompt-parser-evaluator-already-proven",
        "selected": False,
    },
    {
        "alternativeId": "stop-investment",
        "decision": "permissible",
        "reason": "not-selected",
        "selected": False,
    },
)
_COMPONENTS: tuple[tuple[str, str, str], ...] = (
    (
        "attributed-response-evidence",
        "approved",
        "The attributed response evidence is approved.",
    ),
    (
        "schema-authority-review",
        "approved",
        "The schema-authority review is approved.",
    ),
    (
        "proportionality-analysis",
        "approved",
        "The proportionality analysis is approved.",
    ),
    (
        "six-run-diagnostic",
        "authorized-in-principle",
        "The six-run diagnostic is authorized in principle.",
    ),
    (
        "candidate-disposition",
        "approved",
        "The candidate disposition is approved.",
    ),
)
_RESIDUALS: tuple[tuple[str, str], ...] = (
    (
        "deferred-systematic-threshold",
        (
            "A future diagnostic specification must define a closed systematic "
            "schema-failure threshold before execution."
        ),
    ),
    (
        "infrastructure-stop-residual",
        (
            "Another infrastructure failure can stop a future diagnostic before it "
            "answers the schema question."
        ),
    ),
    (
        "evaluated-case-wording",
        (
            "Evaluated-case wording leaves one unscored schema failure unresolved "
            "and does not support rejection."
        ),
    ),
    (
        "limited-headroom",
        "The measured resident headroom is limited and is not a rejection basis.",
    ),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "current-candidate-execution",
    "diagnostic-plan",
    "execution-plan-digest",
    "result-root",
    "operator-approval",
    "candidate-selection",
    "calibration-approval",
    "patchpilot-integration",
    "shadow-mode",
    "production-use",
    "release-or-deployment",
)
_SOURCE_DISQUALIFIERS = {
    "reject-now": "no-supported-mandatory-failure",
    "six-run-diagnostic": "none",
    "full-72-run-continuation": "disproportionate-to-narrow-uncertainty",
    "protocol-forensics": "adapter-prompt-parser-evaluator-already-proven",
    "stop-investment": "none",
}


def _sources() -> dict[str, dict[str, Any]]:
    return {
        "attributedResponseEvidence": load_attributed_response(),
        "candidateDisposition": load_track10_disposition(),
        "diagnosticProportionality": load_diagnostic_proportionality(),
        "investmentStopDecision": load_investment_stop(),
        "schemaInvariantReview": load_schema_invariant_review(),
        "sixRunDiagnosticAuthorization": load_six_run_authorization(),
    }


def _plans() -> list[dict[str, Any]]:
    return [
        {"planDigest": APPROVED_PLAN_DIGEST, "reusable": False},
        {"planDigest": CONSUMED_RETRY_PLAN_DIGEST, "reusable": False},
        {"planDigest": R2_PLAN_DIGEST, "reusable": False},
        {"planDigest": TRACK9A_PLAN_DIGEST, "reusable": False},
    ]


def _response(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "adapterInnerFieldMutation": False,
        "extractedBytes": source["extractedBytes"],
        "extractedDigest": source["extractedDigest"],
        "jsonParse": "passed",
        "missingRequiredFields": list(source["missingRequiredFields"]),
        "outputLimitExceeded": False,
        "responseSchemaValidation": "failed",
        "runId": source["runId"],
        "stdoutBytes": source["stdoutBytes"],
        "stdoutDigest": source["stdoutDigest"],
        "truncation": False,
        "unexpectedFields": list(source["unexpectedFields"]),
    }


def _authority(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "calibrationRequired": True,
        "completeScoredResultRequired": True,
        "invariantGateNames": list(source["invariantGateNames"]),
        "invariantGateTriggered": False,
        "observedRepetitions": 1,
        "oneResponseSupportsCandidateRejection": False,
        "percentageGateKind": "proposed-percentage",
        "percentageGateName": "outputSchemaValidity",
        "percentageRule": "exactly-100",
        "percentageStatus": "unmeasured",
        "perRunResponseContract": "failed",
        "repetitionsRequiredForConsistency": 3,
        "schemaFailureClassification": "measured-continue",
    }


def _boundary(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "casesPerCategory": 1,
        "categories": [row["category"] for row in source["categories"]],
        "categoryCount": 6,
        "contextMemoryRerun": False,
        "decodingAndLimitsUnchanged": True,
        "executionPlanIssued": False,
        "freshEmptyResultRootRequired": True,
        "futureSpecificationRequired": True,
        "hardenedBoundaryUnchanged": True,
        "newOperatorApprovalRequired": True,
        "newPlanDigestRequired": True,
        "operationalCaseIds": "not-selected",
        "operationalThresholdIssued": False,
        "plannedDiagnosticRuns": 6,
        "promptsUnchanged": True,
        "publisherTemplateUnchanged": True,
        "rawOutputRetention": "bounded-immutable",
        "repetitionsPerCase": 1,
        "representativeCaseRule": REPRESENTATIVE_RULE,
        "requiredDiagnostics": list(source["requiredDiagnostics"]),
        "responseSchemaUnchanged": True,
        "reuseAcceptedMemoryEvidence": True,
        "runtimeAndCandidateUnchanged": True,
        "systematicThreshold": THRESHOLD,
    }


def assemble_track10_review() -> dict[str, Any]:
    """Assemble the approved review before its digest is sealed."""
    sources = _sources()
    document = {
        **common(),
        **decision_for(SELECTED_TRACK),
        "acceptedResiduals": [
            {"residualId": residual_id, "statement": statement}
            for residual_id, statement in _RESIDUALS
        ],
        "alternativeDecisions": [dict(row) for row in _ALTERNATIVES],
        "attributedResponseEvidence": "approved",
        "authorityAnalysis": _authority(sources["schemaInvariantReview"]),
        "authorizedScope": _SCOPE,
        "candidateRejectionSupported": False,
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "consumedPlans": _plans(),
        "decision": "six-run diagnostic authorized in principle",
        "diagnosticBoundary": _boundary(sources["sixRunDiagnosticAuthorization"]),
        "investmentStopSelected": False,
        "mandatoryFailureSupported": False,
        "notAuthorized": list(_NOT_AUTHORIZED),
        "operationalThresholdIssued": False,
        "proportionalityAnalysis": "approved",
        "proportionalityJudgment": "six-run-proportionate",
        "qualityVerdict": False,
        "responseEvidence": _response(sources["attributedResponseEvidence"]),
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-18",
        "reviewStatus": "accepted-by-principal-systems-architect",
        "schemaAuthorityReview": "approved",
        "sixRunDiagnostic": "authorized-in-principle",
        "sixRunPrecedesFullRerun": True,
        "sourceDigests": {name: source["identityDigest"] for name, source in sources.items()},
    }
    require_track10_review(document, sources=sources, sealed=False)
    return document


def require_track10_review(
    document: dict[str, Any],
    *,
    sources: dict[str, dict[str, Any]] | None = None,
    sealed: bool = True,
) -> None:
    """Require the approved review to match the six Track 10 decision records."""
    require_session_decision(document)
    loaded = sources if sources is not None else _sources()
    _require_response(document, loaded["attributedResponseEvidence"])
    _require_authority(document, loaded["schemaInvariantReview"])
    _require_alternatives(document, loaded["diagnosticProportionality"])
    _require_boundary(document, loaded["sixRunDiagnosticAuthorization"])
    _require_stop(document, loaded["investmentStopDecision"])
    _require_disposition(document, loaded["candidateDisposition"])
    if document["sourceDigests"] != {
        name: source["identityDigest"] for name, source in loaded.items()
    }:
        raise MeasurementError("record-drift")
    if document["consumedPlans"] != _plans():
        raise MeasurementError("plan-issued")
    if tuple(document["notAuthorized"]) != _NOT_AUTHORIZED:
        raise MeasurementError("contradictory-authority")
    if document["attributedResponseEvidence"] != "approved":
        raise MeasurementError("review-drift")
    if document["schemaAuthorityReview"] != "approved":
        raise MeasurementError("review-drift")
    if document["proportionalityAnalysis"] != "approved":
        raise MeasurementError("review-drift")
    if document["sixRunDiagnostic"] != "authorized-in-principle":
        raise MeasurementError("review-drift")
    if document["reviewDate"] != "2026-11-18":
        raise MeasurementError("review-drift")
    if document["reviewAuthority"] != "PatchPilot Principal Systems Architect":
        raise MeasurementError("review-drift")
    if document["reviewStatus"] != "accepted-by-principal-systems-architect":
        raise MeasurementError("review-drift")
    if document["decision"] != "six-run diagnostic authorized in principle":
        raise MeasurementError("review-drift")
    if document["authorizedScope"] != _SCOPE:
        raise MeasurementError("review-drift")
    if document["candidateRejectionSupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["mandatoryFailureSupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["investmentStopSelected"] is not False:
        raise MeasurementError("stop-selected")
    if document["qualityVerdict"] is not False:
        raise MeasurementError("quality-verdict")
    if document["operationalThresholdIssued"] is not False:
        raise MeasurementError("hidden-threshold")
    if document["sixRunPrecedesFullRerun"] is not True:
        raise MeasurementError("proportionality")
    observed = [
        (item["componentId"], item["disposition"], item["statement"])
        for item in document["componentReviews"]
    ]
    if observed != list(_COMPONENTS):
        raise MeasurementError("review-drift")
    residuals = [(item["residualId"], item["statement"]) for item in document["acceptedResiduals"]]
    if residuals != list(_RESIDUALS):
        raise MeasurementError("review-drift")
    if sealed and document["reviewDigest"] != review_digest(document):
        raise MeasurementError("review-digest")


def _require_response(document: dict[str, Any], source: dict[str, Any]) -> None:
    evidence = document["responseEvidence"]
    if evidence != _response(source):
        raise MeasurementError("response-identity")
    if evidence["runId"] != "case-ground-001-r1" or source["runId"] != evidence["runId"]:
        raise MeasurementError("response-identity")
    if (evidence["stdoutBytes"], evidence["stdoutDigest"]) != (542, source["stdoutDigest"]):
        raise MeasurementError("stdout-identity")
    if source["stdoutBytes"] != 542 or source["stdoutDigest"] != document["stdoutDigest"]:
        raise MeasurementError("stdout-identity")
    extracted = (evidence["extractedBytes"], evidence["extractedDigest"])
    if extracted != (264, source["extractedDigest"]):
        raise MeasurementError("extracted-identity")
    if source["extractedBytes"] != 264 or source["extractedDigest"] != document["extractedDigest"]:
        raise MeasurementError("extracted-identity")
    if source["parseStatus"] != "parsed" or evidence["jsonParse"] != "passed":
        raise MeasurementError("parse-status")
    if source["schemaStatus"] != "invalid" or evidence["responseSchemaValidation"] != "failed":
        raise MeasurementError("schema-status")
    if source["stdoutTruncated"] is not False or source["stderrTruncated"] is not False:
        raise MeasurementError("truncation")
    if evidence["truncation"] is not False:
        raise MeasurementError("truncation")
    if source["outputLimitStatus"] != "within-limit":
        raise MeasurementError("output-limit")
    if evidence["outputLimitExceeded"] is not False:
        raise MeasurementError("output-limit")
    if evidence["adapterInnerFieldMutation"] is not False:
        raise MeasurementError("adapter-preservation")
    if source["adapterAddedInnerFields"] is not False or source["innerObjectUnchanged"] is not True:
        raise MeasurementError("adapter-preservation")
    if source["adapterRenamedFields"] is not False or source["adapterRemovedFields"] is not False:
        raise MeasurementError("adapter-preservation")
    if tuple(evidence["missingRequiredFields"]) != tuple(source["missingRequiredFields"]):
        raise MeasurementError("missing-fields")
    if tuple(source["missingRequiredFields"]) != MISSING_REQUIRED:
        raise MeasurementError("missing-fields")
    if tuple(evidence["unexpectedFields"]) != UNEXPECTED:
        raise MeasurementError("unexpected-fields")
    if tuple(source["unexpectedFields"]) != UNEXPECTED:
        raise MeasurementError("unexpected-fields")
    if source["responseFailureAuthority"] != "candidate-output":
        raise MeasurementError("authority-separation")
    if source["executionStopAuthority"] != "measurement-infrastructure":
        raise MeasurementError("authority-separation")


def _require_authority(document: dict[str, Any], source: dict[str, Any]) -> None:
    analysis = document["authorityAnalysis"]
    if analysis != _authority(source):
        raise MeasurementError("unsupported-rejection")
    if tuple(analysis["invariantGateNames"]) != INVARIANT_GATES:
        raise MeasurementError("invariant-gates")
    if "outputSchemaValidity" in analysis["invariantGateNames"]:
        raise MeasurementError("invariant-gates")
    if source["oneInvalidRunIsInvariantFailure"] is not False:
        raise MeasurementError("unsupported-rejection")
    if source["oneInvalidRunRejectsCandidate"] is not False:
        raise MeasurementError("unsupported-rejection")
    if source["rejectionCurrentlySupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if source["mandatoryFailureSupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if source["percentageGateName"] != "outputSchemaValidity":
        raise MeasurementError("percentage-gate")
    if source["percentageGateKind"] != "proposed-percentage":
        raise MeasurementError("percentage-gate")
    if source["percentageRule"] != "exactly-100":
        raise MeasurementError("percentage-gate")
    if source["percentageStatusOnThisRun"] != "unmeasured":
        raise MeasurementError("percentage-gate")
    if source["fullResultSetRequiredForPercentage"] is not True:
        raise MeasurementError("percentage-gate")
    if source["repetitionsRequiredForConsistency"] != 3 or source["observedRepetitions"] != 1:
        raise MeasurementError("repetition-authority")
    if source["oneRepetitionEstablishesConsistency"] is not False:
        raise MeasurementError("repetition-authority")
    if source["executionContinuationCriterion"] != "measured-continue":
        raise MeasurementError("continuation-criterion")
    if source["majorityThreshold"] != THRESHOLD:
        raise MeasurementError("hidden-threshold")
    if analysis["oneResponseSupportsCandidateRejection"] is not False:
        raise MeasurementError("unsupported-rejection")
    if analysis["perRunResponseContract"] != "failed":
        raise MeasurementError("schema-status")


def _require_alternatives(document: dict[str, Any], source: dict[str, Any]) -> None:
    rows = document["alternativeDecisions"]
    if rows != [dict(row) for row in _ALTERNATIVES]:
        raise MeasurementError("proportionality-selection")
    selected = [row["alternativeId"] for row in rows if row["selected"]]
    if selected != [SELECTED_ALTERNATIVE]:
        raise MeasurementError("proportionality-selection")
    if document["selectedAlternative"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("proportionality-selection")
    if document["proportionalityJudgment"] != "six-run-proportionate":
        raise MeasurementError("proportionality-selection")
    if source["selectedAlternative"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("proportionality-selection")
    if source["proportionalityJudgment"] != "six-run-proportionate":
        raise MeasurementError("proportionality-selection")
    if source["sixRunPrecedesFullRerun"] is not True or source["fullCorpusSelected"] is not False:
        raise MeasurementError("full-corpus-selected")
    by_id = {row["alternativeId"]: row for row in source["alternatives"]}
    if [row["alternativeId"] for row in source["alternatives"] if row["selected"]] != selected:
        raise MeasurementError("proportionality-selection")
    if by_id["reject-now"]["eligible"] is not False:
        raise MeasurementError("unsupported-rejection")
    if by_id["protocol-forensics"]["eligible"] is not False:
        raise MeasurementError("forensics-eligible")
    if by_id["full-72-run-continuation"]["eligible"] is not True:
        raise MeasurementError("full-corpus-selected")
    if by_id["full-72-run-continuation"]["selected"] is not False:
        raise MeasurementError("full-corpus-selected")
    if by_id["stop-investment"]["eligible"] is not True or by_id["stop-investment"]["selected"]:
        raise MeasurementError("stop-selected")
    if by_id["six-run-diagnostic"]["selected"] is not True:
        raise MeasurementError("proportionality-selection")
    for alternative_id, disqualifier in _SOURCE_DISQUALIFIERS.items():
        if by_id[alternative_id]["disqualifier"] != disqualifier:
            raise MeasurementError("proportionality-selection")
        if by_id[alternative_id]["qualityVerdict"] is not False:
            raise MeasurementError("quality-verdict")


def _require_boundary(document: dict[str, Any], source: dict[str, Any]) -> None:
    boundary = document["diagnosticBoundary"]
    if boundary != _boundary(source):
        raise MeasurementError("diagnostic-boundary")
    if document["sixRunDiagnostic"] != "authorized-in-principle":
        raise MeasurementError("diagnostic-boundary")
    if source["authorizationStatus"] != "authorized-in-principle":
        raise MeasurementError("diagnostic-boundary")
    if source["authorizesFutureSession"] is not True:
        raise MeasurementError("execution-authorized")
    if source["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    categories = tuple(boundary["categories"])
    if categories != CATEGORIES or boundary["categoryCount"] != 6:
        raise MeasurementError("category-coverage")
    if len(source["categories"]) != 6:
        raise MeasurementError("category-coverage")
    if any(row["caseId"] != "not-selected" for row in source["categories"]):
        raise MeasurementError("operational-case")
    if any(row["repetitionCount"] != 1 for row in source["categories"]):
        raise MeasurementError("diagnostic-count")
    if any(row["representativeCaseRule"] != REPRESENTATIVE_RULE for row in source["categories"]):
        raise MeasurementError("case-rule")
    if source["operationalCaseIds"] != "not-selected":
        raise MeasurementError("operational-case")
    if boundary["operationalCaseIds"] != "not-selected":
        raise MeasurementError("operational-case")
    if (boundary["plannedDiagnosticRuns"], source["plannedDiagnosticRuns"]) != (6, 6):
        raise MeasurementError("diagnostic-count")
    if boundary["repetitionsPerCase"] != 1 or source["repetitionsPerSelectedCase"] != 1:
        raise MeasurementError("diagnostic-count")
    for name in (
        "promptsUnchanged",
        "responseSchemaUnchanged",
        "publisherTemplateUnchanged",
        "decodingUnchanged",
        "limitsUnchanged",
    ):
        if source[name] is not True:
            raise MeasurementError("diagnostic-boundary")
    if source["hardenedBoundary"] != "required":
        raise MeasurementError("diagnostic-boundary")
    if source["reuseAcceptedMemoryEvidence"] is not True:
        raise MeasurementError("diagnostic-boundary")
    if source["contextMemoryRerun"] is not False or source["memoryRerun"] is not False:
        raise MeasurementError("diagnostic-boundary")
    if source["rawOutputRetention"] != "bounded-immutable":
        raise MeasurementError("raw-output")
    if tuple(source["requiredDiagnostics"]) != REQUIRED_DIAGNOSTICS:
        raise MeasurementError("diagnostics")
    if source["futureSpecification"] != "mandatory":
        raise MeasurementError("future-specification")
    if source["newPlanDigestRequired"] is not True or source["freshResultRootRequired"] is not True:
        raise MeasurementError("plan-issued")
    if source["newOperatorApprovalRequired"] is not True:
        raise MeasurementError("approval-issued")
    if source["systematicThreshold"] != THRESHOLD or boundary["systematicThreshold"] != THRESHOLD:
        raise MeasurementError("hidden-threshold")
    if boundary["operationalThresholdIssued"] is not False:
        raise MeasurementError("plan-issued")
    if boundary["executionPlanIssued"] is not False:
        raise MeasurementError("plan-issued")
    if source["futurePlanDigest"] != "not-issued" or source["operatorApproval"] != "not-issued":
        raise MeasurementError("plan-issued")
    if source["resultRootState"] != "not-created":
        raise MeasurementError("result-root-created")
    if source["candidateModelId"] != document["candidateModelId"]:
        raise MeasurementError("diagnostic-boundary")
    if source["runtimeVersionTag"] != document["runtimeVersionTag"]:
        raise MeasurementError("diagnostic-boundary")


def _require_stop(document: dict[str, Any], source: dict[str, Any]) -> None:
    if source["stopSelected"] is not False or document["investmentStopSelected"] is not False:
        raise MeasurementError("stop-selected")
    if source["stopIsQualityVerdict"] is not False or source["candidateFailureIndependentlyProven"]:
        raise MeasurementError("quality-verdict")
    if source["memoryIsRejectionBasis"] is not False:
        raise MeasurementError("memory-headroom")
    if source["recommendation"] != "continue-only-six-run-in-principle":
        raise MeasurementError("stop-selected")
    if source["selectedAlternative"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("proportionality-selection")


def _require_disposition(document: dict[str, Any], source: dict[str, Any]) -> None:
    if document["track10Disposition"] != SELECTED_TRACK:
        raise MeasurementError("contradictory-authority")
    if source["track10Disposition"] != SELECTED_TRACK:
        raise MeasurementError("contradictory-authority")
    if (
        document["candidateDisposition"] != SELECTED_CANDIDATE
        or source["candidateDisposition"] != SELECTED_CANDIDATE
    ):
        raise MeasurementError("contradictory-authority")
    if source["authorizesFutureDiagnosticInPrinciple"] is not True:
        raise MeasurementError("contradictory-authority")
    if source["authorizesCurrentExecution"] is not False:
        raise MeasurementError("execution-authorized")
    if source["mandatoryFailureSupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if source["sixRunPrecedesFullRerun"] is not True:
        raise MeasurementError("proportionality")
    if source["futurePlanDigest"] != "not-issued":
        raise MeasurementError("plan-issued")
    if source["replacementPlanDigest"] != "not-issued":
        raise MeasurementError("plan-issued")
    if source["operatorApproval"] != "not-issued" or source["resultRootState"] != "not-created":
        raise MeasurementError("plan-issued")


def build_track10_implementation_review() -> dict[str, Any]:
    """Seal the approved review. The digest is computed, not supplied."""
    document = assemble_track10_review()
    document["reviewDigest"] = review_digest(document)
    reject_track10_text(document)
    reject_sensitive(document)
    validate(SCHEMA_NAME, document)
    require_track10_review(document)
    return document


def load_track10_implementation_review() -> dict[str, Any]:
    """Load the committed review and refuse drift from its builder."""
    loaded = json.loads((repo_root() / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    document = build_track10_implementation_review()
    if loaded != document:
        raise MeasurementError("review-drift")
    return loaded
