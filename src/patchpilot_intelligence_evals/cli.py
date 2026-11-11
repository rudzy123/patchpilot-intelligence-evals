"""Deterministic command line for corpus checks, baseline, and candidates."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from patchpilot_intelligence_evals.acquisition_authorization import (
    AcquisitionError,
    load_track6_authorization,
)
from patchpilot_intelligence_evals.artifact_budget import BudgetError, load_artifact_budget
from patchpilot_intelligence_evals.artifact_cache import CacheError, load_cache_policy
from patchpilot_intelligence_evals.artifact_verification import (
    VerificationError,
    load_verification_manifest,
)
from patchpilot_intelligence_evals.candidate_eligibility import (
    EligibilityError,
    load_candidate_eligibility,
)
from patchpilot_intelligence_evals.candidate_evaluation import evaluate_candidate
from patchpilot_intelligence_evals.candidate_format_resolution import (
    FormatResolutionError,
    load_format_resolution,
)
from patchpilot_intelligence_evals.candidate_manifest import ManifestError, load_manifest
from patchpilot_intelligence_evals.comparison import compare_results
from patchpilot_intelligence_evals.conversion_plan import ConversionPlanError, load_conversion_plan
from patchpilot_intelligence_evals.corpus import CorpusError, canonical_dumps, validate_corpus
from patchpilot_intelligence_evals.dependency_architecture_policy import (
    DependencyPolicyError,
    validate_dependency_policy,
)
from patchpilot_intelligence_evals.direct_onnx_evidence import (
    OnnxEvidenceError,
    load_direct_onnx_evidence,
)
from patchpilot_intelligence_evals.evaluator import evaluate_baseline
from patchpilot_intelligence_evals.evidence_closure import EvidenceError, load_closure
from patchpilot_intelligence_evals.execution_attestation import (
    AttestationError,
    load_attestation,
    load_readiness,
    validate_attestation,
)
from patchpilot_intelligence_evals.execution_attestation import (
    load_profile as load_hardened_profile,
)
from patchpilot_intelligence_evals.hardened_execution import (
    HardenedExecutionError,
    visibility_summary,
)
from patchpilot_intelligence_evals.implementation_review import ReviewError, load_review
from patchpilot_intelligence_evals.isolation_profile import IsolationError, load_profile
from patchpilot_intelligence_evals.network_guard import (
    BoundaryError,
    assert_inside_repository,
    network_guard,
)
from patchpilot_intelligence_evals.protocol import ProtocolError
from patchpilot_intelligence_evals.real_candidate_manifest import load_offline_manifest
from patchpilot_intelligence_evals.result_store import (
    ResultStoreError,
    read_execution_result,
    read_validated_artifact,
    write_canonical,
)
from patchpilot_intelligence_evals.runtime_adapter_contract import (
    AdapterError,
    load_adapter_contract,
)
from patchpilot_intelligence_evals.runtime_artifact_verification import (
    RuntimeVerificationError,
)
from patchpilot_intelligence_evals.runtime_artifact_verification import (
    load_verification_manifest as load_runtime_verification_manifest,
)
from patchpilot_intelligence_evals.runtime_authorization import (
    RuntimeAuthorizationError,
    load_assessment,
    load_authorization,
)
from patchpilot_intelligence_evals.runtime_cache import RuntimeCacheError, load_runtime_policy
from patchpilot_intelligence_evals.runtime_security import (
    RuntimeSecurityError,
)
from patchpilot_intelligence_evals.runtime_security import (
    load_assessment as load_runtime_security_assessment,
)
from patchpilot_intelligence_evals.runtime_security import (
    load_authorization as load_runtime_authorization_v2,
)
from patchpilot_intelligence_evals.sandbox_capabilities import (
    SandboxCapabilityError,
    load_capability_report,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root
from patchpilot_intelligence_evals.subprocess_compatibility import (
    SubprocessError,
    load_subprocess_compatibility,
)
from patchpilot_intelligence_evals.tokenizer_eligibility import (
    TokenizerError,
    load_tokenizer_eligibility,
)
from patchpilot_intelligence_evals.track6a_review import Track6AReviewError
from patchpilot_intelligence_evals.track6a_review import load_review as load_track6a_review
from patchpilot_intelligence_evals.track6c_readiness import (
    Track6CReadinessError,
    load_track6c_readiness,
)
from patchpilot_intelligence_evals.track6d_readiness import Track6DError, load_track6d_readiness
from patchpilot_intelligence_evals.workflow_policy import (
    WorkflowPolicyError,
    validate_workflow_policy,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchpilot-evals")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("corpus-validation")
    evaluation = commands.add_parser("baseline-evaluation")
    evaluation.add_argument("--output", default=None)
    manifest = commands.add_parser("candidate-manifest-validation")
    manifest.add_argument("--manifest", required=True)
    real_manifest = commands.add_parser("real-candidate-manifest-validation")
    real_manifest.add_argument("--manifest", required=True)
    commands.add_parser("artifact-cache-policy-validation")
    verification = commands.add_parser("artifact-verification-validation")
    verification.add_argument("--manifest", required=True)
    commands.add_parser("runtime-assessment-validation")
    commands.add_parser("runtime-authorization-validation")
    commands.add_parser("isolation-profile-validation")
    commands.add_parser("evidence-closure-validation")
    commands.add_parser("track6-authorization-validation")
    commands.add_parser("track5-review-validation")
    commands.add_parser("sandbox-capability-validation")
    commands.add_parser("hardened-execution-profile-validation")
    commands.add_parser("hardened-fixture-execution")
    attestation = commands.add_parser("execution-attestation-validation")
    attestation.add_argument("--attestation", default=None)
    commands.add_parser("runtime-security-assessment-validation")
    commands.add_parser("runtime-authorization-v2-validation")
    commands.add_parser("track6b-readiness-validation")
    commands.add_parser("track6a-review-validation")
    commands.add_parser("external-runtime-cache-policy-validation")
    runtime_verification = commands.add_parser("runtime-artifact-verification-validation")
    runtime_verification.add_argument("--manifest", required=True)
    commands.add_parser("runtime-adapter-contract-validation")
    commands.add_parser("candidate-format-resolution-validation")
    commands.add_parser("onnx-conversion-plan-validation")
    commands.add_parser("track6c-readiness-validation")
    commands.add_parser("candidate-eligibility-validation")
    commands.add_parser("tokenizer-eligibility-validation")
    commands.add_parser("direct-onnx-evidence-validation")
    commands.add_parser("artifact-budget-validation")
    commands.add_parser("bounded-subprocess-compatibility-validation")
    commands.add_parser("track6d-readiness-validation")
    commands.add_parser("workflow-policy-validation")
    commands.add_parser("dependency-architecture-policy-validation")
    one_case = commands.add_parser("candidate-execution")
    one_case.add_argument("--manifest", required=True)
    one_case.add_argument("--case-id", required=True)
    one_case.add_argument("--output-dir", default=None)
    complete = commands.add_parser("candidate-evaluation")
    complete.add_argument("--manifest", required=True)
    complete.add_argument("--output-dir", required=True)
    result = commands.add_parser("result-validation")
    result.add_argument("--result", required=True)
    comparison_validation = commands.add_parser("comparison-validation")
    comparison_validation.add_argument("--result", required=True)
    calibration_validation = commands.add_parser("calibration-validation")
    calibration_validation.add_argument("--result", required=True)
    comparison = commands.add_parser("candidate-comparison")
    comparison.add_argument("--left", required=True)
    comparison.add_argument("--right", required=True)
    comparison.add_argument("--output-dir", default=None)
    calibration = commands.add_parser("calibration")
    calibration.add_argument("--output-dir", required=True)
    return parser


def _fail() -> int:
    sys.stdout.write(canonical_dumps({"status": "fail"}) + "\n")
    return 1


def _summary(payload: dict[str, Any]) -> int:
    sys.stdout.write(canonical_dumps(payload) + "\n")
    return 0


def _checked_relative(path: str) -> str:
    assert_inside_repository(path, repo_root())
    return path


def _read_optional_result(path: str) -> dict[str, Any] | None:
    root = repo_root()
    _checked_relative(path)
    try:
        return read_execution_result(path, root=root)
    except ResultStoreError as exc:
        if exc.code == "missing-result":
            return None
        raise


def _read_artifact(path: str, kind: str) -> dict[str, Any]:
    root = repo_root()
    return read_validated_artifact(_checked_relative(path), kind, root=root)


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        # The parent opens a host listener to prove network-namespace denial.
        # The in-process socket hook would hide that proof, so this command
        # stays outside it. The child still runs in the network namespace.
        if args.command == "hardened-fixture-execution":
            summary = visibility_summary()
            _summary(dict(summary))
            return 0 if summary["status"] == "ok" else 1
        with network_guard():
            if args.command == "corpus-validation":
                return _summary(validate_corpus())
            if args.command == "baseline-evaluation":
                result = evaluate_baseline()
                text = canonical_dumps(result) + "\n"
                output = args.output
                if output is not None:
                    _checked_relative(str(output))
                    destination = repo_root() / str(output)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(text, encoding="utf-8")
                else:
                    sys.stdout.write(text)
                return 0
            if args.command == "candidate-manifest-validation":
                manifest = load_manifest(_checked_relative(str(args.manifest)))
                return _summary(
                    {
                        "status": "ok",
                        "candidateId": manifest["candidateId"],
                        "manifestDigest": manifest["manifestDigest"],
                        "productionReady": False,
                    }
                )
            if args.command == "real-candidate-manifest-validation":
                offline = load_offline_manifest(_checked_relative(str(args.manifest)))
                return _summary(
                    {
                        "status": "ok",
                        "candidateId": offline["candidateId"],
                        "candidateKind": offline["candidateKind"],
                        "acquisitionStatus": offline["acquisitionStatus"],
                        "executionStatus": offline["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "external-runtime-cache-policy-validation":
                runtime_policy = load_runtime_policy()
                return _summary(
                    {
                        "status": "ok",
                        "cacheLocation": runtime_policy["cacheLocation"],
                        "runtimeInstalled": False,
                        "acquisitionStatus": runtime_policy["acquisitionStatus"],
                        "executionStatus": runtime_policy["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "runtime-artifact-verification-validation":
                runtime_verified = load_runtime_verification_manifest(
                    _checked_relative(str(args.manifest))
                )
                return _summary(
                    {
                        "status": "ok",
                        "verificationState": runtime_verified["verificationState"],
                        "runtimeInstalled": False,
                        "acquisitionStatus": runtime_verified["acquisitionStatus"],
                        "executionStatus": runtime_verified["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "runtime-adapter-contract-validation":
                contract = load_adapter_contract()
                return _summary(
                    {
                        "status": "ok",
                        "adapterId": contract["adapterId"],
                        "adapterVersion": contract["adapterVersion"],
                        "profileId": contract["profileId"],
                        "executableModelFormat": contract["executableRuntimeModel"]["format"],
                        "realCandidateOutcome": contract["realCandidateOutcome"],
                        "runtimeInstalled": False,
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "candidate-format-resolution-validation":
                resolution = load_format_resolution()
                return _summary(
                    {
                        "status": "ok",
                        "resolutionOutcome": resolution["resolutionOutcome"],
                        "directOnnxQualified": resolution["directOnnxQualified"],
                        "selectionOutcome": resolution["selectionOutcome"],
                        "productionReady": False,
                    }
                )
            if args.command == "onnx-conversion-plan-validation":
                plan = load_conversion_plan()
                return _summary(
                    {
                        "status": "ok",
                        "authorizationOutcome": plan["authorizationOutcome"],
                        "conversionStatus": plan["conversionStatus"],
                        "equivalenceMeasured": plan["equivalenceMeasured"],
                        "productionReady": False,
                    }
                )
            if args.command == "track6c-readiness-validation":
                readiness = load_track6c_readiness()
                return _summary(
                    {
                        "status": "ok",
                        "readinessOutcome": readiness["readinessOutcome"],
                        "verdict": readiness["verdict"],
                        "installationAuthorized": False,
                        "productionReady": False,
                    }
                )
            if args.command == "candidate-eligibility-validation":
                closure = load_candidate_eligibility()
                return _summary(
                    {
                        "status": "ok",
                        "selectionOutcome": closure["selectionOutcome"],
                        "qualifyingCandidateCount": closure["qualifyingCandidateCount"],
                        "scoringApplied": closure["scoringApplied"],
                        "acquisitionStatus": closure["acquisitionStatus"],
                        "executionStatus": closure["executionStatus"],
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "tokenizer-eligibility-validation":
                tokenizer = load_tokenizer_eligibility()
                passing = sum(
                    item["eligibilityOutcome"] == "pass" for item in tokenizer["families"]
                )
                return _summary(
                    {
                        "status": "ok",
                        "passingFamilies": passing,
                        "acquisitionStatus": tokenizer["acquisitionStatus"],
                        "executionStatus": tokenizer["executionStatus"],
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "direct-onnx-evidence-validation":
                onnx = load_direct_onnx_evidence()
                direct_count = sum(item["directPathEligible"] for item in onnx["families"])
                return _summary(
                    {
                        "status": "ok",
                        "directPathCount": direct_count,
                        "graphParsed": False,
                        "acquisitionStatus": onnx["acquisitionStatus"],
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "artifact-budget-validation":
                budget = load_artifact_budget()
                hardware_pass = sum(item["hardwareFit"] == "pass" for item in budget["families"])
                return _summary(
                    {
                        "status": "ok",
                        "hardwarePassCount": hardware_pass,
                        "artifactCapBytes": budget["artifactCapBytes"],
                        "memoryCapBytes": budget["memoryCapBytes"],
                        "productionReady": False,
                    }
                )
            if args.command == "bounded-subprocess-compatibility-validation":
                subprocess_record = load_subprocess_compatibility()
                compatible = sum(
                    item["compatibilityOutcome"] == "pass" for item in subprocess_record["families"]
                )
                return _summary(
                    {
                        "status": "ok",
                        "compatibleCount": compatible,
                        "runtimeNoteQualifiesCandidate": False,
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "track6d-readiness-validation":
                readiness = load_track6d_readiness()
                return _summary(
                    {
                        "status": "ok",
                        "readinessOutcome": readiness["readinessOutcome"],
                        "verdict": readiness["verdict"],
                        "selectionOutcome": readiness["selectionOutcome"],
                        "installationAuthorized": False,
                        "productionReady": False,
                    }
                )
            if args.command == "artifact-cache-policy-validation":
                policy = load_cache_policy()
                return _summary(
                    {
                        "status": "ok",
                        "cacheLocation": policy["cacheLocation"],
                        "acquisitionStatus": policy["acquisitionStatus"],
                        "executionStatus": policy["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "artifact-verification-validation":
                verified = load_verification_manifest(_checked_relative(str(args.manifest)))
                return _summary(
                    {
                        "status": "ok",
                        "verificationState": verified["verificationState"],
                        "acquisitionStatus": verified["acquisitionStatus"],
                        "executionStatus": verified["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "runtime-assessment-validation":
                assessed = load_assessment()
                return _summary(
                    {
                        "status": "ok",
                        "runtimeCount": len(assessed["runtimes"]),
                        "installedDuringSession": False,
                        "productionReady": False,
                    }
                )
            if args.command == "runtime-authorization-validation":
                authorized = load_authorization()
                return _summary(
                    {
                        "status": "ok",
                        "authorizationOutcome": authorized["authorizationOutcome"],
                        "runtimeId": authorized["runtimeId"],
                        "acquisitionStatus": authorized["acquisitionStatus"],
                        "executionStatus": authorized["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "isolation-profile-validation":
                profile = load_profile()
                return _summary(
                    {
                        "status": "ok",
                        "acquisitionBlocked": profile["acquisitionBlocked"],
                        "operatingSystemSandboxClaimed": False,
                        "acquisitionStatus": profile["acquisitionStatus"],
                        "executionStatus": profile["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "evidence-closure-validation":
                closure = load_closure()
                return _summary(
                    {
                        "status": "ok",
                        "selectionOutcome": closure["selectionOutcome"],
                        "qualifyingCandidateCount": closure["qualifyingCandidateCount"],
                        "acquisitionStatus": closure["acquisitionStatus"],
                        "executionStatus": closure["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "track6-authorization-validation":
                decision = load_track6_authorization()
                return _summary(
                    {
                        "status": "ok",
                        "authorizationOutcome": decision["authorizationOutcome"],
                        "selectionOutcome": decision["selectionOutcome"],
                        "blockerCount": len(decision["blockers"]),
                        "acquisitionStatus": decision["acquisitionStatus"],
                        "executionStatus": decision["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "sandbox-capability-validation":
                report = load_capability_report()
                enforced = [
                    item["probeId"]
                    for item in report["probes"]
                    if item["disposition"] == "enforced"
                ]
                return _summary(
                    {
                        "status": "ok",
                        "operatingSystemFamily": report["operatingSystemFamily"],
                        "architecture": report["architecture"],
                        "enforcedCount": len(enforced),
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "hardened-execution-profile-validation":
                profile = load_hardened_profile()
                return _summary(
                    {
                        "status": "ok",
                        "profileId": profile["profileId"],
                        "mechanism": profile["mechanism"],
                        "memoryMechanism": profile["memoryMechanism"],
                        "addressSpaceMechanism": profile["addressSpaceMechanism"],
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "execution-attestation-validation":
                if args.attestation is None:
                    attested = load_attestation()
                else:
                    _checked_relative(str(args.attestation))
                    loaded = json.loads(
                        (repo_root() / str(args.attestation)).read_text(encoding="utf-8")
                    )
                    if not isinstance(loaded, dict):
                        raise AttestationError("record-type")
                    attested = validate_attestation(loaded)
                return _summary(
                    {
                        "status": "ok",
                        "exitClassification": attested["exitClassification"],
                        "runtimeAuthorizationId": attested["runtimeAuthorizationId"],
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "runtime-security-assessment-validation":
                assessed = load_runtime_security_assessment()
                return _summary(
                    {
                        "status": "ok",
                        "runtimeCount": len(assessed["runtimes"]),
                        "installedDuringSession": False,
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "runtime-authorization-v2-validation":
                authorized = load_runtime_authorization_v2()
                return _summary(
                    {
                        "status": "ok",
                        "authorizationOutcome": authorized["authorizationOutcome"],
                        "runtimeId": authorized["runtimeId"],
                        "installationAuthorized": False,
                        "candidateSelected": False,
                        "acquisitionStatus": authorized["acquisitionStatus"],
                        "executionStatus": authorized["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "track6b-readiness-validation":
                readiness = load_readiness()
                return _summary(
                    {
                        "status": "ok",
                        "readiness": readiness["readiness"],
                        "verdict": readiness["verdict"],
                        "blockerCount": len(readiness["blockers"]),
                        "selectionOutcome": readiness["selectionOutcome"],
                        "acquisitionStatus": readiness["acquisitionStatus"],
                        "executionStatus": readiness["executionStatus"],
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "track6a-review-validation":
                review = load_track6a_review()
                return _summary(
                    {
                        "status": "ok",
                        "reviewStatus": review["reviewStatus"],
                        "decision": review["decision"],
                        "profileId": review["profileId"],
                        "profileVersion": review["profileVersion"],
                        "runtimeId": review["runtimeId"],
                        "versionTag": review["versionTag"],
                        "installationAuthorized": False,
                        "installedDuringSession": False,
                        "candidateFormatGap": True,
                        "candidateDecision": review["candidateDecision"],
                        "track6Authorization": review["track6Authorization"],
                        "acquisitionStatus": review["acquisitionStatus"],
                        "executionStatus": review["executionStatus"],
                        "realModelExecuted": False,
                        "productionReady": False,
                    }
                )
            if args.command == "track5-review-validation":
                review = load_review()
                return _summary(
                    {
                        "status": "ok",
                        "reviewStatus": review["reviewStatus"],
                        "runtimeDecision": review["runtimeDecision"],
                        "candidateDecision": review["candidateDecision"],
                        "track6Authorization": review["track6Authorization"],
                        "acquisitionStatus": review["acquisitionStatus"],
                        "executionStatus": review["executionStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "candidate-execution":
                manifest = load_manifest(_checked_relative(str(args.manifest)))
                output_dir = args.output_dir
                result = evaluate_candidate(
                    manifest,
                    output_dir=None if output_dir is None else _checked_relative(str(output_dir)),
                    case_ids=(str(args.case_id),),
                )
                if output_dir is None:
                    return _summary(result)
                return _summary(
                    {
                        "status": "ok",
                        "experimentId": result["experimentId"],
                        "productionReady": False,
                    }
                )
            if args.command == "candidate-evaluation":
                manifest = load_manifest(_checked_relative(str(args.manifest)))
                result = evaluate_candidate(
                    manifest,
                    output_dir=_checked_relative(str(args.output_dir)),
                )
                return _summary(
                    {
                        "status": "ok",
                        "experimentId": result["experimentId"],
                        "productionReady": False,
                        "complete": result["complete"],
                    }
                )
            if args.command == "result-validation":
                loaded = _read_artifact(str(args.result), "candidate-execution-result")
                return _summary(
                    {
                        "status": "ok",
                        "artifact": "candidate-execution-result",
                        "experimentId": loaded["experimentId"],
                        "productionReady": False,
                    }
                )
            if args.command == "comparison-validation":
                _read_artifact(str(args.result), "comparison-result")
                return _summary(
                    {
                        "status": "ok",
                        "artifact": "comparison-result",
                        "productionReady": False,
                    }
                )
            if args.command == "calibration-validation":
                loaded = _read_artifact(str(args.result), "calibration-record")
                return _summary(
                    {
                        "status": "ok",
                        "artifact": "calibration-record",
                        "approvalStatus": loaded["approvalStatus"],
                        "productionReady": False,
                    }
                )
            if args.command == "candidate-comparison":
                comparison = compare_results(
                    _read_optional_result(str(args.left)),
                    _read_optional_result(str(args.right)),
                )
                if args.output_dir is not None:
                    left_id = str(comparison["left"]["experimentId"] or "missing")
                    right_id = str(comparison["right"]["experimentId"] or "missing")
                    relative = (
                        f"{str(args.output_dir).strip('/')}/comparison-{left_id}-{right_id}.json"
                    )
                    write_canonical(
                        _checked_relative(relative),
                        comparison,
                        schema_name="comparison-result",
                    )
                return _summary(comparison)
            if args.command == "calibration":
                from patchpilot_intelligence_evals.calibration import generate_calibration

                record = generate_calibration(_checked_relative(str(args.output_dir)))
                return _summary(
                    {
                        "status": "ok",
                        "productionReady": False,
                        "approvalStatus": record["approvalStatus"],
                        "calibrationDigest": record["calibrationDigest"],
                    }
                )
            if args.command == "workflow-policy-validation":
                return _summary(validate_workflow_policy())
            if args.command == "dependency-architecture-policy-validation":
                return _summary(validate_dependency_policy())
            return _fail()
    except (
        AcquisitionError,
        CorpusError,
        BoundaryError,
        ManifestError,
        ProtocolError,
        CacheError,
        VerificationError,
        RuntimeCacheError,
        RuntimeVerificationError,
        AdapterError,
        FormatResolutionError,
        EligibilityError,
        TokenizerError,
        OnnxEvidenceError,
        BudgetError,
        SubprocessError,
        Track6DError,
        ConversionPlanError,
        Track6CReadinessError,
        RuntimeAuthorizationError,
        RuntimeSecurityError,
        SandboxCapabilityError,
        HardenedExecutionError,
        AttestationError,
        IsolationError,
        EvidenceError,
        ReviewError,
        Track6AReviewError,
        ResultStoreError,
        SchemaValidationError,
        DependencyPolicyError,
        WorkflowPolicyError,
        json.JSONDecodeError,
    ):
        return _fail()


if __name__ == "__main__":
    raise SystemExit(main())
