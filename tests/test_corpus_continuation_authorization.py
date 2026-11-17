"""Track 9 continuation-authorization tests."""

import pytest

from patchpilot_intelligence_evals.corpus_continuation_authorization import (
    build_corpus_continuation_authorization,
    build_withheld_continuation,
    load_corpus_continuation_authorization,
    require_continuation,
)
from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan
from patchpilot_intelligence_evals.measurement_plan import (
    CHAT_TEMPLATE_SHA256,
    CORPUS_DIGEST,
    PROMPT_TEMPLATE_DIGEST,
    TOKENIZER_SHA256,
    MeasurementError,
)
from patchpilot_intelligence_evals.protocol import MAX_STDOUT_BYTES


def test_authorization_is_in_principle_only() -> None:
    document = load_corpus_continuation_authorization()
    plan = load_inference_plan()
    assert document == build_corpus_continuation_authorization()
    assert document["authorizationStatus"] == "authorized-in-principle"
    assert document["currentExecutionAuthority"] is False
    assert document["futurePlanDigest"] == "not-issued"
    assert document["r3Plan"] == "not-issued"
    assert document["operatorApproval"] == "not-issued"
    assert document["resultRootState"] == "not-created"
    assert document["caseCount"] == 24
    assert document["repetitionsPerCase"] == 3
    assert document["plannedRuns"] == 72
    assert document["repeatContext4096"] is False
    assert document["repeatContext8192"] is False
    assert document["omittedPhases"] == ["context-4096", "context-8192"]
    assert document["reuseAcceptedMemoryEvidence"] is True
    assert document["stdoutLimitBytes"] == MAX_STDOUT_BYTES == 65536
    assert (
        document["promptTemplateDigest"] == plan["promptTemplateDigest"] == PROMPT_TEMPLATE_DIGEST
    )
    assert document["corpusDigest"] == plan["corpusDigest"] == CORPUS_DIGEST
    assert document["chatTemplateDigest"] == plan["chatTemplateSha256"] == CHAT_TEMPLATE_SHA256
    assert document["tokenizerDigest"] == TOKENIZER_SHA256
    assert document["promptsUnchanged"] is True
    assert document["responseSchemaUnchanged"] is True
    assert document["metricsUnchanged"] is True
    assert document["gatesUnchanged"] is True
    assert document["artifactsUnchanged"] is True
    raw = document["rawOutputRetention"]
    assert raw["status"] == "required"
    assert raw["availableToCandidate"] is False
    assert raw["availableToLaterRuns"] is False
    assert raw["freeOfGold"] is True
    assert raw["recordParseErrors"] is True
    assert raw["recordSchemaErrors"] is True
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False


def test_withholding_issues_no_plan() -> None:
    document = build_withheld_continuation()
    assert document["authorizationStatus"] == "withheld"
    assert document["withheldReason"] == "proportionality-stop"
    assert document["plannedRuns"] == 0
    assert document["futurePlanDigest"] == "not-issued"
    assert document["currentExecutionAuthority"] is False
    assert document["resultRootState"] == "not-created"
    assert document["rawOutputRetention"]["status"] == "withheld"
    assert document["productionReady"] is False


def test_changed_prompts_are_rejected() -> None:
    document = build_corpus_continuation_authorization()
    document["promptsUnchanged"] = False
    with pytest.raises(MeasurementError) as caught:
        require_continuation(document)
    assert caught.value.code == "continuation-boundary"


def test_repeating_context_measurement_is_rejected() -> None:
    document = build_corpus_continuation_authorization()
    document["repeatContext8192"] = True
    with pytest.raises(MeasurementError) as caught:
        require_continuation(document)
    assert caught.value.code == "continuation-boundary"
