"""Track 9 memory-evidence review. Arithmetic is checked. Run is not called."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import ADDRESS_SPACE_BYTES, MeasurementError
from patchpilot_intelligence_evals.track9_review import (
    CEILING_BYTES,
    COLD_4096_PEAK_BYTES,
    COLD_8192_PEAK_BYTES,
    HEADROOM_BYTES,
    MEMORY_SOURCE_DIGEST,
    R1_SMOKE_PEAK_BYTES,
    WARM_4096_PEAK_BYTES,
    WARM_8192_PEAK_BYTES,
    common,
    load_record,
    seal,
)

SCHEMA_NAME = "memory-evidence-review"
_RECORD = "candidates/authorization/memory-evidence-review.json"
_PROHIBITED = frozenset(
    {
        "additional-provider",
        "concurrency",
        "different-precision",
        "larger-context",
        "longer-output",
        "production-capacity",
    }
)
_ALLOWED = frozenset({"approved-single-process"})


def require_headroom(ceiling: int, peak: int, headroom: int) -> None:
    """Accept only the measured ceiling, warm 8,192 peak, and exact headroom."""
    if ceiling != CEILING_BYTES or peak != WARM_8192_PEAK_BYTES:
        raise MeasurementError("memory-arithmetic")
    if ceiling - peak != headroom or headroom != HEADROOM_BYTES:
        raise MeasurementError("memory-arithmetic")
    if peak >= ceiling:
        raise MeasurementError("memory-arithmetic")


def reject_prohibited_inference(claim: str) -> None:
    """Refuse a memory claim outside the approved single-process scope."""
    if claim in _PROHIBITED or claim not in _ALLOWED:
        raise MeasurementError("memory-scope")


def require_memory(document: dict[str, Any]) -> None:
    """Bind the review to the measured peaks and the prohibited inferences."""
    peaks = (
        document["cold4096PeakBytes"],
        document["warm4096PeakBytes"],
        document["cold8192PeakBytes"],
        document["warm8192PeakBytes"],
    )
    if peaks != (
        COLD_4096_PEAK_BYTES,
        WARM_4096_PEAK_BYTES,
        COLD_8192_PEAK_BYTES,
        WARM_8192_PEAK_BYTES,
    ):
        raise MeasurementError("memory-arithmetic")
    maximum = max(peaks)
    require_headroom(document["ceilingBytes"], maximum, document["minimumHeadroomBytes"])
    if document["maximumMeasuredPeakBytes"] != maximum:
        raise MeasurementError("memory-arithmetic")
    if document["addressSpaceIsResidentCeiling"] is not False:
        raise MeasurementError("memory-scope")
    if ADDRESS_SPACE_BYTES != CEILING_BYTES * 2:
        raise MeasurementError("memory-scope")
    if document["concurrency"] != "prohibited":
        raise MeasurementError("memory-scope")
    if document["largerContext"] != "not-authorized":
        raise MeasurementError("memory-scope")
    if document["longerOutput"] != "not-authorized":
        raise MeasurementError("memory-scope")
    if document["productionCapacity"] != "not-established":
        raise MeasurementError("memory-scope")
    if document["r1ContextMemory"] != "unavailable":
        raise MeasurementError("memory-scope")
    if document["r1SmokePeakBytes"] != R1_SMOKE_PEAK_BYTES:
        raise MeasurementError("memory-scope")
    if document["reviewConclusion"] != "within-ceiling-with-limited-headroom":
        raise MeasurementError("memory-scope")
    if document["sourceMemoryConclusion"] != "within-ceiling":
        raise MeasurementError("memory-scope")
    if document["memoryGate4096"] != "passed" or document["memoryGate8192"] != "passed":
        raise MeasurementError("memory-scope")


def build_memory_evidence_review() -> dict[str, Any]:
    """Scope the accepted resident peaks. R1 smoke is not a context result."""
    document = {
        **common(),
        "additionalProviders": "not-authorized",
        "addressSpaceIsResidentCeiling": False,
        "batchSize": 1,
        "ceilingBytes": CEILING_BYTES,
        "cold4096PeakBytes": COLD_4096_PEAK_BYTES,
        "cold8192PeakBytes": COLD_8192_PEAK_BYTES,
        "concurrency": "prohibited",
        "differentPrecision": "not-authorized",
        "headroomAssessment": "limited",
        "headroomClass": "limited",
        "largerContext": "not-authorized",
        "longerOutput": "not-authorized",
        "maximumMeasuredPeakBytes": WARM_8192_PEAK_BYTES,
        "memoryGate4096": "passed",
        "memoryGate8192": "passed",
        "minimumHeadroomBytes": HEADROOM_BYTES,
        "oneCandidateProcess": "mandatory",
        "oom": False,
        "productionCapacity": "not-established",
        "r1ContextMemory": "unavailable",
        "r1SmokeEvidenceRole": "smoke-only",
        "r1SmokePeakBytes": R1_SMOKE_PEAK_BYTES,
        "reviewConclusion": "within-ceiling-with-limited-headroom",
        "sourceIdentityDigest": MEMORY_SOURCE_DIGEST,
        "sourceMemoryConclusion": "within-ceiling",
        "warm4096PeakBytes": WARM_4096_PEAK_BYTES,
        "warm8192PeakBytes": WARM_8192_PEAK_BYTES,
        "warmRss": "unavailable",
    }
    require_memory(document)
    return seal(document, SCHEMA_NAME)


def load_memory_evidence_review() -> dict[str, Any]:
    """Return the committed memory review."""
    return load_record(_RECORD, build_memory_evidence_review)
