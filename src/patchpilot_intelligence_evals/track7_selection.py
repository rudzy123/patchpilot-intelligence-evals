"""Track 7 selection. A failed gate keeps the weighted score null.

Tie-breaking reuses the Track 6D key. Popularity and benchmark rank are not inputs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    contains_private_marker,
    decide_candidate_discovery,
)
from patchpilot_intelligence_evals.candidate_eligibility import RETRIEVED_ON
from patchpilot_intelligence_evals.explanation_suitability import decide_explanation_suitability
from patchpilot_intelligence_evals.finalist_budget import decide_finalist_budget
from patchpilot_intelligence_evals.finalist_eligibility import decide_finalist_eligibility
from patchpilot_intelligence_evals.finalist_onnx import decide_finalist_onnx
from patchpilot_intelligence_evals.finalist_tokenizer import decide_finalist_tokenizer
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.track6d_readiness import (
    SelectionCandidate,
    qualifies,
    select_candidate,
)

_RECORD = Path("candidates/authorization/track7-selection.json")


class Track7SelectionError(ValueError):
    """A selection record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def blocker_codes(row: dict[str, Any], budget: dict[str, Any]) -> list[str]:
    """Exact reasons a finalist is not selectable. The list is sorted."""
    blockers = set(row["disqualifiers"])
    footprint = budget["footprintBytes"]
    if footprint is None or footprint > ARTIFACT_CAP:
        blockers.add("artifact-footprint-exceeds-8gib")
    if budget["peakMemoryBytes"] is None:
        blockers.add("peak-memory-unknown")
    if row["suitabilityOutcome"] != "suitable-for-offline-evaluation":
        blockers.add(f"explanation-suitability-{row['suitabilityOutcome']}")
    if row["unresolvedConflict"]:
        blockers.add("unresolved-conflict")
    if row["tokenizerOutcome"] != "pass":
        blockers.add("tokenizer-eligibility")
    if row["directOnnxOutcome"] != "pass":
        blockers.add("direct-onnx")
    if row["executionOutcome"] != "pass":
        blockers.add("bounded-execution")
    if not row["fixedRevision"]:
        blockers.add("revision")
    if budget["cpuOnlyViability"] != "pass":
        blockers.add("cpu-only")
    return sorted(blockers)


def choose_candidate(rows: list[dict[str, Any]]) -> str | None:
    """Select only a finalist whose explanation suitability also passes."""
    selectable = [
        item for item in rows if item["suitabilityOutcome"] == "suitable-for-offline-evaluation"
    ]
    return select_candidate([_selection_candidate(item) for item in selectable])


def decide_track7_selection() -> dict[str, Any]:
    """Select at most one finalist. The committed result is no-selection."""
    rows = [_row()]
    chosen = choose_candidate(rows)
    scored = [item for item in rows if item["weightedScore"] is not None]
    qualified = [item for item in rows if item["qualifies"]]
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "selectionOutcome": "selected" if chosen is not None else "no-selection",
        "selectedModelId": chosen,
        "scoringApplied": bool(scored),
        "qualifyingCandidateCount": len(qualified),
        "finalistCount": len(rows),
        "finalistModelIds": [item["modelId"] for item in rows],
        "locallyObservedArtifactDigests": [],
        "candidates": rows,
    }
    return validate_track7_selection(document)


def validate_track7_selection(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one selection record."""
    validate("track7-selection", document)
    if contains_private_marker(document):
        raise Track7SelectionError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise Track7SelectionError("local-digest")
    expected_ids = decide_candidate_discovery()["finalistModelIds"]
    if document["finalistModelIds"] != expected_ids:
        raise Track7SelectionError("finalist-boundary")
    candidates = document["candidates"]
    if [item["modelId"] for item in candidates] != expected_ids:
        raise Track7SelectionError("finalist-boundary")
    if document["finalistCount"] != len(candidates) or len(candidates) > 4:
        raise Track7SelectionError("finalist-count")
    rebuilt = [_row()]
    if candidates != rebuilt:
        raise Track7SelectionError("selection-drift")
    chosen = choose_candidate(candidates)
    if chosen is None:
        if (
            document["selectionOutcome"] != "no-selection"
            or document["selectedModelId"] is not None
        ):
            raise Track7SelectionError("selection")
    elif document["selectionOutcome"] != "selected" or document["selectedModelId"] != chosen:
        raise Track7SelectionError("selection")
    qualified = [item for item in candidates if item["qualifies"]]
    if document["qualifyingCandidateCount"] != len(qualified):
        raise Track7SelectionError("qualifying-count")
    scored = [item for item in candidates if item["weightedScore"] is not None]
    if document["scoringApplied"] is not bool(scored):
        raise Track7SelectionError("scoring-applied")
    if len(qualified) > 1 and chosen is None and document["selectionOutcome"] != "no-selection":
        raise Track7SelectionError("tie")
    return document


def load_track7_selection(root: Path | None = None) -> dict[str, Any]:
    """Load the committed selection and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track7SelectionError("record-type")
    document = validate_track7_selection(loaded)
    if document != decide_track7_selection():
        raise Track7SelectionError("selection-drift")
    return document


def _row() -> dict[str, Any]:
    eligibility = decide_finalist_eligibility()["finalists"][0]
    tokenizer = decide_finalist_tokenizer()["finalists"][0]
    onnx = decide_finalist_onnx()["finalists"][0]
    budget = decide_finalist_budget()["finalists"][0]
    suitability = decide_explanation_suitability()["finalists"][0]
    if eligibility["modelId"] != LFM_MODEL_ID:
        raise Track7SelectionError("finalist-boundary")
    row = {
        "modelId": eligibility["modelId"],
        "weightedScore": eligibility["weightedScore"],
        "categoryScores": eligibility["categoryScores"],
        "mandatoryStatus": eligibility["mandatoryStatus"],
        "disqualifiers": eligibility["disqualifiers"],
        "tokenizerOutcome": tokenizer["eligibilityOutcome"],
        "directOnnxOutcome": "pass" if onnx["directPathEligible"] else "fail",
        "hardwareFit": budget["hardwareFit"],
        "executionOutcome": budget["executionOutcome"],
        "suitabilityOutcome": suitability["suitabilityOutcome"],
        "fixedRevision": True,
        "unresolvedConflict": eligibility["unresolvedConflict"],
        "qualifies": False,
    }
    suitable = row["suitabilityOutcome"] == "suitable-for-offline-evaluation"
    row["qualifies"] = qualifies(_selection_candidate(row, budget)) and suitable
    return row


def _selection_candidate(
    row: dict[str, Any], budget: dict[str, Any] | None = None
) -> SelectionCandidate:
    if budget is None:
        budget = decide_finalist_budget()["finalists"][0]
    footprint = budget["footprintBytes"]
    peak = budget["peakMemoryBytes"]
    mandatory_pass = row["mandatoryStatus"] == "pass" and row["weightedScore"] is not None
    budget_pass = row["hardwareFit"] == "pass" and budget["contextFit"] == "pass"
    return SelectionCandidate(
        model_id=row["modelId"],
        weighted_score=row["weightedScore"],
        mandatory_pass=mandatory_pass,
        tokenizer_pass=row["tokenizerOutcome"] == "pass",
        direct_onnx=row["directOnnxOutcome"] == "pass",
        budget_pass=budget_pass,
        subprocess_pass=row["executionOutcome"] == "pass",
        fixed_revision=row["fixedRevision"],
        unresolved_conflict=row["unresolvedConflict"],
        conversion_authorized=False,
        quantization_approved=False,
        licensing_clarity=2,
        custom_or_remote_code=False,
        peak_memory_bytes=0 if peak is None else int(peak),
        artifact_bytes=0 if footprint is None else int(footprint),
        immutable_identity=2,
        model_card_disclosure=1,
        runtime_maturity=1,
    )
