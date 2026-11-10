"""Filesystem hiding inside the hardened boundary."""

from __future__ import annotations

import json
import shutil
import socket
import tempfile
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.filesystem_policy import (
    FilesystemPolicyError,
    Mount,
    assert_mounts_safe,
)
from patchpilot_intelligence_evals.hardened_execution import (
    execute_hardened,
    host_supports_boundary,
)
from patchpilot_intelligence_evals.schemas import repo_root

_FIXTURE = repo_root() / "tests" / "sandbox_fixtures" / "fs_visibility.py"
_SENTINEL = "synthetic-sentinel"


def _require_boundary() -> None:
    if not host_supports_boundary():
        pytest.skip("unsupported-capability")


def test_home_mounts_are_rejected() -> None:
    with pytest.raises(FilesystemPolicyError) as caught:
        assert_mounts_safe((Mount("/tmp/patchpilot-safe", "/home/operator", True),))
    assert caught.value.code == "identity-path"


def test_visibility_hides_synthetic_sentinels() -> None:
    _require_boundary()
    root = Path(tempfile.mkdtemp(prefix="patchpilot-fs-", dir="/tmp"))
    try:
        hidden = root / "hidden"
        for relative in (
            "gold/marker",
            "prior/marker",
            "siblings/patchpilot/marker",
            "siblings/neural-from-scratch/marker",
            "home/.ssh/marker",
            "home/.aws/marker",
            "home/.azure/marker",
            "home/.config/gcloud/marker",
            "home/.kube/marker",
        ):
            path = hidden / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_SENTINEL + "\n", encoding="utf-8")
        (hidden / "home" / ".git-credentials").write_text(_SENTINEL + "\n", encoding="utf-8")
        (hidden / "home" / ".npmrc").write_text(_SENTINEL + "\n", encoding="utf-8")
        artifact = root / "artifact"
        artifact.mkdir()
        (artifact / "marker").write_text(_SENTINEL + "\n", encoding="utf-8")
        (artifact / "escape").symlink_to(hidden / "gold" / "marker")
        config = root / "config"
        config.mkdir()
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        sock_dir = Path(tempfile.mkdtemp(prefix="patchpilot-sock-", dir="/tmp"))
        sock_path = sock_dir / "h.sock"
        unix_listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        unix_listener.bind(str(sock_path))
        unix_listener.listen(1)
        try:
            request = {
                "port": listener.getsockname()[1],
                "unixSocket": str(sock_path),
            }
            (config / "request.json").write_text(json.dumps(request), encoding="utf-8")
            result = execute_hardened(_FIXTURE, artifact_dir=artifact, config_dir=config)
        finally:
            listener.close()
            unix_listener.close()
            sock_path.unlink(missing_ok=True)
            sock_dir.rmdir()
        assert result.exit_classification == "success"
        assert result.attempts == 1
        assert _SENTINEL.encode() not in result.stdout
        assert b"/home/" not in result.stdout
        report = json.loads(result.stdout)
        assert report["artifact"] is True
        assert report["artifactWriteBlocked"] is True
        assert report["configWriteBlocked"] is True
        assert report["resultCreated"] is True
        assert report["symlinkEscaped"] is False
        assert report["home"] is False
        assert report["homeInMounts"] is False
        assert report["gold"] is False
        assert report["prior"] is False
        assert report["siblingPatchpilot"] is False
        assert report["siblingNeural"] is False
        assert report["ssh"] is False
        assert report["aws"] is False
        assert report["singleUidMap"] is True
        assert report["procBinfmt"] is False
        assert report["numericUidOption"] is True
        assert all("/home/" not in item for item in result.argv)
    finally:
        shutil.rmtree(root, ignore_errors=True)
