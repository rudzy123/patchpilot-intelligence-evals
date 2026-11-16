"""Track 8B-R1 measurement plan. Building this record does not call session Run."""

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
from patchpilot_intelligence_evals.cgroup_memory import empty_memory_events
from patchpilot_intelligence_evals.measurement_plan import (
    ADDRESS_SPACE_BYTES,
    CHAT_TEMPLATE_SHA256,
    MeasurementError,
    authority,
    digest_document,
    empty_memory,
    load_measurement_plan,
)
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.template_compatibility import (
    CHAT_TEMPLATE_SHA256 as TEMPLATE_DIGEST,
)
from patchpilot_intelligence_evals.track8b_records import (
    APPROVED_PLAN_DIGEST,
    load_plan_disposition,
)

SESSION_ID = "intelligence-track-8b-r1"
PRIOR_PLAN_DIGEST = APPROVED_PLAN_DIGEST
RESULT_ROOT_CLASS = "measurement-retry-result"
COMPATIBILITY_BOUNDARY = "template-compatibility-boundary"
SYNTHETIC_CONTENT = "synthetic-user"
SYNTHETIC_RENDERED_DIGEST = "5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d"
PROFILE_ID = "linux-bwrap-systemd-v1"
RESULT_FREE_BYTES = 64 * 1024 * 1024
_PLAN = Path("candidates/authorization/measurement-retry-plan.json")
_APPROVAL = Path("candidates/authorization/measurement-retry-approval.json")
_HISTORICAL_RESULT_ROOTS = (
    Path("/var/tmp/patchpilot-evals-track8b-approved-8280ec63"),
    Path("/var/tmp/patchpilot-evals-track8b-checkpoint"),
)
PHASE_ORDER: tuple[str, ...] = (
    "preflight",
    "template-compatibility",
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
    "prior-phase-failed",
    "result-root-reuse",
    "telemetry-unresolved",
    "unverified-dependency",
)
_SESSION_STOPS = frozenset(STOP_CONDITIONS)
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
        "one-token-smoke",
        "template-compatibility",
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
        4,
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
        5,
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
        6,
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
        7,
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


def empty_retry_memory() -> dict[str, Any]:
    """Resident counters plus ``memory.events``. Address space stays separate."""
    memory = empty_memory()
    memory["memoryEvents"] = empty_memory_events()
    return memory


def reject_prior_plan(supplied: str | None = None) -> dict[str, Any]:
    """Refuse the consumed Track 8B digest. This does not issue a replacement there."""
    disposition = load_plan_disposition()
    if disposition["planDigest"] != PRIOR_PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    if disposition["planDisposition"] != "consumed" or disposition["reusable"] is not False:
        raise MeasurementError("plan-consumed")
    if disposition["replacementPlanDigest"] != "not-issued":
        raise MeasurementError("plan-consumed")
    if supplied == PRIOR_PLAN_DIGEST:
        raise MeasurementError("plan-consumed")
    return disposition


def build_retry_plan(root: Path | None = None) -> dict[str, Any]:
    """Seal a new plan from the consumed plan's artifact identities."""
    reject_prior_plan()
    if CHAT_TEMPLATE_SHA256 != TEMPLATE_DIGEST:
        raise MeasurementError("digest-mismatch")
    previous = load_measurement_plan(root)
    if previous["planDigest"] != PRIOR_PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    document: dict[str, Any] = {
        "addressSpaceBytes": ADDRESS_SPACE_BYTES,
        "calibrationStatus": "not-approved",
        "candidateAttemptId": previous["candidateAttemptId"],
        "candidateFiles": list(previous["candidateFiles"]),
        "candidateModelId": previous["candidateModelId"],
        "chatTemplateSha256": CHAT_TEMPLATE_SHA256,
        "compatibilityBoundary": COMPATIBILITY_BOUNDARY,
        "corpusDigest": previous["corpusDigest"],
        "decoding": decoding(),
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
        "syntheticContent": SYNTHETIC_CONTENT,
        "syntheticRenderedDigest": SYNTHETIC_RENDERED_DIGEST,
        "tasksMax": previous["tasksMax"],
    }
    sealed = digest_document(document, "measurement-retry-plan", "planDigest")
    if sealed["planDigest"] == PRIOR_PLAN_DIGEST:
        raise MeasurementError("digest-mismatch")
    return sealed


def load_retry_plan(root: Path | None = None) -> dict[str, Any]:
    """Load the committed retry plan and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _PLAN).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != build_retry_plan(base):
        raise MeasurementError("record-drift")
    return loaded


def build_retry_approval(root: Path | None = None) -> dict[str, Any]:
    """Bind the new digest. The committed record stays not-approved."""
    plan = build_retry_plan(root)
    return digest_document(
        {
            **frozen_flags(),
            "approvalStatus": "not-approved",
            "planDigest": plan["planDigest"],
        },
        "measurement-retry-approval",
        "identityDigest",
    )


def load_retry_approval(root: Path | None = None) -> dict[str, Any]:
    """Load the committed approval record and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _APPROVAL).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != build_retry_approval(base):
        raise MeasurementError("record-drift")
    return loaded


def require_retry_approval(supplied: str, root: Path | None = None) -> dict[str, Any]:
    """Accept only the new plan digest. The consumed digest stays rejected."""
    reject_prior_plan(supplied)
    plan = load_retry_plan(root)
    if supplied != plan["planDigest"]:
        raise MeasurementError("approval-required")
    if load_retry_approval(root)["planDigest"] != plan["planDigest"]:
        raise MeasurementError("approval-required")
    return plan


def require_open_retry_plan() -> None:
    """Refuse the consumed retry plan before a real launch."""
    from patchpilot_intelligence_evals.track8b_r1_records import load_retry_disposition

    document = load_retry_disposition()
    if document["reusable"] is False or document["planDisposition"] == "consumed":
        raise MeasurementError("plan-consumed")
    if document["replacementPlanDigest"] != "not-issued":
        raise MeasurementError("plan-consumed")
    raise MeasurementError("plan-consumed")


def phase_by_name(plan: dict[str, Any], name: str) -> dict[str, Any]:
    """Return one retry phase definition."""
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


def validate_retry_result_root(root: Path, *, resume: bool) -> Path:
    """Accept a fresh external result root. The historical root stays untouched."""
    try:
        resolved = validate_external_root(root)
    except PlanError as exc:
        raise MeasurementError(exc.code) from exc
    if resolved.is_symlink():
        raise MeasurementError("result-root-reuse")
    if _historical(resolved):
        raise MeasurementError("result-root-reuse")
    mode = resolved.stat().st_mode
    if mode & 0o077:
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


def _historical(resolved: Path) -> bool:
    text = resolved.as_posix()
    if PRIOR_PLAN_DIGEST in text or "track8b-approved" in resolved.name:
        return True
    for historical in _HISTORICAL_RESULT_ROOTS:
        if resolved == historical.resolve():
            return True
    return False


def _reject_foreign_records(resolved: Path) -> None:
    plan_digest = load_retry_plan()["planDigest"]
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
