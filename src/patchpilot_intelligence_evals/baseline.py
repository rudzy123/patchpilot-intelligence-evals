"""Deterministic non-model baseline.

Copying gold supported claims is harness-reference behavior for the scorer.
It is not a model, and a passing run is not a model-quality claim.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps

CANDIDATE: dict[str, str] = {
    "kind": "deterministic-baseline",
    "name": "patchpilot-deterministic-baseline",
    "version": "1",
}
REFUSAL_TEXT = "Deterministic baseline assistance refuses because the case requires refusal."
ASSISTANCE_TEXT = "Deterministic baseline assistance restates authorized structured fields."


def _forbidden_tokens(case: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    injection = case["promptInjection"]
    tokens.extend(str(marker) for marker in injection["markers"])
    for control in case["negativeControls"]:
        tokens.extend(
            [
                str(control["organizationId"]),
                str(control["findingId"]),
                str(control["assetId"]),
                str(control["canary"]),
            ]
        )
    return [token for token in tokens if token]


def _contaminated(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


def run_baseline(case: dict[str, Any]) -> dict[str, Any]:
    """Return schema-shaped assistance. The input mapping is not modified."""
    tokens = _forbidden_tokens(case)
    authorized = {str(item["evidenceId"]): item for item in case["authorizedEvidence"]}
    expected = [
        str(evidence_id)
        for evidence_id in case["expectedCitations"]
        if str(evidence_id) in authorized
    ]
    refused = bool(case["expectedRefusal"])
    if refused:
        claims: list[dict[str, Any]] = []
        citations: list[dict[str, str]] = []
        remediation: list[dict[str, Any]] = []
        source_facts: list[dict[str, str]] = []
        explanation = REFUSAL_TEXT
        refusal_reason = REFUSAL_TEXT
    else:
        claims = []
        for claim in case["goldSupportedClaims"]:
            evidence_ids = [str(item) for item in claim["evidenceIds"]]
            text = str(claim["text"])
            if all(item in authorized for item in evidence_ids) and not _contaminated(text, tokens):
                claims.append(
                    {
                        "claimId": str(claim["claimId"]),
                        "text": text,
                        "evidenceIds": evidence_ids,
                    }
                )
        citations = [{"evidenceId": evidence_id} for evidence_id in expected]
        source_facts = []
        for evidence_id in expected:
            statement = str(authorized[evidence_id]["statement"])
            if not _contaminated(statement, tokens):
                source_facts.append({"evidenceId": evidence_id, "statement": statement})
        remediation = [
            {"text": str(text), "nonAuthoritative": True}
            for text in case["expectedRemediationSuggestions"]
            if not _contaminated(str(text), tokens)
        ]
        explanation = ASSISTANCE_TEXT
        refusal_reason = ""
    missing = [
        str(item) for item in case["missingEvidence"] if not _contaminated(str(item), tokens)
    ]
    uncertainty = [
        str(item) for item in case["expectedUncertainty"] if not _contaminated(str(item), tokens)
    ]
    warnings = [
        str(item) for item in case["expectedSafetyWarnings"] if not _contaminated(str(item), tokens)
    ]
    output: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "candidate": dict(CANDIDATE),
        "authorizedOrganizationId": str(case["authorizedOrganizationId"]),
        "findingId": str(case["findingId"]),
        "refused": refused,
        "refusalReason": refusal_reason,
        "preservedDeterministicFacts": deepcopy(case["deterministicFacts"]),
        "sourceFacts": source_facts,
        "supportedClaims": claims,
        "remediationSuggestions": remediation,
        "missingEvidence": missing,
        "uncertainty": uncertainty,
        "citations": citations,
        "safetyWarnings": warnings,
        "explanationLabel": "deterministic-baseline-assistance",
        "explanationText": explanation,
        "nonAuthoritative": True,
    }
    # Touch the canonical form so callers can rely on stable key ordering later.
    canonical_dumps(output)
    return output
