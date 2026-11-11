"""Track 6C readiness.

Ready requires a qualifying format path. The committed inputs withhold it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_format_resolution import (
    FormatResolutionError,
    validate_format_resolution,
)
from patchpilot_intelligence_evals.conversion_plan import (
    ConversionPlanError,
    validate_conversion_plan,
)
from patchpilot_intelligence_evals.runtime_adapter_contract import (
    AdapterError,
    validate_adapter_contract,
)
from patchpilot_intelligence_evals.runtime_cache import RuntimeCacheError, validate_runtime_policy
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/track6c-readiness.json")
_NOT_READY = "TRACK 6C CONTROLLED STAGING NOT READY"
_READY = "TRACK 6C CONTROLLED STAGING READY"


class Track6CReadinessError(ValueError):
    """A Track 6C readiness record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_track6c(
    format_resolution: dict[str, Any],
    conversion_plan: dict[str, Any],
    adapter: dict[str, Any],
    runtime_policy: dict[str, Any],
) -> dict[str, Any]:
    """Return ready only when a format path and the hardened contract both hold."""
    try:
        checked_format = validate_format_resolution(format_resolution)
        checked_plan = validate_conversion_plan(conversion_plan)
        checked_adapter = validate_adapter_contract(adapter)
        checked_runtime = validate_runtime_policy(runtime_policy)
    except (FormatResolutionError, ConversionPlanError, AdapterError, RuntimeCacheError) as exc:
        raise Track6CReadinessError(exc.code) from exc
    blockers = _blockers(checked_format, checked_plan, checked_adapter, checked_runtime)
    ready = not blockers
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "selectionOutcome": "no-selection",
        "readinessOutcome": "ready" if ready else "not-ready",
        "verdict": _READY if ready else _NOT_READY,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "runtimeId": "onnxruntime",
        "versionTag": "v1.31.1",
        "profileId": checked_adapter["profileId"],
        "profileVersion": checked_adapter["profileVersion"],
        "blockers": blockers,
        "locallyObservedRuntimeDigests": [],
        "locallyObservedModelArtifactDigests": [],
        "installationAuthorized": False,
    }
    return validate_track6c(document)


def validate_track6c(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one Track 6C readiness record."""
    validate("track6c-readiness", document)
    if document["installationAuthorized"] is not False:
        raise Track6CReadinessError("installation-authorized")
    if document["locallyObservedRuntimeDigests"] or document["locallyObservedModelArtifactDigests"]:
        raise Track6CReadinessError("local-digest")
    text = json.dumps(document)
    if "/home/" in text or "https://" in text:
        raise Track6CReadinessError("identity")
    return document


def load_track6c_readiness(root: Path | None = None) -> dict[str, Any]:
    """Load the committed decision and require it to match the pure function."""
    from patchpilot_intelligence_evals.candidate_format_resolution import (
        decide_format_resolution,
    )
    from patchpilot_intelligence_evals.conversion_plan import decide_conversion_plan
    from patchpilot_intelligence_evals.runtime_adapter_contract import load_adapter_contract
    from patchpilot_intelligence_evals.runtime_cache import load_runtime_policy

    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track6CReadinessError("record-type")
    document = validate_track6c(loaded)
    expected = decide_track6c(
        decide_format_resolution(),
        decide_conversion_plan(),
        load_adapter_contract(base),
        load_runtime_policy(base),
    )
    if document != expected:
        raise Track6CReadinessError("readiness-drift")
    return document


def _blockers(
    format_resolution: dict[str, Any],
    conversion_plan: dict[str, Any],
    adapter: dict[str, Any],
    runtime_policy: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if runtime_policy["runtimeId"] != "onnxruntime" or adapter["runtimeId"] != "onnxruntime":
        blockers.append("runtime-identity")
    if adapter["profileId"] != "linux-bwrap-systemd-v1" or adapter["profileVersion"] != "1.0.0":
        blockers.append("hardened-profile")
    direct = (
        format_resolution["resolutionOutcome"] == "direct-onnx"
        and format_resolution["directOnnxQualified"] is True
    )
    authorized = conversion_plan["authorizationOutcome"] == "authorized"
    qualifying = [item for item in format_resolution["families"] if item["qualifies"] is True]
    relevant = qualifying if direct else list(format_resolution["families"])
    present = {str(code) for family in relevant for code in family["blockers"]}
    for code in (
        "bounded-subprocess-compatibility",
        "explicit-weight-use-license",
        "onnx-directory-exceeds-artifact-cap",
        "tokenizer-provenance",
    ):
        if code in present:
            blockers.append(code)
    cap = int(format_resolution["artifactCapBytes"])
    for family in relevant:
        size = family["onnxDirectoryBytes"]
        if isinstance(size, int) and size > cap:
            blockers.append("onnx-directory-exceeds-artifact-cap")
    if not direct and not authorized:
        blockers.extend(
            (
                "conversion-not-authorized",
                "no-qualifying-direct-onnx",
                "sources-not-independently-eligible",
            )
        )
    if not direct:
        if conversion_plan["offlineClosed"] is not True:
            blockers.append("toolchain-not-offline-closed")
        if conversion_plan["equivalenceMeasured"] is not True:
            blockers.append("equivalence-not-measured")
    return sorted(set(blockers))
