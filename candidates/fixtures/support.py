"""Stdin-only helper for deterministic test doubles.

The helper reads the canonical candidate request and builds an explanation
from the finding-explanation input. It does not open corpus cases, gold
labels, prior results, or sibling repositories. These fixtures are not models.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from patchpilot_intelligence_evals.candidate_output import (
    EXPLANATION,
    FORBIDDEN_ORGANIZATION_ID,
    UNSUPPORTED_CLAIM,
    authorized_output,
    instruction_markers,
)
from patchpilot_intelligence_evals.corpus import canonical_dumps

CANDIDATE_VERSION = "1"

__all__ = [
    "EXPLANATION",
    "FORBIDDEN_ORGANIZATION_ID",
    "UNSUPPORTED_CLAIM",
    "authorized_output",
    "emit",
    "finding_input",
    "instruction_markers",
    "read_request",
    "success_response",
]


def read_request() -> dict[str, Any]:
    loaded = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    if not isinstance(loaded, dict):
        raise SystemExit(2)
    return loaded


def finding_input(request: dict[str, Any]) -> dict[str, Any]:
    payload = request.get("findingExplanationInput")
    if not isinstance(payload, dict):
        raise SystemExit(2)
    return payload


def success_response(
    request: dict[str, Any],
    output: dict[str, Any],
    candidate_id: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "protocolVersion": "1.0.0",
        "requestId": request["requestId"],
        "candidateId": candidate_id,
        "candidateVersion": CANDIDATE_VERSION,
        "status": "success",
        "findingExplanationOutput": output,
    }


def emit(response: dict[str, Any]) -> None:
    sys.stdout.write(canonical_dumps(response))
