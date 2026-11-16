"""Track 8A command handlers. Transfer commands stay out of CI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquired_artifact_validation import load_digest_template
from patchpilot_intelligence_evals.acquisition_closeout import load_closeout_template
from patchpilot_intelligence_evals.acquisition_plan import (
    load_acquisition_allowlist,
    load_acquisition_plan,
    preflight_report,
)
from patchpilot_intelligence_evals.acquisition_runner import (
    acquire_candidate,
    acquire_runtime,
)
from patchpilot_intelligence_evals.candidate_staging import load_candidate_manifest_template
from patchpilot_intelligence_evals.hardened_load_proof import (
    LoadProofError,
    launch_offline_load,
    load_attestation_template,
)
from patchpilot_intelligence_evals.runtime_staging import load_runtime_manifest_template
from patchpilot_intelligence_evals.track8a_evidence import load_acquisition_evidence
from patchpilot_intelligence_evals.track8a_review import load_track8a_review
from patchpilot_intelligence_evals.track8b_prerequisites import load_measurement_prerequisites

_HEADER_LIMIT = 2_000_000
OUTSIDE_GUARD = frozenset({"acquire-candidate", "acquire-runtime", "hardened-offline-load-proof"})


def handle(command: str, args: Any) -> dict[str, Any]:
    """Run one Track 8A command and return a path-free summary."""
    if command == "acquisition-plan-validation":
        plan = load_acquisition_plan()
        return _ok(
            planDigest=plan["planDigest"],
            acquisitionStatus=plan["acquisitionStatus"],
            selectionOutcome=plan["selectionOutcome"],
        )
    if command == "acquisition-allowlist-validation":
        allowlist = load_acquisition_allowlist()
        return _ok(
            allowlistDigest=allowlist["allowlistDigest"],
            acquisitionStatus=allowlist["acquisitionStatus"],
        )
    if command == "acquired-runtime-manifest-validation":
        manifest = load_runtime_manifest_template()
        return _ok(manifestState=manifest["manifestState"], telemetry=manifest["telemetry"])
    if command == "acquired-candidate-manifest-validation":
        manifest = load_candidate_manifest_template()
        return _ok(
            manifestState=manifest["manifestState"],
            selectionOutcome=manifest["selectionOutcome"],
        )
    if command == "local-artifact-digests-validation":
        digests = load_digest_template()
        return _ok(
            acquisitionStatus=digests["acquisitionStatus"],
            digestAuthority=digests["digestAuthority"],
        )
    if command == "hardened-load-attestation-validation":
        attestation = load_attestation_template()
        return _ok(
            loadStatus=attestation["loadStatus"],
            inferencePerformed=attestation["inferencePerformed"],
            realModelExecuted=attestation["realModelExecuted"],
        )
    if command == "track8a-acquisition-evidence-validation":
        evidence = load_acquisition_evidence()
        return _ok(
            evidenceClass=evidence["evidenceClass"],
            providerSharedLibraryDisposition=evidence["providerSharedLibraryDisposition"],
            runtimeAcquisition=evidence["runtimeAcquisition"],
            candidateAcquisition=evidence["candidateAcquisition"],
            measurementPerformed=evidence["measurementPerformed"],
            track8bMeasurementAuthorization=evidence["track8bMeasurementAuthorization"],
        )
    if command == "track8a-review-validation":
        review = load_track8a_review()
        return _ok(
            reviewStatus=review["reviewStatus"],
            reviewDigest=review["reviewDigest"],
            providerSharedLibraryDisposition=review["providerSharedLibraryDisposition"],
            track8bMeasurementAuthorization=review["track8bMeasurementAuthorization"],
            measurementPerformed=review["measurementPerformed"],
            selectionOutcome=review["selectionOutcome"],
        )
    if command == "acquisition-closeout-validation" or command == "acquisition-closeout":
        closeout = load_closeout_template()
        return _ok(
            closeoutState=closeout["closeoutState"],
            acquisitionStatus=closeout["acquisitionStatus"],
            measurementPerformed=closeout["measurementPerformed"],
        )
    if command == "track8b-measurement-prerequisites-validation":
        record = load_measurement_prerequisites()
        return _ok(
            readinessOutcome=record["readinessOutcome"],
            verdict=record["verdict"],
            measurementAuthorization=record["measurementAuthorization"],
            measurementPerformed=record["measurementPerformed"],
            selectionOutcome=record["selectionOutcome"],
        )
    if command == "acquisition-preflight":
        report = preflight_report(_path(args.runtime_cache), _path(args.model_cache))
        return _ok(**report)
    if command == "acquire-runtime":
        result = acquire_runtime(Path(args.runtime_cache), str(args.operator_approval))
        return _ok(**result, measurementPerformed=False, selectionOutcome="no-selection")
    if command == "acquire-candidate":
        result = acquire_candidate(
            Path(args.model_cache),
            Path(args.runtime_cache),
            str(args.operator_approval),
        )
        return _ok(**result, measurementPerformed=False, selectionOutcome="no-selection")
    if command == "hardened-offline-load-proof":
        header = _header(Path(args.api_header))
        attestation = launch_offline_load(
            Path(args.runtime_cache),
            Path(args.model_cache),
            header,
        )
        return _ok(
            loadStatus=attestation["loadStatus"],
            inferencePerformed=False,
            measurementPerformed=False,
            realModelExecuted=False,
            selectionOutcome="no-selection",
        )
    raise LoadProofError("unknown-command")


def _ok(**fields: Any) -> dict[str, Any]:
    return {"status": "ok", "productionReady": False, **fields}


def _path(value: object) -> Path | None:
    if value is None:
        return None
    return Path(str(value))


def _header(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise LoadProofError("missing-file")
    if path.stat().st_size > _HEADER_LIMIT:
        raise LoadProofError("size-mismatch")
    return path.read_text(encoding="utf-8")
