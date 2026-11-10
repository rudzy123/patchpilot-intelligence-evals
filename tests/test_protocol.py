"""Closed candidate protocol frames. Track 2 schemas stay the baseline authority."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

import pytest

from patchpilot_intelligence_evals.baseline import run_baseline
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases, sha256_text
from patchpilot_intelligence_evals.metrics import METRIC_NAMES, measure
from patchpilot_intelligence_evals.network_guard import network_guard
from patchpilot_intelligence_evals.protocol import (
    EVALUATOR_VERSION,
    FAILURE_OUTCOMES,
    PROTOCOL_VERSION,
    ProtocolError,
    build_request,
    classify_response,
    execution_constraints,
    experiment_id,
    parse_candidate_stdout,
    validate_request,
)
from patchpilot_intelligence_evals.schemas import (
    CANDIDATE_SCHEMA_NAMES,
    SCHEMA_IDS,
    SCHEMA_NAMES,
    SchemaValidationError,
    error_paths,
    load_schema,
    validate,
)

_DIGEST = "a" * 64
_CANDIDATE_ID = "fixture-conforming"
_CANDIDATE_VERSION = "1"


def _case() -> dict[str, Any]:
    return load_cases()[0]


def _request() -> dict[str, Any]:
    return build_request(_case(), _DIGEST)


def _explanation() -> dict[str, Any]:
    output = run_baseline(_case())
    output["candidate"] = {
        "kind": "future-candidate",
        "name": _CANDIDATE_ID,
        "version": _CANDIDATE_VERSION,
    }
    output["explanationLabel"] = "generated-explanation"
    output["explanationText"] = "Deterministic test double restates authorized structured fields."
    return output


def _success_response() -> dict[str, Any]:
    request = _request()
    return {
        "schemaVersion": "1.0.0",
        "protocolVersion": PROTOCOL_VERSION,
        "requestId": request["requestId"],
        "candidateId": _CANDIDATE_ID,
        "candidateVersion": _CANDIDATE_VERSION,
        "status": "success",
        "findingExplanationOutput": _explanation(),
    }


def _classify(parsed: dict[str, Any]) -> str:
    return classify_response(
        parsed,
        request_id_value=_request()["requestId"],
        candidate_id=_CANDIDATE_ID,
        candidate_version=_CANDIDATE_VERSION,
    )


def _unmeasured_block() -> dict[str, Any]:
    return {name: measure(0, 0) for name in METRIC_NAMES}


def _gate(kind: str) -> dict[str, Any]:
    return {"kind": kind, "status": "unmeasured", "numerator": 0, "denominator": 0}


def _gates() -> dict[str, Any]:
    invariant = {
        "crossTenantDisclosure",
        "unauthorizedStateMutation",
        "affectednessOrPriorityChange",
        "secretDisclosure",
    }
    names = (
        "crossTenantDisclosure",
        "unauthorizedStateMutation",
        "affectednessOrPriorityChange",
        "secretDisclosure",
        "outputSchemaValidity",
        "citationValidity",
        "evidenceAttributionAccuracy",
        "unsupportedFactualClaims",
        "correctRefusal",
        "promptInjectionResistance",
    )
    return {
        name: _gate("invariant" if name in invariant else "proposed-percentage") for name in names
    }


def _categories() -> dict[str, Any]:
    return {
        name: _unmeasured_block()
        for name in (
            "grounding-citation",
            "insufficient-evidence-refusal",
            "prompt-injection",
            "cross-tenant-negative-control",
            "contradiction",
            "stale-unavailable-incomparable",
        )
    }


def _execution_result() -> dict[str, Any]:
    case = _case()
    request = _request()
    return {
        "schemaVersion": "1.0.0",
        "protocolVersion": PROTOCOL_VERSION,
        "purpose": "candidate-performance",
        "productionReady": False,
        "resultDistinctions": {
            "harnessCorrectness": "reported",
            "baselinePerformance": "not-measured",
            "candidatePerformance": "reported",
            "promotionGateStatus": "reported",
            "executionFailures": "distinguished-from-quality-failures",
            "incompleteMetrics": "distinguished-by-unmeasured-status",
        },
        "repositoryCommit": "unknown",
        "corpusVersion": "1.0.0",
        "corpusDigest": _DIGEST,
        "candidateManifestDigest": _DIGEST,
        "candidateId": _CANDIDATE_ID,
        "candidateVersion": _CANDIDATE_VERSION,
        "candidateKind": "deterministic-test-double",
        "experimentManifestDigest": _DIGEST,
        "experimentId": experiment_id(manifest_digest=_DIGEST, corpus_digest=_DIGEST),
        "evaluatorVersion": EVALUATOR_VERSION,
        "pythonVersion": "3.12.0",
        "operatingSystem": "Linux",
        "jsonschemaVersion": "4.23.0",
        "executedAt": "2026-11-09T00:00:00Z",
        "deterministicSettings": {"canonicalJson": "sort_keys_separators_utf8_no_newline"},
        "promptIdentity": "candidate-protocol-1.0.0",
        "executionConstraints": execution_constraints(),
        "complete": False,
        "caseCount": 1,
        "perCase": [
            {
                "caseId": case["caseId"],
                "category": case["category"],
                "executionOutcome": "success",
                "inputDigest": request["findingExplanationInput"]["inputDigest"],
                "outputDigest": _DIGEST,
                "qualityScored": True,
                "metrics": _unmeasured_block(),
            }
        ],
        "byCategory": _categories(),
        "global": _unmeasured_block(),
        "gates": _gates(),
        "unmeasuredMetrics": list(METRIC_NAMES),
        "executionFailureCategories": [],
    }


def _side(*, present: bool) -> dict[str, Any]:
    if not present:
        return {
            "present": False,
            "candidateId": "",
            "candidateVersion": "",
            "candidateManifestDigest": "",
            "corpusDigest": "",
            "corpusVersion": "",
            "protocolVersion": "",
            "experimentId": "",
        }
    return {
        "present": True,
        "candidateId": _CANDIDATE_ID,
        "candidateVersion": _CANDIDATE_VERSION,
        "candidateManifestDigest": _DIGEST,
        "corpusDigest": _DIGEST,
        "corpusVersion": "1.0.0",
        "protocolVersion": PROTOCOL_VERSION,
        "experimentId": _DIGEST,
    }


def _comparison() -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "protocolVersion": PROTOCOL_VERSION,
        "productionReady": False,
        "status": "comparable",
        "reason": "",
        "winner": None,
        "left": _side(present=True),
        "right": _side(present=True),
        "gateComparison": [
            {"gate": "outputSchemaValidity", "leftStatus": "pass", "rightStatus": "pass"}
        ],
    }


def _note(note_id: str) -> dict[str, str]:
    return {"id": note_id, "detail": "Recorded for Principal Architect review."}


def _calibration() -> dict[str, Any]:
    fixture_ids = (
        ("fixture-conforming", "all-gates-pass", "success"),
        ("fixture-unsupported-claim", "gate-unsupported-factual-claims", "success"),
        ("fixture-prompt-injection-following", "gate-prompt-injection-resistance", "success"),
        ("fixture-cross-tenant-leaking", "gate-cross-tenant-disclosure", "success"),
        ("fixture-timeout", "execution-timeout", "timeout"),
        ("fixture-malformed-output", "execution-malformed-output", "malformed-output"),
        ("fixture-excessive-output", "execution-output-limit-exceeded", "output-limit-exceeded"),
        ("fixture-nonzero-exit", "execution-nonzero-exit", "nonzero-exit"),
    )
    body: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "protocolVersion": PROTOCOL_VERSION,
        "productionReady": False,
        "gatesUnchanged": True,
        "approvalStatus": "not-approved",
        "authorizesModel": False,
        "authorizesProvider": False,
        "authorizesShadowMode": False,
        "authorizesProductionComposition": False,
        "authorizesGateChange": False,
        "corpusVersion": "1.0.0",
        "corpusDigest": _DIGEST,
        "fixtureResults": [
            {
                "candidateId": candidate_id,
                "manifestDigest": _DIGEST,
                "intendedSignal": signal,
                "dominantExecutionOutcome": outcome,
                "caseCount": 24,
                "successCount": 24 if outcome == "success" else 0,
                "sensitivity": "detected",
                "gates": _gates(),
            }
            for candidate_id, signal, outcome in fixture_ids
        ],
        "boundaryChecks": [
            {"name": "at-least-95-zero", "status": "unmeasured", "numerator": 0, "denominator": 0}
        ],
        "corpusImbalance": [
            {"category": "contradiction", "count": 3},
            {"category": "cross-tenant-negative-control", "count": 4},
            {"category": "grounding-citation", "count": 6},
            {"category": "insufficient-evidence-refusal", "count": 4},
            {"category": "prompt-injection", "count": 4},
            {"category": "stale-unavailable-incomparable", "count": 3},
        ],
        "insufficientlyExercisedMetrics": ["decisiveEvidenceOmission", "latency"],
        "falsePositiveRisks": [_note("label-aware-double")],
        "falseNegativeRisks": [_note("unscanned-remediation-phrasing")],
        "blindSpots": [_note("small-injection-denominator")],
        "proposedAdjustments": [
            {
                "id": "no-threshold-change",
                "detail": "No gate change is adopted in this track.",
                "adopted": False,
                "approvalStatus": "not-approved",
            }
        ],
        "futureRealCandidatePrerequisites": [_note("separate-provenance-review")],
    }
    digest_payload = dict(body)
    body["calibrationDigest"] = sha256_text(canonical_dumps(digest_payload))
    return body


def _manifest() -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "protocolVersion": PROTOCOL_VERSION,
        "candidateId": _CANDIDATE_ID,
        "candidateVersion": _CANDIDATE_VERSION,
        "candidateKind": "deterministic-test-double",
        "implementation": {
            "interpreter": "current-python",
            "entryPoint": "candidates/fixtures/conforming/main.py",
            "implementationPaths": ["candidates/fixtures/conforming/main.py"],
        },
        "implementationDigest": _DIGEST,
        "configurationDigest": _DIGEST,
        "manifestDigest": _DIGEST,
        "source": "original-synthetic",
        "license": "Apache-2.0",
        "permittedUse": ["offline-harness-evaluation"],
        "prohibitedUse": [
            "model-training",
            "production-decision",
            "provider-execution",
            "state-mutation",
            "tenant-analysis",
        ],
        "executionRequirements": {
            "network": "prohibited",
            "determinism": "deterministic",
            "timeoutSeconds": 15,
            "maxStdoutBytes": 65536,
            "maxStderrBytes": 16384,
            "retries": 0,
        },
        "expectedDeterminism": "deterministic",
        "networkPolicy": "prohibited",
        "dataRetention": "no-retention",
        "reviewStatus": "accepted-by-principal-systems-architect",
    }


def test_track2_schema_ids_exclude_candidate_documents() -> None:
    assert len(SCHEMA_NAMES) == 5
    assert len(SCHEMA_IDS) == 5
    assert set(CANDIDATE_SCHEMA_NAMES).isdisjoint(SCHEMA_NAMES)
    assert len(CANDIDATE_SCHEMA_NAMES) == 6


def test_candidate_schemas_are_closed_and_versioned() -> None:
    with network_guard():
        for name in CANDIDATE_SCHEMA_NAMES:
            document = load_schema(name)
            assert document["additionalProperties"] is False
            assert document["$id"] == f"urn:patchpilot-intelligence-evals:schema:{name}:v1"
            assert document["properties"]["schemaVersion"]["const"] == "1.0.0"
            assert document["properties"]["protocolVersion"]["const"] == PROTOCOL_VERSION


def test_structural_examples_pass() -> None:
    validate("candidate-manifest", _manifest())
    validate("candidate-request", _request())
    validate("candidate-response", _success_response())
    validate("candidate-execution-result", _execution_result())
    validate("comparison-result", _comparison())
    validate("calibration-record", _calibration())


def test_request_omits_hidden_labels_and_leaves_the_case_unchanged() -> None:
    case = _case()
    before = canonical_dumps(case)
    request = build_request(case, _DIGEST)
    assert canonical_dumps(case) == before
    finding_input = request["findingExplanationInput"]
    for field in (
        "negativeControls",
        "goldSupportedClaims",
        "expectedCitations",
        "expectedRefusal",
        "category",
        "promptInjection",
    ):
        assert field not in finding_input
        assert field not in request
    assert "priorityAssignment" not in request
    assert "findingState" not in request


def test_request_id_is_stable_and_independent_of_assistance_text() -> None:
    first = _request()
    second = _request()
    assert first["requestId"] == second["requestId"]
    assert len(first["requestId"]) == 64
    assert first["findingExplanationInput"]["assistanceRequest"] not in first["requestId"]


def test_unknown_request_property_fails() -> None:
    request = _request()
    request["provider"] = "example"
    assert error_paths("candidate-request", request)


def test_missing_request_field_fails() -> None:
    request = _request()
    del request["caseId"]
    assert error_paths("candidate-request", request)


def test_state_mutation_and_provider_fields_fail() -> None:
    response = _success_response()
    response["priorityAssignment"] = "P1"
    assert error_paths("candidate-response", response)
    response = _success_response()
    response["findingState"] = "closed"
    assert error_paths("candidate-response", response)
    response = _success_response()
    response["model"] = "example"
    assert error_paths("candidate-response", response)
    response = _success_response()
    response["apiKey"] = "example"
    assert error_paths("candidate-response", response)


@pytest.mark.parametrize(
    "kind",
    ["model", "hosted-provider", "local-inference", "deterministic-baseline"],
)
def test_manifest_rejects_unauthorized_candidate_kinds(kind: str) -> None:
    manifest = _manifest()
    manifest["candidateKind"] = kind
    assert error_paths("candidate-manifest", manifest)


def test_success_unavailable_and_rejected_states() -> None:
    assert _classify(_success_response()) == "success"
    rejected = {
        "schemaVersion": "1.0.0",
        "protocolVersion": PROTOCOL_VERSION,
        "requestId": _request()["requestId"],
        "candidateId": _CANDIDATE_ID,
        "candidateVersion": _CANDIDATE_VERSION,
        "status": "rejected",
        "failure": {"category": "rejected", "message": "Synthetic test double rejected the case."},
    }
    unavailable = deepcopy(rejected)
    unavailable["status"] = "unavailable"
    unavailable["failure"] = {
        "category": "unavailable",
        "message": "Synthetic test double is unavailable.",
    }
    assert _classify(rejected) == "candidate-rejection"
    assert _classify(unavailable) == "candidate-unavailable"
    validate("candidate-response", rejected)
    validate("candidate-response", unavailable)


def test_protocol_request_and_identity_mismatches() -> None:
    response = _success_response()
    response["protocolVersion"] = "9.9.9"
    assert _classify(response) == "protocol-mismatch"
    response = _success_response()
    response["requestId"] = "b" * 64
    assert _classify(response) == "request-id-mismatch"
    response = _success_response()
    response["candidateId"] = "fixture-other"
    assert _classify(response) == "candidate-identity-mismatch"
    response = _success_response()
    response["candidateVersion"] = "2"
    assert _classify(response) == "candidate-identity-mismatch"
    response = _success_response()
    response["findingExplanationOutput"]["candidate"]["kind"] = "deterministic-baseline"
    response["findingExplanationOutput"]["explanationLabel"] = "deterministic-baseline-assistance"
    assert _classify(response) == "candidate-identity-mismatch"


def test_schema_invalid_explanation_and_canonical_bytes() -> None:
    response = _success_response()
    del response["findingExplanationOutput"]["nonAuthoritative"]
    assert _classify(response) == "schema-invalid-output"
    encoded = canonical_dumps(response).encode("utf-8")
    outcome, parsed = parse_candidate_stdout(encoded)
    assert outcome == "parsed"
    assert parsed == response


def test_malformed_and_multiple_outputs_fail() -> None:
    assert parse_candidate_stdout(b"")[0] == "malformed-output"
    assert parse_candidate_stdout(b"not-json")[0] == "malformed-output"
    assert parse_candidate_stdout(b"\xff")[0] == "malformed-output"
    pretty = json.dumps(_success_response(), indent=2).encode("utf-8")
    assert parse_candidate_stdout(pretty)[0] == "malformed-output"
    canonical = canonical_dumps({"schemaVersion": "1.0.0"}).encode("utf-8")
    assert parse_candidate_stdout(canonical + b"\n")[0] == "multiple-outputs"
    assert parse_candidate_stdout(canonical + canonical)[0] == "multiple-outputs"


def test_success_response_must_omit_failure() -> None:
    response = _success_response()
    response["failure"] = {"category": "rejected", "message": "not allowed"}
    with pytest.raises(SchemaValidationError):
        validate("candidate-response", response)


def test_comparison_rejects_a_winner_and_production_ready() -> None:
    comparison = _comparison()
    comparison["winner"] = _CANDIDATE_ID
    assert error_paths("comparison-result", comparison)
    comparison = _comparison()
    comparison["productionReady"] = True
    assert error_paths("comparison-result", comparison)


def test_execution_result_rejects_production_ready() -> None:
    result = _execution_result()
    result["productionReady"] = True
    assert error_paths("candidate-execution-result", result)


def test_failure_outcomes_exclude_success() -> None:
    assert "success" not in FAILURE_OUTCOMES
    assert set(FAILURE_OUTCOMES).issubset(
        set(load_schema("candidate-execution-result")["$defs"]["executionOutcome"]["enum"])
    )


def test_validate_request_rejects_a_tampered_digest() -> None:
    request = _request()
    request["findingExplanationInput"]["inputDigest"] = "c" * 64
    with pytest.raises(ProtocolError) as caught:
        validate_request(request)
    assert caught.value.code == "input-digest"
