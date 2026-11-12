"""Workflow policy, action pins, and dependency architecture checks."""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.dependency_architecture_policy import (
    DependencyPolicyError,
    validate_dependency_policy,
)
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.workflow_policy import (
    WorkflowPolicyError,
    _command_text,
    _local_action_files,
    classify_action,
    parse_workflow,
    validate_workflow_policy,
    validate_workflow_text,
)

_FIXTURES = repo_root() / "tests" / "fixtures" / "workflow_policy"
_CHECKOUT = "3d3c42e5aac5ba805825da76410c181273ba90b1"
_PROVENANCE = (
    {
        "repository": "actions/checkout",
        "path": "",
        "commitSha": _CHECKOUT,
        "reviewTag": "v7.0.1",
        "authorClass": "github",
    },
)
_INVALID = {
    "invalid-floating-tag.yml": "unpinned-action",
    "invalid-missing-permissions.yml": "missing-permissions",
    "invalid-write-permission.yml": "broad-permissions",
    "invalid-persisted-credentials.yml": "persisted-credentials",
    "invalid-missing-timeout.yml": "missing-timeout",
    "invalid-excessive-timeout.yml": "excessive-timeout",
    "invalid-pull-request-target.yml": "pull-request-target",
    "invalid-path-filter.yml": "path-filter",
    "invalid-job-condition.yml": "conditional-execution",
    "invalid-model-download.yml": "prohibited-command",
    "invalid-runtime-install.yml": "prohibited-command",
    "invalid-docker-run.yml": "prohibited-command",
    "invalid-continue-on-error.yml": "conditional-execution",
    "invalid-secret-index.yml": "token-exposure",
    "invalid-publish.yml": "publish-or-deploy",
    "invalid-missing-provenance.yml": "missing-provenance",
    "invalid-cancel-push.yml": "concurrency",
    "invalid-upload-artifact.yml": "prohibited-command",
    "invalid-cache.yml": "prohibited-command",
}
_INTENDED = (
    "Validation / Quality",
    "Validation / Tests",
    "Validation / Repository Contracts",
    "CodeQL / Analyze",
    "Dependency Review / Dependency Review",
)


def _check_fixture(name: str) -> None:
    _check_fixture_text((_FIXTURES / name).read_text(encoding="utf-8"))


def _check_fixture_text(text: str, source_root: Path | None = None) -> None:
    validate_workflow_text(
        text,
        provenance=_PROVENANCE,
        permissions={"contents": "read"},
        timeouts={"Quality": 15},
        require_name="Sample",
        source_root=source_root,
    )


def test_valid_workflow_fixture_passes() -> None:
    _check_fixture("valid-read-only.yml")


@pytest.mark.parametrize(("name", "code"), sorted(_INVALID.items()))
def test_invalid_workflow_fixtures_fail(name: str, code: str) -> None:
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture(name)
    assert caught.value.code == code


@pytest.mark.parametrize(
    "command",
    (
        "pip install torch",
        "pip3 install torch",
        "uv add transformers",
        "uvx onnxruntime",
        "conda install pytorch",
        "mamba install pytorch",
        "podman run example",
        "gh release download v1",
        "echo ${{ github['token'] }}",
        "echo ${{ toJSON(secrets) }}",
    ),
)
def test_runtime_install_and_token_bypasses_fail(command: str) -> None:
    text = (_FIXTURES / "valid-read-only.yml").read_text(encoding="utf-8")
    text += f"      - name: Extra\n        run: {command}\n"
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(text)
    code = "token-exposure" if "token" in command or "secrets" in command else "prohibited-command"
    assert caught.value.code == code


def test_local_action_is_scanned_and_missing_action_fails(tmp_path: Path) -> None:
    text = (_FIXTURES / "valid-read-only.yml").read_text(encoding="utf-8")
    text += "      - name: Local\n        uses: ./.github/actions/fetch\n"
    with pytest.raises(WorkflowPolicyError) as missing:
        _check_fixture_text(text)
    assert missing.value.code == "missing-local-action"
    with pytest.raises(WorkflowPolicyError) as absent:
        _check_fixture_text(text, source_root=tmp_path)
    assert absent.value.code == "missing-local-action"
    action = tmp_path / ".github" / "actions" / "fetch"
    action.mkdir(parents=True)
    (action / "action.yml").write_text(
        "runs:\n  using: composite\n  steps:\n    - run: curl https://example.invalid/model.bin\n",
        encoding="utf-8",
    )
    (action / "fetch.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    with pytest.raises(WorkflowPolicyError) as prohibited:
        _check_fixture_text(text, source_root=tmp_path)
    assert prohibited.value.code == "prohibited-command"
    (action / "action.yml").write_text(
        "runs:\n  using: composite\n  steps:\n    - run: echo ok\n",
        encoding="utf-8",
    )
    _check_fixture_text(text, source_root=tmp_path)
    script = action / "index.js"
    script.write_text(
        'require("child_process").execSync("docker run --rm alpine:3 echo hi");\n',
        encoding="utf-8",
    )
    with pytest.raises(WorkflowPolicyError) as scripted:
        _check_fixture_text(text, source_root=tmp_path)
    assert scripted.value.code == "prohibited-command"
    script.write_text("console.log(1)\n", encoding="utf-8")
    _check_fixture_text(text, source_root=tmp_path)
    (action / "payload.bin").write_bytes(b"\xff\xfe")
    with pytest.raises(WorkflowPolicyError) as binary:
        _check_fixture_text(text, source_root=tmp_path)
    assert binary.value.code == "unreadable-local-action"


def test_shell_continuation_joins_words_without_inserting_space() -> None:
    assert _command_text("dock\\\ner run") == "docker run"
    assert _command_text("docker \\\nrun") == "docker run"
    assert _command_text("uv p\\\nip install") == "uv pip install"
    assert _command_text("secret\\\ns[") == "secrets["
    assert _command_text("github.\\\ntoken") == "github.token"
    assert _command_text("pull_request_\\\ntarget") == "pull_request_target"
    assert _command_text("uv \\\np\\\nip \\\ninstall") == "uv pip install"
    assert _command_text("dock\\\r\ner run") == "docker run"
    assert _command_text("echo ok\\") == "echo ok\\"
    assert _command_text("docker  run") == "docker  run"
    assert _command_text("echo kept\tspaces") == "echo kept\tspaces"


@pytest.mark.parametrize(
    ("lines", "code"),
    (
        (["dock\\", "er run"], "prohibited-command"),
        (["docker \\", "run alpine"], "prohibited-command"),
        (["uv p\\", "ip install torch"], "prohibited-command"),
        (["secret\\", "s["], "token-exposure"),
        (["github.\\", "token"], "token-exposure"),
        (["pull_request_\\", "target"], "pull-request-target"),
        (["uv \\", "p\\", "ip \\", "install torch"], "prohibited-command"),
    ),
)
def test_continued_prohibited_examples_fail(lines: list[str], code: str) -> None:
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(_run_block(lines))
    assert caught.value.code == code


def test_crlf_continuation_is_removed_before_the_scan() -> None:
    text = (_FIXTURES / "valid-read-only.yml").read_text(encoding="utf-8")
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(text + "dock\\\r\ner run\n")
    assert caught.value.code == "prohibited-command"


def test_lone_backslash_and_benign_continuation_remain_valid() -> None:
    _check_fixture_text(_run_block(["echo ok\\"]))
    _check_fixture_text(_run_block(["echo hello\\", "world"]))
    _check_fixture_text(_run_block(["echo kept  spaces"]))


def test_shell_continuation_cannot_hide_a_container_run(tmp_path: Path) -> None:
    text = (_FIXTURES / "valid-read-only.yml").read_text(encoding="utf-8")
    text += "      - name: Local\n        uses: ./.github/actions/fetch\n"
    action = tmp_path / ".github" / "actions" / "fetch"
    action.mkdir(parents=True)
    (action / "action.yml").write_text(
        "\n".join(
            (
                "name: Fetch",
                "description: Fetch",
                "runs:",
                "  using: composite",
                "  steps:",
                "    - shell: bash",
                "      run: |",
                "        docker \\",
                "          run --rm alpine:3 echo hi",
                "",
            )
        ),
        encoding="utf-8",
    )
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(text, source_root=tmp_path)
    assert caught.value.code == "prohibited-command"
    (action / "action.yml").write_text(
        "runs:\n  using: composite\n  steps:\n    - run: echo ok\n",
        encoding="utf-8",
    )
    (action / "run.sh").write_bytes(b"dock\\\ner run\n")
    with pytest.raises(WorkflowPolicyError) as scripted:
        _check_fixture_text(text, source_root=tmp_path)
    assert scripted.value.code == "prohibited-command"


def test_unreadable_subdirectory_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    action = _writable_action(tmp_path)
    secret = action / "secret"
    secret.mkdir()
    (secret / "evil.sh").write_text("docker run alpine\n", encoding="utf-8")
    real_scandir = os.scandir

    def fake_scandir(path: str | os.PathLike[str] | None = None) -> Iterator[os.DirEntry[str]]:
        if path is not None and Path(path).name == "secret":
            raise PermissionError(13, "denied", str(path))
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", fake_scandir)
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(_local_use(), source_root=tmp_path)
    assert caught.value.code == "unreadable-local-action"


def test_unreadable_file_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    action = _writable_action(tmp_path)
    (action / "locked.sh").write_text("echo ok\n", encoding="utf-8")
    real_open = open

    def fake_open(
        file: str | os.PathLike[str] | int, mode: str = "r", *args: Any, **kwargs: Any
    ) -> Any:
        if not isinstance(file, int) and Path(file).name == "locked.sh":
            raise PermissionError(13, "denied", str(file))
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(_local_use(), source_root=tmp_path)
    assert caught.value.code == "unreadable-local-action"


def test_stat_failure_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    action = _writable_action(tmp_path)
    (action / "ghost").write_text("echo ok\n", encoding="utf-8")
    real_lstat = os.lstat

    def fake_lstat(path: str | os.PathLike[str], *, dir_fd: int | None = None) -> os.stat_result:
        if Path(path).name == "ghost":
            raise OSError(13, "stat failed", str(path))
        return real_lstat(path, dir_fd=dir_fd)

    monkeypatch.setattr(os, "lstat", fake_lstat)
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(_local_use(), source_root=tmp_path)
    assert caught.value.code == "unreadable-local-action"


def test_dangling_and_escaping_symlinks_fail_closed(tmp_path: Path) -> None:
    action = _writable_action(tmp_path)
    (action / "broken").symlink_to(action / "missing")
    with pytest.raises(WorkflowPolicyError) as dangling:
        _check_fixture_text(_local_use(), source_root=tmp_path)
    assert dangling.value.code == "unreadable-local-action"
    (action / "broken").unlink()
    outside = tmp_path / "outside.sh"
    outside.write_text("echo ok\n", encoding="utf-8")
    (action / "escape").symlink_to(outside)
    with pytest.raises(WorkflowPolicyError) as escaped:
        _check_fixture_text(_local_use(), source_root=tmp_path)
    assert escaped.value.code == "unreadable-local-action"


def test_fifo_is_rejected(tmp_path: Path) -> None:
    action = _writable_action(tmp_path)
    os.mkfifo(action / "pipe")
    with pytest.raises(WorkflowPolicyError) as caught:
        _check_fixture_text(_local_use(), source_root=tmp_path)
    assert caught.value.code == "unsupported-local-action-file"


def test_readable_local_action_and_traversal_order(tmp_path: Path) -> None:
    action = _writable_action(tmp_path)
    nested = action / "a"
    nested.mkdir()
    (nested / "c.sh").write_text("echo c\n", encoding="utf-8")
    (action / "b.sh").write_text("echo b\n", encoding="utf-8")
    _check_fixture_text(_local_use(), source_root=tmp_path)
    names = [path.relative_to(action).as_posix() for path in _local_action_files(action)]
    assert names == ["a/c.sh", "action.yml", "b.sh"]


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores directory mode 000")
def test_mode_000_subdirectory_fails_closed(tmp_path: Path) -> None:
    action = _writable_action(tmp_path)
    secret = action / "secret"
    secret.mkdir()
    (secret / "evil.sh").write_text("docker run alpine\n", encoding="utf-8")
    secret.chmod(0)
    try:
        with pytest.raises(WorkflowPolicyError) as caught:
            _check_fixture_text(_local_use(), source_root=tmp_path)
        assert caught.value.code == "unreadable-local-action"
    finally:
        secret.chmod(0o755)


def test_action_classes() -> None:
    assert classify_action(f"actions/checkout@{_CHECKOUT}") == "github"
    assert classify_action(f"github/codeql-action/init@{_CHECKOUT}") == "github"
    assert classify_action(f"astral-sh/setup-uv@{_CHECKOUT}") == "astral"
    assert classify_action("./.github/actions/local") == "repository-local"
    assert classify_action(f"example/action@{_CHECKOUT}") == "third-party"


def test_validation_jobs_keep_existing_coverage() -> None:
    text = (repo_root() / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    document = parse_workflow(text)
    quality = _runs(document, "quality")
    tests = _runs(document, "tests")
    contracts = _runs(document, "repository-contracts")
    assert "uv sync --frozen" in quality
    assert "uv run ruff format --check ." in quality
    assert "uv run ruff check ." in quality
    assert "uv run mypy src tests" in quality
    assert "uv run pytest" not in quality
    assert "uv run pytest" in tests
    assert "ruff" not in tests
    assert "uv run pytest" not in contracts
    assert "ruff format" not in contracts
    assert "track6d-readiness-validation" in contracts
    assert "candidate-discovery-validation" in contracts
    assert "track8-acquisition-authorization-validation" in contracts
    assert "track7-review-validation" in contracts
    assert "track7a-review-validation" in contracts
    assert "storage-safety-synthetic-check" in contracts
    assert contracts.index("storage-safety-synthetic-check") < contracts.index(
        "workflow-policy-validation"
    )
    assert "workflow-policy-validation" in contracts
    assert "dependency-architecture-policy-validation" in contracts
    assert "hardened-fixture-execution" not in text
    assert document["name"] == "Validation"
    assert [job["name"] for job in _project_names(document)] == [
        "Quality",
        "Tests",
        "Repository Contracts",
    ]


def test_codeql_and_dependency_review_are_scoped() -> None:
    codeql = parse_workflow((repo_root() / ".github/workflows/codeql.yml").read_text())
    review = parse_workflow((repo_root() / ".github/workflows/dependency-review.yml").read_text())
    assert codeql["name"] == "CodeQL"
    assert set(codeql["on"]) == {"pull_request", "push", "schedule", "workflow_dispatch"}
    assert "merge_group" not in codeql["on"]
    init = codeql["jobs"]["analyze"]["steps"][1]["with"]
    assert init == {"languages": "python", "build-mode": "none"}
    assert review["name"] == "Dependency Review"
    assert set(review["on"]) == {"pull_request"}
    assert review["permissions"] == {"contents": "read"}


def test_governance_record_is_not_applied() -> None:
    document = json.loads(
        (repo_root() / "docs/operations/workflow-governance.json").read_text(encoding="utf-8")
    )
    contexts = [item["context"] for item in document["intendedRequiredChecks"]]
    assert contexts == list(_INTENDED)
    assert len(contexts) == len(set(contexts))
    assert document["rulesetApplicationStatus"] == "not-applied"
    assert document["pullRequestObservationStatus"] == "not-observed"
    assert document["observedCheckContexts"] == []
    assert document["mergeQueue"] == "not-enabled"
    assert document["classicBranchProtection"] == "absent"
    assert document["currentRuleset"]["requiredCheckContext"] == "validate"
    assert document["currentRuleset"]["bypassActors"] == []
    summary = validate_workflow_policy()
    assert summary["workflowCount"] == 3
    assert summary["actionPinCount"] == 5
    assert summary["productionReady"] is False


def test_workflow_policy_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["workflow-policy-validation"])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["rulesetApplicationStatus"] == "not-applied"
    assert summary["pullRequestObservationStatus"] == "not-observed"


def test_dependency_policy_command_passes_current_lock() -> None:
    policy = json.loads(
        (repo_root() / "docs/security/dependency-architecture-policy.json").read_text(
            encoding="utf-8"
        )
    )
    assert policy["allow"] == []
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["dependency-architecture-policy-validation"])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary == {
        "deniedCount": 0,
        "packageCount": 19,
        "productionReady": False,
        "status": "ok",
    }


@pytest.mark.parametrize(
    "name",
    (
        "datasets",
        "diffusers",
        "sentencepiece",
        "tiktoken",
        "tokenizers",
        "torch-geometric",
        "torchdata",
        "torchtext",
    ),
)
def test_committed_policy_rejects_model_ecosystem_packages(tmp_path: Path, name: str) -> None:
    _write_project(tmp_path, [f"{name}==1.0.0"], [name])
    policy = repo_root() / "docs" / "security" / "dependency-architecture-policy.json"
    destination = tmp_path / "docs" / "security" / "dependency-architecture-policy.json"
    destination.write_text(policy.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(DependencyPolicyError) as caught:
        validate_dependency_policy(tmp_path)
    assert caught.value.code == f"denied-dependency:{name}"


def test_dependency_policy_rejects_prohibited_names(tmp_path: Path) -> None:
    _write_project(tmp_path, ["torch==2.0.0"], ["torch"])
    with pytest.raises(DependencyPolicyError) as caught:
        validate_dependency_policy(tmp_path)
    assert caught.value.code == "denied-dependency:torch"


def test_dependency_policy_rejects_prefix_and_ignores_command_names(tmp_path: Path) -> None:
    _write_project(tmp_path, ["opentelemetry-sdk==1.0.0"], ["opentelemetry-sdk"])
    with pytest.raises(DependencyPolicyError) as caught:
        validate_dependency_policy(tmp_path)
    assert caught.value.code == "denied-dependency:opentelemetry-sdk"
    _write_project(
        tmp_path,
        ["jsonschema>=4"],
        ["jsonschema", "onnx-conversion-plan-validation"],
    )
    summary = validate_dependency_policy(tmp_path)
    assert summary["deniedCount"] == 0


def test_dependency_allow_entry_requires_a_spec_that_names_the_package(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        ["torch==2.0.0"],
        ["torch"],
        allow=[{"name": "jsonschema", "spec": "x"}],
    )
    with pytest.raises(DependencyPolicyError) as unrelated:
        validate_dependency_policy(tmp_path)
    assert unrelated.value.code == "allow-not-denied"
    _write_project(
        tmp_path,
        ["torch==2.0.0"],
        ["torch"],
        allow=[{"name": "torch", "spec": "missing.md"}],
    )
    with pytest.raises(DependencyPolicyError) as missing:
        validate_dependency_policy(tmp_path)
    assert missing.value.code == "allow-spec-missing"
    _write_project(
        tmp_path,
        ["torch==2.0.0"],
        ["torch"],
        allow=[{"name": "torch", "spec": "docs/specs/example.md"}],
        spec_text="This spec does not name the distribution.",
    )
    with pytest.raises(DependencyPolicyError) as unnamed:
        validate_dependency_policy(tmp_path)
    assert unnamed.value.code == "allow-spec-does-not-name-package"
    _write_project(
        tmp_path,
        ["torch==2.0.0"],
        ["torch"],
        allow=[{"name": "torch", "spec": "docs/specs/example.md"}],
        spec_text="The package torch stays unauthorized in this example.",
    )
    summary = validate_dependency_policy(tmp_path)
    assert summary["status"] == "ok"


def _run_block(lines: list[str]) -> str:
    text = (_FIXTURES / "valid-read-only.yml").read_text(encoding="utf-8")
    body = "\n".join(f"          {line}" for line in lines)
    return f"{text}      - name: Extra\n        run: |\n{body}\n"


def _local_use() -> str:
    text = (_FIXTURES / "valid-read-only.yml").read_text(encoding="utf-8")
    return text + "      - name: Local\n        uses: ./.github/actions/fetch\n"


def _writable_action(tmp_path: Path) -> Path:
    action = tmp_path / ".github" / "actions" / "fetch"
    action.mkdir(parents=True)
    (action / "action.yml").write_text(
        "runs:\n  using: composite\n  steps:\n    - run: echo ok\n",
        encoding="utf-8",
    )
    return action


def _runs(document: dict[str, object], job_id: str) -> str:
    jobs = document["jobs"]
    assert isinstance(jobs, dict)
    job = jobs[job_id]
    assert isinstance(job, dict)
    steps = job["steps"]
    assert isinstance(steps, list)
    return "\n".join(str(step["run"]) for step in steps if isinstance(step, dict) and "run" in step)


def _project_names(document: dict[str, object]) -> list[dict[str, object]]:
    jobs = document["jobs"]
    assert isinstance(jobs, dict)
    names = []
    for job in jobs.values():
        assert isinstance(job, dict)
        names.append(job)
    return names


def _write_project(
    root: Path,
    requirements: list[str],
    locked: list[str],
    allow: list[dict[str, str]] | None = None,
    spec_text: str | None = None,
) -> None:
    policy = {
        "schemaVersion": 1,
        "allow": [] if allow is None else allow,
        "denyExact": ["onnx", "torch"],
        "denyPrefixes": ["opentelemetry-"],
    }
    destination = root / "docs" / "security"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "dependency-architecture-policy.json").write_text(
        json.dumps(policy),
        encoding="utf-8",
    )
    joined = ", ".join(f'"{item}"' for item in requirements)
    (root / "pyproject.toml").write_text(
        "\n".join(
            (
                "[project]",
                'name = "example"',
                'version = "0.0.0"',
                'requires-python = ">=3.12,<3.13"',
                f"dependencies = [{joined}]",
                "",
                "[build-system]",
                'requires = ["setuptools"]',
                'build-backend = "setuptools.build_meta"',
                "",
            )
        ),
        encoding="utf-8",
    )
    packages = "\n".join(f'[[package]]\nname = "{name}"\nversion = "0.0.0"\n' for name in locked)
    (root / "uv.lock").write_text(f"version = 1\nrevision = 5\n\n{packages}", encoding="utf-8")
    if spec_text is not None:
        spec = root / "docs" / "specs" / "example.md"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text(spec_text, encoding="utf-8")
