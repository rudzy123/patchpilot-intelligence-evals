"""Track 8B-R2 inference retry plan. Building this record does not call Run."""

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
from patchpilot_intelligence_evals.measurement_plan import (
    ADDRESS_SPACE_BYTES,
    CHAT_TEMPLATE_SHA256,
    MeasurementError,
    authority,
    digest_document,
)
from patchpilot_intelligence_evals.measurement_retry_plan import (
    PRIOR_PLAN_DIGEST,
    reject_prior_plan,
)
from patchpilot_intelligence_evals.runtime_dependency_closure import closure_digest
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.template_compatibility import (
    CHAT_TEMPLATE_SHA256 as TEMPLATE_DIGEST,
)
from patchpilot_intelligence_evals.track8b_records import load_plan_disposition

SESSION_ID = "intelligence-track-8b-r2"
CONSUMED_RETRY_PLAN_DIGEST = "572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b"
RESULT_ROOT_CLASS = "inference-retry-result"
PROFILE_ID = "linux-bwrap-systemd-v1"
RESULT_FREE_BYTES = 64 * 1024 * 1024
FRESH_RESULT_ROOT = Path("/var/tmp/patchpilot-evals-track8b-r2")
_PLAN = Path("candidates/authorization/inference-retry-plan.json")
_APPROVAL = Path("candidates/authorization/inference-retry-approval.json")
_HISTORICAL_RESULT_ROOTS = (
    Path("/var/tmp/patchpilot-evals-track8b-approved-8280ec63"),
    Path("/var/tmp/patchpilot-evals-track8b-checkpoint"),
    Path("/var/tmp/patchpilot-evals-track8b-r1-572fc9da"),
)
_HISTORICAL_NAMES = (
    "track8b-approved",
    "track8b-checkpoint",
    "track8b-r1-572fc9da",
)
PHASE_ORDER: tuple[str, ...] = (
    "preflight",
    "template-compatibility",
    "dynamic-link-precheck",
    "one-token-smoke",
    "short-generation",
    "context-4096",
    "context-8192",
    "corpus-evaluation",
)
STOP_CONDITIONS: tuple[str, ...] = (
    "approval-required",
    "cleanup-failure",
    "compatibility-failure",
    "digest-mismatch",
    "excessive-output",
    "gold-visible",
    "insufficient-capacity",
    "isolation-failure",
    "memory-ceiling",
    "missing-root",
    "network-violation",
    "oom",
    "plan-consumed",
    "precheck-failed",
    "prior-phase-failed",
    "result-root-reuse",
    "telemetry-unresolved",
    "unverified-dependency",
)
_SESSION_STOPS = frozenset(STOP_CONDITIONS)
_CONSUMED = frozenset({PRIOR_PLAN_DIGEST, CONSUMED_RETRY_PLAN_DIGEST})
_PHASE_ROWS: tuple[tuple[object, ...], ...] = (
    (1, "preflight", None, 0, None, 1, False, "none", 1, 8192, 8192, 900, 600),
    (
        2,
        "template-compatibility",
        "preflight",
        0,
        None,
        1,
        False,
        "synthetic-fixture",
        1,
        8192,
        8192,
        900,
        600,
    ),
    (
        3,
        "dynamic-link-precheck",
        "template-compatibility",
        0,
        None,
        1,
        False,
        "dynamic-link",
        1,
        8192,
        8192,
        900,
        600,
    ),
    (
        4,
        "one-token-smoke",
        "dynamic-link-precheck",
        1,
        None,
        1,
        False,
        "chat-template",
        60,
        8192,
        262144,
        900,
        600,
    ),
    (
        5,
        "short-generation",
        "one-token-smoke",
        32,
        None,
        1,
        True,
        "chat-template",
        120,
        8192,
        262144,
        900,
        600,
    ),
    (
        6,
        "context-4096",
        "short-generation",
        1,
        4096,
        1,
        True,
        "repeated-token-id",
        300,
        8192,
        262144,
        900,
        600,
    ),
    (
        7,
        "context-8192",
        "context-4096",
        1,
        8192,
        1,
        True,
        "repeated-token-id",
        600,
        8192,
        262144,
        900,
        600,
    ),
    (
        8,
        "corpus-evaluation",
        "context-8192",
        256,
        None,
        3,
        False,
        "protocol-request",
        15,
        65536,
        16384,
        900,
        600,
    ),
)


def frozen_flags(
    *,
    measurement_performed: bool = False,
    measurement_completed: bool = False,
    run_invoked: bool = False,
    model_session_created: bool = False,
    real_model_executed: bool = False,
) -> dict[str, Any]:
    """Authority fields that stay locked unless a phase observation sets them."""
    return {
        **authority(),
        "consumedRetryPlanDigest": CONSUMED_RETRY_PLAN_DIGEST,
        "dependencyClosureDigest": closure_digest(),
        "dynamicLinkPrecheckDigest": "not-executed",
        "measurementCompleted": measurement_completed,
        "measurementPerformed": measurement_performed,
        "modelSessionCreated": model_session_created,
        "priorPlanDigest": PRIOR_PLAN_DIGEST,
        "realModelExecuted": real_model_executed,
        "resultRootClass": RESULT_ROOT_CLASS,
        "runInvoked": run_invoked,
        "sessionId": SESSION_ID,
    }


def decoding() -> dict[str, Any]:
    """The approved greedy settings. The recorded seed is unused."""
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


def require_consumed_priors(supplied: str | None = None) -> None:
    """Refuse both consumed digests. This session does not issue a replacement."""
    reject_prior_plan(supplied)
    from patchpilot_intelligence_evals.track8b_r1_records import load_retry_disposition

    disposition = load_retry_disposition()
    if disposition["planDigest"] != CONSUMED_RETRY_PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    if disposition["planDisposition"] != "consumed" or disposition["reusable"] is not False:
        raise MeasurementError("plan-consumed")
    if disposition["replacementPlanDigest"] != "not-issued":
        raise MeasurementError("plan-consumed")
    if supplied == CONSUMED_RETRY_PLAN_DIGEST:
        raise MeasurementError("plan-consumed")
    track8b = load_plan_disposition()
    if track8b["replacementPlanDigest"] != "not-issued":
        raise MeasurementError("plan-consumed")


def build_inference_plan(root: Path | None = None) -> dict[str, Any]:
    """Seal a new plan. Both earlier digests stay consumed."""
    require_consumed_priors()
    if CHAT_TEMPLATE_SHA256 != TEMPLATE_DIGEST:
        raise MeasurementError("digest-mismatch")
    from patchpilot_intelligence_evals.measurement_retry_plan import load_retry_plan

    previous = load_retry_plan(root)
    if previous["planDigest"] != CONSUMED_RETRY_PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    if previous["priorPlanDigest"] != PRIOR_PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    document: dict[str, Any] = {
        "addressSpaceBytes": ADDRESS_SPACE_BYTES,
        "calibrationStatus": "not-approved",
        "candidateAttemptId": previous["candidateAttemptId"],
        "candidateFiles": list(previous["candidateFiles"]),
        "candidateModelId": previous["candidateModelId"],
        "chatTemplateSha256": CHAT_TEMPLATE_SHA256,
        "compatibilityBoundary": "template-compatibility-boundary",
        "consumedRetryPlanDigest": CONSUMED_RETRY_PLAN_DIGEST,
        "corpusDigest": previous["corpusDigest"],
        "decoding": decoding(),
        "dependencyClosureDigest": closure_digest(),
        "dynamicLinkPrecheckDigest": "not-executed",
        "eosTokenId": previous["eosTokenId"],
        "executionStatus": "not-executed",
        "harnessCandidateId": previous["harnessCandidateId"],
        "headerMember": dict(previous["headerMember"]),
        "hostCapabilityClass": previous["hostCapabilityClass"],
        "installationAuthorized": False,
        "interOpThreads": previous["interOpThreads"],
        "intraOpThreads": previous["intraOpThreads"],
        "measurementAuthorization": "not-authorized",
        "measurementCompleted": False,
        "measurementPerformed": False,
        "memoryMaxBytes": previous["memoryMaxBytes"],
        "memorySwapMaxBytes": 0,
        "modelSessionCreated": False,
        "onnxRevision": previous["onnxRevision"],
        "operatorApproval": "required",
        "phases": [_phase(row) for row in _PHASE_ROWS],
        "priorPlanDigest": PRIOR_PLAN_DIGEST,
        "priorPlanDisposition": "consumed",
        "priorPlanReusable": False,
        "productionReady": False,
        "profileId": PROFILE_ID,
        "profileVersion": "1.0.0",
        "promptTemplateDigest": previous["promptTemplateDigest"],
        "protocolCandidateVersion": previous["protocolCandidateVersion"],
        "realModelExecuted": False,
        "repeatedTokenId": previous["repeatedTokenId"],
        "replacementPlanDigest": "not-issued",
        "resultRootClass": RESULT_ROOT_CLASS,
        "runInvoked": False,
        "runtimeArchiveSha256": previous["runtimeArchiveSha256"],
        "runtimeAttemptId": previous["runtimeAttemptId"],
        "runtimeFiles": list(previous["runtimeFiles"]),
        "runtimeRevision": previous["runtimeRevision"],
        "runtimeVersionTag": previous["runtimeVersionTag"],
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "sessionId": SESSION_ID,
        "shortPrompt": previous["shortPrompt"],
        "smokePrompt": previous["smokePrompt"],
        "sourceRevision": previous["sourceRevision"],
        "stopConditions": list(STOP_CONDITIONS),
        "syntheticContent": "synthetic-user",
        "syntheticRenderedDigest": (
            "5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d"
        ),
        "tasksMax": previous["tasksMax"],
    }
    sealed = digest_document(document, "inference-retry-plan", "planDigest")
    if sealed["planDigest"] in _CONSUMED:
        raise MeasurementError("digest-mismatch")
    return sealed


def load_inference_plan(root: Path | None = None) -> dict[str, Any]:
    """Load the committed plan and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _PLAN).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != build_inference_plan(base):
        raise MeasurementError("record-drift")
    return loaded


def build_inference_approval(root: Path | None = None) -> dict[str, Any]:
    """Bind the new digest. The committed record stays not-approved."""
    plan = build_inference_plan(root)
    return digest_document(
        {
            **frozen_flags(),
            "approvalStatus": "not-approved",
            "planDigest": plan["planDigest"],
        },
        "inference-retry-approval",
        "identityDigest",
    )


def load_inference_approval(root: Path | None = None) -> dict[str, Any]:
    """Load the committed approval record and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _APPROVAL).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != build_inference_approval(base):
        raise MeasurementError("record-drift")
    return loaded


def require_inference_retry_approval(supplied: str, root: Path | None = None) -> dict[str, Any]:
    """Refuse the consumed R2 digest and both earlier digests."""
    require_consumed_priors(supplied)
    plan = load_inference_plan(root)
    if supplied != plan["planDigest"]:
        raise MeasurementError("approval-required")
    if load_inference_approval(root)["planDigest"] != plan["planDigest"]:
        raise MeasurementError("approval-required")
    from patchpilot_intelligence_evals.track8b_r2_records import load_plan_disposition

    disposition = load_plan_disposition()
    if disposition["planDigest"] != plan["planDigest"]:
        raise MeasurementError("digest-mismatch")
    if disposition["planDisposition"] != "consumed" or disposition["reusable"] is not False:
        raise MeasurementError("record-drift")
    if (
        disposition["replacementPlanDigest"] != "not-issued"
        or disposition["r3Plan"] != "not-issued"
    ):
        raise MeasurementError("record-drift")
    raise MeasurementError("plan-consumed")


def phase_by_name(plan: dict[str, Any], name: str) -> dict[str, Any]:
    """Return one inference-retry phase definition."""
    for phase in plan["phases"]:
        if phase["phase"] == name and isinstance(phase, dict):
            return phase
    raise MeasurementError("phase")


def prerequisite_name(phase: str) -> str | None:
    """Return the phase that must already have passed."""
    if phase not in PHASE_ORDER:
        raise MeasurementError("phase")
    index = PHASE_ORDER.index(phase)
    if index == 0:
        return None
    return PHASE_ORDER[index - 1]


def session_stop(cause: str | None) -> bool:
    """Return whether a cause blocks every later phase."""
    return cause in _SESSION_STOPS


def validate_inference_result_root(root: Path, *, resume: bool) -> Path:
    """Accept a fresh external result root. Historical roots stay untouched."""
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


def prepare_fresh_result_root(root: Path) -> Path:
    """Create an empty owner-only result root when the path is absent."""
    if _historical(root):
        raise MeasurementError("result-root-reuse")
    if not root.exists():
        root.mkdir(mode=0o700)
        owner_mode(root)
    return validate_inference_result_root(root, resume=False)


def _historical(resolved: Path) -> bool:
    text = resolved.as_posix()
    if PRIOR_PLAN_DIGEST in text or CONSUMED_RETRY_PLAN_DIGEST in text:
        return True
    if any(name in resolved.name for name in _HISTORICAL_NAMES):
        return True
    lexical = Path(os.path.abspath(resolved))
    for historical in _HISTORICAL_RESULT_ROOTS:
        if lexical == Path(os.path.abspath(historical)) or resolved == historical.resolve():
            return True
    return False


def _reject_foreign_records(resolved: Path) -> None:
    plan_digest = load_inference_plan()["planDigest"]
    for path in resolved.rglob("*.json"):
        if path.is_symlink() or not path.is_file():
            raise MeasurementError("result-root-reuse")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise MeasurementError("record-type")
        if loaded.get("planDigest") != plan_digest:
            raise MeasurementError("result-root-reuse")
        if loaded.get("priorPlanDigest") not in {None, PRIOR_PLAN_DIGEST}:
            raise MeasurementError("result-root-reuse")
        if loaded.get("consumedRetryPlanDigest") not in {None, CONSUMED_RETRY_PLAN_DIGEST}:
            raise MeasurementError("result-root-reuse")


def _phase(row: tuple[object, ...]) -> dict[str, Any]:
    (
        order,
        phase,
        prerequisite,
        max_new_tokens,
        input_tokens,
        repetitions,
        cold_warm,
        prompt,
        generation_budget,
        stdout_bytes,
        stderr_bytes,
        wall,
        cpu,
    ) = row
    return {
        "batchSize": 1,
        "coldWarm": cold_warm,
        "cpuSeconds": cpu,
        "generationBudgetSeconds": generation_budget,
        "inputTokens": input_tokens,
        "maxNewTokens": max_new_tokens,
        "order": order,
        "phase": phase,
        "phaseBoundaryDwellMilliseconds": 150,
        "prerequisite": prerequisite,
        "promptConstruction": prompt,
        "repetitions": repetitions,
        "sampleIntervalMilliseconds": 100,
        "stderrBytes": stderr_bytes,
        "stdoutBytes": stdout_bytes,
        "wallClockSeconds": wall,
    }


def owner_mode(path: Path) -> None:
    """Restrict a new result directory to its owner before any phase writes."""
    os.chmod(path, 0o700)
