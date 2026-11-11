"""Runtime inventory checks. Temporary synthetic bytes only. No runtime is downloaded."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.runtime_artifact_verification import (
    RuntimeVerificationError,
    inspect_runtime,
    load_verification_template,
    not_staged_verification,
)
from patchpilot_intelligence_evals.runtime_cache import place_quarantine

_LIBRARY = "libonnxruntime.so.1.31.1"
_ELF = b"\x7fELFsynthetic-runtime"
_LICENSE = b"synthetic-mit\n"
_NOTICE = b"synthetic-notice\n"
_IDENTITY = b'{"runtimeId":"onnxruntime","telemetry":"disabled","versionTag":"v1.31.1"}'
_TEMPLATE = "candidates/templates/runtime-artifact-verification-template.json"


def _files(identity: bytes = _IDENTITY, library: bytes = _ELF) -> dict[str, bytes]:
    return {
        _LIBRARY: library,
        "LICENSE": _LICENSE,
        "ThirdPartyNotices.txt": _NOTICE,
        "runtime-identity.json": identity,
    }


def _expected(files: dict[str, bytes], *, upstream: bool = False) -> list[dict[str, object]]:
    roles = {
        _LIBRARY: ("shared-library", "elf"),
        "LICENSE": ("license", "not-executable"),
        "ThirdPartyNotices.txt": ("notice", "not-executable"),
        "runtime-identity.json": ("configuration", "not-executable"),
    }
    expected: list[dict[str, object]] = []
    for name, payload in files.items():
        role, executable_format = roles[name]
        digest = hashlib.sha256(payload).hexdigest() if upstream else None
        expected.append(
            {
                "fileName": name,
                "role": role,
                "expectedBytes": len(payload),
                "upstreamSha256": digest,
                "executableFormat": executable_format,
            }
        )
    return expected


def test_template_is_not_staged(capsys: pytest.CaptureFixture[str]) -> None:
    template = load_verification_template()
    assert template == not_staged_verification()
    assert template["verificationState"] == "not-staged"
    assert template["locallyObservedArtifactDigests"] == []
    assert template["runtimeInstalled"] is False
    assert template["malwareDetectionClaimed"] is False
    assert template["productionReady"] is False
    assert "/home/" not in json.dumps(template)
    assert main(["runtime-artifact-verification-validation", "--manifest", _TEMPLATE]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["verificationState"] == "not-staged"
    assert summary["runtimeInstalled"] is False


def test_matching_inventory_verifies(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    root.mkdir()
    files = _files()
    place_quarantine(root, "runtime-ok", files)
    manifest = inspect_runtime(
        root / "quarantine" / "runtime-ok",
        _expected(files, upstream=True),
        attempt_id="runtime-ok",
    )
    assert manifest["verificationState"] == "verified"
    assert manifest["telemetryConfiguration"] == "disabled"
    assert manifest["upstreamDigestComparison"] == "matched"
    assert manifest["locallyObservedArtifactDigests"]
    assert manifest["reasonCodes"] == []


def test_non_elf_library_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    root.mkdir()
    files = _files(library=b"not-elf")
    place_quarantine(root, "runtime-format", files)
    manifest = inspect_runtime(
        root / "quarantine" / "runtime-format",
        _expected(files),
        attempt_id="runtime-format",
    )
    assert manifest["verificationState"] == "rejected"
    assert "unsupported-executable-format" in manifest["reasonCodes"]
    assert manifest["locallyObservedArtifactDigests"] == []
    assert manifest["malwareDetectionClaimed"] is False


def test_unapproved_library_and_writable_file_are_rejected(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    root.mkdir()
    files = _files()
    quarantine = place_quarantine(root, "runtime-extra", files)
    extra = quarantine / "libcuda.so.1"
    extra.write_bytes(b"\x7fELFextra")
    extra.chmod(0o444)
    manifest = inspect_runtime(quarantine, _expected(files), attempt_id="runtime-extra")
    assert "unapproved-shared-library" in manifest["reasonCodes"]
    assert "unexpected-file" in manifest["reasonCodes"]
    library = quarantine / _LIBRARY
    library.chmod(0o644)
    writable = inspect_runtime(quarantine, _expected(files), attempt_id="runtime-extra")
    assert "writable-artifact" in writable["reasonCodes"]


def test_telemetry_version_license_and_identity_fail(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    root.mkdir()
    enabled = b'{"runtimeId":"onnxruntime","telemetry":"enabled","versionTag":"v1.31.1"}'
    files = _files(identity=enabled)
    place_quarantine(root, "runtime-telemetry", files)
    telemetry = inspect_runtime(
        root / "quarantine" / "runtime-telemetry",
        _expected(files),
        attempt_id="runtime-telemetry",
    )
    assert "telemetry-enabled" in telemetry["reasonCodes"]
    wrong_version = b'{"runtimeId":"onnxruntime","telemetry":"disabled","versionTag":"v1.30.0"}'
    version_files = _files(identity=wrong_version)
    place_quarantine(root, "runtime-version", version_files)
    version = inspect_runtime(
        root / "quarantine" / "runtime-version",
        _expected(version_files),
        attempt_id="runtime-version",
    )
    assert "version-mismatch" in version["reasonCodes"]
    other = b'{"runtimeId":"transformers","telemetry":"disabled","versionTag":"v1.31.1"}'
    identity_files = _files(identity=other)
    place_quarantine(root, "runtime-id", identity_files)
    identity = inspect_runtime(
        root / "quarantine" / "runtime-id",
        _expected(identity_files),
        attempt_id="runtime-id",
    )
    assert "runtime-identity" in identity["reasonCodes"]
    files = _files()
    expected = _expected(files, upstream=True)
    for item in expected:
        if item["fileName"] == "LICENSE":
            item["upstreamSha256"] = "a" * 64
    place_quarantine(root, "runtime-license", files)
    licensed = inspect_runtime(
        root / "quarantine" / "runtime-license",
        expected,
        attempt_id="runtime-license",
    )
    assert "license-mismatch" in licensed["reasonCodes"]


def test_traversal_name_is_rejected() -> None:
    with pytest.raises(RuntimeVerificationError) as caught:
        inspect_runtime(
            Path("/tmp"),
            [
                {
                    "fileName": "../escape",
                    "role": "notice",
                    "expectedBytes": 1,
                    "upstreamSha256": None,
                    "executableFormat": "not-executable",
                }
            ],
            attempt_id="runtime-escape",
        )
    assert caught.value.code == "unexpected-file"
