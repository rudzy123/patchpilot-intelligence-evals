"""Smoke, short generation, and context phases. Later phases wait on earlier records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.candidate_inference import (
    Launcher,
    child_indexes,
    classify_execution,
    launch_child,
    measurement_limits,
)
from patchpilot_intelligence_evals.corpus import canonical_dumps
from patchpilot_intelligence_evals.evaluator import repository_commit
from patchpilot_intelligence_evals.hardened_execution import execute_hardened
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    RUNTIME_ATTEMPT,
    TOKENIZER_SHA256,
    MeasurementError,
    authority,
    bind_verified_roots,
    digest_document,
    empty_memory,
    empty_timing,
    load_measurement_plan,
    phase_by_name,
    prerequisite_name,
    read_verified_header,
    require_operator_approval,
    validate_result_root,
)
from patchpilot_intelligence_evals.schemas import validate
from patchpilot_intelligence_evals.track8b_records import build_preflight_record

PHASE_FILES = {
    "preflight": "preflight.json",
    "one-token-smoke": "one-token-smoke.json",
    "short-generation": "short-generation.json",
    "context-4096": "context-4096.json",
    "context-8192": "context-8192.json",
    "corpus-evaluation": "corpus-summary.json",
}


def build_smoke_template() -> dict[str, Any]:
    """Committed smoke record. It has not been executed."""
    plan = load_measurement_plan()
    return digest_document(
        {
            **authority(),
            "exitClassification": "not-executed",
            "generationTokens": None,
            "inputTokens": None,
            "maxNewTokens": 1,
            "memory": empty_memory(),
            "networkResult": "not-performed",
            "outputDigest": None,
            "phase": "not-executed",
            "planDigest": plan["planDigest"],
            "processCleanup": "not-performed",
            "realModelExecuted": False,
            "repositoryCommit": "not-executed",
            "stopCause": None,
            "timing": empty_timing(),
        },
        "smoke-execution",
        "identityDigest",
    )


def build_context_template() -> dict[str, Any]:
    """Committed context record. It has not been executed."""
    plan = load_measurement_plan()
    return digest_document(
        {
            **authority(),
            "batchSize": 1,
            "coldMemory": empty_memory(),
            "coldTiming": empty_timing(),
            "contextTokens": None,
            "exitClassification": "not-executed",
            "maxNewTokens": 1,
            "networkResult": "not-performed",
            "outputDigest": None,
            "phase": "not-executed",
            "planDigest": plan["planDigest"],
            "processCleanup": "not-performed",
            "promptConstruction": "not-executed",
            "realModelExecuted": False,
            "repeatedTokenId": None,
            "repositoryCommit": "not-executed",
            "stopCause": None,
            "tokenizerSha256": TOKENIZER_SHA256,
            "warmMemory": empty_memory(),
            "warmTiming": empty_timing(),
        },
        "context-memory-measurement",
        "identityDigest",
    )


def run_preflight(runtime_root: Path, model_root: Path, result_root: Path) -> dict[str, Any]:
    """Recompute promoted digests. This does not create a session."""
    binding = bind_verified_roots(runtime_root, model_root)
    validate_result_root(result_root)
    document = build_preflight_record(status="ok")
    if document["archiveAttemptId"] != binding["archiveAttemptId"]:
        raise MeasurementError("digest-mismatch")
    if document["candidateAttemptId"] != binding["candidateAttemptId"]:
        raise MeasurementError("digest-mismatch")
    if document["runtimeAttemptId"] != binding["runtimeAttemptId"]:
        raise MeasurementError("digest-mismatch")
    reject_sensitive(document)
    _write_new(result_root, PHASE_FILES["preflight"], document)
    return document


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
    """Run one smoke, short, or context phase after its prerequisite passed."""
    plan = require_operator_approval(approval)
    phase = phase_by_name(plan, phase_name)
    if phase_name not in {"one-token-smoke", "short-generation", "context-4096", "context-8192"}:
        raise MeasurementError("phase")
    _require_prior(result_root, phase_name)
    if bind:
        bind_verified_roots(runtime_root, model_root)
    if indexes is not None:
        header_indexes = indexes
    elif bind:
        header_indexes = child_indexes(read_verified_header(runtime_root))
    else:
        raise MeasurementError("unverified-dependency")
    config = _config(plan, phase, header_indexes)
    runtime_dir = runtime_root / "verified" / RUNTIME_ATTEMPT
    model_dir = model_root / "verified" / CANDIDATE_ATTEMPT
    result, sampler = launch_child(
        config,
        runtime_dir=runtime_dir,
        model_dir=model_dir,
        limits=measurement_limits(phase),
        launcher=launcher,
        sampler=None,
    )
    classified = classify_execution(result, sampler, cold_warm=bool(phase["coldWarm"]))
    if phase_name in {"one-token-smoke", "short-generation"}:
        document = _smoke_document(plan, phase, classified, executed)
        schema = "smoke-execution"
    else:
        counted = classified["inputTokens"]
        if counted != phase["inputTokens"]:
            classified["exitClassification"] = "inference-failure"
            classified["stopCause"] = "inference-failure"
        document = _context_document(plan, phase, classified, executed)
        schema = "context-memory-measurement"
    sealed = digest_document(document, schema, "identityDigest")
    _write_new(result_root, PHASE_FILES[phase_name], sealed)
    return sealed


def _config(plan: dict[str, Any], phase: dict[str, Any], indexes: dict[str, int]) -> dict[str, Any]:
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
        "repeatedTokenId": int(plan["repeatedTokenId"]),
    }


def _smoke_document(
    plan: dict[str, Any],
    phase: dict[str, Any],
    classified: dict[str, Any],
    executed: bool,
) -> dict[str, Any]:
    memory = classified["coldMemory"]
    timing = dict(classified["coldTiming"])
    if phase["coldWarm"]:
        if classified["warmMemory"]["telemetry"] == "complete":
            memory = classified["warmMemory"]
        timing["generationSeconds"] = classified["warmTiming"]["generationSeconds"]
    return {
        **authority(),
        "exitClassification": classified["exitClassification"],
        "generationTokens": classified["newTokens"]
        if classified["exitClassification"] == "success"
        else None,
        "inputTokens": classified["inputTokens"]
        if isinstance(classified["inputTokens"], int)
        else None,
        "maxNewTokens": int(phase["maxNewTokens"]),
        "memory": memory,
        "networkResult": classified["networkResult"],
        "outputDigest": classified["outputDigest"],
        "phase": phase["phase"],
        "planDigest": plan["planDigest"],
        "processCleanup": classified["cleanup"],
        "realModelExecuted": executed and classified["exitClassification"] == "success",
        "repositoryCommit": repository_commit(),
        "stopCause": classified["stopCause"],
        "timing": timing,
    }


def _context_document(
    plan: dict[str, Any],
    phase: dict[str, Any],
    classified: dict[str, Any],
    executed: bool,
) -> dict[str, Any]:
    return {
        **authority(),
        "batchSize": 1,
        "coldMemory": classified["coldMemory"],
        "coldTiming": classified["coldTiming"],
        "contextTokens": phase["inputTokens"],
        "exitClassification": classified["exitClassification"],
        "maxNewTokens": 1,
        "networkResult": classified["networkResult"],
        "outputDigest": classified["outputDigest"],
        "phase": phase["phase"],
        "planDigest": plan["planDigest"],
        "processCleanup": classified["cleanup"],
        "promptConstruction": "repeated-token-id",
        "realModelExecuted": executed and classified["exitClassification"] == "success",
        "repeatedTokenId": int(plan["repeatedTokenId"]),
        "repositoryCommit": repository_commit(),
        "stopCause": classified["stopCause"],
        "tokenizerSha256": TOKENIZER_SHA256,
        "warmMemory": classified["warmMemory"],
        "warmTiming": classified["warmTiming"],
    }


def _require_prior(result_root: Path, phase_name: str) -> None:
    previous = prerequisite_name(phase_name)
    if previous is None:
        return
    path = result_root / PHASE_FILES[previous]
    if path.is_symlink() or not path.is_file():
        raise MeasurementError("prior-phase-failed")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not _passed(previous, document):
        raise MeasurementError("prior-phase-failed")


def _passed(phase_name: str, document: dict[str, Any]) -> bool:
    if phase_name == "preflight":
        return document.get("status") == "ok" and document.get("realModelExecuted") is False
    return document.get("exitClassification") == "success" and document.get("stopCause") is None


def _write_new(root: Path, name: str, document: dict[str, Any]) -> None:
    destination = root / name
    if destination.exists() or destination.is_symlink():
        raise MeasurementError("overwrite")
    destination.write_text(canonical_dumps(document) + "\n", encoding="utf-8")


def load_phase(result_root: Path, phase_name: str) -> dict[str, Any]:
    """Load one external phase record."""
    path = result_root / PHASE_FILES[phase_name]
    if path.is_symlink() or not path.is_file():
        raise MeasurementError("missing-root")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise MeasurementError("record-type")
    return document


def withheld(phase_name: str, result_root: Path) -> bool:
    """Return whether a phase must stay unstarted."""
    try:
        _require_prior(result_root, phase_name)
    except MeasurementError:
        return True
    return False


def validate_templates() -> None:
    """Validate the committed not-executed templates."""
    validate("smoke-execution", build_smoke_template())
    validate("context-memory-measurement", build_context_template())
