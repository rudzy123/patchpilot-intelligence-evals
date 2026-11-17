"""Adapter classification without loading the promoted library."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.candidate_inference import (
    assert_no_gold,
    classify_execution,
)
from patchpilot_intelligence_evals.candidate_inference_main import (
    argmax_last,
    input_allowed,
    past_name,
)
from patchpilot_intelligence_evals.cgroup_memory import ScopeSampler
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import MeasurementError


def _result(report: dict[str, object] | None = None, *, code: int = 0) -> ExecutionResult:
    payload = b"" if report is None else json.dumps(report).encode("utf-8")
    return ExecutionResult(
        exit_classification="success" if code == 0 else "nonzero",
        return_code=code,
        stdout=b"",
        stderr=b"",
        cleanup="reaped",
        attempts=1,
        report=payload,
        argv=(),
    )


def _sample(sampler: ScopeSampler, *, peak: int | None, oom: int | None, phase: str) -> None:
    sampler.samples.append(
        {
            "cgroupCurrentBytes": 1,
            "cgroupPeakBytes": peak,
            "oomEvents": oom,
            "phase": phase,
            "processRssBytes": 1,
            "processTreeRssBytes": 1,
            "virtualAddressBytes": 50,
        }
    )


def test_allowlist_and_argmax() -> None:
    assert input_allowed("input_ids") is True
    assert input_allowed("past_key_values.2.key") is True
    assert input_allowed("labels") is False
    assert past_name("present.2.key") == "past_key_values.2.key"
    assert past_name("present_conv.0") == "past_conv.0"
    assert past_name("logits") is None
    import ctypes

    values = (ctypes.c_float * 6)(1, 3, 2, 0, 4, 1)
    pointer = ctypes.cast(values, ctypes.c_void_p).value
    assert pointer is not None
    assert argmax_last(pointer, sequence=2, vocab=3) == 1


def test_gold_keys_are_rejected() -> None:
    with pytest.raises(MeasurementError) as caught:
        assert_no_gold({"promptInjection": []})
    assert caught.value.code == "gold-visible"


def test_missing_peak_and_ceiling_stop() -> None:
    missing = ScopeSampler()
    _sample(missing, peak=None, oom=0, phase="cold")
    assert classify_execution(_result(), missing, cold_warm=False)["exitClassification"] == (
        "telemetry-unresolved"
    )
    high = ScopeSampler()
    _sample(high, peak=12884901888 + 1, oom=0, phase="cold")
    assert classify_execution(_result(), high, cold_warm=False)["exitClassification"] == (
        "memory-ceiling"
    )
    oom = ScopeSampler()
    _sample(oom, peak=10, oom=1, phase="cold")
    assert classify_execution(_result(), oom, cold_warm=False)["exitClassification"] == "oom"


def test_cleanup_does_not_downgrade_a_sealed_window() -> None:
    sampler = ScopeSampler()
    _sample(sampler, peak=5_709_541_376, oom=0, phase="cold")
    sampler.samples[-1]["cgroupCurrentBytes"] = 3_129_344
    sampler.samples[-1]["processRssBytes"] = None
    sampler.child_state = "exited"
    sampler.last_complete = dict(sampler.samples[-1])
    sampler.post_exit_reads.append({"effect": "diagnostic", "readError": "enxio"})
    classified = classify_execution(
        _result({"network": {"dns": "gaierror", "ipv4": "OSError"}}),
        sampler,
        cold_warm=False,
    )
    assert classified["exitClassification"] == "success"
    assert classified["cleanup"] == "reaped"
    assert classified["networkResult"] == "denied"
    assert classified["coldMemory"]["telemetry"] == "complete"
    assert classified["coldMemory"]["cgroupCurrentBytes"] == 3_129_344
    assert classified["coldMemory"]["oomEvents"] == 0
    assert sampler.blocked_classification is None


def test_virtual_size_does_not_set_the_resident_result() -> None:
    sampler = ScopeSampler()
    _sample(sampler, peak=10, oom=0, phase="cold")
    classified = classify_execution(
        _result({"network": {"dns": "gaierror", "ipv4": "OSError"}, "outputDigest": "ab" * 32}),
        sampler,
        cold_warm=False,
    )
    assert classified["exitClassification"] == "success"
    assert classified["coldMemory"]["virtualAddressBytes"] == 50
    assert classified["coldMemory"]["cgroupPeakBytes"] == 10


def test_synthetic_tokenizer_round_trip() -> None:
    from patchpilot_intelligence_evals.verified_tokenizer import VerifiedTokenizer

    document = {
        "added_tokens": [{"content": "<s>", "id": 0}],
        "model": {
            "merges": [["a", "b"]],
            "type": "BPE",
            "vocab": {"a": 1, "b": 2, "ab": 3},
        },
    }
    tokenizer = VerifiedTokenizer(document, "synthetic:{content}")
    assert tokenizer.render("ab") == "synthetic:ab"
    assert tokenizer.encode("<s>ab") == [0, 3]
    assert tokenizer.decode([0, 3]).endswith("ab")


def test_child_source_has_no_direct_session_call() -> None:
    from pathlib import Path

    text = Path("src/patchpilot_intelligence_evals/candidate_inference_main.py").read_text(
        encoding="utf-8"
    )
    assert "Run(" not in text
    assert "import onnxruntime" not in text
