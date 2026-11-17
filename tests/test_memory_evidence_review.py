"""Track 9 memory-review tests."""

import pytest

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.memory_evidence_review import (
    build_memory_evidence_review,
    load_memory_evidence_review,
    reject_prohibited_inference,
    require_headroom,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate
from patchpilot_intelligence_evals.track8b_r1_records import load_memory_defect
from patchpilot_intelligence_evals.track8b_r2_records import load_memory_conclusion


def test_memory_arithmetic_matches_the_accepted_record() -> None:
    review = load_memory_evidence_review()
    source = load_memory_conclusion()
    assert review == build_memory_evidence_review()
    assert review["ceilingBytes"] == source["ceilingBytes"] == 12_884_901_888
    assert review["cold4096PeakBytes"] == source["cold4096PeakBytes"] == 7_284_371_456
    assert review["warm4096PeakBytes"] == source["warm4096PeakBytes"] == 8_511_131_648
    assert review["cold8192PeakBytes"] == source["cold8192PeakBytes"] == 9_816_231_936
    assert review["warm8192PeakBytes"] == source["warm8192PeakBytes"] == 12_271_669_248
    assert review["minimumHeadroomBytes"] == source["minimumHeadroomBytes"] == 613_232_640
    assert review["ceilingBytes"] - review["maximumMeasuredPeakBytes"] == 613_232_640
    assert review["sourceMemoryConclusion"] == "within-ceiling"
    assert review["headroomAssessment"] == "limited"
    assert review["reviewConclusion"] == "within-ceiling-with-limited-headroom"
    assert review["memoryGate4096"] == "passed"
    assert review["memoryGate8192"] == "passed"
    assert review["concurrency"] == "prohibited"
    assert review["largerContext"] == "not-authorized"
    assert review["productionCapacity"] == "not-established"
    assert review["oneCandidateProcess"] == "mandatory"
    assert review["addressSpaceIsResidentCeiling"] is False
    assert review["comparisonWinner"] is None
    assert review["productionReady"] is False


def test_r1_smoke_peak_is_not_context_evidence() -> None:
    review = load_memory_evidence_review()
    defect = load_memory_defect()
    assert review["r1SmokePeakBytes"] == defect["smokePeakBytes"] == 46_288_896
    assert review["r1ContextMemory"] == "unavailable"
    assert review["r1SmokeEvidenceRole"] == "smoke-only"
    assert defect["correctedConclusion"] == "unavailable"


def test_wrong_headroom_is_rejected() -> None:
    with pytest.raises(MeasurementError) as caught:
        require_headroom(12_884_901_888, 12_271_669_248, 1)
    assert caught.value.code == "memory-arithmetic"


def test_prohibited_memory_inferences_are_rejected() -> None:
    reject_prohibited_inference("approved-single-process")
    for claim in (
        "concurrency",
        "larger-context",
        "longer-output",
        "production-capacity",
        "different-precision",
        "additional-provider",
    ):
        with pytest.raises(MeasurementError) as caught:
            reject_prohibited_inference(claim)
        assert caught.value.code == "memory-scope"


def test_schema_rejects_a_concurrency_claim() -> None:
    document = build_memory_evidence_review()
    document["concurrency"] = "allowed"
    with pytest.raises(SchemaValidationError):
        validate("memory-evidence-review", document)
