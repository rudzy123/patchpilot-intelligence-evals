"""Track 9 review validators. They read committed records and do not call Run."""

from __future__ import annotations

import argparse
from typing import Any

from patchpilot_intelligence_evals.behavioral_evidence_review import (
    load_behavioral_evidence_review,
)
from patchpilot_intelligence_evals.candidate_disposition import load_candidate_disposition
from patchpilot_intelligence_evals.corpus_continuation_authorization import (
    load_corpus_continuation_authorization,
)
from patchpilot_intelligence_evals.evaluation_evidence_review import (
    load_evaluation_evidence_inventory,
)
from patchpilot_intelligence_evals.memory_evidence_review import load_memory_evidence_review
from patchpilot_intelligence_evals.proportionality_decision import load_proportionality_decision
from patchpilot_intelligence_evals.track9_implementation_review import (
    load_track9_implementation_review,
)

VALIDATION = (
    "evaluation-evidence-inventory-validation",
    "memory-evidence-review-validation",
    "behavioral-evidence-review-validation",
    "proportionality-decision-validation",
    "corpus-continuation-authorization-validation",
    "candidate-disposition-validation",
    "track9-implementation-review-validation",
)


def register(commands: Any) -> None:
    """Add the Track 9 review validators. There is no execute command."""
    for name in VALIDATION:
        commands.add_parser(name)


def handle(command: str, _args: argparse.Namespace) -> dict[str, Any]:
    """Validate one committed Track 9 record and return a path-free summary."""
    if command == "evaluation-evidence-inventory-validation":
        document = load_evaluation_evidence_inventory()
        return _ok(
            itemCount=document["itemCount"],
            unresolved=document["evidenceClassCounts"]["unresolved"],
        )
    if command == "memory-evidence-review-validation":
        document = load_memory_evidence_review()
        return _ok(
            minimumHeadroomBytes=document["minimumHeadroomBytes"],
            reviewConclusion=document["reviewConclusion"],
        )
    if command == "behavioral-evidence-review-validation":
        document = load_behavioral_evidence_review()
        return _ok(
            behavioralConclusion=document["behavioralConclusion"],
            schemaFailureAuthority=document["schemaFailureAuthority"],
        )
    if command == "proportionality-decision-validation":
        document = load_proportionality_decision()
        return _ok(selectedAlternative=document["selectedAlternative"])
    if command == "corpus-continuation-authorization-validation":
        document = load_corpus_continuation_authorization()
        return _ok(
            authorizationStatus=document["authorizationStatus"],
            futurePlanDigest=document["futurePlanDigest"],
            plannedRuns=document["plannedRuns"],
        )
    if command == "candidate-disposition-validation":
        document = load_candidate_disposition()
        return _ok(
            candidateDisposition=document["candidateDisposition"],
            track9Disposition=document["track9Disposition"],
        )
    if command == "track9-implementation-review-validation":
        document = load_track9_implementation_review()
        return _ok(
            corpusOnlyContinuation=document["corpusOnlyContinuation"],
            reviewDigest=document["reviewDigest"],
            reviewStatus=document["reviewStatus"],
        )
    raise KeyError(command)


def _ok(**fields: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "comparisonWinner": None,
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": "ok",
    }
    payload.update(fields)
    return payload
