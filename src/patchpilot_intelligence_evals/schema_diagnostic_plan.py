"""Track 10A diagnostic plan. Building this record does not call Run."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import (
    PlanError,
    available_bytes,
    validate_external_root,
)
from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.candidate_discovery import LFM_MODEL_ID
from patchpilot_intelligence_evals.corpus_continuation_plan import (
    ENVELOPE_SCHEMA_ID,
    EXPLANATION_SCHEMA_ID,
    FAILURE_AUTHORITIES,
    PROFILE_ID,
    RESULT_FREE_BYTES,
    RUNTIME_LIBRARY_SHA256,
    SOURCE_REVISION,
    STOP_CONDITIONS,
    SYNTHETIC_RENDERED_DIGEST,
    historical_rejections,
    response_schema_digest,
)
from patchpilot_intelligence_evals.corpus_continuation_plan import (
    FRESH_RESULT_ROOT as TRACK9A_RESULT_ROOT,
)
from patchpilot_intelligence_evals.diagnostic_case_selection import (
    PLANNED_RUNS,
    SELECTION_RULE,
    select_diagnostic_cases,
)
from patchpilot_intelligence_evals.finalist_budget import RUNTIME_TAG
from patchpilot_intelligence_evals.inference_retry_plan import (
    CONSUMED_RETRY_PLAN_DIGEST,
    owner_mode,
)
from patchpilot_intelligence_evals.measurement_plan import (
    ADDRESS_SPACE_BYTES,
    ARCHIVE_SHA256,
    CANDIDATE_ATTEMPT,
    CHAT_TEMPLATE_SHA256,
    CORPUS_DIGEST,
    HARNESS_CANDIDATE_ID,
    PROMPT_TEMPLATE_DIGEST,
    PROTOCOL_CANDIDATE_VERSION,
    RUNTIME_ATTEMPT,
    TOKENIZER_SHA256,
    MeasurementError,
    authority,
    digest_document,
)
from patchpilot_intelligence_evals.memory_evidence_review import load_memory_evidence_review
from patchpilot_intelligence_evals.protocol import (
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    PROMPT_IDENTITY,
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
)
from patchpilot_intelligence_evals.runtime_dependency_closure import closure_digest
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.six_run_diagnostic_authorization import (
    load_six_run_authorization,
)
from patchpilot_intelligence_evals.track8b_r2_records import PLAN_DIGEST as R2_PLAN_DIGEST
from patchpilot_intelligence_evals.track8b_records import APPROVED_PLAN_DIGEST
from patchpilot_intelligence_evals.track9_review import (
    COLD_4096_PEAK_BYTES,
    COLD_8192_PEAK_BYTES,
    DEPENDENCY_CLOSURE_DIGEST,
    HEADROOM_BYTES,
    MEMORY_SOURCE_DIGEST,
    WARM_4096_PEAK_BYTES,
    WARM_8192_PEAK_BYTES,
)
from patchpilot_intelligence_evals.track9a_records import (
    EXTRACTED_DIGEST,
    STDOUT_DIGEST,
)
from patchpilot_intelligence_evals.track9a_records import PLAN_DIGEST as CORPUS_PLAN_DIGEST
from patchpilot_intelligence_evals.track10_implementation_review import (
    load_track10_implementation_review,
)
from patchpilot_intelligence_evals.track10_review import (
    EXTRACTED_BYTES,
    STDOUT_BYTES,
)

SESSION_ID = "intelligence-track-10a"
RESULT_ROOT_CLASS = "schema-diagnostic-result"
FRESH_RESULT_ROOT = Path("/var/tmp/patchpilot-evals-track10a-schema")
TRACK10_AUTHORIZATION_DIGEST = "36478fd164229829eb159d7da42977f8e9a7d1e01e34afccbd63f1d18ce5b98b"
TRACK10_REVIEW_DIGEST = "b609cb2eb63ddfc998ec95757ea2423f033f876657b8ce0ed7ce4e5702638a28"
_PLAN = Path("candidates/authorization/schema-diagnostic-plan.json")
_APPROVAL = Path("candidates/authorization/schema-diagnostic-approval.json")
_CONSUMED = frozenset(
    {APPROVED_PLAN_DIGEST, CONSUMED_RETRY_PLAN_DIGEST, R2_PLAN_DIGEST, CORPUS_PLAN_DIGEST}
)
_HISTORICAL_RESULT_ROOTS = (
    Path("/var/tmp/patchpilot-evals-track8a"),
    Path("/var/tmp/patchpilot-evals-track8a/runtime-cache"),
    Path("/var/tmp/patchpilot-evals-track8a/model-cache"),
    Path("/var/tmp/patchpilot-evals-track8b-approved-8280ec63"),
    Path("/var/tmp/patchpilot-evals-track8b-checkpoint"),
    Path("/var/tmp/patchpilot-evals-track8b-r1-572fc9da"),
    Path("/var/tmp/patchpilot-evals-track8b-r2"),
    TRACK9A_RESULT_ROOT,
)
_HISTORICAL_NAMES = (
    "track8a",
    "track8b-approved",
    "track8b-checkpoint",
    "track8b-r1",
    "track8b-r2",
    "track9a",
)
_OMITTED = (
    "context-4096",
    "context-8192",
    "one-token-smoke",
    "short-generation",
    "full-corpus",
)
PHASE_ORDER: tuple[str, ...] = (
    "preflight",
    "template-compatibility",
    "dynamic-link-precheck",
    "schema-diagnostic",
)


def systematic_threshold() -> dict[str, Any]:
    """Return the threshold fixed before any diagnostic observation."""
    return {
        "countedAuthority": "candidate-output",
        "minimumDistinctCategories": 3,
        "minimumQualifyingFailures": 4,
        "name": "systematic-schema-failure",
        "requireAdapterInnerFieldMutation": False,
        "requireBlockingInfrastructure": False,
        "requireExtractionAuthority": True,
        "requireIntendedSchema": True,
        "requireJsonParseAuthority": True,
        "requireOutputLimitExceeded": False,
        "requireRawOutputRetained": True,
        "requireTruncated": False,
        "requiredCompletedRuns": 6,
    }


def identity_fields(plan: dict[str, Any]) -> dict[str, Any]:
    """Authority pins copied onto every Track 10A record."""
    return {
        **authority(),
        "comparisonWinner": None,
        "consumedCorpusPlanDigest": CORPUS_PLAN_DIGEST,
        "consumedInferencePlanDigest": R2_PLAN_DIGEST,
        "consumedRetryPlanDigest": CONSUMED_RETRY_PLAN_DIGEST,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": APPROVED_PLAN_DIGEST,
        "replacementPlanDigest": "not-issued",
        "resultRootClass": RESULT_ROOT_CLASS,
        "sessionId": SESSION_ID,
        "track10AuthorizationDigest": TRACK10_AUTHORIZATION_DIGEST,
        "track10ReviewDigest": TRACK10_REVIEW_DIGEST,
    }


def artifact_pins(plan: dict[str, Any]) -> dict[str, str]:
    """Runtime, corpus, prompt, and response-schema identities copied from the plan."""
    return {
        "chatTemplateDigest": str(plan["chatTemplateDigest"]),
        "corpusDigest": str(plan["corpusDigest"]),
        "promptTemplateDigest": str(plan["promptTemplateDigest"]),
        "responseSchemaDigest": str(plan["responseSchema"]["digest"]),
        "runtimeArchiveSha256": str(plan["runtimeArchiveSha256"]),
        "runtimeLibrarySha256": str(plan["runtimeLibrarySha256"]),
        "syntheticRenderedDigest": str(plan["syntheticRenderedDigest"]),
        "tokenizerDigest": str(plan["tokenizerDigest"]),
    }


def build_schema_diagnostic_plan(root: Path | None = None) -> dict[str, Any]:
    """Seal the six-run plan. Historical digests stay consumed."""
    del root
    _require_track10_authority()
    if closure_digest() != DEPENDENCY_CLOSURE_DIGEST:
        raise MeasurementError("digest-mismatch")
    if response_schema_digest() == "":
        raise MeasurementError("response-schema-mismatch")
    document: dict[str, Any] = {
        **authority(),
        "acceptedMemory": _accepted_memory(),
        "addressSpaceBytes": ADDRESS_SPACE_BYTES,
        "artifactsUnchanged": True,
        "automaticCandidateRejection": False,
        "automaticCandidateSelection": False,
        "batchSize": 1,
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateModelId": LFM_MODEL_ID,
        "candidatePrecision": "FP32",
        "caseCount": PLANNED_RUNS,
        "chatTemplateDigest": CHAT_TEMPLATE_SHA256,
        "cleanup": "process-tree",
        "comparisonWinner": None,
        "consumedPlans": _consumed_plans(),
        "contextMemoryRerun": False,
        "corpusDigest": CORPUS_DIGEST,
        "cpuSeconds": 600,
        "currentExecutionAuthority": False,
        "decoding": _decoding(),
        "dependencyClosureDigest": DEPENDENCY_CLOSURE_DIGEST,
        "diagnosticPolicy": _diagnostic_policy(),
        "dynamicLinkPrecheckDigest": "not-executed",
        "eosTokenId": 7,
        "executionStatus": "not-executed",
        "fullCorpusExecuted": False,
        "generationBudgetSeconds": 15,
        "goldIsolation": "mandatory",
        "harnessCandidateId": HARNESS_CANDIDATE_ID,
        "historicalResponse": _historical_response(),
        "hostCapabilityClass": "linux-cgroup-v2-user-scope",
        "interOpThreads": 1,
        "intraOpThreads": 8,
        "maxNewTokens": 256,
        "measurementCompleted": False,
        "measurementPerformed": False,
        "memoryMaxBytes": MEMORY_CAP,
        "memoryRerun": False,
        "memorySwapMaxBytes": 0,
        "modelSessionCreated": False,
        "networkDenial": "os-level",
        "omittedPhases": list(_OMITTED),
        "onnxRevision": PROTOCOL_CANDIDATE_VERSION,
        "operationalCaseSelection": SELECTION_RULE,
        "operatorApproval": "required",
        "percentageMetrics": False,
        "phases": _phases(),
        "plainSubprocessFallback": False,
        "plannedRuns": PLANNED_RUNS,
        "profileId": PROFILE_ID,
        "profileVersion": "1.0.0",
        "promptTemplateDigest": PROMPT_TEMPLATE_DIGEST,
        "promptsUnchanged": True,
        "promotionGateAttempt": False,
        "rawOutputRetention": _raw_policy(),
        "realModelExecuted": False,
        "replacementPlanDigest": "not-issued",
        "repetitionsPerCase": 1,
        "representsCompleteCorpus": False,
        "responseSchema": _response_schema(),
        "responseSchemaUnchanged": True,
        "resultRootClass": RESULT_ROOT_CLASS,
        "resultRootState": "not-created",
        "retries": 0,
        "runInvoked": False,
        "runs": select_diagnostic_cases(),
        "runtimeArchiveSha256": ARCHIVE_SHA256,
        "runtimeAttemptId": RUNTIME_ATTEMPT,
        "runtimeLibrarySha256": RUNTIME_LIBRARY_SHA256,
        "runtimeVersionTag": RUNTIME_TAG,
        "sessionId": SESSION_ID,
        "shell": False,
        "sourceRevision": SOURCE_REVISION,
        "stderrBytes": MAX_STDERR_BYTES,
        "stdoutBytes": MAX_STDOUT_BYTES,
        "stopConditions": list(STOP_CONDITIONS),
        "syntheticRenderedDigest": SYNTHETIC_RENDERED_DIGEST,
        "systematicThreshold": systematic_threshold(),
        "tasksMax": 32,
        "tokenizerDigest": TOKENIZER_SHA256,
        "track10AuthorizationDigest": TRACK10_AUTHORIZATION_DIGEST,
        "track10ReviewDigest": TRACK10_REVIEW_DIGEST,
        "wallClockSeconds": 900,
    }
    sealed = digest_document(document, "schema-diagnostic-plan", "planDigest")
    if sealed["planDigest"] in _CONSUMED:
        raise MeasurementError("digest-mismatch")
    return sealed


def load_schema_diagnostic_plan(root: Path | None = None) -> dict[str, Any]:
    """Load the committed plan and require it to match the builder."""
    return _load(root, _PLAN, build_schema_diagnostic_plan)


def build_schema_diagnostic_approval(root: Path | None = None) -> dict[str, Any]:
    """Bind the new digest. The committed record stays not-approved."""
    plan = build_schema_diagnostic_plan(root)
    return digest_document(
        {
            **authority(),
            "approvalStatus": "not-approved",
            "comparisonWinner": None,
            "consumedCorpusPlanDigest": CORPUS_PLAN_DIGEST,
            "consumedInferencePlanDigest": R2_PLAN_DIGEST,
            "consumedRetryPlanDigest": CONSUMED_RETRY_PLAN_DIGEST,
            "currentExecutionAuthority": False,
            "measurementCompleted": False,
            "measurementPerformed": False,
            "modelSessionCreated": False,
            "operatorCheckpoint": "required",
            "planDigest": plan["planDigest"],
            "plannedRuns": PLANNED_RUNS,
            "priorPlanDigest": APPROVED_PLAN_DIGEST,
            "realModelExecuted": False,
            "replacementPlanDigest": "not-issued",
            "repetitionsPerCase": 1,
            "resultRootClass": RESULT_ROOT_CLASS,
            "runInvoked": False,
            "runs": plan["runs"],
            "sessionId": SESSION_ID,
            "systematicThreshold": plan["systematicThreshold"],
            "track10AuthorizationDigest": TRACK10_AUTHORIZATION_DIGEST,
            "track10ReviewDigest": TRACK10_REVIEW_DIGEST,
        },
        "schema-diagnostic-approval",
        "identityDigest",
    )


def load_schema_diagnostic_approval(root: Path | None = None) -> dict[str, Any]:
    """Load the committed approval and require it to match the builder."""
    return _load(root, _APPROVAL, build_schema_diagnostic_approval)


def diagnostic_rejections() -> list[dict[str, str]]:
    """Prove each consumed plan is refused before a diagnostic launch."""
    rows = historical_rejections()
    try:
        require_schema_diagnostic_approval(CORPUS_PLAN_DIGEST)
    except MeasurementError as exc:
        result = str(exc)
    else:
        raise MeasurementError("plan-consumed")
    if result != "plan-consumed":
        raise MeasurementError("plan-consumed")
    rows.append(
        {
            "digest": CORPUS_PLAN_DIGEST,
            "function": "require_schema_diagnostic_approval",
            "result": result,
        }
    )
    return rows


def require_schema_diagnostic_approval(supplied: str, root: Path | None = None) -> dict[str, Any]:
    """Accept only the new plan digest. Every historical digest stays consumed."""
    if supplied in _CONSUMED:
        raise MeasurementError("plan-consumed")
    historical_rejections()
    from patchpilot_intelligence_evals.track9a_records import load_plan_disposition

    disposition = load_plan_disposition()
    if disposition["planDigest"] != CORPUS_PLAN_DIGEST:
        raise MeasurementError("plan-consumed")
    if disposition["planDisposition"] != "consumed" or disposition["reusable"] is not False:
        raise MeasurementError("plan-consumed")
    if disposition["replacementPlanDigest"] != "not-issued":
        raise MeasurementError("plan-consumed")
    plan = load_schema_diagnostic_plan(root)
    approval = load_schema_diagnostic_approval(root)
    if supplied != plan["planDigest"] or approval["planDigest"] != plan["planDigest"]:
        raise MeasurementError("approval-required")
    if approval["approvalStatus"] != "not-approved":
        raise MeasurementError("approval-required")
    if plan["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    if plan["planDigest"] in _CONSUMED:
        raise MeasurementError("plan-consumed")
    return plan


def validate_diagnostic_root(root: Path, *, resume: bool) -> Path:
    """Accept one fresh external root. Historical roots stay untouched."""
    if root.is_absolute() and ".." not in root.parts and _historical(Path(os.path.abspath(root))):
        raise MeasurementError("result-root-reuse")
    try:
        resolved = validate_external_root(root)
    except PlanError as exc:
        raise MeasurementError(exc.code) from exc
    if resolved.is_symlink() or _historical(resolved):
        raise MeasurementError("result-root-reuse")
    if resolved.stat().st_mode & 0o077:
        raise MeasurementError("missing-root")
    if available_bytes(resolved) < RESULT_FREE_BYTES:
        raise MeasurementError("insufficient-capacity")
    entries = [item for item in resolved.iterdir() if item.name != ".measurement-write-probe"]
    if entries and not resume:
        raise MeasurementError("result-root-reuse")
    if resume:
        _reject_foreign_records(resolved)
    probe = resolved / ".measurement-write-probe"
    try:
        probe.write_text("ok\n", encoding="utf-8")
    except OSError as exc:
        raise MeasurementError("missing-root") from exc
    finally:
        probe.unlink(missing_ok=True)
    return resolved


def prepare_diagnostic_root(root: Path) -> Path:
    """Create an empty owner-only root when the path is absent."""
    if _historical(root):
        raise MeasurementError("result-root-reuse")
    if not root.exists():
        root.mkdir(mode=0o700)
        owner_mode(root)
    return validate_diagnostic_root(root, resume=False)


def _require_track10_authority() -> None:
    authorization = load_six_run_authorization()
    review = load_track10_implementation_review()
    if authorization["identityDigest"] != TRACK10_AUTHORIZATION_DIGEST:
        raise MeasurementError("digest-mismatch")
    if authorization["authorizationStatus"] != "authorized-in-principle":
        raise MeasurementError("contradictory-authority")
    if authorization["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    if authorization["selectedAlternative"] != "six-run-diagnostic":
        raise MeasurementError("contradictory-authority")
    if authorization["futurePlanDigest"] != "not-issued":
        raise MeasurementError("plan-issued")
    if authorization["operatorApproval"] != "not-issued":
        raise MeasurementError("approval-required")
    if authorization["resultRootState"] != "not-created":
        raise MeasurementError("result-root-reuse")
    if authorization["operationalCaseIds"] != "not-selected":
        raise MeasurementError("category-coverage")
    if (
        authorization["selectionOutcome"] != "no-selection"
        or authorization["productionReady"] is not False
    ):
        raise MeasurementError("contradictory-authority")
    if (
        authorization["calibrationStatus"] != "not-approved"
        or authorization["comparisonWinner"] is not None
    ):
        raise MeasurementError("contradictory-authority")
    if review["reviewDigest"] != TRACK10_REVIEW_DIGEST:
        raise MeasurementError("digest-mismatch")
    if review["sixRunDiagnostic"] != "authorized-in-principle":
        raise MeasurementError("contradictory-authority")


def _accepted_memory() -> dict[str, Any]:
    review = load_memory_evidence_review()
    if review["reviewConclusion"] != "within-ceiling-with-limited-headroom":
        raise MeasurementError("digest-mismatch")
    if review["sourceIdentityDigest"] != MEMORY_SOURCE_DIGEST:
        raise MeasurementError("digest-mismatch")
    if (
        review["cold4096PeakBytes"] != COLD_4096_PEAK_BYTES
        or review["warm4096PeakBytes"] != WARM_4096_PEAK_BYTES
        or review["cold8192PeakBytes"] != COLD_8192_PEAK_BYTES
        or review["warm8192PeakBytes"] != WARM_8192_PEAK_BYTES
        or review["ceilingBytes"] != MEMORY_CAP
        or review["minimumHeadroomBytes"] != HEADROOM_BYTES
    ):
        raise MeasurementError("digest-mismatch")
    return {
        "ceilingBytes": MEMORY_CAP,
        "cold4096PeakBytes": COLD_4096_PEAK_BYTES,
        "cold8192PeakBytes": COLD_8192_PEAK_BYTES,
        "conclusion": "within-ceiling-with-limited-headroom",
        "minimumHeadroomBytes": HEADROOM_BYTES,
        "remeasured": False,
        "reviewDigest": review["identityDigest"],
        "sourceDigest": MEMORY_SOURCE_DIGEST,
        "warm4096PeakBytes": WARM_4096_PEAK_BYTES,
        "warm8192PeakBytes": WARM_8192_PEAK_BYTES,
    }


def _historical_response() -> dict[str, Any]:
    return {
        "countedInDiagnostic": False,
        "executionStopAuthority": "measurement-infrastructure",
        "executionStopCause": "telemetry-unresolved",
        "extractedBytes": EXTRACTED_BYTES,
        "extractedDigest": EXTRACTED_DIGEST,
        "responseFailureAuthority": "candidate-output",
        "runId": "case-ground-001-r1",
        "stdoutBytes": STDOUT_BYTES,
        "stdoutDigest": STDOUT_DIGEST,
    }


def _consumed_plans() -> list[dict[str, Any]]:
    return [
        {"planDigest": APPROVED_PLAN_DIGEST, "reusable": False, "track": "track-8b"},
        {"planDigest": CONSUMED_RETRY_PLAN_DIGEST, "reusable": False, "track": "track-8b-r1"},
        {"planDigest": R2_PLAN_DIGEST, "reusable": False, "track": "track-8b-r2"},
        {"planDigest": CORPUS_PLAN_DIGEST, "reusable": False, "track": "track-9a"},
    ]


def _decoding() -> dict[str, Any]:
    return {
        "method": "greedy-argmax",
        "repetitionPenalty": 1,
        "seed": 0,
        "seedControl": "unused",
        "seedSupport": False,
        "temperature": 0,
        "topK": 1,
        "topP": 1,
    }


def _phases() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous: str | None = None
    for index, name in enumerate(PHASE_ORDER, start=1):
        rows.append({"order": index, "phase": name, "prerequisite": previous})
        previous = name
    return rows


def _response_schema() -> dict[str, Any]:
    return {
        "digest": response_schema_digest(),
        "envelopeId": ENVELOPE_SCHEMA_ID,
        "explanationId": EXPLANATION_SCHEMA_ID,
        "promptIdentity": PROMPT_IDENTITY,
        "protocolVersion": PROTOCOL_VERSION,
        "schemaVersion": SCHEMA_VERSION,
    }


def _raw_policy() -> dict[str, Any]:
    return {
        "availableToCandidate": False,
        "availableToLaterRuns": False,
        "boundedByStdoutLimit": True,
        "freeOfGold": True,
        "hostIdentityExcluded": True,
        "immutable": True,
        "redaction": "synthetic-data-rules",
        "status": "required",
    }


def _diagnostic_policy() -> dict[str, Any]:
    return {
        "distinctStages": True,
        "erasePriorStageOnFailure": False,
        "failureAuthorities": list(FAILURE_AUTHORITIES),
        "retainBeforeExtraction": True,
    }


def _historical(resolved: Path) -> bool:
    lexical = Path(os.path.abspath(resolved))
    text = lexical.as_posix()
    if any(digest in text for digest in _CONSUMED):
        return True
    for historical in _HISTORICAL_RESULT_ROOTS:
        historical_abs = Path(os.path.abspath(historical))
        if lexical == historical_abs or historical_abs in lexical.parents:
            return True
    return any(name in lexical.name for name in _HISTORICAL_NAMES)


def _reject_foreign_records(resolved: Path) -> None:
    plan_digest = load_schema_diagnostic_plan()["planDigest"]
    for path in resolved.rglob("*.json"):
        if path.is_symlink() or not path.is_file():
            raise MeasurementError("result-root-reuse")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or loaded.get("planDigest") != plan_digest:
            raise MeasurementError("result-root-reuse")


def _load(root: Path | None, relative: Path, builder: Any) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != builder(base):
        raise MeasurementError("record-drift")
    return loaded
