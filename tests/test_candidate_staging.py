"""Candidate inventory checks using listed identities, not downloaded bytes."""

from __future__ import annotations

import pytest

from patchpilot_intelligence_evals.candidate_staging import (
    CandidateStagingError,
    compare_selected_file,
    load_candidate_manifest_template,
    not_acquired_candidate_manifest,
    require_license_text,
    require_selected_path,
)


def test_candidate_template_matches_the_builder() -> None:
    manifest = load_candidate_manifest_template()
    assert manifest == not_acquired_candidate_manifest()
    assert manifest["manifestState"] == "not-acquired"
    assert manifest["noticePresent"] is False
    assert manifest["observedFiles"] == []
    assert manifest["locallyObservedArtifactDigests"] == []
    assert manifest["productionReady"] is False
    assert len(manifest["expectedFiles"]) == 11


def test_unselected_paths_are_rejected() -> None:
    require_selected_path("onnx/model.onnx")
    with pytest.raises(CandidateStagingError) as caught:
        require_selected_path("onnx/model_fp16.onnx")
    assert caught.value.code == "unexpected-file"
    with pytest.raises(CandidateStagingError) as quantized:
        require_selected_path("onnx/model_q4.onnx")
    assert quantized.value.code == "unexpected-file"


def test_size_and_license_checks() -> None:
    with pytest.raises(CandidateStagingError) as caught:
        compare_selected_file("config.json", 1, "ab" * 32)
    assert caught.value.code == "size-mismatch"
    assert compare_selected_file("tokenizer.json", 3_297_799, "cd" * 32) == "not-provided"
    require_license_text(b"LFM Open License v1.0\n")
    with pytest.raises(CandidateStagingError) as license_error:
        require_license_text(b"MIT")
    assert license_error.value.code == "license-mismatch"
