"""Track 5 evidence closure. This module does not edit the accepted shortlist."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.isolation_profile import has_acquisition_blocker
from patchpilot_intelligence_evals.schemas import repo_root, validate

MANDATORY_CRITERIA: tuple[str, ...] = (
    "explicit-weight-use-license",
    "clear-commercial-use-position",
    "clear-redistribution-position",
    "immutable-official-revision",
    "no-remote-code-requirement",
    "fully-offline-runtime-support",
    "tokenizer-provenance",
    "artifact-digest-capability",
    "local-resource-fit",
    "bounded-subprocess-compatibility",
    "no-mandatory-telemetry",
    "no-tenant-data-requirement",
    "official-model-card",
    "documented-limitations",
    "no-production-dependency",
)
PINNED_REVISIONS: dict[str, str] = {
    "Qwen/Qwen2.5-1.5B-Instruct": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    "Qwen/Qwen2.5-3B-Instruct": "aa8e72537993ba99e69dfaafa59ed015b17504d1",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct": "31b70e2e869a7173562077fd711b654946d38674",
    "allenai/OLMo-2-0425-1B-Instruct": "48d788eca847d4d7548f375ad03d3c9312f6139e",
    "google/gemma-3-1b-it": "dcc83ea841ab6100d6b47a070329e1ba4cf78752",
}
REQUIRED_GAPS: dict[str, tuple[str, ...]] = {
    "Qwen/Qwen2.5-1.5B-Instruct": ("documented-limitations",),
    "Qwen/Qwen2.5-3B-Instruct": ("artifact-digest-capability", "documented-limitations"),
    "HuggingFaceTB/SmolLM2-1.7B-Instruct": (
        "explicit-weight-use-license",
        "tokenizer-provenance",
    ),
    "allenai/OLMo-2-0425-1B-Instruct": (
        "explicit-weight-use-license",
        "tokenizer-provenance",
    ),
    "google/gemma-3-1b-it": (
        "tokenizer-provenance",
        "artifact-digest-capability",
        "fully-offline-runtime-support",
    ),
}
ALLOWED_RESOLUTIONS: dict[tuple[str, str], tuple[str, str]] = {
    ("Qwen/Qwen2.5-3B-Instruct", "artifact-digest-capability"): ("fail", "pass"),
}
QWEN3_SHARDS: tuple[tuple[str, int, str], ...] = (
    (
        "model-00001-of-00002.safetensors",
        3968658944,
        "67347b23fb4165b652eb6611f5e1f2a06dfcddba8e909df1b2b0b1857bee06c2",
    ),
    (
        "model-00002-of-00002.safetensors",
        2203268048,
        "a40d941d0e7e0b966ad8b62bb6d6b7c88cce1299197b599d9d0a4ce59aabfc1d",
    ),
)
_CLOSURE = Path("candidates/authorization/candidate-evidence-closure.json")
_SHORTLIST = Path("candidates/authorization/candidate-shortlist.json")


class EvidenceError(ValueError):
    """An evidence-closure check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def failing_criteria(criteria: dict[str, Any]) -> list[str]:
    """Return failed criterion names in shortlist order."""
    return [name for name in MANDATORY_CRITERIA if criteria[name] == "fail"]


def assert_score_closed(criteria: dict[str, Any], weighted_score: object) -> None:
    """Keep a weighted score null until every mandatory criterion passes."""
    if failing_criteria(criteria):
        if weighted_score is not None:
            raise EvidenceError("score-forbidden")
        return
    if not isinstance(weighted_score, int):
        raise EvidenceError("score-required")


def validate_closure(
    document: dict[str, Any],
    shortlist: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a closure against the accepted shortlist without modifying it."""
    validate("candidate-evidence-closure", document)
    if not has_acquisition_blocker():
        raise EvidenceError("isolation-blocker")
    if document["locallyObservedArtifactDigests"]:
        raise EvidenceError("local-digest")
    accepted = shortlist if shortlist is not None else _load_json(_SHORTLIST)
    by_shortlist = {str(item["modelId"]): item for item in accepted["candidates"]}
    by_closure = {str(item["modelId"]): item for item in document["candidates"]}
    if list(by_closure) != list(PINNED_REVISIONS):
        raise EvidenceError("candidate-set")
    if set(by_closure) != set(by_shortlist):
        raise EvidenceError("candidate-set")
    qualifying = 0
    for model_id, revision in PINNED_REVISIONS.items():
        candidate = by_closure[model_id]
        prior = by_shortlist[model_id]
        if candidate["revision"] != revision or prior["revision"] != revision:
            raise EvidenceError("revision")
        if candidate["locallyObservedArtifactDigests"]:
            raise EvidenceError("local-digest")
        criteria = candidate["mandatoryCriteria"]
        _require_resolution(model_id, prior["mandatoryCriteria"], criteria)
        failed = failing_criteria(criteria)
        if "bounded-subprocess-compatibility" not in failed:
            raise EvidenceError("bounded-subprocess")
        if list(candidate["previousDisqualifiers"]) != _ordered(prior["disqualifiers"]):
            raise EvidenceError("previous-disqualifiers")
        if list(candidate["disqualifiers"]) != failed:
            raise EvidenceError("disqualifier-mismatch")
        if candidate["mandatoryStatus"] != "fail":
            raise EvidenceError("mandatory-status")
        assert_score_closed(criteria, candidate["weightedScore"])
        _require_gaps(model_id, candidate)
        _require_artifact(model_id, candidate["publisherArtifact"])
        _require_residuals(model_id, candidate["conflicts"])
        qualifying += int(not failed)
    if qualifying != 0 or document["qualifyingCandidateCount"] != 0:
        raise EvidenceError("qualifying-count")
    if document["selectionOutcome"] != "no-selection" or document["selectedModelId"] is not None:
        raise EvidenceError("selection")
    if document["scoringApplied"] is not False:
        raise EvidenceError("scoring")
    return document


def load_closure(root: Path | None = None) -> dict[str, Any]:
    """Load the committed closure and the accepted shortlist."""
    base = root if root is not None else repo_root()
    return validate_closure(_load_json(_CLOSURE, base), _load_json(_SHORTLIST, base))


def _require_resolution(
    model_id: str,
    previous: dict[str, Any],
    current: dict[str, Any],
) -> None:
    for name in MANDATORY_CRITERIA:
        before = str(previous[name])
        after = str(current[name])
        if before == after:
            continue
        allowed = ALLOWED_RESOLUTIONS.get((model_id, name))
        if allowed != (before, after):
            raise EvidenceError("unauthorized-change")
    for (owner, name), (before, after) in ALLOWED_RESOLUTIONS.items():
        if owner != model_id:
            continue
        if str(previous[name]) != before or str(current[name]) != after:
            raise EvidenceError("required-resolution")


def _require_gaps(model_id: str, candidate: dict[str, Any]) -> None:
    expected = REQUIRED_GAPS[model_id]
    gaps = candidate["gaps"]
    if [str(item["gapId"]) for item in gaps] != list(expected):
        raise EvidenceError("gap-set")
    criteria = candidate["mandatoryCriteria"]
    for gap in gaps:
        resolved = gap["status"] == "resolved"
        if resolved is not (criteria[str(gap["gapId"])] == "pass"):
            raise EvidenceError("gap-status")


def _require_artifact(model_id: str, artifact: dict[str, Any]) -> None:
    shards = artifact["shards"]
    total = sum(int(item["byteCount"]) for item in shards)
    if total != int(artifact["byteCount"]):
        raise EvidenceError("artifact-bytes")
    names = [str(item["fileName"]) for item in shards]
    if len(names) != len(set(names)):
        raise EvidenceError("artifact-names")
    agreed = artifact["digestDisposition"] == "agreed"
    hashes = [item["sha256"] for item in shards]
    if agreed and any(item is None for item in hashes):
        raise EvidenceError("artifact-digest")
    if not agreed and artifact["upstreamSha256"] is not None:
        raise EvidenceError("artifact-digest")
    if agreed and len(shards) == 1 and artifact["upstreamSha256"] != hashes[0]:
        raise EvidenceError("artifact-digest")
    if agreed and len(shards) != 1 and artifact["upstreamSha256"] is not None:
        raise EvidenceError("artifact-digest")
    if model_id != "Qwen/Qwen2.5-3B-Instruct":
        return
    observed = [
        (str(item["fileName"]), int(item["byteCount"]), str(item["sha256"])) for item in shards
    ]
    if tuple(observed) != QWEN3_SHARDS or artifact["digestDisposition"] != "agreed":
        raise EvidenceError("qwen3-digest")


def _require_residuals(model_id: str, conflicts: list[dict[str, Any]]) -> None:
    topics = {str(item["topic"]) for item in conflicts}
    if model_id in {"Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-3B-Instruct"}:
        if "tokenizer filenames" not in topics:
            raise EvidenceError("tokenizer-residual")
    if model_id == "Qwen/Qwen2.5-3B-Instruct" and "shard digest" not in topics:
        raise EvidenceError("digest-conflict")


def _ordered(names: list[str]) -> list[str]:
    return [name for name in MANDATORY_CRITERIA if name in names]


def _load_json(relative: Path, root: Path | None = None) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise EvidenceError("record-type")
    return loaded
