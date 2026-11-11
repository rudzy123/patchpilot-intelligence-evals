"""Fail closed when a dependency matches a prohibited architecture category.

The check reads the committed policy, pyproject.toml, and uv.lock. It does not
install a package or contact a model hub.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.schemas import repo_root

_POLICY_PATH = Path("docs/security/dependency-architecture-policy.json")
_POLICY_KEYS = frozenset({"schemaVersion", "allow", "denyExact", "denyPrefixes"})
_ALLOW_KEYS = frozenset({"name", "spec"})
_NAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")


class DependencyPolicyError(ValueError):
    """A dependency or policy record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def normalize_name(name: str) -> str:
    """Return the PEP 503 normalized distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def validate_dependency_policy(root: Path | None = None) -> dict[str, Any]:
    """Scan direct and locked distributions against the committed deny list."""
    base = root if root is not None else repo_root()
    policy = _load_policy(base)
    names = _project_names(base) | _lock_names(base)
    allowed = _allowed_names(base, policy)
    denied = sorted(name for name in names if _is_denied(name, policy) and name not in allowed)
    if denied:
        raise DependencyPolicyError(f"denied-dependency:{denied[0]}")
    return {
        "status": "ok",
        "packageCount": len(names),
        "deniedCount": 0,
        "productionReady": False,
    }


def _load_policy(root: Path) -> dict[str, Any]:
    path = root / _POLICY_PATH
    if not path.is_file():
        raise DependencyPolicyError("missing-policy")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or set(loaded) != _POLICY_KEYS:
        raise DependencyPolicyError("policy-schema")
    if loaded["schemaVersion"] != 1:
        raise DependencyPolicyError("policy-schema")
    allow = loaded["allow"]
    exact = loaded["denyExact"]
    prefixes = loaded["denyPrefixes"]
    if not isinstance(allow, list) or not isinstance(exact, list) or not isinstance(prefixes, list):
        raise DependencyPolicyError("policy-schema")
    if not exact or not prefixes:
        raise DependencyPolicyError("policy-schema")
    normalized_exact: list[str] = []
    for item in exact:
        if not isinstance(item, str):
            raise DependencyPolicyError("policy-schema")
        normalized = normalize_name(item)
        if normalized != item or normalized in normalized_exact:
            raise DependencyPolicyError("policy-schema")
        normalized_exact.append(normalized)
    normalized_prefixes: list[str] = []
    for item in prefixes:
        if not isinstance(item, str):
            raise DependencyPolicyError("policy-schema")
        normalized = normalize_name(item)
        if normalized != item or len(normalized) < 8 or not normalized.endswith("-"):
            raise DependencyPolicyError("policy-schema")
        if normalized in normalized_prefixes:
            raise DependencyPolicyError("policy-schema")
        normalized_prefixes.append(normalized)
    for entry in allow:
        if not isinstance(entry, dict) or set(entry) != _ALLOW_KEYS:
            raise DependencyPolicyError("policy-schema")
        if not isinstance(entry["name"], str) or normalize_name(entry["name"]) != entry["name"]:
            raise DependencyPolicyError("policy-schema")
        if entry["name"] not in normalized_exact and not any(
            entry["name"].startswith(prefix) for prefix in normalized_prefixes
        ):
            raise DependencyPolicyError("allow-not-denied")
        if not isinstance(entry["spec"], str):
            raise DependencyPolicyError("policy-schema")
    return loaded


def _allowed_names(root: Path, policy: dict[str, Any]) -> set[str]:
    allowed: set[str] = set()
    for entry in policy["allow"]:
        name = str(entry["name"])
        relative = str(entry["spec"])
        if relative.startswith("/") or ".." in Path(relative).parts:
            raise DependencyPolicyError("allow-spec-missing")
        spec_path = root / relative
        if not spec_path.is_file():
            raise DependencyPolicyError("allow-spec-missing")
        try:
            spec_path.resolve().relative_to(root.resolve())
        except ValueError as exc:
            raise DependencyPolicyError("allow-spec-missing") from exc
        text = spec_path.read_text(encoding="utf-8").lower()
        if not re.search(rf"(?<![a-z0-9]){re.escape(name)}(?![a-z0-9])", text):
            raise DependencyPolicyError("allow-spec-does-not-name-package")
        allowed.add(name)
    return allowed


def _is_denied(name: str, policy: dict[str, Any]) -> bool:
    if name in policy["denyExact"]:
        return True
    return any(name.startswith(prefix) for prefix in policy["denyPrefixes"])


def _project_names(root: Path) -> set[str]:
    path = root / "pyproject.toml"
    if not path.is_file():
        raise DependencyPolicyError("missing-project")
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    requirements: list[str] = []
    project = document.get("project", {})
    if isinstance(project, dict):
        _take_requirements(requirements, project.get("dependencies"))
        optional = project.get("optional-dependencies", {})
        if isinstance(optional, dict):
            for value in optional.values():
                _take_requirements(requirements, value)
    groups = document.get("dependency-groups", {})
    if isinstance(groups, dict):
        for value in groups.values():
            _take_requirements(requirements, value)
    build = document.get("build-system", {})
    if isinstance(build, dict):
        _take_requirements(requirements, build.get("requires"))
    tool = document.get("tool", {})
    if isinstance(tool, dict):
        uv_tool = tool.get("uv", {})
        if isinstance(uv_tool, dict):
            for key in ("dev-dependencies", "constraint-dependencies", "override-dependencies"):
                _take_requirements(requirements, uv_tool.get(key))
    return {_distribution_name(item) for item in requirements}


def _lock_names(root: Path) -> set[str]:
    path = root / "uv.lock"
    if not path.is_file():
        raise DependencyPolicyError("missing-lock")
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    packages = document.get("package")
    if not isinstance(packages, list):
        raise DependencyPolicyError("lock-packages")
    names: set[str] = set()
    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("name"), str):
            raise DependencyPolicyError("lock-packages")
        names.add(normalize_name(str(package["name"])))
    if not names:
        raise DependencyPolicyError("lock-packages")
    return names


def _take_requirements(destination: list[str], value: object) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        raise DependencyPolicyError("project-requirements")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise DependencyPolicyError("project-requirements")
        destination.append(item)


def _distribution_name(requirement: str) -> str:
    token = requirement.split(";", 1)[0].strip()
    token = re.split(r"[<>=!~\s\[]", token, maxsplit=1)[0]
    if not _NAME.fullmatch(token):
        raise DependencyPolicyError("project-requirements")
    return normalize_name(token)
