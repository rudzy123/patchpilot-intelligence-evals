"""Legal, provenance, and model-card decisions for Track 7 finalists.

A clear restriction is a pass on the clarity criteria. Unknown terms fail.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
    decide_candidate_discovery,
    evidence,
)
from patchpilot_intelligence_evals.candidate_eligibility import (
    MANDATORY,
    RETRIEVED_ON,
    EligibilityError,
    weighted_score,
)
from patchpilot_intelligence_evals.finalist_budget import decide_finalist_budget
from patchpilot_intelligence_evals.finalist_onnx import decide_finalist_onnx
from patchpilot_intelligence_evals.finalist_tokenizer import decide_finalist_tokenizer
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/finalist-eligibility.json")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_CLEAR = frozenset({"granted", "restricted", "not-granted"})
_INSTRUMENTS = frozenset({"revision-license-file", "separate-instrument"})
_SOURCE_LICENSE = (
    f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/{LFM_SOURCE_REVISION}/LICENSE"
)
_CARD = f"https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/{LFM_SOURCE_REVISION}/README.md"


class FinalistEligibilityError(ValueError):
    """An eligibility record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def grant_result(value: str) -> str:
    """A named grant is clear. Unresolved and any other token fail."""
    return "pass" if value in _CLEAR else "fail"


def mandatory_map(
    *,
    license_instrument: str,
    commercial_grant: str,
    redistribution_grant: str,
    remote_code_required: bool,
    hosted_api_required: bool,
    telemetry_required: bool,
    official_card: bool,
    known_limitations: str,
    reliability_limitations: str,
    tokenizer_pass: bool,
    digest_pass: bool,
    hardware_pass: bool,
    execution_pass: bool,
    revision_fixed: bool,
) -> dict[str, str]:
    """Map recorded facts onto the existing mandatory criteria."""
    limitations = known_limitations == "stated" and reliability_limitations == "stated"
    offline = not hosted_api_required and not telemetry_required
    return {
        "explicit-weight-use-license": ("pass" if license_instrument in _INSTRUMENTS else "fail"),
        "clear-commercial-use-position": grant_result(commercial_grant),
        "clear-redistribution-position": grant_result(redistribution_grant),
        "immutable-official-revision": "pass" if revision_fixed else "fail",
        "no-remote-code-requirement": "fail" if remote_code_required else "pass",
        "fully-offline-runtime-support": "pass" if offline else "fail",
        "tokenizer-provenance": "pass" if tokenizer_pass else "fail",
        "artifact-digest-capability": "pass" if digest_pass else "fail",
        "local-resource-fit": "pass" if hardware_pass else "fail",
        "bounded-subprocess-compatibility": "pass" if execution_pass else "fail",
        "no-mandatory-telemetry": "fail" if telemetry_required else "pass",
        "no-tenant-data-requirement": "pass",
        "official-model-card": "pass" if official_card else "fail",
        "documented-limitations": "pass" if limitations else "fail",
        "no-production-dependency": "pass",
    }


def decide_finalist_eligibility() -> dict[str, Any]:
    """Build the committed legal decision for the discovery finalist."""
    _require_finalist()
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "finalistCount": 1,
        "finalistModelIds": [LFM_MODEL_ID],
        "locallyObservedArtifactDigests": [],
        "finalists": [_lfm()],
    }
    return validate_finalist_eligibility(document)


def validate_finalist_eligibility(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one finalist eligibility record."""
    validate("finalist-eligibility", document)
    if contains_private_marker(document):
        raise FinalistEligibilityError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise FinalistEligibilityError("local-digest")
    _require_finalist(document["finalistModelIds"])
    finalists = document["finalists"]
    if [item["modelId"] for item in finalists] != document["finalistModelIds"]:
        raise FinalistEligibilityError("finalist-boundary")
    if document["finalistCount"] != len(finalists):
        raise FinalistEligibilityError("finalist-count")
    for item in finalists:
        if item["mandatoryCriteria"] != _criteria_for(item):
            raise FinalistEligibilityError("mandatory-criteria")
        if not _score_matches(item):
            raise FinalistEligibilityError("weighted-score")
        if item["unresolvedConflict"] is not _unresolved(item):
            raise FinalistEligibilityError("conflict")
        if not _revision_applicable(item):
            raise FinalistEligibilityError("revision")
        if not _evidence_ok(item):
            raise FinalistEligibilityError("evidence")
    return document


def load_finalist_eligibility(root: Path | None = None) -> dict[str, Any]:
    """Load the committed eligibility record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise FinalistEligibilityError("record-type")
    document = validate_finalist_eligibility(loaded)
    if document != decide_finalist_eligibility():
        raise FinalistEligibilityError("eligibility-drift")
    return document


def _criteria_for(item: dict[str, Any]) -> dict[str, str]:
    tokenizer = decide_finalist_tokenizer()["finalists"][0]
    budget = decide_finalist_budget()["finalists"][0]
    onnx = decide_finalist_onnx()["finalists"][0]
    if tokenizer["modelId"] != item["modelId"] or budget["modelId"] != item["modelId"]:
        raise FinalistEligibilityError("finalist-boundary")
    weights = [
        entry
        for entry in onnx["files"]
        if entry["selected"] and entry["role"] in {"graph", "external-data"}
    ]
    digest_pass = bool(weights) and all(entry["publishedSha256"] for entry in weights)
    revision_fixed = bool(_SHA.fullmatch(item["revision"])) and bool(
        _SHA.fullmatch(item["onnxRevision"])
    )
    return mandatory_map(
        license_instrument=item["licenseInstrument"],
        commercial_grant=item["commercialGrant"],
        redistribution_grant=item["redistributionGrant"],
        remote_code_required=item["remoteCodeRequired"],
        hosted_api_required=item["hostedApiRequired"],
        telemetry_required=item["telemetryRequired"],
        official_card=item["officialCard"],
        known_limitations=item["knownLimitations"],
        reliability_limitations=item["reliabilityLimitations"],
        tokenizer_pass=tokenizer["eligibilityOutcome"] == "pass",
        digest_pass=digest_pass,
        hardware_pass=budget["hardwareFit"] == "pass",
        execution_pass=budget["executionOutcome"] == "pass",
        revision_fixed=revision_fixed,
    )


def _score_matches(item: dict[str, Any]) -> bool:
    criteria = item["mandatoryCriteria"]
    if set(criteria) != set(MANDATORY):
        return False
    failures = [name for name in MANDATORY if criteria[name] != "pass"]
    passed = not failures
    if item["disqualifiers"] != sorted(failures):
        return False
    if item["mandatoryStatus"] != ("pass" if passed else "fail"):
        return False
    if item["scoringEligible"] is not passed:
        return False
    if item["commercialUseResult"] != grant_result(item["commercialGrant"]):
        return False
    if item["redistributionResult"] != grant_result(item["redistributionGrant"]):
        return False
    if item["modificationResult"] != grant_result(item["modificationGrant"]):
        return False
    if not passed:
        return item["weightedScore"] is None and item["categoryScores"] is None
    try:
        score = weighted_score(criteria, item["categoryScores"])
    except EligibilityError as exc:
        raise FinalistEligibilityError(exc.code) from exc
    matched: bool = item["weightedScore"] == score
    return matched


def _unresolved(item: dict[str, Any]) -> bool:
    grants = (
        item["commercialGrant"],
        item["redistributionGrant"],
        item["modificationGrant"],
    )
    if any(grant not in _CLEAR for grant in grants):
        return True
    return any(conflict["status"] == "unresolved" for conflict in item["conflicts"])


def _revision_applicable(item: dict[str, Any]) -> bool:
    allowed = {item["revision"], item["onnxRevision"]}
    for entry in item["evidence"]:
        revision = entry["immutableRevision"]
        if revision is not None and revision not in allowed:
            return False
    return True


def _evidence_ok(item: dict[str, Any]) -> bool:
    classes = set()
    ids = set()
    for entry in item["evidence"]:
        classes.add(entry["evidenceClass"])
        ids.add(entry["evidenceId"])
        if entry["applicability"] != item["modelId"]:
            return False
        if '"' in entry["claim"] or "'" in entry["claim"]:
            return False
    if "authoritative" not in classes or "lfm-weight-license" not in ids:
        return False
    for conflict in item["conflicts"]:
        if '"' in conflict["summary"] or "'" in conflict["summary"]:
            return False
        if conflict["status"] == "unresolved" and conflict["disposition"] != "unresolved":
            return False
    return True


def _require_finalist(model_ids: list[str] | None = None) -> None:
    expected = decide_candidate_discovery()["finalistModelIds"]
    if expected != [LFM_MODEL_ID]:
        raise FinalistEligibilityError("finalist-boundary")
    if model_ids is not None and model_ids != expected:
        raise FinalistEligibilityError("finalist-boundary")


def _lfm() -> dict[str, Any]:
    row: dict[str, Any] = {
        "modelId": LFM_MODEL_ID,
        "revision": LFM_SOURCE_REVISION,
        "onnxRevision": LFM_ONNX_REVISION,
        "publisher": "Liquid AI",
        "sourceCodeLicense": "LFM Open License v1.0",
        "weightLicense": "LFM Open License v1.0",
        "licenseInstrument": "revision-license-file",
        "commercialGrant": "restricted",
        "redistributionGrant": "granted",
        "modificationGrant": "granted",
        "attributionRequired": True,
        "revenueThresholdUsd": 10000000,
        "intendedUse": "agentic tasks, data extraction, and retrieval augmented generation",
        "excludedUse": "knowledge-intensive tasks and programming are not recommended",
        "knownLimitations": "stated",
        "languageLimitations": "stated",
        "safetyLimitations": "not-stated",
        "reliabilityLimitations": "stated",
        "remoteCodeRequired": False,
        "hostedApiRequired": False,
        "telemetryRequired": False,
        "officialCard": True,
        "conflicts": [
            {
                "conflictId": "trust-remote-code-example",
                "status": "resolved",
                "disposition": "restrictive-reading",
                "summary": (
                    "The ONNX quickstart sets trust_remote_code, and the pinned trees "
                    "contain no custom Python module. The flag is not a load requirement."
                ),
            },
            {
                "conflictId": "published-memory-figures",
                "status": "resolved",
                "disposition": "restrictive-reading",
                "summary": (
                    "Sub-1GB figures are tied to NPU and Q4_0 rows and do not establish "
                    "FP32 ONNX peak memory."
                ),
            },
            {
                "conflictId": "safety-limitations",
                "status": "unresolved",
                "disposition": "unresolved",
                "summary": (
                    "The card states a knowledge-task limitation and does not state "
                    "safety limitations."
                ),
            },
        ],
        "evidence": [
            evidence(
                "lfm-weight-license",
                "LFM2.5 source LICENSE file",
                _SOURCE_LICENSE,
                "Liquid AI",
                LFM_SOURCE_REVISION,
                (
                    "The pinned LICENSE is LFM Open License v1.0 from Liquid AI, Inc. "
                    "It grants reproduction and distribution subject to a commercial "
                    "condition of 10000000 USD annual revenue, plus attribution duties."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "none",
            ),
            evidence(
                "lfm-model-card",
                "LFM2.5-1.2B-Instruct model card",
                _CARD,
                "Liquid AI",
                LFM_SOURCE_REVISION,
                (
                    "The pinned card states intended agentic, extraction, and retrieval "
                    "uses, and it states that knowledge-intensive tasks and programming "
                    "are not recommended. It does not state safety limitations."
                ),
                "authoritative",
                LFM_MODEL_ID,
                "none",
            ),
        ],
    }
    row["commercialUseResult"] = grant_result(row["commercialGrant"])
    row["redistributionResult"] = grant_result(row["redistributionGrant"])
    row["modificationResult"] = grant_result(row["modificationGrant"])
    row["remoteCodeResult"] = "fail" if row["remoteCodeRequired"] else "pass"
    limitations = row["knownLimitations"] == "stated" and row["reliabilityLimitations"] == "stated"
    row["modelCardLimitationsResult"] = "pass" if limitations else "fail"
    criteria = _criteria_for(row)
    failures = [name for name in MANDATORY if criteria[name] != "pass"]
    row["mandatoryCriteria"] = criteria
    row["disqualifiers"] = sorted(failures)
    row["mandatoryStatus"] = "pass" if not failures else "fail"
    row["scoringEligible"] = not failures
    row["weightedScore"] = None
    row["categoryScores"] = None
    row["unresolvedConflict"] = _unresolved(row)
    return row
