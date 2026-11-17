"""Track 9 evaluation evidence inventory. This module does not call Run."""

from __future__ import annotations

from collections import Counter
from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError, sha256_file
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track9_review import (
    BEHAVIOR_SOURCE_DIGEST,
    FORENSICS_SOURCE_DIGEST,
    MEMORY_SOURCE_DIGEST,
    PLAN_DIGEST,
    PRIOR_PLAN_DIGEST,
    PROPORTIONALITY_SOURCE_DIGEST,
    R2_ATTEMPT_DIGEST,
    R2_CGROUP_DIGEST,
    R2_DISPOSITION_DIGEST,
    R2_REVIEW_DIGEST,
    R2_TRACK9_DIGEST,
    common,
    load_record,
    seal,
)

SCHEMA_NAME = "evaluation-evidence-inventory"
_RECORD = "candidates/authorization/evaluation-evidence-inventory.json"
_NARRATIVE = "docs/provenance/track8b-r2-measurement-evidence.md"
_CLASSES = (
    "candidate-evidence",
    "measurement-infrastructure-evidence",
    "security-boundary-evidence",
    "unresolved",
    "not-applicable",
)
_ROWS: tuple[tuple[str, str, str, str, bool, bool, bool, bool, bool], ...] = (
    (
        "track8b-plan-file",
        "candidates/authorization/measurement-plan.json",
        PRIOR_PLAN_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        True,
    ),
    (
        "track8b-plan-consumed",
        "candidates/authorization/track8b-plan-disposition.json",
        "ee3d55af35764bc67df4926060c30a3636c36b0d895119d3342ad12cba2e6238",
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-tokenizer-stop",
        "candidates/authorization/track8b-stopped-attempt.json",
        "23e845298c7b37f74ca04dea30ad4095e68ebfc69cfae8ae2681ce5ff3631a82",
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        True,
    ),
    (
        "track8b-template-compatibility",
        "candidates/authorization/track8b-template-compatibility-defect.json",
        "657a22d553828bc8128a993211eacd92a64502818426f147e5b37e914fe3cc19",
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        False,
    ),
    (
        "track8b-operator-approval",
        "candidates/authorization/measurement-operator-approval.json",
        "507f64153ad7afd6c90da0d6627bcb902ed94e9e4eee9f84bb19ee3834462dee",
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-readiness",
        "candidates/authorization/track9-readiness.json",
        "8fc85f5531cc7035d7cd7fa9f2951c6ce898c4e9bcb883fb77185d7517d9c298",
        "not-applicable",
        False,
        False,
        False,
        False,
        True,
    ),
    (
        "track8b-r1-plan-file",
        "candidates/authorization/measurement-retry-plan.json",
        "572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b",
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        True,
    ),
    (
        "track8b-r1-plan-consumed",
        "candidates/authorization/track8b-r1-plan-disposition.json",
        "6e6f77ee4e535b0897ddf537ec32eca3a245ea7a589d78ac93f8bf15c7f17873",
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-r1-operator-approval",
        "candidates/authorization/measurement-retry-approval.json",
        "be0dad3c725b20aa2ae7c12fb0c94b510ddbb8089f40dbc99dd1197b83c07d01",
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-r1-inference-stop",
        "candidates/authorization/track8b-r1-stopped-attempt.json",
        "05526ca57f2eaecbc1152fc0b0cce22f0f2fc46c8ed138aa7cb8b9a2044764e0",
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        True,
    ),
    (
        "track8b-r1-dependency-mount",
        "candidates/authorization/track8b-r1-dependency-mount-defect.json",
        "29678d3ac6e679585df8ea8e7ab360246e0528f82d6f92f45a9dd493128da3c4",
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        False,
    ),
    (
        "track8b-r1-memory-unavailable",
        "candidates/authorization/track8b-r1-memory-conclusion-defect.json",
        "a70007aee400f531448bd0456dcc52e08ea9a58457d84473de7eeafb3da617ec",
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-r1-readiness-template",
        "candidates/authorization/retry-track9-readiness.json",
        "4235efdbebbff1b5f3ffaa2291f8524f8cf4826c5a3a6901126f1e3d7cea4f09",
        "not-applicable",
        False,
        False,
        False,
        False,
        True,
    ),
    (
        "track8b-r1-readiness-stopped",
        "candidates/authorization/track8b-r1-stopped-track9-readiness.json",
        "e62c83bd62776202f830309eed985e9982ebe5fee66d356278b42556d2eb2824",
        "not-applicable",
        False,
        False,
        False,
        False,
        True,
    ),
    (
        "track8b-r2-plan-file",
        "candidates/authorization/inference-retry-plan.json",
        PLAN_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        True,
    ),
    (
        "track8b-r2-plan-consumed",
        "candidates/authorization/track8b-r2-plan-disposition.json",
        R2_DISPOSITION_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        True,
    ),
    (
        "track8b-r2-operator-approval",
        "candidates/authorization/inference-retry-approval.json",
        "61f14e11f0451d41f1d59783ccaa0bce873525f902bff2f4ba5fcb8ee0aa3f8c",
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-r2-stopped-attempt",
        "candidates/authorization/track8b-r2-stopped-attempt.json",
        R2_ATTEMPT_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        True,
        True,
        True,
        True,
    ),
    (
        "track8b-r2-accepted-memory",
        "candidates/authorization/track8b-r2-memory-conclusion.json",
        MEMORY_SOURCE_DIGEST,
        "candidate-evidence",
        True,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-r2-limited-headroom",
        "candidates/authorization/track8b-r2-memory-conclusion.json",
        MEMORY_SOURCE_DIGEST,
        "candidate-evidence",
        True,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-r2-cgroup-sampling",
        "candidates/authorization/track8b-r2-cgroup-sampling-defect.json",
        R2_CGROUP_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        False,
    ),
    (
        "track8b-r2-network-denial",
        "candidates/authorization/track8b-r2-cgroup-sampling-defect.json",
        R2_CGROUP_DIGEST,
        "security-boundary-evidence",
        False,
        True,
        False,
        True,
        False,
    ),
    (
        "track8b-r2-unsealed-launch",
        "candidates/authorization/track8b-r2-cgroup-sampling-defect.json",
        R2_CGROUP_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        True,
        True,
        True,
        False,
    ),
    (
        "track8b-r2-schema-forensics",
        "candidates/authorization/track8b-r2-schema-forensics.json",
        FORENSICS_SOURCE_DIGEST,
        "unresolved",
        False,
        False,
        True,
        True,
        True,
    ),
    (
        "track8b-r2-raw-output-absent",
        "candidates/authorization/track8b-r2-schema-forensics.json",
        FORENSICS_SOURCE_DIGEST,
        "unresolved",
        False,
        False,
        True,
        True,
        True,
    ),
    (
        "track8b-r2-behavioral-interpretation",
        "candidates/authorization/track8b-r2-behavioral-interpretation.json",
        BEHAVIOR_SOURCE_DIGEST,
        "unresolved",
        False,
        False,
        True,
        True,
        True,
    ),
    (
        "track8b-r2-metrics-absent",
        "candidates/authorization/track8b-r2-behavioral-interpretation.json",
        BEHAVIOR_SOURCE_DIGEST,
        "unresolved",
        False,
        False,
        True,
        True,
        True,
    ),
    (
        "track8b-r2-comparison-withheld",
        "candidates/authorization/track8b-r2-behavioral-interpretation.json",
        BEHAVIOR_SOURCE_DIGEST,
        "not-applicable",
        False,
        False,
        False,
        False,
        True,
    ),
    (
        "track8b-r2-proportionality-review",
        "candidates/authorization/track8b-r2-proportionality-review.json",
        PROPORTIONALITY_SOURCE_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        False,
        False,
        True,
        True,
    ),
    (
        "track8b-r2-readiness-template",
        "candidates/authorization/inference-retry-track9-readiness.json",
        "2b9e4b238af00dabea717ed95ff8fd5f79cd6af0f57553100f42692bfd8e72e2",
        "not-applicable",
        False,
        False,
        False,
        False,
        True,
    ),
    (
        "track8b-r2-readiness-stopped",
        "candidates/authorization/track8b-r2-stopped-track9-readiness.json",
        R2_TRACK9_DIGEST,
        "not-applicable",
        False,
        False,
        False,
        False,
        True,
    ),
    (
        "track8b-r2-dynamic-link-precheck",
        "candidates/authorization/track8b-r2-stopped-track9-readiness.json",
        R2_TRACK9_DIGEST,
        "security-boundary-evidence",
        False,
        True,
        False,
        True,
        False,
    ),
    (
        "track8b-r2-dependency-closure",
        "candidates/authorization/track8b-r2-stopped-track9-readiness.json",
        R2_TRACK9_DIGEST,
        "measurement-infrastructure-evidence",
        False,
        True,
        False,
        True,
        False,
    ),
    (
        "track8b-r2-implementation-review",
        "candidates/authorization/track8b-r2-implementation-review.json",
        R2_REVIEW_DIGEST,
        "measurement-infrastructure-evidence",
        True,
        True,
        True,
        True,
        True,
    ),
    (
        "track8b-r2-no-r3",
        "candidates/authorization/track8b-r2-plan-disposition.json",
        R2_DISPOSITION_DIGEST,
        "not-applicable",
        False,
        False,
        False,
        True,
        True,
    ),
)


def _item(row: tuple[str, str, str, str, bool, bool, bool, bool, bool]) -> dict[str, Any]:
    return {
        "evidenceClass": row[3],
        "itemId": row[0],
        "sourceIdentityDigest": row[2],
        "sourceRecord": row[1],
        "supportsBehavior": row[6],
        "supportsContinuation": row[7],
        "supportsDisposition": row[8],
        "supportsExecution": row[5],
        "supportsMemory": row[4],
    }


def narrative_digest() -> str:
    """Digest the committed R2 narrative. The external result root is not read."""
    return sha256_file(repo_root() / _NARRATIVE)


def items() -> list[dict[str, Any]]:
    """Material Track 8B, R1, and R2 findings in a stable order."""
    rows = [_item(row) for row in _ROWS]
    rows.append(
        {
            "evidenceClass": "security-boundary-evidence",
            "itemId": "track8b-r2-phase-boundary",
            "sourceIdentityDigest": narrative_digest(),
            "sourceRecord": _NARRATIVE,
            "supportsBehavior": False,
            "supportsContinuation": True,
            "supportsDisposition": False,
            "supportsExecution": True,
            "supportsMemory": False,
        }
    )
    return rows


def require_inventory(document: dict[str, Any]) -> None:
    """Refuse a duplicate, unclassified, or self-citing inventory."""
    found = [item["itemId"] for item in document["items"]]
    if len(found) != len(set(found)):
        raise MeasurementError("inventory-duplicate")
    counts: Counter[str] = Counter(item["evidenceClass"] for item in document["items"])
    if set(document["evidenceClassCounts"]) != set(_CLASSES):
        raise MeasurementError("inventory-class")
    for name in _CLASSES:
        if counts[name] < 1 or document["evidenceClassCounts"][name] != counts[name]:
            raise MeasurementError("inventory-class")
    if document["itemCount"] != len(document["items"]):
        raise MeasurementError("inventory-incomplete")
    candidate = {
        item["itemId"]
        for item in document["items"]
        if item["evidenceClass"] == "candidate-evidence"
    }
    if candidate != {"track8b-r2-accepted-memory", "track8b-r2-limited-headroom"}:
        raise MeasurementError("inventory-class")
    memory = _one(document, "track8b-r1-memory-unavailable")
    if memory["supportsMemory"] is not False:
        raise MeasurementError("inventory-class")
    forensics = _one(document, "track8b-r2-schema-forensics")
    if forensics["evidenceClass"] != "unresolved":
        raise MeasurementError("inventory-class")
    if document["sealedRunFilesCommitted"] is not False:
        raise MeasurementError("inventory-incomplete")
    if document["externalResultRootsRead"] is not False:
        raise MeasurementError("inventory-incomplete")


def _one(document: dict[str, Any], item_id: str) -> dict[str, Any]:
    matches = [item for item in document["items"] if item["itemId"] == item_id]
    if len(matches) != 1:
        raise MeasurementError("inventory-incomplete")
    found = matches[0]
    if not isinstance(found, dict):
        raise MeasurementError("inventory-incomplete")
    return found


def build_evaluation_evidence_inventory() -> dict[str, Any]:
    """Closed inventory of committed evidence. No external root is copied."""
    rows = items()
    counts = {name: 0 for name in _CLASSES}
    for item in rows:
        counts[item["evidenceClass"]] += 1
    document = {
        **common(),
        "evidenceClassCounts": counts,
        "externalResultRootsModified": False,
        "externalResultRootsRead": False,
        "itemCount": len(rows),
        "items": rows,
        "r1SmokePeakCitedAsContext": False,
        "sealedRunFilesCommitted": False,
    }
    require_inventory(document)
    return seal(document, SCHEMA_NAME)


def load_evaluation_evidence_inventory() -> dict[str, Any]:
    """Return the committed inventory."""
    return load_record(_RECORD, build_evaluation_evidence_inventory)
