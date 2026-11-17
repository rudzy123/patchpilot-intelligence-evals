"""Bounded raw bytes stay immutable and are sealed before extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.bounded_raw_output import (
    load_raw_template,
    retain_bounded_output,
)
from patchpilot_intelligence_evals.corpus_continuation_plan import prepare_continuation_root
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.protocol import MAX_STDOUT_BYTES


def test_template_retains_nothing() -> None:
    document = load_raw_template()
    assert document["retentionStatus"] == "not-retained"
    assert document["stdoutDigest"] is None
    assert document["availableToLaterRuns"] is False
    assert document["freeOfGold"] is True


def test_retained_bytes_are_immutable(tmp_path: Path) -> None:
    root = prepare_continuation_root(tmp_path / "raw-root")
    stdout = b'{"status":"success"}'
    sealed = retain_bounded_output(
        root,
        case_id="case-ground-001",
        repetition=1,
        run_id="case-ground-001-r1",
        stdout=stdout,
        stderr=b"stderr",
        limit_status="within-limit",
    )
    stored = root / "runs" / "case-ground-001-r1" / "stdout.bin"
    assert stored.read_bytes() == stdout
    assert stored.stat().st_mode & 0o777 == 0o400
    assert sealed["stdoutBytes"] == len(stdout)
    assert sealed["stdoutTruncated"] is False
    assert sealed["immutable"] is True
    with pytest.raises(MeasurementError) as caught:
        retain_bounded_output(
            root,
            case_id="case-ground-001",
            repetition=1,
            run_id="case-ground-001-r1",
            stdout=stdout,
            stderr=b"",
            limit_status="within-limit",
        )
    assert caught.value.code == "result-root-reuse"
    assert stored.read_bytes() == stdout


def test_oversize_output_is_not_stored(tmp_path: Path) -> None:
    root = prepare_continuation_root(tmp_path / "oversize-root")
    with pytest.raises(MeasurementError) as caught:
        retain_bounded_output(
            root,
            case_id="case-ground-001",
            repetition=1,
            run_id="case-ground-001-r1",
            stdout=b"x" * (MAX_STDOUT_BYTES + 1),
            stderr=b"",
            limit_status="within-limit",
        )
    assert caught.value.code == "excessive-output"
    assert not (root / "runs").exists()


def test_truncation_flag_follows_the_limit(tmp_path: Path) -> None:
    root = prepare_continuation_root(tmp_path / "truncated-root")
    sealed = retain_bounded_output(
        root,
        case_id="case-ground-001",
        repetition=2,
        run_id="case-ground-001-r2",
        stdout=b"kept",
        stderr=b"",
        limit_status="stdout-limit-exceeded",
    )
    assert sealed["stdoutTruncated"] is True
    assert sealed["stderrTruncated"] is False
    assert sealed["outputLimitStatus"] == "stdout-limit-exceeded"
