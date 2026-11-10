"""Network, environment, and credential policy for the hardened boundary.

Outbound denial is a Linux network namespace. The in-process socket hook is
not this control.
"""

from __future__ import annotations

NAMESPACE_ARGUMENTS: tuple[str, ...] = (
    "--unshare-user",
    "--unshare-pid",
    "--unshare-ipc",
    "--unshare-uts",
    "--unshare-net",
    "--unshare-cgroup",
    "--die-with-parent",
    "--new-session",
    "--hostname",
    "sandbox",
    "--chdir",
    "/results",
    "--clearenv",
)

CONSTRUCTED_ENVIRONMENT: tuple[tuple[str, str], ...] = (
    ("PATH", "/opt/runtime/bin:/usr/bin"),
    ("PYTHONHOME", "/opt/runtime"),
    ("LANG", "C.UTF-8"),
    ("LC_ALL", "C.UTF-8"),
    ("PYTHONDONTWRITEBYTECODE", "1"),
    ("PYTHONIOENCODING", "utf-8"),
    ("PYTHONUTF8", "1"),
)

ALLOWED_ENVIRONMENT: frozenset[str] = frozenset(
    {key for key, _value in CONSTRUCTED_ENVIRONMENT} | {"PWD"}
)

DENIED_ENVIRONMENT_NAMES: tuple[str, ...] = (
    "HOME",
    "SSH_AUTH_SOCK",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AZURE_CLIENT_SECRET",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "KUBECONFIG",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "GIT_ASKPASS",
    "NPM_TOKEN",
)


def namespace_arguments() -> list[str]:
    """Return the bubblewrap namespace and environment arguments."""
    return [*NAMESPACE_ARGUMENTS, *environment_arguments()]


def environment_arguments() -> list[str]:
    """Return ``--setenv`` arguments for the constructed allowlist."""
    arguments: list[str] = []
    for key, value in CONSTRUCTED_ENVIRONMENT:
        arguments.extend(["--setenv", key, value])
    return arguments


def environment_is_minimal(names: list[str] | tuple[str, ...]) -> bool:
    """Return whether a child environment contains only constructed names."""
    return set(names) <= ALLOWED_ENVIRONMENT and "HOME" not in names
