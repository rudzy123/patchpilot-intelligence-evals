"""Compare two candidate execution results without choosing a production winner.

Track 2 gate definitions stay unchanged. Incompatible corpus, protocol, or
completeness is reported as incomparable. A missing artifact is not ranked.
"""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.evaluator import GATE_NAMES
from patchpilot_intelligence_evals.protocol import PROTOCOL_VERSION
from patchpilot_intelligence_evals.schemas import validate

_EMPTY_SIDE: dict[str, Any] = {
    "present": False,
    "candidateId": "",
    "candidateVersion": "",
    "candidateManifestDigest": "",
    "corpusDigest": "",
    "corpusVersion": "",
    "protocolVersion": "",
    "experimentId": "",
}


def _side(result: dict[str, Any] | None) -> dict[str, Any]:
    if result is None:
        return dict(_EMPTY_SIDE)
    return {
        "present": True,
        "candidateId": str(result["candidateId"]),
        "candidateVersion": str(result["candidateVersion"]),
        "candidateManifestDigest": str(result["candidateManifestDigest"]),
        "corpusDigest": str(result["corpusDigest"]),
        "corpusVersion": str(result["corpusVersion"]),
        "protocolVersion": str(result["protocolVersion"]),
        "experimentId": str(result["experimentId"]),
    }


def _reason(left: dict[str, Any] | None, right: dict[str, Any] | None) -> str | None:
    if left is None and right is None:
        return "missing-both"
    if left is None:
        return "missing-left"
    if right is None:
        return "missing-right"
    if not left["complete"] or not right["complete"]:
        return "incomplete-result"
    if left["corpusDigest"] != right["corpusDigest"]:
        return "corpus-digest"
    if left["corpusVersion"] != right["corpusVersion"]:
        return "corpus-version"
    if left["protocolVersion"] != right["protocolVersion"]:
        return "protocol-version"
    if left["protocolVersion"] != PROTOCOL_VERSION:
        return "protocol-version"
    return None


def compare_results(
    left: dict[str, Any] | None,
    right: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return a closed comparison. ``winner`` is always null."""
    reason = _reason(left, right)
    if reason is None and left is not None and right is not None:
        comparison: dict[str, Any] = {
            "schemaVersion": "1.0.0",
            "protocolVersion": PROTOCOL_VERSION,
            "productionReady": False,
            "status": "comparable",
            "reason": "",
            "winner": None,
            "left": _side(left),
            "right": _side(right),
            "gateComparison": [
                {
                    "gate": name,
                    "leftStatus": str(left["gates"][name]["status"]),
                    "rightStatus": str(right["gates"][name]["status"]),
                }
                for name in GATE_NAMES
            ],
        }
    else:
        status = (
            "missing-result"
            if reason is not None and reason.startswith("missing")
            else "incomparable"
        )
        comparison = {
            "schemaVersion": "1.0.0",
            "protocolVersion": PROTOCOL_VERSION,
            "productionReady": False,
            "status": status,
            "reason": reason or "incomparable",
            "winner": None,
            "left": _side(left),
            "right": _side(right),
            "gateComparison": [],
        }
    validate("comparison-result", comparison)
    return comparison
