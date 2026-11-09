"""Structural checks for the 24-case synthetic corpus."""

from __future__ import annotations

import json

from patchpilot_intelligence_evals.corpus import (
    CASE_IDS,
    EXPECTED_COUNTS,
    case_digest,
    cases_dir,
    invalid_url_hosts,
    load_cases,
    load_manifest,
    secret_pattern_names,
    to_candidate_input,
    validate_corpus,
)
from patchpilot_intelligence_evals.provenance import PROVENANCE_SENTENCE, REVIEW_STATUS
from patchpilot_intelligence_evals.schemas import validate


def test_exactly_24_cases_and_taxonomy() -> None:
    summary = validate_corpus()
    assert summary["caseCount"] == 24
    assert summary["taxonomyCounts"] == EXPECTED_COUNTS
    cases = load_cases()
    assert [case["caseId"] for case in cases] == sorted(CASE_IDS)
    counts: dict[str, int] = {}
    for case in cases:
        counts[case["category"]] = counts.get(case["category"], 0) + 1
    assert counts == EXPECTED_COUNTS


def test_digests_and_manifest_order() -> None:
    cases = load_cases()
    manifest = load_manifest()
    assert [item["caseId"] for item in manifest["cases"]] == sorted(
        item["caseId"] for item in manifest["cases"]
    )
    for case in cases:
        assert case["caseDigest"] == case_digest(case)
        validate("evaluation-case", case)
    assert manifest["provenance"] == PROVENANCE_SENTENCE
    assert manifest["reviewStatus"] == REVIEW_STATUS
    assert manifest["reviewStatus"] == "accepted-by-principal-systems-architect"
    for phrase in (
        "2026-11-09",
        "PatchPilot Principal Systems Architect",
        "corpus structure, provenance, tenant controls, evaluation taxonomy, "
        "deterministic-baseline use, and promotion-gate suitability for Intelligence Track 2",
        "harness and future offline-candidate evaluation only",
        "does not approve a real model, scientifically calibrate the percentage gates, "
        "or authorize production composition",
    ):
        assert phrase in manifest["provenance"]


def test_identifiers_are_unique_and_south_is_not_authorized() -> None:
    evidence_ids: set[str] = set()
    for case in load_cases():
        assert case["authorizedOrganizationId"] != "org-synthetic-south"
        assert case["sourceDeclaration"] == "original-synthetic"
        assert case["license"] == "Apache-2.0"
        for evidence in case["authorizedEvidence"]:
            assert evidence["evidenceId"] not in evidence_ids
            evidence_ids.add(evidence["evidenceId"])


def test_negative_controls_stay_out_of_authorized_context() -> None:
    for case in load_cases():
        projection = {key: value for key, value in case.items() if key != "negativeControls"}
        blob = json.dumps(projection)
        candidate = json.dumps(to_candidate_input(case))
        for control in case["negativeControls"]:
            for token in control.values():
                assert token not in blob
                assert token not in candidate


def test_secret_and_url_scanners() -> None:
    for path in cases_dir().glob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert secret_pattern_names(text) == []
        assert invalid_url_hosts(text) == []
    assert secret_pattern_names("password = hunter2")
    assert secret_pattern_names("AKIAIOSFODNN7EXAMPLE")
    assert invalid_url_hosts("see https://example.com/advisory")
    assert invalid_url_hosts("see https://docs.example.invalid/synthetic/note") == []
