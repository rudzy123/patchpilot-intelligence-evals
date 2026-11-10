"""Track 6 acquisition decision. Authorization does not acquire or execute a model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_cache import load_cache_policy
from patchpilot_intelligence_evals.artifact_verification import load_verification_template
from patchpilot_intelligence_evals.evidence_closure import load_closure
from patchpilot_intelligence_evals.isolation_profile import has_acquisition_blocker, load_profile
from patchpilot_intelligence_evals.protocol import (
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    PROTOCOL_VERSION,
    TIMEOUT_SECONDS,
)
from patchpilot_intelligence_evals.runtime_authorization import (
    load_authorization as load_runtime_authorization,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

PREREQUISITES: tuple[str, ...] = (
    "one-qualifying-candidate",
    "one-authorized-runtime",
    "cache-and-verification",
    "isolation-without-acquisition-blocker",
    "hardware-fit",
    "immutable-revision-and-source",
    "tokenizer-provenance",
    "weight-license-and-commercial-use",
    "redistribution-unnecessary",
    "no-gate-change",
)
_STATEMENTS: dict[str, str] = {
    "one-qualifying-candidate": "No pinned candidate passes every mandatory criterion.",
    "one-authorized-runtime": "The runtime decision is no-runtime.",
    "cache-and-verification": "Cache validation or artifact verification is not available.",
    "isolation-without-acquisition-blocker": (
        "The isolation profile still has an acquisition blocker."
    ),
    "hardware-fit": "The recorded hardware envelope is outside the Track 4 limits.",
    "immutable-revision-and-source": (
        "No qualifying candidate has an immutable revision and official source."
    ),
    "tokenizer-provenance": "Tokenizer provenance is not resolved for a qualifying candidate.",
    "weight-license-and-commercial-use": (
        "Weight license and commercial use are not both resolved for a qualifying candidate."
    ),
    "redistribution-unnecessary": (
        "A qualifying candidate has not shown that redistribution is unnecessary."
    ),
    "no-gate-change": (
        "Authorization would require a corpus, metric, gate, or fixture-limit change."
    ),
}
_RECORD = Path("candidates/authorization/track6-acquisition-authorization.json")
_HARDWARE = Path("candidates/authorization/evaluation-hardware-profile.json")
_ARTIFACT_LIMIT = 8589934592
_PEAK_MEMORY_LIMIT = 12884901888


class AcquisitionError(ValueError):
    """A Track 6 check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_authorization(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one authorization decision, including an in-memory example."""
    validate("track6-acquisition-authorization", document)
    if document["locallyObservedArtifactDigests"]:
        raise AcquisitionError("local-digest")
    identifiers = [str(item["prerequisiteId"]) for item in document["prerequisites"]]
    if identifiers != list(PREREQUISITES):
        raise AcquisitionError("prerequisite-set")
    failed = [
        str(item["prerequisiteId"])
        for item in document["prerequisites"]
        if item["status"] != "pass"
    ]
    blockers = [str(item["prerequisiteId"]) for item in document["blockers"]]
    if blockers != failed:
        raise AcquisitionError("blocker-mismatch")
    for blocker in document["blockers"]:
        if blocker["statement"] != _STATEMENTS[str(blocker["prerequisiteId"])]:
            raise AcquisitionError("blocker-statement")
    gate_failed = "no-gate-change" in failed
    if bool(document["gatesChanged"]) is not gate_failed:
        raise AcquisitionError("gate-flag")
    authorized = document["authorizationOutcome"] == "authorized"
    if authorized is not (not failed):
        raise AcquisitionError("outcome")
    if authorized and document["selectedModelId"] is None:
        raise AcquisitionError("selection")
    return document


def decide(
    prerequisites: dict[str, bool],
    identity: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Authorize only when every prerequisite passes. Otherwise withhold."""
    if set(prerequisites) != set(PREREQUISITES):
        raise AcquisitionError("prerequisite-set")
    if any(not isinstance(prerequisites[name], bool) for name in PREREQUISITES):
        raise AcquisitionError("prerequisite-set")
    failed = [name for name in PREREQUISITES if prerequisites[name] is False]
    authorized = not failed
    if authorized and identity is None:
        raise AcquisitionError("missing-identity")
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "retrievedOn": "2026-11-10",
        "authorizationOutcome": "authorized" if authorized else "not-authorized",
        "selectionOutcome": "selected" if authorized else "no-selection",
        "selectedModelId": identity["modelId"] if authorized and identity is not None else None,
        "runtimeId": identity["runtimeId"] if authorized and identity is not None else None,
        "immutableRevision": (
            identity["revision"] if authorized and identity is not None else None
        ),
        "prerequisites": [
            {"prerequisiteId": name, "status": "pass" if prerequisites[name] else "fail"}
            for name in PREREQUISITES
        ],
        "blockers": [{"prerequisiteId": name, "statement": _STATEMENTS[name]} for name in failed],
        "gatesChanged": "no-gate-change" in failed,
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
    }
    return validate_authorization(document)


def current_prerequisites() -> dict[str, bool]:
    """Read the committed boundary and return each prerequisite as a boolean."""
    closure = load_closure()
    runtime = load_runtime_authorization()
    qualified = (
        closure["qualifyingCandidateCount"] == 1 and closure["selectionOutcome"] == "selected"
    )
    runtime_ready = (
        runtime["authorizationOutcome"] == "authorized" and runtime["runtimeId"] is not None
    )
    return {
        "one-qualifying-candidate": qualified,
        "one-authorized-runtime": runtime_ready,
        "cache-and-verification": _cache_ready(),
        "isolation-without-acquisition-blocker": not has_acquisition_blocker(),
        "hardware-fit": _hardware_fits(),
        "immutable-revision-and-source": qualified and closure["selectedModelId"] is not None,
        "tokenizer-provenance": qualified,
        "weight-license-and-commercial-use": qualified,
        "redistribution-unnecessary": qualified,
        "no-gate-change": _gates_unchanged(),
    }


def load_track6_authorization(root: Path | None = None) -> dict[str, Any]:
    """Load the committed decision and require it to match the current boundary."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AcquisitionError("record-type")
    document = validate_authorization(loaded)
    if document != decide(current_prerequisites()):
        raise AcquisitionError("authorization-drift")
    return document


def _cache_ready() -> bool:
    policy = load_cache_policy()
    template = load_verification_template()
    return (
        policy["promotionRequiresCompleteVerification"] is True
        and policy["acquisitionStatus"] == "not-acquired"
        and template["verificationState"] == "not-acquired"
        and template["acquisitionStatus"] == "not-acquired"
    )


def _hardware_fits() -> bool:
    loaded = json.loads((repo_root() / _HARDWARE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return False
    validate("evaluation-hardware-profile", loaded)
    envelope = loaded["resourceEnvelope"]
    memory_bytes = int(loaded["totalMemoryKib"]) * 1024
    storage_floor = int(envelope["maximumArtifactBytes"]) * int(
        envelope["minimumFreeStorageMultiple"]
    )
    return (
        loaded["operatingSystemFamily"] == "Linux"
        and loaded["cpuArchitecture"] == "x86_64"
        and loaded["gpuAvailability"] == "unavailable"
        and envelope["gpuRequired"] is False
        and envelope["quantizationApproved"] is False
        and envelope["maximumArtifactBytes"] == _ARTIFACT_LIMIT
        and envelope["maximumPeakProcessMemoryBytes"] == _PEAK_MEMORY_LIMIT
        and envelope["maximumContextTokens"] == 8192
        and envelope["timeoutSeconds"] == TIMEOUT_SECONDS
        and memory_bytes >= _PEAK_MEMORY_LIMIT
        and int(loaded["availableStorageBytes"]) >= storage_floor
    )


def _gates_unchanged() -> bool:
    profile = load_profile()
    return (
        PROTOCOL_VERSION == "1.0.0"
        and TIMEOUT_SECONDS == 15
        and MAX_STDOUT_BYTES == 65536
        and MAX_STDERR_BYTES == 16384
        and profile["fixtureTimeoutSeconds"] == 15
    )
