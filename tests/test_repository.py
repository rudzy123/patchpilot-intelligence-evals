"""Repository rules, relative links, and the command line."""

from __future__ import annotations

import json
import re
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.candidate_manifest import load_manifest
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.provenance import PROVENANCE_SENTENCE
from patchpilot_intelligence_evals.schemas import (
    CANDIDATE_SCHEMA_NAMES,
    SCHEMA_NAMES,
    TRACK6A_SCHEMA_NAMES,
    TRACK6B_SCHEMA_NAMES,
    TRACK6C_SCHEMA_NAMES,
    load_schema,
    repo_root,
    validate,
)

_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_FORBIDDEN = (
    "torch",
    "tensorflow",
    "jax",
    "transformers",
    "huggingface",
    "sentence-transformers",
    "langchain",
    "llama-index",
    "chromadb",
    "openai",
    "anthropic",
)
_DOCUMENTS = (
    "README.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "SECURITY.md",
    "NOTICE",
    "docs/architecture/evaluation-boundary.md",
    "docs/architecture/corpus-policy.md",
    "docs/architecture/metric-definitions.md",
    "docs/architecture/promotion-gates.md",
    "docs/architecture/candidate-protocol.md",
    "docs/architecture/subprocess-isolation.md",
    "docs/architecture/calibration-protocol.md",
    "docs/architecture/result-retention.md",
    "docs/architecture/real-candidate-selection.md",
    "docs/architecture/real-candidate-acquisition.md",
    "docs/architecture/real-candidate-isolation.md",
    "docs/architecture/real-candidate-evaluation-plan.md",
    "docs/architecture/real-candidate-boundary.md",
    "docs/architecture/external-artifact-cache.md",
    "docs/architecture/model-artifact-verification.md",
    "docs/architecture/runtime-selection.md",
    "docs/architecture/track6-acquisition-boundary.md",
    "docs/architecture/linux-isolation-capabilities.md",
    "docs/architecture/hardened-execution.md",
    "docs/architecture/runtime-authorization.md",
    "docs/architecture/track6b-acquisition-prerequisites.md",
    "docs/architecture/external-runtime-staging.md",
    "docs/architecture/runtime-adapter-contract.md",
    "docs/architecture/candidate-format-resolution.md",
    "docs/architecture/onnx-conversion-boundary.md",
    "docs/architecture/track6c-readiness.md",
    "docs/architecture/candidate-eligibility-closure.md",
    "docs/architecture/tokenizer-eligibility.md",
    "docs/architecture/direct-onnx-eligibility.md",
    "docs/architecture/track6d-acquisition-readiness.md",
    "docs/architecture/protected-repository-validation.md",
    "docs/security/github-actions-supply-chain.md",
    "docs/operations/required-checks.md",
    "docs/operations/main-ruleset-procedure.md",
    "docs/provenance/github-action-pins.md",
    "docs/provenance/initial-corpus-provenance.md",
    "docs/provenance/runtime-evidence.md",
    "docs/provenance/candidate-fixtures.md",
    "docs/provenance/candidate-shortlist.md",
    "docs/provenance/selected-candidate-authorization.md",
    "docs/provenance/candidate-evidence-closure.md",
    "docs/provenance/track5-implementation-review.md",
    "docs/provenance/track6a-implementation-review.md",
    "docs/provenance/runtime-staging-provenance.md",
    "docs/provenance/conversion-toolchain-evidence.md",
    "docs/provenance/candidate-license-closure.md",
    "docs/provenance/direct-onnx-evidence.md",
)


def test_license_and_provenance_text() -> None:
    license_text = (repo_root() / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in license_text
    assert "Version 2.0, January 2004" in license_text
    provenance = (repo_root() / "docs/provenance/initial-corpus-provenance.md").read_text(
        encoding="utf-8"
    )
    assert PROVENANCE_SENTENCE in provenance


def test_relative_links_resolve() -> None:
    root = repo_root()
    for relative in _DOCUMENTS:
        document = root / relative
        text = document.read_text(encoding="utf-8")
        for match in _LINK.findall(text):
            assert not match.startswith(("http://", "https://"))
            target = (document.parent / match).resolve()
            assert target.is_file()
            target.relative_to(root)


def test_dependencies_exclude_model_stacks() -> None:
    text = (repo_root() / "pyproject.toml").read_text(encoding="utf-8").lower()
    for name in _FORBIDDEN:
        assert name not in text
    assert "jsonschema" in text


def test_validation_workflow_is_pinned_and_has_no_secrets() -> None:
    text = (repo_root() / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "permissions:\n  contents: read\n" in text
    assert 'python-version: "3.12"' in text
    assert 'version: "0.13.0"' in text
    assert "enable-cache: false" in text
    assert "persist-credentials: false" in text
    assert 'github-token: ""' in text
    assert "secrets." not in text
    assert "github.token" not in text
    for command in (
        "uv sync --frozen",
        "uv run ruff format --check .",
        "uv run ruff check .",
        "uv run mypy src tests",
        "uv run pytest",
        "uv run patchpilot-evals corpus-validation",
        "uv run patchpilot-evals baseline-evaluation",
        "uv run patchpilot-evals candidate-manifest-validation --manifest",
        "uv run patchpilot-evals candidate-evaluation --manifest",
        "uv run patchpilot-evals candidate-execution --manifest",
        "uv run patchpilot-evals result-validation --result",
        "uv run patchpilot-evals comparison-validation --result",
        "uv run patchpilot-evals calibration-validation --result",
        "uv run patchpilot-evals calibration --output-dir",
        "uv run patchpilot-evals real-candidate-manifest-validation --manifest",
        "uv run patchpilot-evals artifact-cache-policy-validation",
        "uv run patchpilot-evals artifact-verification-validation --manifest",
        "uv run patchpilot-evals runtime-assessment-validation",
        "uv run patchpilot-evals runtime-authorization-validation",
        "uv run patchpilot-evals isolation-profile-validation",
        "uv run patchpilot-evals evidence-closure-validation",
        "uv run patchpilot-evals track6-authorization-validation",
        "uv run patchpilot-evals track5-review-validation",
        "uv run patchpilot-evals sandbox-capability-validation",
        "uv run patchpilot-evals hardened-execution-profile-validation",
        "uv run patchpilot-evals execution-attestation-validation",
        "uv run patchpilot-evals runtime-security-assessment-validation",
        "uv run patchpilot-evals runtime-authorization-v2-validation",
        "uv run patchpilot-evals track6b-readiness-validation",
        "uv run patchpilot-evals track6a-review-validation",
        "uv run patchpilot-evals external-runtime-cache-policy-validation",
        "uv run patchpilot-evals runtime-artifact-verification-validation --manifest",
        "uv run patchpilot-evals runtime-adapter-contract-validation",
        "uv run patchpilot-evals candidate-format-resolution-validation",
        "uv run patchpilot-evals onnx-conversion-plan-validation",
        "uv run patchpilot-evals track6c-readiness-validation",
        "uv run patchpilot-evals candidate-eligibility-validation",
        "uv run patchpilot-evals tokenizer-eligibility-validation",
        "uv run patchpilot-evals direct-onnx-evidence-validation",
        "uv run patchpilot-evals artifact-budget-validation",
        "uv run patchpilot-evals bounded-subprocess-compatibility-validation",
        "uv run patchpilot-evals track6d-readiness-validation",
        "uv run patchpilot-evals workflow-policy-validation",
        "uv run patchpilot-evals dependency-architecture-policy-validation",
    ):
        assert command in text
    uses = re.findall(r"uses: (\S+)", text)
    checkout = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
    setup_uv = "astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2"
    assert uses == [checkout, setup_uv, checkout, setup_uv, checkout, setup_uv]
    for name in ("torch", "transformers", "openai", "anthropic", "huggingface"):
        assert name not in text.lower()


def test_help_lists_commands() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer), pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0
    text = buffer.getvalue()
    assert "corpus-validation" in text
    assert "baseline-evaluation" in text
    assert "candidate-manifest-validation" in text
    assert "candidate-evaluation" in text
    assert "candidate-comparison" in text
    assert "comparison-validation" in text
    assert "calibration-validation" in text
    assert "calibration" in text
    assert "real-candidate-manifest-validation" in text
    assert "artifact-cache-policy-validation" in text
    assert "artifact-verification-validation" in text
    assert "runtime-assessment-validation" in text
    assert "runtime-authorization-validation" in text
    assert "isolation-profile-validation" in text
    assert "evidence-closure-validation" in text
    assert "track6-authorization-validation" in text
    assert "track5-review-validation" in text
    assert "sandbox-capability-validation" in text
    assert "hardened-execution-profile-validation" in text
    assert "hardened-fixture-execution" in text
    assert "execution-attestation-validation" in text
    assert "runtime-security-assessment-validation" in text
    assert "runtime-authorization-v2-validation" in text
    assert "track6b-readiness-validation" in text
    assert "track6a-review-validation" in text
    assert "external-runtime-cache-policy-validation" in text
    assert "runtime-artifact-verification-validation" in text
    assert "runtime-adapter-contract-validation" in text
    assert "candidate-format-resolution-validation" in text
    assert "onnx-conversion-plan-validation" in text
    assert "track6c-readiness-validation" in text
    assert "candidate-eligibility-validation" in text
    assert "tokenizer-eligibility-validation" in text
    assert "direct-onnx-evidence-validation" in text
    assert "artifact-budget-validation" in text
    assert "bounded-subprocess-compatibility-validation" in text
    assert "track6d-readiness-validation" in text
    assert "workflow-policy-validation" in text
    assert "dependency-architecture-policy-validation" in text


def test_committed_json_files_validate() -> None:
    root = repo_root()
    names = (
        SCHEMA_NAMES
        + CANDIDATE_SCHEMA_NAMES
        + TRACK6A_SCHEMA_NAMES
        + TRACK6B_SCHEMA_NAMES
        + TRACK6C_SCHEMA_NAMES
    )
    for name in names:
        document = load_schema(name)
        assert document["additionalProperties"] is False
    for path in sorted((root / "corpus" / "cases").glob("*.json")):
        validate("evaluation-case", json.loads(path.read_text(encoding="utf-8")))
    for path in sorted((root / "candidates" / "fixtures").glob("*/manifest.json")):
        relative = path.relative_to(root).as_posix()
        manifest = load_manifest(relative)
        assert manifest["manifestDigest"]
        validate("candidate-manifest", manifest)
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(
            [
                "candidate-manifest-validation",
                "--manifest",
                "candidates/fixtures/conforming/manifest.json",
            ]
        )
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["status"] == "ok"
    assert summary["candidateId"] == "fixture-conforming"
    assert summary["productionReady"] is False


def test_cli_validation_and_optional_output(tmp_path: Path) -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["corpus-validation"])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["caseCount"] == 24
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["baseline-evaluation", "--output", "../patchpilot/leak.json"])
    assert code == 1
    destination_name = "baseline-result.json"
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("patchpilot_intelligence_evals.cli.repo_root", lambda: tmp_path)
    try:
        code = main(["baseline-evaluation", "--output", destination_name])
        assert code == 0
        destination = tmp_path / destination_name
        assert destination.is_file()
        payload = json.loads(destination.read_text(encoding="utf-8"))
        assert payload["productionReady"] is False
    finally:
        monkeypatch.undo()
