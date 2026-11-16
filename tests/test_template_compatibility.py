"""Template compatibility stays closed and does not create a session."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.candidate_inference import (
    launch_child,
    measurement_limits,
)
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import (
    MeasurementError,
    load_measurement_plan,
    phase_by_name,
)
from patchpilot_intelligence_evals.template_compatibility import (
    CHAT_TEMPLATE_SHA256,
    TemplateCompatibilityError,
    validate_chat_template,
)
from patchpilot_intelligence_evals.track8b_records import (
    APPROVED_PLAN_DIGEST,
    VERIFIED_TEMPLATE_DIGEST,
    build_preflight_record,
    load_plan_disposition,
    load_preflight_template,
    load_stopped_attempt,
    load_stopped_closeout,
    load_template_defect,
    load_track8b_review,
)
from patchpilot_intelligence_evals.verified_tokenizer import VerifiedTokenizer

_FIXTURE = Path("tests/fixtures/verified-chat-template.jinja")
_SPACED = """{{- bos_token -}}
{%- for message in messages -%}
{{- "<|im_start|>" + message["role"] + "\\n" -}}
{{- message["content"] + "<|im_end|>\\n" -}}
{%- endfor -%}
{%- if add_generation_prompt -%}
{{- "<|im_start|>assistant\\n" -}}
{%- endif -%}
"""
_COMPACT = """{{- bos_token -}}
{%- for message in messages -%}
{{- "<|im_start|>"+message["role"]+"\\n" -}}
{{- message["content"]+"<|im_end|>\\n" -}}
{%- endfor -%}
{%- if add_generation_prompt -%}
{{- "<|im_start|>assistant\\n" -}}
{%- endif -%}
"""


def _verified() -> str:
    return _FIXTURE.read_text(encoding="utf-8")


def test_verified_template_does_not_need_the_length_spelling() -> None:
    template = _verified()
    assert "messages | length" not in template
    assert CHAT_TEMPLATE_SHA256 == VERIFIED_TEMPLATE_DIGEST
    result = validate_chat_template(
        template,
        expected_digest=CHAT_TEMPLATE_SHA256,
        content="synthetic-user",
    )
    assert result["compatibility"] == "supported"
    assert result["templateDigest"] == CHAT_TEMPLATE_SHA256
    assert result["renderedShape"] == "user-turn-with-generation-prompt"
    assert result["runInvoked"] is False
    assert result["sessionCreated"] is False


def test_operator_whitespace_does_not_decide_compatibility() -> None:
    spaced = validate_chat_template(_SPACED, expected_digest=None, content="synthetic-user")
    compact = validate_chat_template(_COMPACT, expected_digest=None, content="synthetic-user")
    assert spaced["renderedDigest"] == compact["renderedDigest"]
    assert " + " in _SPACED
    assert " + " not in _COMPACT


def test_unsupported_construct_fails_closed() -> None:
    with pytest.raises(TemplateCompatibilityError) as caught:
        validate_chat_template('{% include "x" %}', expected_digest=None, content="synthetic-user")
    assert caught.value.code == "unsupported-template-language"


def test_digest_mismatch_fails_before_rendering(monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("rendered")

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.template_compatibility._render_nodes",
        explode,
    )
    with pytest.raises(TemplateCompatibilityError) as caught:
        validate_chat_template(
            _verified() + " ",
            expected_digest=CHAT_TEMPLATE_SHA256,
            content="synthetic-user",
        )
    assert caught.value.code == "identity-mismatch"


def test_invalid_rendered_prompt_fails_closed() -> None:
    with pytest.raises(TemplateCompatibilityError) as caught:
        validate_chat_template('{{- "nope" -}}', expected_digest=None, content="synthetic-user")
    assert caught.value.code == "invalid-rendered-prompt"


def test_rendered_digest_is_stable() -> None:
    first = validate_chat_template(
        _verified(),
        expected_digest=CHAT_TEMPLATE_SHA256,
        content="synthetic-user",
    )
    second = validate_chat_template(
        _verified(),
        expected_digest=CHAT_TEMPLATE_SHA256,
        content="synthetic-user",
    )
    assert first["renderedDigest"] == second["renderedDigest"]


def test_compatibility_validation_creates_no_session() -> None:
    before = set(sys.modules)
    result = validate_chat_template(
        _verified(),
        expected_digest=CHAT_TEMPLATE_SHA256,
        content="synthetic-user",
    )
    added = set(sys.modules) - before
    source = Path("src/patchpilot_intelligence_evals/template_compatibility.py").read_text(
        encoding="utf-8"
    )
    assert result["sessionCreated"] is False
    assert result["runInvoked"] is False
    assert "Run(" not in source
    assert "import onnxruntime" not in source
    assert "model.onnx" not in source
    assert not any("onnx" in name for name in added)


def test_tokenizer_uses_the_checked_render() -> None:
    template = _verified()
    tokenizer = VerifiedTokenizer(
        {"model": {"merges": [], "type": "BPE", "vocab": {"a": 1}}},
        template,
    )
    rendered = tokenizer.render("synthetic-user")
    assert rendered == (
        "<|startoftext|><|im_start|>user\nsynthetic-user<|im_end|>\n<|im_start|>assistant\n"
    )
    source = Path("src/patchpilot_intelligence_evals/verified_tokenizer.py").read_text(
        encoding="utf-8"
    )
    assert "messages | length" not in source


def test_future_preflight_carries_frozen_authority() -> None:
    template = load_preflight_template()
    live = build_preflight_record(status="ok")
    for document in (template, live):
        assert document["selectionOutcome"] == "no-selection"
        assert document["calibrationStatus"] == "not-approved"
        assert document["productionReady"] is False
        assert document["measurementPerformed"] is False
        assert document["runInvoked"] is False
        assert document["planDigest"] == APPROVED_PLAN_DIGEST
    assert template["status"] == "not-executed"
    assert live["status"] == "ok"


def test_stopped_attempt_and_plan_stay_consumed() -> None:
    attempt = load_stopped_attempt()
    closeout = load_stopped_closeout()
    disposition = load_plan_disposition()
    review = load_track8b_review()
    defect = load_template_defect()
    plan = load_measurement_plan()
    assert plan["planDigest"] == APPROVED_PLAN_DIGEST
    assert plan["executionStatus"] == "not-executed"
    assert attempt["stopCause"] == "tokenizer-failure"
    assert attempt["runInvoked"] is False
    assert attempt["sessionCreated"] is False
    assert attempt["realModelExecuted"] is False
    assert attempt["shortGeneration"] == "not-executed"
    assert attempt["context4096"] == "not-executed"
    assert attempt["context8192"] == "withheld"
    assert attempt["corpusEvaluation"] == "not-executed"
    assert attempt["candidateMetrics"] == "not-produced"
    assert attempt["track9Readiness"] == "not-ready"
    assert attempt["historicalPreflightOmittedCalibrationStatus"] is True
    assert attempt["calibrationRemainedNotApproved"] is True
    assert attempt["calibrationDecisionChanged"] is False
    assert closeout["closeoutState"] == "stopped"
    assert closeout["historicalPreflightOmittedCalibrationStatus"] is True
    statuses = {item["phase"]: item["status"] for item in closeout["phases"]}
    assert statuses["context-8192"] == "withheld"
    assert disposition["planDisposition"] == "consumed"
    assert disposition["reusable"] is False
    assert disposition["replacementPlanDigest"] == "not-issued"
    assert disposition["nextRunRequiresNewPlan"] is True
    assert disposition["nextRunRequiresOperatorApproval"] is True
    assert review["reviewStatus"] == "stopped-attempt-accepted-corrections-prepared"
    assert review["calibrationDecisionChanged"] is False
    assert defect["templateBytesChanged"] is False
    assert defect["verifiedTemplateDigest"] == VERIFIED_TEMPLATE_DIGEST
    assert defect["runInvoked"] is False
    assert defect["sessionCreated"] is False


def test_real_launcher_refuses_the_consumed_plan(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def explode(*_args: object, **_kwargs: object) -> ExecutionResult:
        raise AssertionError("launcher")

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.candidate_inference.execute_hardened",
        explode,
    )
    plan = load_measurement_plan()
    with pytest.raises(MeasurementError) as caught:
        launch_child(
            {"phase": "one-token-smoke"},
            runtime_dir=tmp_path,
            model_dir=tmp_path,
            limits=measurement_limits(phase_by_name(plan, "one-token-smoke")),
            launcher=explode,
        )
    assert caught.value.code == "plan-consumed"


def test_synthetic_launcher_still_receives_the_checker(tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        seen["companions"] = kwargs["companions"]
        return ExecutionResult(
            exit_classification="not-executed",
            return_code=0,
            stdout=b"",
            stderr=b"",
            cleanup="reaped",
            attempts=1,
            report=b"",
            argv=(),
        )

    plan = load_measurement_plan()
    launch_child(
        {"phase": "one-token-smoke"},
        runtime_dir=tmp_path,
        model_dir=tmp_path,
        limits=measurement_limits(phase_by_name(plan, "one-token-smoke")),
        launcher=launcher,
    )
    companions = seen["companions"]
    assert isinstance(companions, tuple)
    assert [path.name for path in companions] == [
        "verified_tokenizer.py",
        "template_compatibility.py",
    ]
