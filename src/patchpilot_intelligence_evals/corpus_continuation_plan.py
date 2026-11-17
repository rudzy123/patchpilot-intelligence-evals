"""Track 9A corpus-only plan. Building this record does not call Run."""

from __future__ import annotations

import hashlib
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
from patchpilot_intelligence_evals.corpus import CASE_IDS
from patchpilot_intelligence_evals.corpus_continuation_authorization import (
    load_corpus_continuation_authorization,
)
from patchpilot_intelligence_evals.finalist_budget import RUNTIME_TAG
from patchpilot_intelligence_evals.inference_retry_plan import (
    CONSUMED_RETRY_PLAN_DIGEST,
    owner_mode,
    require_inference_retry_approval,
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
from patchpilot_intelligence_evals.measurement_retry_plan import require_open_retry_plan
from patchpilot_intelligence_evals.memory_evidence_review import load_memory_evidence_review
from patchpilot_intelligence_evals.protocol import (
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    PROMPT_IDENTITY,
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
)
from patchpilot_intelligence_evals.runtime_dependency_closure import closure_digest
from patchpilot_intelligence_evals.schemas import repo_root, schema_path
from patchpilot_intelligence_evals.track8b_r2_records import PLAN_DIGEST as R2_PLAN_DIGEST
from patchpilot_intelligence_evals.track8b_records import (
    APPROVED_PLAN_DIGEST,
    require_reusable_plan,
)
from patchpilot_intelligence_evals.track9_implementation_review import (
    load_track9_implementation_review,
)
from patchpilot_intelligence_evals.track9_review import (
    COLD_4096_PEAK_BYTES,
    COLD_8192_PEAK_BYTES,
    DEPENDENCY_CLOSURE_DIGEST,
    HEADROOM_BYTES,
    MEMORY_SOURCE_DIGEST,
    WARM_4096_PEAK_BYTES,
    WARM_8192_PEAK_BYTES,
)

SESSION_ID = "intelligence-track-9a"
RESULT_ROOT_CLASS = "corpus-continuation-result"
PROFILE_ID = "linux-bwrap-systemd-v1"
FRESH_RESULT_ROOT = Path("/var/tmp/patchpilot-evals-track9a-corpus")
TRACK9_AUTHORIZATION_DIGEST = "e7325c76745505e533afaf12b108470fb6a2a2c765e5f7335b3b1ce1ef6c7477"
TRACK9_REVIEW_DIGEST = "d9dcf838be1d90f05ef69e53ae86822b34ca9aa1a4681a752306defe4d2cd305"
RUNTIME_LIBRARY_SHA256 = "a96f132e5eb5ca04e23a7d2fc1078fb95aa591e8d71d0f237702ece3a1e0f4ea"
SOURCE_REVISION = "b9d816ab510f9a28dca37cb182e9da8b0226e13c"
SYNTHETIC_RENDERED_DIGEST = "5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d"
ENVELOPE_SCHEMA_ID = "urn:patchpilot-intelligence-evals:schema:candidate-response:v1"
EXPLANATION_SCHEMA_ID = "urn:patchpilot-intelligence-evals:schema:finding-explanation-output:v1"
RESULT_FREE_BYTES = 64 * 1024 * 1024
CASE_COUNT = 24
REPETITIONS = 3
PLANNED_RUNS = 72
_PLAN = Path("candidates/authorization/corpus-continuation-plan.json")
_APPROVAL = Path("candidates/authorization/corpus-continuation-approval.json")
_CONSUMED = frozenset({APPROVED_PLAN_DIGEST, CONSUMED_RETRY_PLAN_DIGEST, R2_PLAN_DIGEST})
_HISTORICAL_RESULT_ROOTS = (
    Path("/var/tmp/patchpilot-evals-track8a"),
    Path("/var/tmp/patchpilot-evals-track8a/runtime-cache"),
    Path("/var/tmp/patchpilot-evals-track8a/model-cache"),
    Path("/var/tmp/patchpilot-evals-track8b-approved-8280ec63"),
    Path("/var/tmp/patchpilot-evals-track8b-checkpoint"),
    Path("/var/tmp/patchpilot-evals-track8b-r1-572fc9da"),
    Path("/var/tmp/patchpilot-evals-track8b-r2"),
)
_HISTORICAL_NAMES = (
    "track8a",
    "track8b-approved",
    "track8b-checkpoint",
    "track8b-r1",
    "track8b-r2",
)
PHASE_ORDER: tuple[str, ...] = (
    "preflight",
    "template-compatibility",
    "dynamic-link-precheck",
    "corpus-evaluation",
)
STOP_CONDITIONS: tuple[str, ...] = (
    "approval-required",
    "cleanup-failure",
    "compatibility-failure",
    "corpus-mismatch",
    "digest-mismatch",
    "evaluator-failure",
    "excessive-output",
    "gold-visible",
    "isolation-failure",
    "memory-ceiling",
    "network-violation",
    "oom",
    "plan-consumed",
    "precheck-failed",
    "prompt-mismatch",
    "raw-output-unretained",
    "response-schema-mismatch",
    "result-root-reuse",
    "telemetry-unresolved",
    "unclassified-launch",
    "unverified-dependency",
)
FAILURE_AUTHORITIES: tuple[str, ...] = (
    "adapter",
    "candidate-output",
    "evaluator",
    "measurement-infrastructure",
    "protocol",
    "security-boundary",
    "unresolved",
)
_OMITTED = ("context-4096", "context-8192", "one-token-smoke", "short-generation")
_MEASURED_CONTINUE = frozenset(
    {
        "inference-failure",
        "malformed-response",
        "model-load-failure",
        "nonzero-exit",
        "runtime-startup-failure",
        "schema-failure",
        "success",
        "timeout",
        "tokenizer-failure",
    }
)


def response_schema_digest() -> str:
    """Hash the committed response schemas. The files are not rewritten."""
    envelope = schema_path("candidate-response").read_bytes()
    explanation = schema_path("finding-explanation-output").read_bytes()
    return hashlib.sha256(envelope + b"\n" + explanation).hexdigest()


def run_inventory() -> list[dict[str, Any]]:
    """Return the 72 serial run identities. Case order follows the corpus."""
    if len(CASE_IDS) != CASE_COUNT:
        raise MeasurementError("corpus-mismatch")
    rows: list[dict[str, Any]] = []
    for case_id in CASE_IDS:
        for repetition in range(1, REPETITIONS + 1):
            rows.append(
                {
                    "caseId": case_id,
                    "repetition": repetition,
                    "runId": f"{case_id}-r{repetition}",
                }
            )
    if len(rows) != PLANNED_RUNS or len({row["runId"] for row in rows}) != PLANNED_RUNS:
        raise MeasurementError("run-inventory")
    return rows


def identity_fields(plan: dict[str, Any]) -> dict[str, Any]:
    """Authority pins copied onto every Track 9A record."""
    return {
        **authority(),
        "comparisonWinner": None,
        "consumedInferencePlanDigest": R2_PLAN_DIGEST,
        "consumedRetryPlanDigest": CONSUMED_RETRY_PLAN_DIGEST,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": APPROVED_PLAN_DIGEST,
        "r3Plan": "not-issued",
        "replacementPlanDigest": "not-issued",
        "resultRootClass": RESULT_ROOT_CLASS,
        "sessionId": SESSION_ID,
        "track9AuthorizationDigest": TRACK9_AUTHORIZATION_DIGEST,
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


def continuation_stop(cause: str | None) -> bool:
    """Return whether a cause withholds every later run."""
    return cause in STOP_CONDITIONS


def measured_continue(outcome: str) -> bool:
    """Return whether one measured outcome may be followed by another case."""
    return outcome in _MEASURED_CONTINUE


def historical_rejections() -> list[dict[str, str]]:
    """Prove each consumed plan is refused before Run."""
    checks: tuple[tuple[str, str, Any], ...] = (
        (APPROVED_PLAN_DIGEST, "require_reusable_plan", require_reusable_plan),
        (CONSUMED_RETRY_PLAN_DIGEST, "require_open_retry_plan", require_open_retry_plan),
        (
            R2_PLAN_DIGEST,
            "require_inference_retry_approval",
            lambda: require_inference_retry_approval(R2_PLAN_DIGEST),
        ),
    )
    rows: list[dict[str, str]] = []
    for digest, name, function in checks:
        try:
            function()
        except MeasurementError as exc:
            result = str(exc)
        else:
            raise MeasurementError("plan-consumed")
        if result != "plan-consumed":
            raise MeasurementError("plan-consumed")
        rows.append({"digest": digest, "function": name, "result": result})
    return rows


def build_corpus_plan(root: Path | None = None) -> dict[str, Any]:
    """Seal the corpus-only plan. Historical digests stay consumed."""
    _require_track9_authority(root)
    if closure_digest() != DEPENDENCY_CLOSURE_DIGEST:
        raise MeasurementError("digest-mismatch")
    document: dict[str, Any] = {
        **authority(),
        "acceptedMemory": _accepted_memory(root),
        "addressSpaceBytes": ADDRESS_SPACE_BYTES,
        "artifactsUnchanged": True,
        "batchSize": 1,
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateModelId": LFM_MODEL_ID,
        "candidatePrecision": "FP32",
        "caseCount": CASE_COUNT,
        "chatTemplateDigest": CHAT_TEMPLATE_SHA256,
        "cleanup": "process-tree",
        "comparisonWinner": None,
        "consumedPlans": _consumed_plans(),
        "corpusDigest": CORPUS_DIGEST,
        "cpuSeconds": 600,
        "currentExecutionAuthority": False,
        "decoding": _decoding(),
        "dependencyClosureDigest": DEPENDENCY_CLOSURE_DIGEST,
        "diagnosticPolicy": _diagnostic_policy(),
        "dynamicLinkPrecheckDigest": "not-executed",
        "eosTokenId": 7,
        "executionStatus": "not-executed",
        "gatesUnchanged": True,
        "generationBudgetSeconds": 15,
        "goldIsolation": "mandatory",
        "harnessCandidateId": HARNESS_CANDIDATE_ID,
        "hostCapabilityClass": "linux-cgroup-v2-user-scope",
        "interOpThreads": 1,
        "intraOpThreads": 8,
        "maxNewTokens": 256,
        "measurementCompleted": False,
        "measurementPerformed": False,
        "memoryMaxBytes": MEMORY_CAP,
        "memorySwapMaxBytes": 0,
        "metricsUnchanged": True,
        "modelSessionCreated": False,
        "networkDenial": "os-level",
        "omittedPhases": list(_OMITTED),
        "onnxRevision": PROTOCOL_CANDIDATE_VERSION,
        "operatorApproval": "required",
        "phases": _phases(),
        "plainSubprocessFallback": False,
        "plannedRuns": PLANNED_RUNS,
        "profileId": PROFILE_ID,
        "profileVersion": "1.0.0",
        "promptTemplateDigest": PROMPT_TEMPLATE_DIGEST,
        "promptsUnchanged": True,
        "r3Plan": "not-issued",
        "rawOutputRetention": _raw_policy(),
        "realModelExecuted": False,
        "replacementPlanDigest": "not-issued",
        "repetitionsPerCase": REPETITIONS,
        "responseSchema": _response_schema(),
        "responseSchemaUnchanged": True,
        "resultRootClass": RESULT_ROOT_CLASS,
        "resultRootState": "not-created",
        "retries": 0,
        "runInvoked": False,
        "runs": run_inventory(),
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
        "tasksMax": 32,
        "tokenizerDigest": TOKENIZER_SHA256,
        "track9AuthorizationDigest": TRACK9_AUTHORIZATION_DIGEST,
        "track9ReviewDigest": TRACK9_REVIEW_DIGEST,
        "wallClockSeconds": 900,
    }
    sealed = digest_document(document, "corpus-continuation-plan", "planDigest")
    if sealed["planDigest"] in _CONSUMED:
        raise MeasurementError("digest-mismatch")
    return sealed


def load_corpus_plan(root: Path | None = None) -> dict[str, Any]:
    """Load the committed plan and require it to match the builder."""
    return _load(root, _PLAN, build_corpus_plan)


def build_corpus_approval(root: Path | None = None) -> dict[str, Any]:
    """Bind the new digest. The committed record stays not-approved."""
    plan = build_corpus_plan(root)
    return digest_document(
        {
            **authority(),
            "approvalStatus": "not-approved",
            "comparisonWinner": None,
            "consumedInferencePlanDigest": R2_PLAN_DIGEST,
            "consumedRetryPlanDigest": CONSUMED_RETRY_PLAN_DIGEST,
            "currentExecutionAuthority": False,
            "measurementCompleted": False,
            "measurementPerformed": False,
            "modelSessionCreated": False,
            "operatorCheckpoint": "required",
            "planDigest": plan["planDigest"],
            "priorPlanDigest": APPROVED_PLAN_DIGEST,
            "r3Plan": "not-issued",
            "realModelExecuted": False,
            "replacementPlanDigest": "not-issued",
            "resultRootClass": RESULT_ROOT_CLASS,
            "runInvoked": False,
            "sessionId": SESSION_ID,
            "track9AuthorizationDigest": TRACK9_AUTHORIZATION_DIGEST,
        },
        "corpus-continuation-approval",
        "identityDigest",
    )


def load_corpus_approval(root: Path | None = None) -> dict[str, Any]:
    """Load the committed approval and require it to match the builder."""
    return _load(root, _APPROVAL, build_corpus_approval)


def require_corpus_approval(supplied: str, root: Path | None = None) -> dict[str, Any]:
    """Refuse every digest. The Track 9A plan is consumed and is not reusable."""
    if supplied in _CONSUMED:
        raise MeasurementError("plan-consumed")
    historical_rejections()
    plan = load_corpus_plan(root)
    approval = load_corpus_approval(root)
    if supplied != plan["planDigest"] or approval["planDigest"] != plan["planDigest"]:
        raise MeasurementError("approval-required")
    if approval["approvalStatus"] != "not-approved":
        raise MeasurementError("approval-required")
    if plan["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    from patchpilot_intelligence_evals.track9a_records import load_plan_disposition

    disposition = load_plan_disposition()
    if disposition["planDigest"] != plan["planDigest"]:
        raise MeasurementError("digest-mismatch")
    if disposition["planDisposition"] != "consumed" or disposition["reusable"] is not False:
        raise MeasurementError("record-drift")
    if disposition["replacementPlanDigest"] != "not-issued":
        raise MeasurementError("record-drift")
    raise MeasurementError("plan-consumed")


def validate_continuation_root(root: Path, *, resume: bool) -> Path:
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


def prepare_continuation_root(root: Path) -> Path:
    """Create an empty owner-only root when the path is absent."""
    if _historical(root):
        raise MeasurementError("result-root-reuse")
    if not root.exists():
        root.mkdir(mode=0o700)
        owner_mode(root)
    return validate_continuation_root(root, resume=False)


def _require_track9_authority(root: Path | None) -> None:
    base = root if root is not None else repo_root()
    authorization = load_corpus_continuation_authorization()
    review = load_track9_implementation_review()
    if authorization["identityDigest"] != TRACK9_AUTHORIZATION_DIGEST:
        raise MeasurementError("digest-mismatch")
    if authorization["futurePlanDigest"] != "not-issued":
        raise MeasurementError("plan-issued")
    if authorization["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    if review["reviewDigest"] != TRACK9_REVIEW_DIGEST:
        raise MeasurementError("digest-mismatch")
    if review["selectionOutcome"] != "no-selection" or review["productionReady"] is not False:
        raise MeasurementError("contradictory-authority")
    if base != repo_root() and not (base / _PLAN).is_file():
        return


def _accepted_memory(root: Path | None) -> dict[str, Any]:
    del root
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


def _consumed_plans() -> list[dict[str, Any]]:
    return [
        {"planDigest": APPROVED_PLAN_DIGEST, "reusable": False, "track": "track-8b"},
        {"planDigest": CONSUMED_RETRY_PLAN_DIGEST, "reusable": False, "track": "track-8b-r1"},
        {"planDigest": R2_PLAN_DIGEST, "reusable": False, "track": "track-8b-r2"},
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
    plan_digest = load_corpus_plan()["planDigest"]
    for path in resolved.rglob("*.json"):
        if path.is_symlink() or not path.is_file():
            raise MeasurementError("result-root-reuse")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or loaded.get("planDigest") != plan_digest:
            raise MeasurementError("result-root-reuse")


def _load(
    root: Path | None,
    relative: Path,
    builder: Any,
) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != builder(base):
        raise MeasurementError("record-drift")
    return loaded
