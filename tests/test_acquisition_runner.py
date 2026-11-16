"""Synthetic transfer and runtime promotion. No socket is opened."""

from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.acquisition_plan import load_acquisition_allowlist
from patchpilot_intelligence_evals.acquisition_runner import (
    TransferError,
    acquire_runtime,
    promote_runtime_archive,
    transfer_file,
)
from patchpilot_intelligence_evals.finalist_budget import RUNTIME_PACKAGE

_HEADER = """
#define ORT_API_VERSION 21
typedef enum { ORT_LOGGING_LEVEL_ERROR = 3 } OrtLoggingLevel;
struct OrtApi {
ORT_API_STATUS(ORT_API_CALL *CreateEnv)();
ORT_API_STATUS(ORT_API_CALL *CreateStatus)();
ORT_API_STATUS(ORT_API_CALL *CreateSession)();
ORT_API_STATUS(ORT_API_CALL *CreateSessionOptions)();
ORT_API_STATUS(ORT_API_CALL *DisableTelemetryEvents)();
ORT_API_STATUS(ORT_API_CALL *GetErrorMessage)();
ORT_API_STATUS(ORT_API_CALL *ReleaseEnv)();
ORT_API_STATUS(ORT_API_CALL *ReleaseSession)();
ORT_API_STATUS(ORT_API_CALL *ReleaseSessionOptions)();
ORT_API_STATUS(ORT_API_CALL *SessionGetInputCount)();
ORT_API_STATUS(ORT_API_CALL *SessionGetOutputCount)();
};
"""


class _Body:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def read(self, size: int | None = None) -> bytes:
        if size is None:
            data = self.payload
            self.payload = b""
            return data
        data = self.payload[:size]
        self.payload = self.payload[size:]
        return data

    def close(self) -> None:
        return None


def test_transfer_rejects_an_unlisted_url(tmp_path: Path) -> None:
    allowlist = load_acquisition_allowlist()
    destination = tmp_path / "archive.tgz"

    def exchange(host: str, path: str) -> tuple[int, dict[str, str], _Body]:
        raise AssertionError((host, path))

    with pytest.raises(TransferError) as caught:
        transfer_file(
            "https://example.com/archive.tgz",
            destination,
            expected_bytes=4,
            allowlist=allowlist,
            overall_seconds=30,
            exchange=exchange,
        )
    assert caught.value.code == "unauthorized-source"
    assert not destination.exists()


def test_redirect_to_an_unobserved_cdn_saves_no_body(tmp_path: Path) -> None:
    allowlist = load_acquisition_allowlist()
    destination = tmp_path / "archive.tgz"
    url = str(allowlist["allowedUrls"][0])

    def exchange(host: str, path: str) -> tuple[int, dict[str, str], _Body]:
        assert host == "github.com"
        assert path
        return (
            302,
            {"location": "https://cdn-lfs.huggingface.co/object"},
            _Body(b"not-saved"),
        )

    with pytest.raises(TransferError) as caught:
        transfer_file(
            url,
            destination,
            expected_bytes=8,
            allowlist=allowlist,
            overall_seconds=30,
            exchange=exchange,
        )
    assert caught.value.code == "unauthorized-redirect"
    assert not destination.exists()


def test_plan_scoped_redirect_saves_only_the_final_body(tmp_path: Path) -> None:
    allowlist = load_acquisition_allowlist()
    destination = tmp_path / "archive.tgz"
    url = str(allowlist["allowedUrls"][0])
    calls = {"count": 0}

    def exchange(host: str, path: str) -> tuple[int, dict[str, str], _Body]:
        calls["count"] += 1
        if calls["count"] == 1:
            assert host == "github.com"
            return (
                302,
                {"location": "https://release-assets.githubusercontent.com/object"},
                _Body(b"redirect-body-not-saved"),
            )
        assert host == "release-assets.githubusercontent.com"
        return 200, {"content-length": "4"}, _Body(b"data")

    digest = transfer_file(
        url,
        destination,
        expected_bytes=4,
        allowlist=allowlist,
        overall_seconds=30,
        exchange=exchange,
    )
    assert calls["count"] == 2
    assert destination.read_bytes() == b"data"
    assert b"redirect-body-not-saved" not in destination.read_bytes()
    assert len(digest) == 64


def test_short_body_is_deleted(tmp_path: Path) -> None:
    allowlist = load_acquisition_allowlist()
    destination = tmp_path / "archive.tgz"
    url = str(allowlist["allowedUrls"][0])

    def exchange(host: str, path: str) -> tuple[int, dict[str, str], _Body]:
        assert host == "github.com"
        assert path
        return 200, {"content-length": "4"}, _Body(b"nope")

    with pytest.raises(TransferError) as caught:
        transfer_file(
            url,
            destination,
            expected_bytes=8,
            allowlist=allowlist,
            overall_seconds=30,
            exchange=exchange,
        )
    assert caught.value.code == "size-mismatch"
    assert not destination.exists()


def test_approval_is_required_before_a_runtime_transfer(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    root.mkdir()

    def exchange(host: str, path: str) -> tuple[int, dict[str, str], _Body]:
        raise AssertionError((host, path))

    with pytest.raises(TransferError) as caught:
        acquire_runtime(root, "nope", exchange=exchange)
    assert caught.value.code == "approval-required"
    assert not (root / "quarantine").exists()


def test_runtime_archive_promotes_only_the_flat_verified_set(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    root.mkdir()
    attempt = root / "quarantine" / "rt-synthetic"
    attempt.mkdir(parents=True)
    archive = attempt / RUNTIME_PACKAGE
    _write_archive(archive, extra_library=False)
    result = promote_runtime_archive(root, "rt-synthetic", network_barrier=lambda: None)
    assert result["status"] == "verified"
    assert result["executed"] is False
    verified = root / "verified" / result["promotionAttemptId"]
    metadata = {"promotion-journal.json", "verification-seal.json"}
    names = sorted(
        path.name for path in verified.iterdir() if path.is_file() and path.name not in metadata
    )
    assert names == [
        "LICENSE",
        "ThirdPartyNotices.txt",
        "libonnxruntime.so.1.31.1",
        "runtime-identity.json",
    ]
    assert not any(path.is_symlink() for path in verified.iterdir())
    identity = (verified / "runtime-identity.json").read_text(encoding="utf-8")
    assert '"telemetry": "disabled"' in identity


def test_extra_shared_library_stops_promotion(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    root.mkdir()
    attempt = root / "quarantine" / "rt-extra"
    attempt.mkdir(parents=True)
    _write_archive(attempt / RUNTIME_PACKAGE, extra_library=True)
    with pytest.raises(TransferError) as caught:
        promote_runtime_archive(root, "rt-extra", network_barrier=lambda: None)
    assert caught.value.code == "unexpected-file"
    assert any((root / "rejected").glob("rp-*"))


def _write_archive(path: Path, *, extra_library: bool) -> None:
    prefix = "onnxruntime-linux-x64-1.31.1/"
    with tarfile.open(path, "w:gz") as archive:
        _add_bytes(archive, prefix + "lib/libonnxruntime.so.1.31.1", b"\x7fELFsynthetic")
        _add_bytes(
            archive,
            prefix + "LICENSE",
            b"MIT\nPermission is hereby granted\n",
        )
        _add_bytes(archive, prefix + "ThirdPartyNotices.txt", b"notices\n")
        _add_bytes(archive, prefix + "include/onnxruntime_c_api.h", _HEADER.encode("utf-8"))
        _add_link(archive, prefix + "lib/libonnxruntime.so", "libonnxruntime.so.1.31.1")
        if extra_library:
            _add_bytes(archive, prefix + "lib/libextra.so", b"\x7fELFextra")


def _add_bytes(archive: tarfile.TarFile, name: str, payload: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    info.mode = 0o644
    archive.addfile(info, io.BytesIO(payload))


def _add_link(archive: tarfile.TarFile, name: str, target: str) -> None:
    info = tarfile.TarInfo(name)
    info.type = tarfile.SYMTYPE
    info.linkname = target
    archive.addfile(info)
