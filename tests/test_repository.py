"""Repository rules, relative links, and the command line."""

from __future__ import annotations

import json
import re
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.provenance import PROVENANCE_SENTENCE
from patchpilot_intelligence_evals.schemas import repo_root

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
    "docs/provenance/initial-corpus-provenance.md",
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


def test_cli_validation_and_optional_output() -> None:
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
    relative = "build/baseline-result.json"
    destination = repo_root() / relative
    try:
        code = main(["baseline-evaluation", "--output", relative])
        assert code == 0
        assert destination.is_file()
        payload = json.loads(destination.read_text(encoding="utf-8"))
        assert payload["productionReady"] is False
    finally:
        if destination.exists():
            destination.unlink()
        build_dir = repo_root() / "build"
        if build_dir.exists():
            build_dir.rmdir()
