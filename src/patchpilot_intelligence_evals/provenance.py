"""Initial-corpus provenance. This module does not import corpus records."""

from __future__ import annotations

PROVENANCE_SENTENCE = (
    "The initial corpus is original synthetic Apache-2.0 work for this repository, "
    "with no copied tenant, customer, production prompt, SBOM, advisory payload, or "
    "educational notebook content, and with no neural-from-scratch notebook content. "
    "Review status is accepted on 2026-11-09 by the PatchPilot Principal Systems Architect "
    "for corpus structure, provenance, tenant controls, evaluation taxonomy, "
    "deterministic-baseline use, and promotion-gate suitability for Intelligence Track 2. "
    "This acceptance authorizes harness and future offline-candidate evaluation only. "
    "It does not approve a real model, scientifically calibrate the percentage gates, "
    "or authorize production composition."
)

REVIEW_STATUS = "accepted-by-principal-systems-architect"
LICENSE_ID = "Apache-2.0"
SOURCE_DECLARATION = "original-synthetic"


class ProvenanceError(ValueError):
    """The manifest provenance fields do not match the recorded sentence."""


def require_manifest_provenance(manifest: dict[str, object]) -> None:
    if manifest.get("provenance") != PROVENANCE_SENTENCE:
        raise ProvenanceError("provenance sentence mismatch")
    if manifest.get("reviewStatus") != REVIEW_STATUS:
        raise ProvenanceError("review status mismatch")
    if manifest.get("license") != LICENSE_ID:
        raise ProvenanceError("license mismatch")
