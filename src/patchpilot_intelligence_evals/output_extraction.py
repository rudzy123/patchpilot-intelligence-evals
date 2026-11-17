"""Separate candidate-envelope extraction from retained raw bytes."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.protocol import parse_candidate_stdout


def extract_envelope(stdout: bytes) -> dict[str, Any]:
    """Classify stdout without rewriting the retained bytes."""
    if stdout == b"":
        return _empty("empty")
    try:
        stdout.decode("utf-8")
    except UnicodeDecodeError:
        return _empty("encoding-failure")
    outcome, parsed = parse_candidate_stdout(stdout)
    if outcome != "parsed" or parsed is None:
        status = "multiple-outputs" if outcome == "multiple-outputs" else "malformed-output"
        return {
            "extractedBytes": 0,
            "extractedDigest": None,
            "extractionStatus": status,
            "parsed": None,
        }
    explanation = parsed.get("findingExplanationOutput")
    if not isinstance(explanation, dict):
        return {
            "extractedBytes": 0,
            "extractedDigest": None,
            "extractionStatus": "extracted",
            "parsed": parsed,
        }
    encoded = canonical_dumps(explanation).encode("utf-8")
    return {
        "extractedBytes": len(encoded),
        "extractedDigest": sha256_text(encoded.decode("utf-8")),
        "extractionStatus": "extracted",
        "parsed": parsed,
    }


def _empty(status: str) -> dict[str, Any]:
    return {
        "extractedBytes": 0,
        "extractedDigest": None,
        "extractionStatus": status,
        "parsed": None,
    }
