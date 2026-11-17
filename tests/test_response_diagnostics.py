"""Diagnostics record schema facts without storing explanation text."""

from __future__ import annotations

from patchpilot_intelligence_evals.response_diagnostics import diagnose_response, generation_facts


def _side(**updates: object) -> dict[str, object]:
    facts = generation_facts(b"")
    facts.update(updates)
    return facts


def test_missing_and_unexpected_fields_are_names_only() -> None:
    parsed = {
        "candidateId": "fixture-lfm25-instruct",
        "candidateVersion": "1",
        "protocolVersion": "1.0.0",
        "requestId": "a" * 64,
        "schemaVersion": "1.0.0",
        "status": "unavailable",
        "surpriseField": "hidden-value",
    }
    diagnosed = diagnose_response(
        {
            "extractedBytes": 0,
            "extractedDigest": None,
            "extractionStatus": "extracted",
            "parsed": parsed,
        },
        _side(generationObserved=True, parseCategory="parsed", utf8=True),
    )
    assert "status" not in diagnosed["missingRequired"] or "failure" in diagnosed["missingRequired"]
    assert "surpriseField" in diagnosed["unexpectedFields"]
    assert "hidden-value" not in str(diagnosed["unexpectedFields"])
    assert diagnosed["schemaStatus"] == "invalid"


def test_bad_evidence_id_is_a_path_not_a_value() -> None:
    parsed = {
        "candidateId": "fixture-lfm25-instruct",
        "candidateVersion": "1",
        "findingExplanationOutput": {"citations": [{"evidenceId": "not-synthetic"}]},
        "protocolVersion": "1.0.0",
        "requestId": "b" * 64,
        "schemaVersion": "1.0.0",
        "status": "success",
    }
    diagnosed = diagnose_response(
        {
            "extractedBytes": 0,
            "extractedDigest": None,
            "extractionStatus": "extracted",
            "parsed": parsed,
        },
        _side(),
    )
    assert diagnosed["evidenceIdFindings"]
    assert "not-synthetic" not in diagnosed["evidenceIdFindings"]


def test_absent_side_file_does_not_invent_a_parse() -> None:
    facts = generation_facts(b"")
    assert facts["generationObserved"] is False
    assert facts["parseCategory"] == "not-performed"
