"""Closed schema checks. Examples come from the synthetic corpus and small mutations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from patchpilot_intelligence_evals.baseline import run_baseline
from patchpilot_intelligence_evals.corpus import load_cases, to_candidate_input
from patchpilot_intelligence_evals.evaluator import evaluate_baseline, experiment_manifest
from patchpilot_intelligence_evals.schemas import (
    SCHEMA_NAMES,
    error_paths,
    load_schema,
    validate,
)


def _case() -> dict[str, Any]:
    return load_cases()[0]


def _output() -> dict[str, Any]:
    return run_baseline(_case())


def test_schemas_are_closed_and_versioned() -> None:
    for name in SCHEMA_NAMES:
        document = load_schema(name)
        assert document["additionalProperties"] is False
        assert document["$id"] == f"urn:patchpilot-intelligence-evals:schema:{name}:v1"
        assert document["properties"]["schemaVersion"]["const"] == "1.0.0"


def test_valid_examples_pass() -> None:
    case = _case()
    validate("evaluation-case", case)
    validate("finding-explanation-input", to_candidate_input(case))
    validate("finding-explanation-output", _output())
    result = evaluate_baseline()
    validate("evaluation-result", result)
    validate("experiment-manifest", experiment_manifest(result))


def test_unknown_property_fails() -> None:
    output = _output()
    output["extra"] = 1
    assert error_paths("finding-explanation-output", output)


def test_missing_required_field_fails() -> None:
    output = _output()
    del output["schemaVersion"]
    assert error_paths("finding-explanation-output", output)


def test_invalid_priority_authority_fails() -> None:
    output = _output()
    output["priorityAssignment"] = "P1"
    assert error_paths("finding-explanation-output", output)
    facts = deepcopy(output["preservedDeterministicFacts"])
    facts["priority"] = "P0"
    output = _output()
    output["preservedDeterministicFacts"] = facts
    assert error_paths("finding-explanation-output", output)


def test_invalid_tenant_reference_fails() -> None:
    case = _case()
    case["authorizedOrganizationId"] = "org-real-customer"
    assert error_paths("evaluation-case", case)


def test_malformed_citation_fails() -> None:
    output = _output()
    output["citations"] = ["evidence-synthetic-ground-001"]
    assert error_paths("finding-explanation-output", output)
    output = _output()
    output["citations"] = [{"evidenceId": "not-an-evidence-id"}]
    assert error_paths("finding-explanation-output", output)


def test_state_mutation_field_fails() -> None:
    output = _output()
    output["findingState"] = "closed"
    assert error_paths("finding-explanation-output", output)


def test_refusal_with_claim_fails() -> None:
    output = _output()
    output["refused"] = True
    output["refusalReason"] = "refused"
    assert error_paths("finding-explanation-output", output)


def test_future_candidate_label_is_allowed() -> None:
    output = _output()
    output["candidate"] = {
        "kind": "future-candidate",
        "name": "synthetic-future-candidate",
        "version": "0",
    }
    output["explanationLabel"] = "generated-explanation"
    validate("finding-explanation-output", output)


def test_production_ready_true_fails() -> None:
    result = evaluate_baseline()
    result["productionReady"] = True
    assert error_paths("evaluation-result", result)


def test_negative_controls_are_absent_from_input_schema() -> None:
    schema = load_schema("finding-explanation-input")
    assert "negativeControls" not in schema["properties"]


@pytest.mark.parametrize("name", list(SCHEMA_NAMES))
def test_schema_file_loads(name: str) -> None:
    assert load_schema(name)["title"]
