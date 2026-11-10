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
    "docs/provenance/initial-corpus-provenance.md",
    "docs/provenance/candidate-fixtures.md",
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
    ):
        assert command in text
    uses = re.findall(r"uses: (\S+)", text)
    assert uses == [
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2",
    ]
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


def test_committed_json_files_validate() -> None:
    root = repo_root()
    for name in SCHEMA_NAMES + CANDIDATE_SCHEMA_NAMES:
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
