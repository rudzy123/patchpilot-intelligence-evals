"""Closeout keeps authority frozen and records proportionality."""

from __future__ import annotations

import json
from pathlib import Path

from patchpilot_intelligence_evals.inference_behavioral_measurement import record_corpus_stop
from patchpilot_intelligence_evals.inference_retry_closeout import (
    build_closeout,
    build_closeout_template,
    load_closeout_template,
)
from patchpilot_intelligence_evals.inference_retry_plan import PHASE_ORDER


def test_closeout_template_is_not_closed() -> None:
    document = load_closeout_template()
    assert document == build_closeout_template()
    assert document["closeoutState"] == "not-closed"
    assert document["comparisonWinner"] is None
    assert document["memoryConclusion"] == "unavailable"
    assert document["behavioralConclusion"] == "not-measured"
    assert document["furtherRetryAssumed"] is False
    assert document["proportionalityRecommendation"] == "not-applicable"
    assert document["productionReady"] is False
    assert [item["phase"] for item in document["phases"]] == list(PHASE_ORDER)
    assert all(item["status"] == "not-executed" for item in document["phases"])


def test_corpus_telemetry_stop_requires_review(tmp_path: Path) -> None:
    (tmp_path / "dynamic-link-precheck.json").write_text(
        json.dumps(
            {
                "broadHostLibraryMounted": False,
                "createSessionCalled": False,
                "getApiCalled": False,
                "identityDigest": "ab" * 32,
                "libraryClosed": True,
                "modelSessionCreated": False,
                "networkResult": "denied",
                "processCleanup": "reaped",
                "providerLoaded": False,
                "runInvoked": False,
                "status": "passed",
                "symbolBoundary": "held",
                "unexpectedPath": False,
            }
        ),
        encoding="utf-8",
    )
    record_corpus_stop(tmp_path, "telemetry-unresolved")
    closeout = build_closeout(tmp_path)
    assert closeout["stopCause"] == "telemetry-unresolved"
    assert closeout["proportionalityRecommendation"] == "review-required"
    assert closeout["proportionalityRationale"] == "infrastructure-defect-requires-review"
    assert closeout["furtherRetryAssumed"] is False
    assert closeout["comparisonWinner"] is None
    assert closeout["productionReady"] is False
