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
from patchpilot_intelligence_evals.artifact_cache import CacheError, load_cache_policy
from patchpilot_intelligence_evals.artifact_verification import (
    VerificationError,
    load_verification_manifest,
)
from patchpilot_intelligence_evals.candidate_evaluation import evaluate_candidate
from patchpilot_intelligence_evals.candidate_manifest import ManifestError, load_manifest
from patchpilot_intelligence_evals.comparison import compare_results
from patchpilot_intelligence_evals.corpus import CorpusError, canonical_dumps, validate_corpus
from patchpilot_intelligence_evals.evaluator import evaluate_baseline
from patchpilot_intelligence_evals.evidence_closure import EvidenceError, load_closure
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
from patchpilot_intelligence_evals.runtime_authorization import (
    RuntimeAuthorizationError,
    load_assessment,
    load_authorization,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root


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
            return _fail()
    except (
        AcquisitionError,
        CorpusError,
        BoundaryError,
        ManifestError,
        ProtocolError,
        CacheError,
        VerificationError,
        RuntimeAuthorizationError,
        IsolationError,
        EvidenceError,
        ResultStoreError,
        SchemaValidationError,
        json.JSONDecodeError,
    ):
        return _fail()


if __name__ == "__main__":
    raise SystemExit(main())
