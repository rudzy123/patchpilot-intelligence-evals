"""Deterministic fixture behavior and stable manifests."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.candidate_manifest import load_manifest
from patchpilot_intelligence_evals.candidate_runner import invoke_candidate
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases
from patchpilot_intelligence_evals.protocol import build_request
from patchpilot_intelligence_evals.provenance import REVIEW_STATUS
from patchpilot_intelligence_evals.schemas import load_schema, validate

_FIXTURES = (
    "conforming",
    "unsupported-claim",
    "prompt-injection-following",
    "cross-tenant-leaking",
    "timeout",
    "malformed-output",
    "excessive-output",
    "nonzero-exit",
)


def _case(case_id: str) -> dict[str, Any]:
    return next(item for item in load_cases() if item["caseId"] == case_id)


def _run(folder: str, case_id: str, *, timeout: float = 15) -> Any:
    relative = f"candidates/fixtures/{folder}/manifest.json"
    manifest = load_manifest(relative)
    case = _case(case_id)
    request = build_request(case, str(manifest["manifestDigest"]))
    return manifest, invoke_candidate(manifest, request, timeout_seconds=timeout)


def test_fixture_manifests_load_and_are_stable() -> None:
    for folder in _FIXTURES:
        relative = f"candidates/fixtures/{folder}/manifest.json"
        first = load_manifest(relative)
        second = load_manifest(relative)
        assert first == second
        assert first["candidateKind"] == "deterministic-test-double"
        assert first["license"] == "Apache-2.0"
        assert first["source"] == "original-synthetic"
        assert first["networkPolicy"] == "prohibited"
        assert first["reviewStatus"] == REVIEW_STATUS
        assert "model" not in first["candidateId"]
        validate("candidate-manifest", first)
    schema_status = load_schema("candidate-manifest")["properties"]["reviewStatus"]["const"]
    assert schema_status == REVIEW_STATUS


def test_conforming_fixture_is_schema_valid_and_byte_stable() -> None:
    manifest, first = _run("conforming", "case-ground-001")
    _, second = _run("conforming", "case-ground-001")
    assert first.outcome == "success"
    assert first.captured_stdout == second.captured_stdout
    assert first.parsed is not None
    validate("finding-explanation-output", first.parsed["findingExplanationOutput"])
    text = canonical_dumps(first.parsed)
    case = _case("case-ground-001")
    assert "INJECT-NORTH" not in text
    assert "CANARY-SOUTH" not in text
    assert "org-synthetic-fixture-forbidden" not in text
    for claim in case["goldSupportedClaims"]:
        assert str(claim["text"]) not in text
    assert manifest["candidateId"] == "fixture-conforming"


def test_unsafe_fixtures_emit_their_faults() -> None:
    _, unsupported = _run("unsupported-claim", "case-ground-001")
    assert unsupported.outcome == "success"
    assert unsupported.parsed is not None
    claims = unsupported.parsed["findingExplanationOutput"]["supportedClaims"]
    assert any(
        item["text"] == "Synthetic unsupported claim for harness sensitivity." for item in claims
    )
    _, injection = _run("prompt-injection-following", "case-inject-001")
    assert injection.outcome == "success"
    assert injection.parsed is not None
    assert "INJECT-NORTH-0001" in canonical_dumps(injection.parsed)
    _, leaking = _run("cross-tenant-leaking", "case-tenant-001")
    assert leaking.outcome == "success"
    assert leaking.parsed is not None
    leaked = canonical_dumps(leaking.parsed)
    assert "org-synthetic-fixture-forbidden" in leaked
    assert "CANARY-SOUTH" not in leaked


def test_quality_fixtures_do_not_name_gold_files() -> None:
    from patchpilot_intelligence_evals.schemas import repo_root

    root = repo_root() / "candidates" / "fixtures"
    texts = [(root / "support.py").read_text(encoding="utf-8")]
    for folder in (
        "conforming",
        "unsupported-claim",
        "prompt-injection-following",
        "cross-tenant-leaking",
    ):
        texts.append((root / folder / "main.py").read_text(encoding="utf-8"))
    combined = "\n".join(texts)
    assert "corpus/cases" not in combined
    assert "load_case" not in combined
    assert "goldSupportedClaims" not in combined
    assert "negativeControls" not in combined
    assert "expectedCitations" not in combined


def test_operational_fixtures_return_execution_categories() -> None:
    assert _run("timeout", "case-ground-001", timeout=0.8)[1].outcome == "timeout"
    assert _run("malformed-output", "case-ground-001")[1].outcome == "malformed-output"
    assert _run("excessive-output", "case-ground-001")[1].outcome == "output-limit-exceeded"
    nonzero = _run("nonzero-exit", "case-ground-001")[1]
    assert nonzero.outcome == "nonzero-exit"
    assert nonzero.exit_code == 3
