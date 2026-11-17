"""Failure authority cites retained diagnostics and stays singular."""

from __future__ import annotations

from patchpilot_intelligence_evals.failure_attribution import attribute_failure

_RAW = {"retentionStatus": "retained"}


def _diagnostic(**updates: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "adapterFallback": False,
        "adapterTruncated": False,
        "extractionStatus": "extracted",
        "generationObserved": True,
        "parseStatus": "parsed",
        "schemaStatus": "invalid",
        "trailingBytes": 0,
    }
    payload.update(updates)
    return payload


def test_candidate_output_requires_retained_unmodified_diagnostics() -> None:
    assert attribute_failure("schema-failure", _RAW, _diagnostic()) == "candidate-output"
    assert attribute_failure(
        "malformed-response", _RAW, _diagnostic(schemaStatus="not-performed")
    ) == ("candidate-output")
    assert attribute_failure("schema-failure", _RAW, _diagnostic(adapterFallback=True)) == "adapter"
    assert attribute_failure("schema-failure", _RAW, _diagnostic(generationObserved=False)) == (
        "unresolved"
    )
    assert attribute_failure(
        "schema-failure", {"retentionStatus": "not-retained"}, _diagnostic()
    ) == ("unresolved")


def test_infrastructure_and_security_are_distinct() -> None:
    assert attribute_failure("isolation-failure", _RAW, _diagnostic()) == "security-boundary"
    assert attribute_failure("network-violation", _RAW, _diagnostic()) == "security-boundary"
    assert attribute_failure("oom", _RAW, _diagnostic()) == "measurement-infrastructure"
    assert attribute_failure("telemetry-unresolved", _RAW, _diagnostic()) == (
        "measurement-infrastructure"
    )
    assert attribute_failure("excessive-output", _RAW, _diagnostic()) == "protocol"
    assert (
        attribute_failure("excessive-output", {"retentionStatus": "not-retained"}, _diagnostic())
        == "measurement-infrastructure"
    )
    assert attribute_failure("tokenizer-failure", _RAW, _diagnostic()) == "adapter"
    assert attribute_failure("success", _RAW, _diagnostic()) is None
    assert attribute_failure("timeout", _RAW, _diagnostic()) == "candidate-output"
