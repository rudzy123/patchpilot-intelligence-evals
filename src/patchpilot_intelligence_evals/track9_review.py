"""Shared Track 9 review identity. Building these records does not call Run."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import LFM_MODEL_ID
from patchpilot_intelligence_evals.finalist_budget import RUNTIME_TAG
from patchpilot_intelligence_evals.inference_retry_plan import CONSUMED_RETRY_PLAN_DIGEST
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    CHAT_TEMPLATE_SHA256,
    CORPUS_DIGEST,
    PROMPT_TEMPLATE_DIGEST,
    RUNTIME_ATTEMPT,
    TOKENIZER_SHA256,
    MeasurementError,
    authority,
    digest_document,
)
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track8b_r2_records import (
    CEILING_BYTES,
    HEADROOM_BYTES,
    PLAN_DIGEST,
    PRIOR_PLAN_DIGEST,
    WARM_8192_PEAK_BYTES,
)

SESSION_ID = "intelligence-track-9"
FUTURE_PLAN = "not-issued"
R3_PLAN = "not-issued"
PRECISION = "FP32"
COLD_4096_PEAK_BYTES = 7_284_371_456
WARM_4096_PEAK_BYTES = 8_511_131_648
COLD_8192_PEAK_BYTES = 9_816_231_936
R1_SMOKE_PEAK_BYTES = 46_288_896
DEPENDENCY_CLOSURE_DIGEST = "7e86fd24935ac651811ab4ae7d00e471369109843fb947a2dfa9f5a5905b82dd"
DYNAMIC_LINK_PRECHECK_DIGEST = "ecb67d19b6ad0bfcdf5cd42724ebd8e0652790d79f00c6a149c4d8a49c772748"
MEMORY_SOURCE_DIGEST = "400b520b6d6c404415143ba8f9dbac31a2788f5d2864622281d213d7b24f328b"
BEHAVIOR_SOURCE_DIGEST = "74a5b0cd54889851d2326553ab7e7cfce1c73149f7f9abebe1041507346e2460"
FORENSICS_SOURCE_DIGEST = "78a45f40b45c5721aed52411214ec28866587a7d9de0c8cc6b670e72e8d81924"
PROPORTIONALITY_SOURCE_DIGEST = "d60aedf08c86ca6f67d548c772cc624cc23a3f51cbb8a93fd9d135ced50e5c8a"
R2_DISPOSITION_DIGEST = "2b8d1cf3f90df48d220ba98de0f1dd5104c4096ba83196c370b9770c45e83ea0"
R2_ATTEMPT_DIGEST = "d9be9bb55fe2f97fdc2bca2169c915b24e9fc156926b4e71325422c16f2aeb0a"
R2_CGROUP_DIGEST = "6d8a4845819d7886401f808aff2160f728e5b80edf753001af3de70067872d1e"
R2_TRACK9_DIGEST = "f98ed1dae406d67f5574db076b0c4eb83f8c89c113fead3b0d5a170b40ced435"
R2_REVIEW_DIGEST = "5f65d94434fb77741479a783be6d757055a673c7843429af6ed55b8e6aa13747"
_FORBIDDEN = ("/home/", "/var/", "http://", "https://", "InferenceSession", "onnxruntime")


def common() -> dict[str, Any]:
    """Identity and authority fields locked on every Track 9 record."""
    return {
        **authority(),
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateModelId": LFM_MODEL_ID,
        "candidatePrecision": PRECISION,
        "comparisonWinner": None,
        "consumedRetryPlanDigest": CONSUMED_RETRY_PLAN_DIGEST,
        "containsExecutionInstructions": False,
        "currentExecutionAuthority": False,
        "futurePlanDigest": FUTURE_PLAN,
        "planDigest": PLAN_DIGEST,
        "priorPlanDigest": PRIOR_PLAN_DIGEST,
        "r3Plan": R3_PLAN,
        "replacementPlanDigest": FUTURE_PLAN,
        "runtimeAttemptId": RUNTIME_ATTEMPT,
        "runtimeVersionTag": RUNTIME_TAG,
        "sessionId": SESSION_ID,
    }


def reject_track9_text(document: Mapping[str, Any]) -> None:
    """Reject host paths, transfer URLs, and execution instructions."""
    text = json.dumps(document)
    if any(marker in text for marker in _FORBIDDEN):
        raise MeasurementError("identity")
    if ".." in text:
        raise MeasurementError("identity")


def seal(document: dict[str, Any], schema_name: str) -> dict[str, Any]:
    """Digest one closed record. This does not create a plan or a result root."""
    reject_track9_text(document)
    return digest_document(document, schema_name, "identityDigest")


def load_record(relative: str, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    """Load one committed record and refuse drift from its builder."""
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded


__all__ = [
    "BEHAVIOR_SOURCE_DIGEST",
    "CEILING_BYTES",
    "CHAT_TEMPLATE_SHA256",
    "COLD_4096_PEAK_BYTES",
    "COLD_8192_PEAK_BYTES",
    "CORPUS_DIGEST",
    "DEPENDENCY_CLOSURE_DIGEST",
    "DYNAMIC_LINK_PRECHECK_DIGEST",
    "FORENSICS_SOURCE_DIGEST",
    "HEADROOM_BYTES",
    "MEMORY_SOURCE_DIGEST",
    "PLAN_DIGEST",
    "PRIOR_PLAN_DIGEST",
    "PROMPT_TEMPLATE_DIGEST",
    "PROPORTIONALITY_SOURCE_DIGEST",
    "R1_SMOKE_PEAK_BYTES",
    "R2_ATTEMPT_DIGEST",
    "R2_CGROUP_DIGEST",
    "R2_DISPOSITION_DIGEST",
    "R2_REVIEW_DIGEST",
    "R2_TRACK9_DIGEST",
    "TOKENIZER_SHA256",
    "WARM_4096_PEAK_BYTES",
    "WARM_8192_PEAK_BYTES",
    "common",
    "load_record",
    "seal",
]
