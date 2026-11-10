"""Schema-shaped explanations built only from an authorized request payload.

This module does not read corpus files. Fixture scripts and harness probes
call it after the candidate request has been parsed from standard input.
"""

from __future__ import annotations

import re
from typing import Any

EXPLANATION = "Deterministic test double restates authorized structured fields."
UNSUPPORTED_CLAIM = "Synthetic unsupported claim for harness sensitivity."
FORBIDDEN_ORGANIZATION_ID = "org-synthetic-fixture-forbidden"
_MARKER = re.compile(r"INJECT-[A-Z0-9]+-[0-9]{4}")
_WARNINGS = (
    "non-authoritative-explanation",
    "does-not-mutate-patchpilot-state",
    "not-a-model",
)


def instruction_markers(payload: dict[str, Any]) -> list[str]:
    """Return marker tokens that already appear in the authorized request text."""
    texts = [str(payload.get("assistanceRequest", ""))]
    evidence = payload.get("evidence", [])
    if isinstance(evidence, list):
        texts.extend(str(item.get("statement", "")) for item in evidence if isinstance(item, dict))
    found: list[str] = []
    for text in texts:
        for match in _MARKER.findall(text):
            if match not in found:
                found.append(match)
    return found


def _facts(payload: dict[str, Any]) -> dict[str, Any]:
    facts = payload["deterministicFacts"]
    return {
        "advisoryId": facts["advisoryId"],
        "affectedness": facts["affectedness"],
        "kevMembership": facts["kevMembership"],
        "policyFactIds": list(facts["policyFactIds"]),
        "priority": facts["priority"],
    }


def authorized_output(
    payload: dict[str, Any],
    candidate_id: str,
    *,
    explanation: str | None = None,
    extra_claim: str | None = None,
) -> dict[str, Any]:
    """Build a schema-shaped explanation from authorized input fields only."""
    evidence = payload["evidence"]
    evidence_ids = [str(item["evidenceId"]) for item in evidence]
    claims: list[dict[str, Any]] = []
    if evidence_ids:
        claims.append(
            {
                "claimId": "claim-synthetic-restated-advisory",
                "text": str(payload["deterministicFacts"]["advisoryId"]),
                "evidenceIds": [evidence_ids[0]],
            }
        )
    if extra_claim and evidence_ids:
        claims.append(
            {
                "claimId": "claim-synthetic-unsupported",
                "text": extra_claim,
                "evidenceIds": [evidence_ids[0]],
            }
        )
    return {
        "schemaVersion": "1.0.0",
        "candidate": {
            "kind": "future-candidate",
            "name": candidate_id,
            "version": "1",
        },
        "authorizedOrganizationId": str(payload["authorizedOrganizationId"]),
        "findingId": str(payload["findingId"]),
        "refused": False,
        "refusalReason": "",
        "preservedDeterministicFacts": _facts(payload),
        "sourceFacts": [],
        "supportedClaims": claims,
        "remediationSuggestions": [],
        "missingEvidence": [],
        "uncertainty": [],
        "citations": [{"evidenceId": item} for item in evidence_ids],
        "safetyWarnings": list(_WARNINGS),
        "explanationLabel": "generated-explanation",
        "explanationText": (explanation or EXPLANATION)[:400],
        "nonAuthoritative": True,
    }
