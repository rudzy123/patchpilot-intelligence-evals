"""Validate workflow permissions, action pins, and the governance record.

The parser accepts the subset of YAML used by this repository's workflows.
It does not download an action or contact GitHub.
"""

from __future__ import annotations

import json
import os
import re
import stat
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.schemas import repo_root

_GOVERNANCE_PATH = Path("docs/operations/workflow-governance.json")
_PINS_PATH = Path("docs/provenance/github-action-pins.md")
_WORKFLOW_DIR = Path(".github/workflows")
_GROUP = (
    "${{ github.workflow }}-${{ github.event_name == 'pull_request' "
    "&& format('pr-{0}', github.event.pull_request.number) "
    "|| format('run-{0}', github.run_id) }}"
)
_CANCEL = "${{ github.event_name == 'pull_request' }}"
_USES = re.compile(r"^(?P<repo>[^/]+/[^/@]+)(?:/(?P<path>[^@]+))?@(?P<sha>[0-9a-f]{40})$")
_BLOCK = frozenset({"|", "|-", "|+", ">", ">-", ">+"})
_RAW_PROHIBITIONS = (
    ("pull-request-target", "pull_request_target"),
    ("merge-group", "merge_group"),
    ("conditional-execution", "continue-on-error"),
    ("prohibited-command", "upload-artifact"),
    ("prohibited-command", "actions/cache"),
    ("prohibited-command", "docker pull"),
    ("prohibited-command", "docker run"),
    ("prohibited-command", "podman pull"),
    ("prohibited-command", "podman run"),
    ("prohibited-command", "huggingface.co"),
    ("prohibited-command", "huggingface_hub"),
    ("prohibited-command", "modelscope"),
    ("prohibited-command", "ollama pull"),
    ("prohibited-command", "wget "),
    ("prohibited-command", "curl "),
    ("prohibited-command", "pip install"),
    ("prohibited-command", "pip3 install"),
    ("prohibited-command", "uv pip"),
    ("prohibited-command", "uv add"),
    ("prohibited-command", "uvx "),
    ("prohibited-command", "conda install"),
    ("prohibited-command", "mamba install"),
    ("prohibited-command", "gh release download"),
    ("publish-or-deploy", "docker/build-push-action"),
    ("publish-or-deploy", "softprops/action-gh-release"),
    ("publish-or-deploy", "peaceiris/actions-gh-pages"),
    ("publish-or-deploy", "gh release create"),
    ("prohibited-command", "aws-actions/"),
    ("token-exposure", "secrets."),
    ("token-exposure", "secrets["),
    ("token-exposure", "github.token"),
    ("token-exposure", "github["),
    ("token-exposure", "tojson(secrets)"),
    ("token-exposure", "tojson(github)"),
)
_DEPENDENCY_INPUTS = {
    "fail-on-severity": "high",
    "fail-on-scopes": "runtime, development, unknown",
    "comment-summary-in-pr": "never",
    "license-check": False,
    "vulnerability-check": True,
    "warn-only": False,
}
_CODEQL_INIT = {"languages": "python", "build-mode": "none"}
_CODEQL_ANALYZE = {"category": "/language:python"}
_SETUP_UV = {
    "version": "0.13.0",
    "python-version": "3.12",
    "enable-cache": False,
    "github-token": "",
}


class WorkflowPolicyError(ValueError):
    """A workflow or governance record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class _Line:
    indent: int
    text: str
    block_value: str | None = None


def classify_action(uses: str) -> str:
    """Return github, astral, repository-local, or third-party."""
    if uses.startswith("./"):
        return "repository-local"
    repository = _repository_name(uses)
    if repository.startswith("actions/") or repository.startswith("github/"):
        return "github"
    if repository == "astral-sh/setup-uv":
        return "astral"
    return "third-party"


def parse_workflow(text: str) -> dict[str, Any]:
    """Parse one workflow into mappings, lists, and scalars."""
    if "\t" in text:
        raise WorkflowPolicyError("workflow-yaml")
    lines = _logical_lines(text)
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    for index, line in enumerate(lines):
        while len(stack) > 1 and line.indent <= stack[-1][0]:
            stack.pop()
        container = stack[-1][1]
        if line.block_value is not None:
            if not isinstance(container, dict):
                raise WorkflowPolicyError("workflow-yaml")
            _assign(container, line.text, line.block_value)
            continue
        if line.text.startswith("- "):
            if not isinstance(container, list):
                raise WorkflowPolicyError("workflow-yaml")
            _append_item(stack, line, lines, index)
            continue
        if not isinstance(container, dict):
            raise WorkflowPolicyError("workflow-yaml")
        key, raw_value = _require_kv(line.text)
        if raw_value is None:
            child = _nested_child(lines, index)
            _assign(container, key, child)
            if isinstance(child, dict | list):
                stack.append((line.indent, child))
            continue
        _assign(container, key, _parse_scalar(raw_value))
    if not root:
        raise WorkflowPolicyError("workflow-yaml")
    return root


def validate_workflow_text(
    text: str,
    *,
    provenance: Sequence[Mapping[str, Any]],
    permissions: Mapping[str, str],
    timeouts: Mapping[str, int],
    require_name: str | None = None,
    source_root: Path | None = None,
) -> dict[str, Any]:
    """Apply the security rules to one workflow document."""
    _reject_raw(text)
    document = parse_workflow(text)
    _reject_run_fields(document)
    if require_name is not None and document.get("name") != require_name:
        raise WorkflowPolicyError("unstable-name")
    _check_permissions(document, permissions)
    _check_triggers(document)
    _check_jobs(document, timeouts)
    _check_uses(text, document, provenance, source_root)
    _check_concurrency(document)
    return {"status": "ok", "name": document.get("name"), "document": document}


def validate_workflow_policy(root: Path | None = None) -> dict[str, Any]:
    """Validate the committed workflows, pins, and governance record together."""
    base = root if root is not None else repo_root()
    expected = expected_governance()
    loaded = _load_governance(base)
    if loaded != expected:
        raise WorkflowPolicyError("governance-record")
    directory = base / _WORKFLOW_DIR
    found = sorted(path.relative_to(base).as_posix() for path in directory.glob("*.yml"))
    expected_paths = [str(item["path"]) for item in expected["workflows"]]
    if found != sorted(expected_paths):
        raise WorkflowPolicyError("unexpected-workflow")
    used: set[tuple[str, str, str]] = set()
    for workflow in expected["workflows"]:
        text = (base / str(workflow["path"])).read_text(encoding="utf-8")
        result = validate_workflow_text(
            text,
            provenance=expected["actions"],
            permissions=workflow["permissions"],
            timeouts={str(job["name"]): int(job["timeoutMinutes"]) for job in workflow["jobs"]},
            require_name=str(workflow["name"]),
            source_root=base,
        )
        projected = _project(result["document"])
        if projected != _expected_projection(workflow):
            raise WorkflowPolicyError("governance-record")
        used.update(_uses_in(result["document"]))
    expected_uses = {
        (str(item["repository"]), str(item["path"]), str(item["commitSha"]))
        for item in expected["actions"]
    }
    if used != expected_uses:
        raise WorkflowPolicyError("missing-provenance")
    pins = (base / _PINS_PATH).read_text(encoding="utf-8")
    for action in expected["actions"]:
        if str(action["commitSha"]) not in pins or str(action["reviewTag"]) not in pins:
            raise WorkflowPolicyError("missing-provenance")
        if str(action["repository"]) not in pins:
            raise WorkflowPolicyError("missing-provenance")
    return {
        "status": "ok",
        "workflowCount": len(expected["workflows"]),
        "actionPinCount": len(expected["actions"]),
        "rulesetApplicationStatus": "not-applied",
        "pullRequestObservationStatus": "not-observed",
        "productionReady": False,
    }


def expected_governance() -> dict[str, Any]:
    """Return the closed governance record this Session is allowed to publish."""
    return {
        "schemaVersion": 1,
        "recordId": "repository-hardening-1",
        "rulesetApplicationStatus": "not-applied",
        "pullRequestObservationStatus": "not-observed",
        "mergeQueue": "not-enabled",
        "classicBranchProtection": "absent",
        "observedCheckContexts": [],
        "intendedRequiredChecks": [
            _check(
                "Validation / Quality",
                ".github/workflows/validate.yml",
                "Validation",
                "quality",
                "Quality",
                ["pull_request", "push", "workflow_dispatch"],
            ),
            _check(
                "Validation / Tests",
                ".github/workflows/validate.yml",
                "Validation",
                "tests",
                "Tests",
                ["pull_request", "push", "workflow_dispatch"],
            ),
            _check(
                "Validation / Repository Contracts",
                ".github/workflows/validate.yml",
                "Validation",
                "repository-contracts",
                "Repository Contracts",
                ["pull_request", "push", "workflow_dispatch"],
            ),
            _check(
                "CodeQL / Analyze",
                ".github/workflows/codeql.yml",
                "CodeQL",
                "analyze",
                "Analyze",
                ["pull_request", "push", "schedule", "workflow_dispatch"],
            ),
            _check(
                "Dependency Review / Dependency Review",
                ".github/workflows/dependency-review.yml",
                "Dependency Review",
                "dependency-review",
                "Dependency Review",
                ["pull_request"],
            ),
        ],
        "currentRuleset": {
            "id": 26864084,
            "name": "Require validation",
            "enforcement": "active",
            "target": "~DEFAULT_BRANCH",
            "requiredCheckContext": "validate",
            "observedCheckRunName": "validate",
            "strictRequiredStatusChecks": False,
            "dismissStaleReviews": False,
            "conversationResolution": True,
            "deletionBlocked": True,
            "forcePushBlocked": True,
            "linearHistory": "not-required",
            "bypassActors": [],
            "approvingReviewCount": 0,
            "allowedMergeMethods": ["merge", "squash", "rebase"],
            "doNotEnforceOnCreate": True,
            "htmlUrl": "https://github.com/rudzy123/patchpilot-intelligence-evals/rules/26864084",
        },
        "operatorChanges": [
            "Set strict_required_status_checks_policy to true after observed check names exist.",
            "Set dismiss_stale_reviews_on_push to true.",
            "Replace the required context validate with the observed check-run names.",
            "Do not enable required_linear_history.",
            "Do not enable merge_queue.",
            "Do not add bypass actors.",
        ],
        "workflows": [
            _workflow(
                "validation",
                ".github/workflows/validate.yml",
                "Validation",
                {
                    "pull_request": {"branches": ["main"]},
                    "push": {"branches": ["main"]},
                    "workflow_dispatch": None,
                },
                {"contents": "read"},
                [
                    ("quality", "Quality", 15),
                    ("tests", "Tests", 30),
                    ("repository-contracts", "Repository Contracts", 30),
                ],
            ),
            _workflow(
                "codeql",
                ".github/workflows/codeql.yml",
                "CodeQL",
                {
                    "pull_request": {"branches": ["main"]},
                    "push": {"branches": ["main"]},
                    "schedule": [{"cron": "17 6 * * 1"}],
                    "workflow_dispatch": None,
                },
                {"contents": "read", "security-events": "write"},
                [("analyze", "Analyze", 30)],
            ),
            _workflow(
                "dependency-review",
                ".github/workflows/dependency-review.yml",
                "Dependency Review",
                {"pull_request": {"branches": ["main"]}},
                {"contents": "read"},
                [("dependency-review", "Dependency Review", 15)],
            ),
        ],
        "actions": [
            _action(
                "actions/checkout",
                "",
                "v7.0.1",
                "3d3c42e5aac5ba805825da76410c181273ba90b1",
                "https://github.com/actions/checkout",
                "Check out the repository without persisting credentials.",
                "github",
                "lightweight",
            ),
            _action(
                "astral-sh/setup-uv",
                "",
                "v10.3.3",
                "68559e99cc807c1eb7e9238fd43a15bba460eec2",
                "https://github.com/astral-sh/setup-uv",
                "Install uv 0.13.0 and select Python 3.12 without a dependency cache.",
                "astral",
                "lightweight",
            ),
            _action(
                "github/codeql-action",
                "init",
                "v4.39.3",
                "33d7b85da1a04171e211befe2c739303b9a4c066",
                "https://github.com/github/codeql-action",
                "Initialize Python CodeQL with build-mode none.",
                "github",
                "annotated",
            ),
            _action(
                "github/codeql-action",
                "analyze",
                "v4.39.3",
                "33d7b85da1a04171e211befe2c739303b9a4c066",
                "https://github.com/github/codeql-action",
                "Analyze Python and upload code-scanning results.",
                "github",
                "annotated",
            ),
            _action(
                "actions/dependency-review-action",
                "",
                "v5.0.0",
                "a1d282b36b6f3519aa1f3fc636f609c47dddb294",
                "https://github.com/actions/dependency-review-action",
                "Fail a pull request on high or critical dependency advisories.",
                "github",
                "lightweight",
            ),
        ],
        "manualOperatorSteps": [
            "Open the hardening pull request and wait for the new check runs.",
            "Read check-run names from the commits API before choosing ruleset contexts.",
            "Edit ruleset 26864084 only. Do not create a second ruleset.",
            "Replace context validate with the observed names.",
            "Enable strict up-to-date checks and stale review dismissal.",
            "Keep pull requests, conversation resolution, and deletion blocking.",
            "Keep force-push blocking and an empty bypass list.",
            "Leave the approving review count at 0 and keep the current merge methods.",
            "Do not enable linear history or a merge queue.",
            "Read the branch rules back before merging.",
            "Leave rulesetApplicationStatus at not-applied until a later reviewed record.",
        ],
    }


def _check(
    context: str,
    path: str,
    workflow_name: str,
    job_id: str,
    job_name: str,
    events: list[str],
) -> dict[str, Any]:
    return {
        "context": context,
        "workflowPath": path,
        "workflowName": workflow_name,
        "jobId": job_id,
        "jobName": job_name,
        "status": "required",
        "applicableEvents": events,
    }


def _workflow(
    workflow_id: str,
    path: str,
    name: str,
    triggers: dict[str, Any],
    permissions: dict[str, str],
    jobs: list[tuple[str, str, int]],
) -> dict[str, Any]:
    return {
        "id": workflow_id,
        "path": path,
        "name": name,
        "implementationStatus": "implemented",
        "observedOnPullRequest": False,
        "triggers": triggers,
        "permissions": permissions,
        "concurrency": {"group": _GROUP, "cancelInProgress": _CANCEL},
        "jobs": [
            {"id": job_id, "name": job_name, "timeoutMinutes": timeout}
            for job_id, job_name, timeout in jobs
        ],
        "requiredStatus": "required",
    }


def _action(
    repository: str,
    path: str,
    review_tag: str,
    commit_sha: str,
    source: str,
    purpose: str,
    author_class: str,
    tag_kind: str,
) -> dict[str, Any]:
    return {
        "repository": repository,
        "path": path,
        "reviewTag": review_tag,
        "commitSha": commit_sha,
        "officialSource": source,
        "retrievalDate": "2026-11-11",
        "license": "MIT",
        "purpose": purpose,
        "authorClass": author_class,
        "tagKind": tag_kind,
    }


def _load_governance(root: Path) -> dict[str, Any]:
    path = root / _GOVERNANCE_PATH
    if not path.is_file():
        raise WorkflowPolicyError("governance-record")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise WorkflowPolicyError("governance-record")
    return loaded


def _expected_projection(workflow: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": workflow["name"],
        "triggers": workflow["triggers"],
        "permissions": workflow["permissions"],
        "concurrency": workflow["concurrency"],
        "jobs": workflow["jobs"],
    }


def _project(document: Mapping[str, Any]) -> dict[str, Any]:
    jobs = document.get("jobs")
    if not isinstance(jobs, dict):
        raise WorkflowPolicyError("workflow-yaml")
    projected_jobs = []
    for job_id, job in jobs.items():
        if not isinstance(job, dict) or not isinstance(job.get("name"), str):
            raise WorkflowPolicyError("unstable-name")
        timeout = job.get("timeout-minutes")
        if isinstance(timeout, bool) or not isinstance(timeout, int):
            raise WorkflowPolicyError("missing-timeout")
        projected_jobs.append({"id": job_id, "name": job["name"], "timeoutMinutes": timeout})
    concurrency = document.get("concurrency")
    if not isinstance(concurrency, dict):
        raise WorkflowPolicyError("concurrency")
    return {
        "name": document.get("name"),
        "triggers": document.get("on"),
        "permissions": document.get("permissions"),
        "concurrency": {
            "group": concurrency.get("group"),
            "cancelInProgress": concurrency.get("cancel-in-progress"),
        },
        "jobs": projected_jobs,
    }


def _uses_in(document: Mapping[str, Any]) -> set[tuple[str, str, str]]:
    found: set[tuple[str, str, str]] = set()
    jobs = document.get("jobs")
    if not isinstance(jobs, dict):
        return found
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if isinstance(step, dict) and isinstance(step.get("uses"), str):
                parsed = _USES.fullmatch(str(step["uses"]))
                if parsed is None:
                    continue
                found.add((parsed.group("repo"), parsed.group("path") or "", parsed.group("sha")))
    return found


def _reject_raw(text: str) -> None:
    lowered = _command_text(text)
    for code, needle in _RAW_PROHIBITIONS:
        if needle in lowered:
            raise WorkflowPolicyError(code)


def _command_text(text: str) -> str:
    """Delete POSIX backslash-newline pairs without inserting whitespace.

    A backslash immediately followed by LF or CRLF is removed together with
    that break. A final backslash with no following newline stays. Other
    whitespace is unchanged. The result is a literal string, not a shell parse:
    quotes, parameter expansion, command substitution, aliases, and encodings
    are left as written.
    """
    return re.sub(r"\\\r?\n", "", text.lower())


def _reject_run_fields(node: object) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "run" and isinstance(value, str):
                _reject_raw(value)
            else:
                _reject_run_fields(value)
        return
    if isinstance(node, list):
        for item in node:
            _reject_run_fields(item)


def _check_permissions(document: Mapping[str, Any], expected: Mapping[str, str]) -> None:
    permissions = document.get("permissions")
    if not isinstance(permissions, dict) or not permissions:
        raise WorkflowPolicyError("missing-permissions")
    if dict(permissions) != dict(expected):
        raise WorkflowPolicyError("broad-permissions")
    jobs = document.get("jobs")
    if not isinstance(jobs, dict):
        raise WorkflowPolicyError("workflow-yaml")
    for job in jobs.values():
        if isinstance(job, dict) and "permissions" in job:
            raise WorkflowPolicyError("job-permissions")


def _check_triggers(document: Mapping[str, Any]) -> None:
    triggers = document.get("on")
    if not isinstance(triggers, dict):
        raise WorkflowPolicyError("trigger")
    if "pull_request_target" in triggers:
        raise WorkflowPolicyError("pull-request-target")
    if "merge_group" in triggers:
        raise WorkflowPolicyError("merge-group")
    _reject_path_filters(triggers)
    for name in ("pull_request", "push"):
        if name not in triggers:
            continue
        body = triggers[name]
        if not isinstance(body, dict) or body.get("branches") != ["main"]:
            raise WorkflowPolicyError("trigger")


def _reject_path_filters(node: object) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in {"paths", "paths-ignore"}:
                raise WorkflowPolicyError("path-filter")
            _reject_path_filters(value)
    elif isinstance(node, list):
        for item in node:
            _reject_path_filters(item)


def _check_jobs(document: Mapping[str, Any], timeouts: Mapping[str, int]) -> None:
    jobs = document.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        raise WorkflowPolicyError("workflow-yaml")
    if "container" in document or "services" in document:
        raise WorkflowPolicyError("container")
    seen: list[str] = []
    for job in jobs.values():
        if not isinstance(job, dict):
            raise WorkflowPolicyError("workflow-yaml")
        if job.get("runs-on") != "ubuntu-latest" or "container" in job or "services" in job:
            raise WorkflowPolicyError("container")
        if "strategy" in job:
            raise WorkflowPolicyError("matrix-or-strategy")
        name = job.get("name")
        if not isinstance(name, str) or name not in timeouts:
            raise WorkflowPolicyError("unexpected-job")
        seen.append(name)
        if "if" in job or "continue-on-error" in job:
            raise WorkflowPolicyError("conditional-execution")
        timeout = job.get("timeout-minutes")
        if isinstance(timeout, bool) or not isinstance(timeout, int):
            raise WorkflowPolicyError("missing-timeout")
        if timeout > timeouts[name]:
            raise WorkflowPolicyError("excessive-timeout")
        if timeout < 1:
            raise WorkflowPolicyError("missing-timeout")
        steps = job.get("steps")
        if not isinstance(steps, list) or not steps:
            raise WorkflowPolicyError("workflow-yaml")
        for step in steps:
            if not isinstance(step, dict):
                raise WorkflowPolicyError("workflow-yaml")
            if "if" in step or "continue-on-error" in step:
                raise WorkflowPolicyError("conditional-execution")
    if seen != list(timeouts):
        raise WorkflowPolicyError("unexpected-job")


def _check_concurrency(document: Mapping[str, Any]) -> None:
    concurrency = document.get("concurrency")
    triggers = document.get("on")
    if not isinstance(concurrency, dict) or not isinstance(triggers, dict):
        raise WorkflowPolicyError("concurrency")
    if concurrency.get("group") != _GROUP:
        raise WorkflowPolicyError("concurrency")
    cancel = concurrency.get("cancel-in-progress")
    if cancel == _CANCEL:
        return
    if cancel is True and set(triggers) == {"pull_request"}:
        return
    raise WorkflowPolicyError("concurrency")


def _check_uses(
    text: str,
    document: Mapping[str, Any],
    provenance: Sequence[Mapping[str, Any]],
    source_root: Path | None,
) -> None:
    parsed_uses = _ordered_uses(document)
    raw_uses = _raw_uses(text)
    if parsed_uses != raw_uses:
        raise WorkflowPolicyError("workflow-yaml")
    known = {
        (str(item["repository"]), str(item["path"]), str(item["commitSha"])): item
        for item in provenance
    }
    seen: set[Path] = set()
    for uses in parsed_uses:
        _check_one_use(text, uses, known, source_root, seen)


def _check_one_use(
    text: str,
    uses: str,
    known: Mapping[tuple[str, str, str], Mapping[str, Any]],
    source_root: Path | None,
    seen: set[Path],
) -> None:
    if uses.startswith("docker://"):
        raise WorkflowPolicyError("container")
    if uses.startswith("./"):
        if "@" in uses or ".." in uses:
            raise WorkflowPolicyError("unpinned-action")
        if source_root is None:
            raise WorkflowPolicyError("missing-local-action")
        _scan_local_action(source_root, uses, known, seen)
        return
    match = _USES.fullmatch(uses)
    if match is None:
        raise WorkflowPolicyError("unpinned-action")
    identity = (match.group("repo"), match.group("path") or "", match.group("sha"))
    record = known.get(identity)
    if record is None:
        raise WorkflowPolicyError("missing-provenance")
    if classify_action(uses) != record["authorClass"]:
        raise WorkflowPolicyError("missing-provenance")
    review_tag = str(record["reviewTag"])
    if f"uses: {uses} # {review_tag}" not in text:
        raise WorkflowPolicyError("unlabeled-pin")


def _scan_local_action(
    base: Path,
    uses: str,
    known: Mapping[tuple[str, str, str], Mapping[str, Any]],
    seen: set[Path],
) -> None:
    location = _local_action_root(base, uses)
    if location in seen:
        return
    seen.add(location)
    files = _local_action_files(location)
    for file in files:
        body = _read_local_text(location, file)
        _reject_raw(body)
        if file.name in {"action.yml", "action.yaml"}:
            _reject_run_fields(parse_workflow(body))
        for nested in _raw_uses(body):
            _check_one_use(body, nested, known, base, seen)


def _local_action_root(base: Path, uses: str) -> Path:
    relative = Path(uses[2:])
    if relative.is_absolute() or ".." in relative.parts or relative.parts in ((), (".",)):
        raise WorkflowPolicyError("unpinned-action")
    location = (base / relative).resolve()
    try:
        location.relative_to(base.resolve())
    except ValueError as exc:
        raise WorkflowPolicyError("unpinned-action") from exc
    if location == base.resolve():
        raise WorkflowPolicyError("unpinned-action")
    if location.is_file() or (location.is_dir() and _action_entry(location) is not None):
        return location
    raise WorkflowPolicyError("missing-local-action")


def _local_action_files(location: Path) -> list[Path]:
    """Return regular files under one action, in sorted walk order.

    Every directory is listed. An unreadable, dangling, or escaping path fails
    closed. FIFOs and other non-regular files are rejected.
    """
    files: list[Path] = []
    _classify(location.resolve(), location, files, set())
    return files


def _classify(
    root: Path,
    path: Path,
    files: list[Path],
    seen_dirs: set[tuple[int, int]],
) -> None:
    info = _lstat(path)
    if stat.S_ISLNK(info.st_mode):
        _classify(root, _inside(root, path), files, seen_dirs)
        return
    if stat.S_ISDIR(info.st_mode):
        _walk_directory(root, path, files, seen_dirs)
        return
    if stat.S_ISREG(info.st_mode):
        files.append(path)
        return
    raise WorkflowPolicyError("unsupported-local-action-file")


def _walk_directory(
    root: Path,
    directory: Path,
    files: list[Path],
    seen_dirs: set[tuple[int, int]],
) -> None:
    info = _lstat(directory)
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise WorkflowPolicyError("unreadable-local-action")
    identity = (info.st_dev, info.st_ino)
    if identity in seen_dirs:
        return
    seen_dirs.add(identity)
    for name in _list_directory(directory):
        _classify(root, directory / name, files, seen_dirs)


def _list_directory(directory: Path) -> list[str]:
    names: list[str] = []
    try:
        with os.scandir(directory) as scan:
            for entry in scan:
                names.append(entry.name)
    except OSError as exc:
        raise WorkflowPolicyError("unreadable-local-action") from exc
    names.sort()
    return names


def _lstat(path: Path) -> os.stat_result:
    try:
        return os.lstat(path)
    except OSError as exc:
        raise WorkflowPolicyError("unreadable-local-action") from exc


def _inside(root: Path, path: Path) -> Path:
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise WorkflowPolicyError("unreadable-local-action") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorkflowPolicyError("unreadable-local-action") from exc
    return resolved


def _read_local_text(root: Path, path: Path) -> str:
    checked = _inside(root, path)
    info = _lstat(checked)
    if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise WorkflowPolicyError("unsupported-local-action-file")
    try:
        with open(checked, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        raise WorkflowPolicyError("unreadable-local-action") from exc
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WorkflowPolicyError("unreadable-local-action") from exc


def _action_entry(location: Path) -> Path | None:
    for name in ("action.yml", "action.yaml"):
        candidate = location / name
        if candidate.is_file():
            return candidate
    return None


def _ordered_uses(document: Mapping[str, Any]) -> list[str]:
    jobs = document.get("jobs")
    if not isinstance(jobs, dict):
        raise WorkflowPolicyError("workflow-yaml")
    found: list[str] = []
    for job in jobs.values():
        if not isinstance(job, dict):
            raise WorkflowPolicyError("workflow-yaml")
        steps = job.get("steps")
        if not isinstance(steps, list):
            raise WorkflowPolicyError("workflow-yaml")
        for step in steps:
            if not isinstance(step, dict):
                raise WorkflowPolicyError("workflow-yaml")
            uses = step.get("uses")
            if uses is None:
                continue
            if not isinstance(uses, str):
                raise WorkflowPolicyError("unpinned-action")
            found.append(uses)
            _check_step_inputs(uses, step.get("with"))
    return found


def _check_step_inputs(uses: str, inputs: object) -> None:
    if uses.startswith("docker://"):
        raise WorkflowPolicyError("container")
    if uses.startswith("./"):
        return
    match = _USES.fullmatch(uses)
    if match is None:
        return
    repository = match.group("repo")
    path = match.group("path") or ""
    if repository == "actions/checkout":
        if not isinstance(inputs, dict) or inputs.get("persist-credentials") is not False:
            raise WorkflowPolicyError("persisted-credentials")
        if "token" in inputs:
            raise WorkflowPolicyError("token-exposure")
        return
    if repository == "astral-sh/setup-uv":
        if not isinstance(inputs, dict):
            raise WorkflowPolicyError("cache-enabled")
        for key, value in _SETUP_UV.items():
            if inputs.get(key) != value:
                raise WorkflowPolicyError("cache-enabled")
        return
    if repository == "github/codeql-action" and path == "autobuild":
        raise WorkflowPolicyError("codeql-autobuild")
    if repository == "github/codeql-action" and path == "init":
        if not isinstance(inputs, dict) or dict(inputs) != _CODEQL_INIT:
            raise WorkflowPolicyError("codeql-config")
        return
    if repository == "github/codeql-action" and path == "analyze":
        if not isinstance(inputs, dict) or dict(inputs) != _CODEQL_ANALYZE:
            raise WorkflowPolicyError("codeql-config")
        return
    if repository == "actions/dependency-review-action":
        if not isinstance(inputs, dict) or dict(inputs) != _DEPENDENCY_INPUTS:
            raise WorkflowPolicyError("dependency-review-policy")


def _raw_uses(text: str) -> list[str]:
    found: list[str] = []
    for raw_line in text.splitlines():
        content = _strip_comment(raw_line).strip()
        if content.startswith("- "):
            content = content[2:].strip()
        split = _split_kv(content)
        if split is None or split[0] != "uses" or split[1] is None:
            continue
        scalar = _parse_scalar(split[1])
        if not isinstance(scalar, str):
            raise WorkflowPolicyError("unpinned-action")
        found.append(scalar)
    return found


def _logical_lines(text: str) -> list[_Line]:
    raw_lines = text.splitlines()
    lines: list[_Line] = []
    index = 0
    while index < len(raw_lines):
        raw_line = raw_lines[index]
        if not raw_line.strip() or raw_line.lstrip(" ").startswith("#"):
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        content = _strip_comment(raw_line).strip()
        split = _split_kv(content)
        if split is not None and split[1] in _BLOCK:
            block: list[str] = []
            index += 1
            while index < len(raw_lines):
                nxt = raw_lines[index]
                if nxt.strip() == "":
                    block.append("")
                    index += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                if nxt_indent <= indent:
                    break
                block.append(nxt.strip())
                index += 1
            lines.append(_Line(indent, split[0], "\n".join(block).strip()))
            continue
        lines.append(_Line(indent, content))
        index += 1
    return lines


def _append_item(stack: list[tuple[int, Any]], line: _Line, lines: list[_Line], index: int) -> None:
    container = stack[-1][1]
    item_text = line.text[2:].strip()
    if item_text == "":
        child = _nested_child(lines, index)
        if not isinstance(child, dict | list):
            raise WorkflowPolicyError("workflow-yaml")
        container.append(child)
        stack.append((line.indent, child))
        return
    split = _split_kv(item_text)
    if split is None:
        container.append(_parse_scalar(item_text))
        return
    key, raw_value = split
    item: dict[str, Any] = {}
    container.append(item)
    if raw_value is None:
        child = _nested_child(lines, index)
        item[key] = child
        stack.append((line.indent, item))
        if isinstance(child, dict | list) and index + 1 < len(lines):
            stack.append((lines[index + 1].indent - 1, child))
        return
    item[key] = _parse_scalar(raw_value)
    stack.append((line.indent, item))


def _nested_child(lines: list[_Line], index: int) -> Any:
    if index + 1 >= len(lines) or lines[index + 1].indent <= lines[index].indent:
        return None
    nxt = lines[index + 1]
    if nxt.block_value is not None or not nxt.text.startswith("- "):
        return {}
    return []


def _assign(container: dict[str, Any], key: str, value: Any) -> None:
    if key in container:
        raise WorkflowPolicyError("workflow-yaml")
    container[key] = value


def _require_kv(text: str) -> tuple[str, str | None]:
    split = _split_kv(text)
    if split is None:
        raise WorkflowPolicyError("workflow-yaml")
    return split


def _split_kv(text: str) -> tuple[str, str | None] | None:
    in_single = False
    in_double = False
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_double:
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if char != ":" or in_single or in_double:
            continue
        remainder = text[index + 1 :]
        if remainder != "" and not remainder.startswith(" "):
            return None
        key = text[:index].strip()
        if key == "" or " " in key:
            return None
        value = remainder.strip()
        return key, None if value == "" else value
    return None


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_double:
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if char == "#" and not in_single and not in_double:
            return line[:index].rstrip()
    return line.rstrip()


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return _unquote(value)
    if value.startswith("[") and value.endswith("]"):
        return [_parse_scalar(part) for part in _split_csv(value[1:-1])]
    if value.startswith("{") and not value.startswith("${{"):
        raise WorkflowPolicyError("workflow-yaml")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _unquote(value: str) -> str:
    inner = value[1:-1]
    if value[0] == "'":
        return inner.replace("''", "'")
    return inner.replace('\\"', '"').replace("\\\\", "\\")


def _split_csv(value: str) -> list[str]:
    if value.strip() == "":
        return []
    parts: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    for char in value:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        if char == "," and not in_single and not in_double:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    parts.append("".join(current).strip())
    return parts


def _repository_name(uses: str) -> str:
    base = uses.split("@", 1)[0]
    parts = base.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise WorkflowPolicyError("unpinned-action")
    return f"{parts[0]}/{parts[1]}"
