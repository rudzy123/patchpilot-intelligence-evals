"""Track 6D readiness. Selection stays closed unless every gate passes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import decide_artifact_budget
from patchpilot_intelligence_evals.candidate_eligibility import (
    MODEL_IDS,
    decide_candidate_eligibility,
)
from patchpilot_intelligence_evals.direct_onnx_evidence import decide_direct_onnx_evidence
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.subprocess_compatibility import decide_subprocess_compatibility
from patchpilot_intelligence_evals.tokenizer_eligibility import decide_tokenizer_eligibility

_RECORD = Path("candidates/authorization/track6d-acquisition-readiness.json")
_VERDICTS = {
    "ready": "TRACK 6D CONTROLLED ACQUISITION READY",
    "ready-with-residuals": "TRACK 6D CONTROLLED ACQUISITION READY WITH DOCUMENTED RESIDUALS",
    "not-ready": "TRACK 6D CONTROLLED ACQUISITION NOT READY",
    "blocked": "TRACK 6D CONTROLLED ACQUISITION BLOCKED BY UNRESOLVED AUTHORITY",
}


class Track6DError(ValueError):
    """A Track 6D record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class SelectionCandidate:
    """One comparable candidate. Disqualified scores stay unset."""

    model_id: str
    weighted_score: int | None
    mandatory_pass: bool
    tokenizer_pass: bool
    direct_onnx: bool
    budget_pass: bool
    subprocess_pass: bool
    fixed_revision: bool
    unresolved_conflict: bool
    conversion_authorized: bool
    quantization_approved: bool
    licensing_clarity: int
    custom_or_remote_code: bool
    peak_memory_bytes: int
    artifact_bytes: int
    immutable_identity: int
    model_card_disclosure: int
    runtime_maturity: int


def qualifies(candidate: SelectionCandidate) -> bool:
    """Every Track 4, tokenizer, ONNX, budget, and subprocess gate must pass."""
    return (
        candidate.weighted_score is not None
        and candidate.mandatory_pass
        and candidate.tokenizer_pass
        and candidate.direct_onnx
        and candidate.budget_pass
        and candidate.subprocess_pass
        and candidate.fixed_revision
        and not candidate.unresolved_conflict
        and not candidate.conversion_authorized
        and not candidate.quantization_approved
    )


def selection_key(candidate: SelectionCandidate) -> tuple[int, ...]:
    """Higher score first, then the seven Track 4 tie-break steps."""
    remote_penalty = 0 if candidate.custom_or_remote_code else 1
    return (
        candidate.weighted_score or 0,
        candidate.licensing_clarity,
        remote_penalty,
        -candidate.peak_memory_bytes,
        -candidate.artifact_bytes,
        candidate.immutable_identity,
        candidate.model_card_disclosure,
        candidate.runtime_maturity,
    )


def select_candidate(candidates: list[SelectionCandidate]) -> str | None:
    """Select one qualifying candidate. A remaining tie stays no-selection."""
    eligible = [item for item in candidates if qualifies(item)]
    if not eligible:
        return None
    best = max(eligible, key=selection_key)
    tied = [item for item in eligible if selection_key(item) == selection_key(best)]
    if len(tied) != 1:
        return None
    return best.model_id


def decide_track6d_readiness() -> dict[str, Any]:
    """Derive readiness from the other Track 6C decisions."""
    eligibility = decide_candidate_eligibility()
    tokenizer = decide_tokenizer_eligibility()
    onnx = decide_direct_onnx_evidence()
    budget = decide_artifact_budget()
    subprocess = decide_subprocess_compatibility()
    blockers = sorted(
        {name for item in eligibility["candidates"] for name in item["disqualifiers"]}
    )
    selected = _selected(eligibility, tokenizer, onnx, budget, subprocess)
    outcome = "not-ready" if selected is None else "ready"
    count = 0 if selected is None else 1
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "selectionOutcome": "no-selection" if selected is None else "selected",
        "selectedModelId": selected,
        "scoringApplied": selected is not None,
        "qualifyingCandidateCount": count,
        "readinessOutcome": outcome,
        "verdict": _VERDICTS[outcome],
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "installationAuthorized": False,
        "conversionAuthorized": False,
        "quantizationApproved": False,
        "blockers": blockers,
        "locallyObservedArtifactDigests": [],
    }
    return validate_track6d_readiness(document)


def validate_track6d_readiness(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one readiness record."""
    validate("track6d-acquisition-readiness", document)
    outcome = str(document["readinessOutcome"])
    if document["verdict"] != _VERDICTS[outcome]:
        raise Track6DError("verdict")
    selected = document["selectedModelId"]
    if document["selectionOutcome"] == "no-selection":
        inconsistent = (
            selected is not None
            or document["scoringApplied"]
            or document["qualifyingCandidateCount"]
        )
        if inconsistent:
            raise Track6DError("selection")
        if outcome not in {"not-ready", "blocked"}:
            raise Track6DError("readiness")
    elif selected not in MODEL_IDS or document["qualifyingCandidateCount"] != 1:
        raise Track6DError("selection")
    if document["installationAuthorized"] or document["conversionAuthorized"]:
        raise Track6DError("authorization")
    if document["locallyObservedArtifactDigests"] != []:
        raise Track6DError("local-digest")
    return document


def load_track6d_readiness(root: Path | None = None) -> dict[str, Any]:
    """Load the committed record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track6DError("record-type")
    document = validate_track6d_readiness(loaded)
    if document != decide_track6d_readiness():
        raise Track6DError("readiness-drift")
    return document


def _selected(
    eligibility: dict[str, Any],
    tokenizer: dict[str, Any],
    onnx: dict[str, Any],
    budget: dict[str, Any],
    subprocess: dict[str, Any],
) -> str | None:
    by_model = {item["modelId"]: item for item in eligibility["candidates"]}
    token_pass = {
        item["modelId"]: item["eligibilityOutcome"] == "pass" for item in tokenizer["families"]
    }
    onnx_pass = {item["modelId"]: item["directPathEligible"] for item in onnx["families"]}
    budget_pass = {item["modelId"]: item["hardwareFit"] == "pass" for item in budget["families"]}
    subprocess_pass = {
        item["modelId"]: item["compatibilityOutcome"] == "pass" for item in subprocess["families"]
    }
    candidates = []
    for model_id in MODEL_IDS:
        item = by_model[model_id]
        candidates.append(
            SelectionCandidate(
                model_id=model_id,
                weighted_score=item["weightedScore"],
                mandatory_pass=item["mandatoryStatus"] == "pass",
                tokenizer_pass=token_pass[model_id],
                direct_onnx=bool(onnx_pass[model_id]),
                budget_pass=budget_pass[model_id],
                subprocess_pass=subprocess_pass[model_id],
                fixed_revision=True,
                unresolved_conflict=False,
                conversion_authorized=False,
                quantization_approved=False,
                licensing_clarity=0,
                custom_or_remote_code=item["remoteCodeResult"] != "pass",
                peak_memory_bytes=0,
                artifact_bytes=0,
                immutable_identity=0,
                model_card_disclosure=0,
                runtime_maturity=0,
            )
        )
    return select_candidate(candidates)
