"""Synthetic artifact verification. No publisher weight file is read or stored."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.artifact_verification import (
    VerificationError,
    inspect_attempt,
    load_verification_manifest,
    not_acquired_verification,
)
from patchpilot_intelligence_evals.cli import main

_TEMPLATE = "candidates/templates/model-artifact-verification-template.json"


def test_not_acquired_template_has_no_local_digests(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_verification_manifest(_TEMPLATE)
    assert document == not_acquired_verification()
    assert document["verificationState"] == "not-acquired"
    assert document["locallyObservedArtifactDigests"] == []
    assert document["observedFiles"] == []
    assert document["malwareDetectionClaimed"] is False
    assert document["productionReady"] is False
    assert main(["artifact-verification-validation", "--manifest", _TEMPLATE]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["verificationState"] == "not-acquired"
    assert summary["productionReady"] is False


def test_remote_code_and_executable_bytes_are_rejected(tmp_path: Path) -> None:
    payload = b"\x7fELFsynthetic"
    target = tmp_path / "model.safetensors"
    target.write_bytes(payload)
    expected = [
        {"fileName": "model.safetensors", "expectedBytes": len(payload), "upstreamSha256": None}
    ]
    remote = inspect_attempt(
        tmp_path,
        expected,
        attempt_id="attempt-remote",
        remote_code_required=True,
        tokenizer_provenance_recorded=True,
        license_reference_recorded=True,
    )
    assert remote["verificationState"] == "rejected"
    assert "remote-code" in remote["reasonCodes"]
    assert remote["locallyObservedArtifactDigests"] == []
    executable = inspect_attempt(
        tmp_path,
        expected,
        attempt_id="attempt-elf",
        tokenizer_provenance_recorded=True,
        license_reference_recorded=True,
    )
    assert executable["verificationState"] == "rejected"
    assert executable["executableContentDetected"] is True
    assert executable["malwareDetectionClaimed"] is False
    with pytest.raises(VerificationError) as caught:
        inspect_attempt(
            tmp_path,
            [{"fileName": "../escape.safetensors", "expectedBytes": 1, "upstreamSha256": None}],
            attempt_id="attempt-path",
            tokenizer_provenance_recorded=True,
            license_reference_recorded=True,
        )
    assert caught.value.code == "unsupported-format"
