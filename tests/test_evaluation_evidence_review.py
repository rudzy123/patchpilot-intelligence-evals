"""Track 9 evidence inventory tests."""

import pytest

from patchpilot_intelligence_evals.evaluation_evidence_review import (
    build_evaluation_evidence_inventory,
    load_evaluation_evidence_inventory,
    narrative_digest,
)
from patchpilot_intelligence_evals.inference_retry_plan import CONSUMED_RETRY_PLAN_DIGEST
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, sha256_file
from patchpilot_intelligence_evals.schemas import TRACK9_SCHEMA_NAMES, load_schema, repo_root
from patchpilot_intelligence_evals.track8b_r2_records import PLAN_DIGEST, PRIOR_PLAN_DIGEST

_CLASSES = {
    "candidate-evidence",
    "measurement-infrastructure-evidence",
    "security-boundary-evidence",
    "unresolved",
    "not-applicable",
}


def test_inventory_matches_its_builder() -> None:
    document = load_evaluation_evidence_inventory()
    assert document == build_evaluation_evidence_inventory()
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False
    assert document["futurePlanDigest"] == "not-issued"
    assert document["planDigest"] == PLAN_DIGEST
    assert document["priorPlanDigest"] == PRIOR_PLAN_DIGEST
    assert document["consumedRetryPlanDigest"] == CONSUMED_RETRY_PLAN_DIGEST


def test_inventory_is_complete_and_classified() -> None:
    document = load_evaluation_evidence_inventory()
    identifiers = [item["itemId"] for item in document["items"]]
    assert len(identifiers) == len(set(identifiers)) == document["itemCount"]
    assert set(document["evidenceClassCounts"]) == _CLASSES
    assert sum(document["evidenceClassCounts"].values()) == document["itemCount"]
    candidate = {
        item["itemId"]
        for item in document["items"]
        if item["evidenceClass"] == "candidate-evidence"
    }
    assert candidate == {"track8b-r2-accepted-memory", "track8b-r2-limited-headroom"}
    memory = next(
        item for item in document["items"] if item["itemId"] == "track8b-r1-memory-unavailable"
    )
    assert memory["supportsMemory"] is False
    forensics = next(
        item for item in document["items"] if item["itemId"] == "track8b-r2-schema-forensics"
    )
    assert forensics["evidenceClass"] == "unresolved"
    assert document["sealedRunFilesCommitted"] is False
    assert document["externalResultRootsRead"] is False
    assert document["externalResultRootsModified"] is False
    assert document["r1SmokePeakCitedAsContext"] is False
    for item in document["items"]:
        assert not item["sourceRecord"].startswith("/")
        assert (repo_root() / item["sourceRecord"]).is_file()


def test_phase_narrative_digest_matches_the_committed_note() -> None:
    document = load_evaluation_evidence_inventory()
    narrative = next(
        item for item in document["items"] if item["itemId"] == "track8b-r2-phase-boundary"
    )
    path = repo_root() / narrative["sourceRecord"]
    assert narrative["sourceIdentityDigest"] == narrative_digest() == sha256_file(path)
    assert narrative["evidenceClass"] == "security-boundary-evidence"


def test_track9_schemas_pin_authority_and_consumed_plans() -> None:
    for name in TRACK9_SCHEMA_NAMES:
        schema = load_schema(name)
        assert schema["additionalProperties"] is False
        properties = schema["properties"]
        assert properties["productionReady"]["const"] is False
        assert properties["selectionOutcome"]["const"] == "no-selection"
        assert properties["calibrationStatus"]["const"] == "not-approved"
        assert properties["comparisonWinner"]["const"] is None
        assert properties["futurePlanDigest"]["const"] == "not-issued"
        assert properties["r3Plan"]["const"] == "not-issued"
        assert properties["currentExecutionAuthority"]["const"] is False
        assert properties["planDigest"]["const"] == PLAN_DIGEST
        assert properties["priorPlanDigest"]["const"] == PRIOR_PLAN_DIGEST
        assert properties["consumedRetryPlanDigest"]["const"] == CONSUMED_RETRY_PLAN_DIGEST
        assert properties["candidateModelId"]["const"] == "LiquidAI/LFM2.5-1.2B-Instruct"
        assert properties["runtimeVersionTag"]["const"] == "v1.31.1"


def test_no_r3_authorization_file_is_created() -> None:
    root = repo_root() / "candidates" / "authorization"
    assert list(root.glob("*r3*")) == []


def test_duplicate_inventory_is_rejected() -> None:
    from patchpilot_intelligence_evals.evaluation_evidence_review import require_inventory

    document = build_evaluation_evidence_inventory()
    document["items"].append(document["items"][0])
    with pytest.raises(MeasurementError) as caught:
        require_inventory(document)
    assert caught.value.code == "inventory-duplicate"
