"""Advisory Track 11 readiness. This record does not reject or select a candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.schema_diagnostic_closeout import build_closeout_template
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    artifact_pins,
    identity_fields,
    load_schema_diagnostic_plan,
)
from patchpilot_intelligence_evals.schema_diagnostic_summary import AUTHORITY_BLOCKS
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/authorization/track11-readiness.json")


def build_track11_template() -> dict[str, Any]:
    """Committed readiness before the diagnostic runs."""
    plan = load_schema_diagnostic_plan()
    closeout = build_closeout_template()
    return digest_document(
        _body(
            plan,
            conclusion="not-executed",
            outcome="not-executed",
            verdict="TRACK 11 NOT EXECUTED",
            recommendation="not-executed",
            rejection=False,
            proportionality=False,
            stop=closeout["stopCause"],
        ),
        "track11-readiness",
        "identityDigest",
    )


def load_track11_template() -> dict[str, Any]:
    """Load the committed readiness record and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_track11_template():
        raise MeasurementError("record-drift")
    return loaded


def recommend(closeout: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    """Choose one advisory Track 11 verdict. It does not authorize another run."""
    plan = load_schema_diagnostic_plan()
    conclusion = str(summary["diagnosticConclusion"])
    stop = closeout.get("stopCause")
    stop_text = stop if isinstance(stop, str) else None
    if conclusion == "blocked-by-unresolved-authority" or stop_text in AUTHORITY_BLOCKS:
        outcome = "blocked"
        verdict = "BLOCKED BY UNRESOLVED AUTHORITY"
        recommendation = "principal-architect-review"
        rejection = False
        proportionality = False
    elif conclusion == "systematic-schema-failure-established":
        outcome = "ready-for-disposition-review"
        verdict = "TRACK 11 DISPOSITION REVIEW ADVISORY"
        recommendation = "disposition-review-eligible"
        rejection = True
        proportionality = False
    elif conclusion == "systematic-schema-failure-not-established":
        outcome = "advisory-not-established"
        verdict = "TRACK 11 PROPORTIONALITY ADVISORY"
        recommendation = "proportionality-review-eligible"
        rejection = False
        proportionality = True
    elif conclusion == "not-executed":
        outcome = "not-executed"
        verdict = "TRACK 11 NOT EXECUTED"
        recommendation = "not-executed"
        rejection = False
        proportionality = False
    else:
        outcome = "not-ready"
        verdict = "TRACK 11 NOT READY"
        recommendation = "principal-architect-review"
        rejection = False
        proportionality = False
    return digest_document(
        _body(
            plan,
            conclusion=conclusion,
            outcome=outcome,
            verdict=verdict,
            recommendation=recommendation,
            rejection=rejection,
            proportionality=proportionality,
            stop=stop_text,
        ),
        "track11-readiness",
        "identityDigest",
    )


def _body(
    plan: dict[str, Any],
    *,
    conclusion: str,
    outcome: str,
    verdict: str,
    recommendation: str,
    rejection: bool,
    proportionality: bool,
    stop: str | None,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "authorizesFullCorpus": False,
        "authorizesRejection": False,
        "authorizesSelection": False,
        "diagnosticConclusion": conclusion,
        "nextRecommendation": recommendation,
        "proportionalityReviewEligible": proportionality,
        "readinessOutcome": outcome,
        "rejectionEligibleForReview": rejection,
        "stopCause": stop,
        "verdict": verdict,
    }
