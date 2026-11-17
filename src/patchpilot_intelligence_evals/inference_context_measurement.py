"""Smoke, short generation, and context phases for the inference retry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_inference import Launcher, child_indexes
from patchpilot_intelligence_evals.corpus import sha256_text
from patchpilot_intelligence_evals.corrected_candidate_inference import (
    phase_limits,
    render_phase_prompt,
    repeated_token_ids,
)
from patchpilot_intelligence_evals.evaluator import repository_commit
from patchpilot_intelligence_evals.hardened_candidate_inference import launch_inference
from patchpilot_intelligence_evals.hardened_execution import execute_hardened
from patchpilot_intelligence_evals.inference_retry_plan import (
    decoding,
    load_inference_plan,
    phase_by_name,
    require_inference_retry_approval,
)
from patchpilot_intelligence_evals.inference_retry_preflight import (
    PHASE_FILES,
    SYNTHETIC_RENDERED_DIGEST,
    load_phase,
    passed,
    require_prior,
    utc_timestamp,
    write_new,
)
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    RUNTIME_ATTEMPT,
    TOKENIZER_SHA256,
    MeasurementError,
    digest_document,
    empty_timing,
)
from patchpilot_intelligence_evals.measurement_retry_plan import empty_retry_memory
from patchpilot_intelligence_evals.measurement_retry_preflight import (
    read_publisher_template as _read,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

_SMOKE = Path("candidates/templates/inference-retry-smoke-template.json")
_CONTEXT_TEMPLATE = Path("candidates/templates/inference-retry-context-memory-template.json")
_GENERATION = frozenset({"one-token-smoke", "short-generation"})
_CONTEXT_PHASES = frozenset({"context-4096", "context-8192"})


def build_smoke_template() -> dict[str, Any]:
    """Committed smoke record. It has not been executed."""
    plan = load_inference_plan()
    return digest_document(
        _smoke_body(
            plan,
            phase="not-executed",
            max_new_tokens=1,
            classified=_empty_classified(),
            executed=False,
            run_invoked=False,
            session_created=False,
            prompt="",
            rendered=None,
            precheck_digest="not-executed",
        ),
        "inference-retry-smoke",
        "identityDigest",
    )


def build_context_template() -> dict[str, Any]:
    """Committed context record. It has not been executed."""
    plan = load_inference_plan()
    return digest_document(
        _context_body(
            plan,
            phase="not-executed",
            tokens=None,
            classified=_empty_classified(),
            executed=False,
            run_invoked=False,
            session_created=False,
            precheck_digest="not-executed",
        ),
        "inference-retry-context-memory",
        "identityDigest",
    )


def load_smoke_template() -> dict[str, Any]:
    """Load the committed smoke template and require it to match the builder."""
    return _load(_SMOKE, build_smoke_template)


def load_context_template() -> dict[str, Any]:
    """Load the committed context template and require it to match the builder."""
    return _load(_CONTEXT_TEMPLATE, build_context_template)


def execute_phase(
    phase_name: str,
    *,
    approval: str,
    runtime_root: Path,
    model_root: Path,
    result_root: Path,
    indexes: dict[str, int] | None = None,
    launcher: Launcher = execute_hardened,
    executed: bool = False,
    bind: bool = True,
) -> dict[str, Any]:
    """Run one smoke, short, or context phase after the precheck has passed."""
    plan = require_inference_retry_approval(approval)
    if phase_name not in _GENERATION and phase_name not in _CONTEXT_PHASES:
        raise MeasurementError("phase")
    phase = phase_by_name(plan, phase_name)
    require_prior(result_root, phase_name)
    _require_compatibility(result_root)
    if phase_name == "context-8192":
        _require_context_predecessor(result_root, "context-4096")
    if bind:
        from patchpilot_intelligence_evals.measurement_plan import bind_verified_roots

        bind_verified_roots(runtime_root, model_root)
    if indexes is not None:
        header_indexes = indexes
    elif bind:
        header_indexes = child_indexes(read_verified_header(runtime_root))
    else:
        raise MeasurementError("unverified-dependency")
    template = ""
    rendered: str | None = None
    if phase["promptConstruction"] == "chat-template":
        template = _read(model_root)
        content = plan["smokePrompt"] if phase_name == "one-token-smoke" else plan["shortPrompt"]
        rendered = render_phase_prompt(template, str(content))
    elif phase["promptConstruction"] == "repeated-token-id":
        repeated_token_ids(int(plan["repeatedTokenId"]), int(phase["inputTokens"]))
    config = _config(plan, phase, header_indexes, rendered)
    classified, run_invoked, session_created = launch_inference(
        config,
        approval=approval,
        runtime_dir=runtime_root / "verified" / RUNTIME_ATTEMPT,
        model_dir=model_root / "verified" / CANDIDATE_ATTEMPT,
        result_root=result_root,
        limits=phase_limits(phase),
        launcher=launcher,
        executed=executed,
    )
    if phase_name in _CONTEXT_PHASES and classified["inputTokens"] != phase["inputTokens"]:
        if classified["exitClassification"] == "success":
            classified["exitClassification"] = "inference-failure"
            classified["stopCause"] = "inference-failure"
            classified["outputDigest"] = None
    precheck_digest = _precheck_digest(result_root)
    if phase_name in _GENERATION:
        document = _smoke_body(
            plan,
            phase=phase_name,
            max_new_tokens=int(phase["maxNewTokens"]),
            classified=classified,
            executed=executed,
            run_invoked=run_invoked,
            session_created=session_created,
            prompt=_prompt(plan, phase_name),
            rendered=rendered,
            precheck_digest=precheck_digest,
        )
        schema = "inference-retry-smoke"
    else:
        document = _context_body(
            plan,
            phase=phase_name,
            tokens=int(phase["inputTokens"]),
            classified=classified,
            executed=executed,
            run_invoked=run_invoked,
            session_created=session_created,
            precheck_digest=precheck_digest,
        )
        schema = "inference-retry-context-memory"
    sealed = digest_document(document, schema, "identityDigest")
    validate(schema, sealed)
    write_new(result_root, PHASE_FILES[phase_name], sealed)
    return sealed


def _require_compatibility(result_root: Path) -> None:
    document = load_phase(result_root, "template-compatibility")
    if not passed("template-compatibility", document):
        raise MeasurementError("prior-phase-failed")
    if document.get("renderedDigest") != SYNTHETIC_RENDERED_DIGEST:
        raise MeasurementError("digest-mismatch")


def _require_context_predecessor(result_root: Path, phase_name: str) -> None:
    document = load_phase(result_root, phase_name)
    if not passed(phase_name, document):
        raise MeasurementError("prior-phase-failed")


def _precheck_digest(result_root: Path) -> str:
    document = load_phase(result_root, "dynamic-link-precheck")
    digest = document.get("identityDigest")
    if not isinstance(digest, str):
        raise MeasurementError("precheck-failed")
    return digest


def _config(
    plan: dict[str, Any],
    phase: dict[str, Any],
    indexes: dict[str, int],
    rendered: str | None,
) -> dict[str, Any]:
    prompt = ""
    if phase["phase"] == "one-token-smoke":
        prompt = str(plan["smokePrompt"])
    elif phase["phase"] == "short-generation":
        prompt = str(plan["shortPrompt"])
    return {
        "coldWarm": bool(phase["coldWarm"]),
        "eosTokenId": int(plan["eosTokenId"]),
        "generationBudgetSeconds": int(phase["generationBudgetSeconds"]),
        "harnessCandidateId": plan["harnessCandidateId"],
        "indexes": indexes,
        "inputTokenCount": phase["inputTokens"],
        "interOpThreads": int(plan["interOpThreads"]),
        "intraOpThreads": int(plan["intraOpThreads"]),
        "maxNewTokens": int(phase["maxNewTokens"]),
        "phase": phase["phase"],
        "prompt": prompt,
        "promptConstruction": phase["promptConstruction"],
        "protocolCandidateVersion": plan["protocolCandidateVersion"],
        "renderedDigest": None if rendered is None else sha256_text(rendered),
        "repeatedTokenId": int(plan["repeatedTokenId"]),
    }


def _prompt(plan: dict[str, Any], phase_name: str) -> str:
    if phase_name == "one-token-smoke":
        return str(plan["smokePrompt"])
    if phase_name == "short-generation":
        return str(plan["shortPrompt"])
    return ""


def _empty_classified() -> dict[str, Any]:
    return {
        "cleanup": "not-performed",
        "coldMemory": empty_retry_memory(),
        "coldTiming": empty_timing(),
        "exitClassification": "not-executed",
        "inputTokens": None,
        "networkResult": "not-performed",
        "newTokens": None,
        "outputDigest": None,
        "stopCause": None,
        "warmMemory": empty_retry_memory(),
        "warmTiming": empty_timing(),
    }


def _links(plan: dict[str, Any], precheck_digest: str) -> dict[str, Any]:
    return {
        "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
        "dependencyClosureDigest": plan["dependencyClosureDigest"],
        "dynamicLinkPrecheckDigest": precheck_digest,
    }


def _smoke_body(
    plan: dict[str, Any],
    *,
    phase: str,
    max_new_tokens: int,
    classified: dict[str, Any],
    executed: bool,
    run_invoked: bool,
    session_created: bool,
    prompt: str,
    rendered: str | None,
    precheck_digest: str,
) -> dict[str, Any]:
    success = classified["exitClassification"] == "success"
    observed = executed and phase != "not-executed"
    return {
        "calibrationStatus": "not-approved",
        "coldMemory": classified["coldMemory"],
        "coldTiming": classified["coldTiming"],
        "compatibilityPrecededSession": observed,
        "decoding": decoding(),
        "exitClassification": classified["exitClassification"],
        "generationTokens": classified["newTokens"] if success else None,
        "inputDigest": sha256_text(prompt) if prompt else None,
        "installationAuthorized": False,
        "maxNewTokens": max_new_tokens,
        "measurementCompleted": observed,
        "measurementPerformed": observed,
        "modelSessionCreated": observed and session_created,
        "networkResult": classified["networkResult"],
        "outputDigest": classified["outputDigest"] if success else None,
        "phase": phase,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": plan["priorPlanDigest"],
        "processCleanup": classified["cleanup"],
        "productionReady": False,
        "profileId": plan["profileId"],
        "realModelExecuted": observed and success and run_invoked,
        "renderedDigest": None if rendered is None else sha256_text(rendered),
        "repositoryCommit": "not-executed" if phase == "not-executed" else repository_commit(),
        "resultRootClass": plan["resultRootClass"],
        "runInvoked": observed and run_invoked,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "sessionId": plan["sessionId"],
        "stopCause": classified["stopCause"],
        "templateDigest": plan["chatTemplateSha256"],
        "timestamp": "not-executed" if phase == "not-executed" else utc_timestamp(),
        "tokenCount": classified["inputTokens"]
        if isinstance(classified["inputTokens"], int)
        else None,
        "warmMemory": classified["warmMemory"],
        "warmTiming": classified["warmTiming"],
        **_links(plan, precheck_digest),
    }


def _context_body(
    plan: dict[str, Any],
    *,
    phase: str,
    tokens: int | None,
    classified: dict[str, Any],
    executed: bool,
    run_invoked: bool,
    session_created: bool,
    precheck_digest: str,
) -> dict[str, Any]:
    success = classified["exitClassification"] == "success"
    observed = executed and phase != "not-executed"
    identity = None if tokens is None else sha256_text(f"574x{tokens}")
    return {
        "batchSize": 1,
        "calibrationStatus": "not-approved",
        "coldMemory": classified["coldMemory"],
        "coldTiming": classified["coldTiming"],
        "contextTokens": tokens if observed or phase != "not-executed" else None,
        "decoding": decoding(),
        "exitClassification": classified["exitClassification"],
        "inputDigest": identity if phase != "not-executed" else None,
        "installationAuthorized": False,
        "maxNewTokens": 1,
        "measurementCompleted": observed,
        "measurementPerformed": observed,
        "modelSessionCreated": observed and session_created,
        "networkResult": classified["networkResult"],
        "outputDigest": classified["outputDigest"] if success else None,
        "phase": phase,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": plan["priorPlanDigest"],
        "processCleanup": classified["cleanup"],
        "productionReady": False,
        "profileId": plan["profileId"],
        "promptConstruction": "not-executed" if phase == "not-executed" else "repeated-token-id",
        "realModelExecuted": observed and success and run_invoked,
        "repeatedTokenId": None if phase == "not-executed" else int(plan["repeatedTokenId"]),
        "repositoryCommit": "not-executed" if phase == "not-executed" else repository_commit(),
        "resultRootClass": plan["resultRootClass"],
        "runInvoked": observed and run_invoked,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "sessionId": plan["sessionId"],
        "stopCause": classified["stopCause"],
        "timestamp": "not-executed" if phase == "not-executed" else utc_timestamp(),
        "tokenizerSha256": TOKENIZER_SHA256,
        "warmMemory": classified["warmMemory"],
        "warmTiming": classified["warmTiming"],
        **_links(plan, precheck_digest),
    }


def _load(relative: Path, builder: Any) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded


def read_verified_header(runtime_root: Path) -> str:
    """Read the verified ONNX header through the existing helper."""
    from patchpilot_intelligence_evals.measurement_plan import read_verified_header as read_header

    return read_header(runtime_root)
