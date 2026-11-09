"""In-process network and path hooks. These tests do not open sibling repositories."""

from __future__ import annotations

import socket
from urllib import request as urllib_request

import pytest

from patchpilot_intelligence_evals.network_guard import (
    BoundaryError,
    NetworkProhibited,
    assert_inside_repository,
    network_guard,
    read_allowed_env,
)
from patchpilot_intelligence_evals.schemas import SCHEMA_NAMES, load_schema, repo_root


def test_socket_dns_and_url_hooks_fail_closed() -> None:
    with network_guard():
        with pytest.raises(NetworkProhibited):
            socket.socket()
        with pytest.raises(NetworkProhibited):
            socket.getaddrinfo("example.invalid", 443)
        with pytest.raises(NetworkProhibited):
            urllib_request.urlopen("https://example.invalid/synthetic")
        for name in SCHEMA_NAMES:
            assert load_schema(name)["$id"].startswith("urn:")


def test_hooks_restore_after_exit() -> None:
    original = socket.socket
    with network_guard():
        with pytest.raises(NetworkProhibited):
            socket.socket()
    assert socket.socket is original


def test_sibling_paths_are_rejected_lexically() -> None:
    root = repo_root()
    with pytest.raises(BoundaryError):
        assert_inside_repository("../patchpilot", root)
    with pytest.raises(BoundaryError):
        assert_inside_repository("../neural-from-scratch/notebook.ipynb", root)
    with pytest.raises(BoundaryError):
        assert_inside_repository("/etc/passwd", root)
    assert_inside_repository("corpus/manifest.json", root)


def test_environment_allowlist_rejects_provider_names() -> None:
    with pytest.raises(BoundaryError):
        read_allowed_env("AWS_SECRET_ACCESS_KEY")
    with pytest.raises(BoundaryError):
        read_allowed_env("OPENAI_API_KEY")
    value = read_allowed_env("PATH")
    assert value is None or isinstance(value, str)
