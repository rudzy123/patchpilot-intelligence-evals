"""Redacted Track 8A acquisition evidence. Absolute cache roots are not stored."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquired_artifact_validation import load_digest_template
from patchpilot_intelligence_evals.acquisition_closeout import load_closeout_template
from patchpilot_intelligence_evals.acquisition_plan import (
    chosen_files,
    load_acquisition_allowlist,
    load_acquisition_plan,
    reject_sensitive,
)
from patchpilot_intelligence_evals.candidate_staging import load_candidate_manifest_template
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.finalist_budget import (
    RUNTIME_LISTED_BYTES,
    RUNTIME_LISTED_SHA256,
)
from patchpilot_intelligence_evals.hardened_load_proof import load_attestation_template
from patchpilot_intelligence_evals.runtime_staging import load_runtime_manifest_template
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.track8_authorization import load_track8_authorization
from patchpilot_intelligence_evals.track8a_readiness import load_track8a_readiness
from patchpilot_intelligence_evals.track8b_readiness import load_track8b_readiness

_RECORD = Path("candidates/authorization/track8a-acquisition-evidence.json")
_PLAN_DIGEST = "349c1d666bb4106e284cd0b41f6bac6b4ea65b9d2c5edee8eb358dfc006aec92"
_ALLOWLIST_DIGEST = "cce59885779e2a0e41761205fde5275df5606bea040fc9366a839017fdf4108e"
_DISPOSITION = "not required for the authorized CPU-only path"
_ARCHIVE_NAME = "onnxruntime-linux-x64-1.31.1.tgz"
_METADATA = frozenset({"promotion-journal.json", "verification-seal.json"})
_LOCAL_CANDIDATE: dict[str, str] = {
    "onnx/model.onnx": "240b836266733940519db3893df325b4cfac8bb87222acbfa0f05dd8c87a6639",
    "onnx/model.onnx_data": "04339fb19070d30e0b5523dfecf21b5a469dd3056a43ccd050ce6e756f039ebe",
    "onnx/model.onnx_data_1": "cf2d2083fb09ebc8dfcdc46709ed1b9bc978dd7a08a83a6993f30c078b3e6fc5",
    "onnx/model.onnx_data_2": "5817c9c46604164ef96aa9524e34422edc3ffa86e480bafbbcc80de38c0a7759",
    "tokenizer.json": "0a1f2cb9fc2769030ca1f4207e81c1af493319373d41b8d3cf5be53860c13760",
    "config.json": "dd5d4c6e32a992ad7ddac5c07f5e4711e42c69125f2b94287af7a8ec19963be5",
    "generation_config.json": "25f750b7e6a790f86ed01cd6f128f905152cb60bbfe2e6618ceca833b452cf80",
    "tokenizer_config.json": "0f11f4ffa5750369414bb24e41f26e2bbf23f1d01def533cad5f584e59ae3bef",
    "chat_template.jinja": "f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176",
    "LICENSE": "5188f2b355da20647257a3156db5834c794e5fb5e6d8dc4d4cdbb3180e75b85b",
    "README.md": "262795fd562da67904b5d5c638b15d5ca394053b13dc4d8cda9a372b5798ea14",
}
_RUNTIME_FILES: tuple[dict[str, Any], ...] = (
    {
        "fileName": "libonnxruntime.so.1.31.1",
        "logicalBytes": 29345384,
        "localSha256": "a96f132e5eb5ca04e23a7d2fc1078fb95aa591e8d71d0f237702ece3a1e0f4ea",
        "role": "runtime-library",
        "upstreamSha256": None,
    },
    {
        "fileName": "LICENSE",
        "logicalBytes": 1073,
        "localSha256": "2f07c72751aed99790b8a4869cf2311df85a860b22ded05fa22803587a48922c",
        "role": "license",
        "upstreamSha256": None,
    },
    {
        "fileName": "ThirdPartyNotices.txt",
        "logicalBytes": 338088,
        "localSha256": "143764b952fdb1a7c69ce653bfba74a7744d6a8a573bfb73e235fba356c83de3",
        "role": "notice",
        "upstreamSha256": None,
    },
    {
        "fileName": "runtime-identity.json",
        "logicalBytes": 100,
        "localSha256": "7acf64c903f72486d2ae596d4b8343ba03b245155573998e8d4380a23f752028",
        "role": "runtime-identity",
        "upstreamSha256": None,
    },
)
_ATTEMPTS: tuple[dict[str, Any], ...] = (
    {
        "attemptClass": "rejected-promotion",
        "attemptId": "rp-6ae550e563c80876",
        "cleanupAuthorization": "rejected-payload",
        "cleanupStatus": "already-clean",
        "executableEligibility": False,
        "finalState": "rejection-metadata-retained",
        "reason": "unexpected-file; payload already absent",
        "reclaimedBytes": 0,
        "retainedEvidence": "rejection-record",
        "verifiedStateEligibility": False,
    },
    {
        "attemptClass": "rejected-promotion",
        "attemptId": "rp-9e0d257950c038e7",
        "cleanupAuthorization": "rejected-payload",
        "cleanupStatus": "clean",
        "executableEligibility": False,
        "finalState": "rejection-metadata-retained",
        "reason": "missing-file; superseded payload deleted",
        "reclaimedBytes": 29684545,
        "retainedEvidence": "rejection-record",
        "verifiedStateEligibility": False,
    },
    {
        "attemptClass": "duplicate-transport",
        "attemptId": "rm-d993520d8fb9c771",
        "cleanupAuthorization": "quarantine-payload",
        "cleanupStatus": "clean",
        "executableEligibility": False,
        "finalState": "removed",
        "reason": "superseded duplicate extract deleted",
        "reclaimedBytes": 1126948,
        "retainedEvidence": "none",
        "verifiedStateEligibility": False,
    },
    {
        "attemptClass": "empty-quarantine",
        "attemptId": "rm-48372d57a0ec2f91",
        "cleanupAuthorization": "quarantine-payload",
        "cleanupStatus": "clean",
        "executableEligibility": False,
        "finalState": "removed",
        "reason": "empty superseded attempt deleted",
        "reclaimedBytes": 0,
        "retainedEvidence": "none",
        "verifiedStateEligibility": False,
    },
    {
        "attemptClass": "superseded-transport",
        "attemptId": "rm-35b0d6b6e52c93d0",
        "cleanupAuthorization": "quarantine-payload",
        "cleanupStatus": "clean",
        "executableEligibility": False,
        "finalState": "removed",
        "reason": "excluded unpack members deleted",
        "reclaimedBytes": 1126948,
        "retainedEvidence": "none",
        "verifiedStateEligibility": False,
    },
)
_RETAINED: tuple[dict[str, Any], ...] = (
    {
        "attemptClass": "runtime-archive",
        "attemptId": "rt-e791f1518ae46ead",
        "cleanupAuthorization": "not-authorized",
        "executableEligibility": False,
        "finalState": "retained",
        "reason": "published archive digest evidence",
        "verifiedStateEligibility": False,
    },
    {
        "attemptClass": "verified-runtime",
        "attemptId": "rp-c2fe1c88f694fc1e",
        "cleanupAuthorization": "not-authorized",
        "executableEligibility": False,
        "finalState": "promoted",
        "reason": "verified promoted runtime",
        "verifiedStateEligibility": True,
    },
    {
        "attemptClass": "verified-candidate",
        "attemptId": "cd-20b7ceee37a62cba",
        "cleanupAuthorization": "not-authorized",
        "executableEligibility": False,
        "finalState": "promoted",
        "reason": "verified promoted candidate",
        "verifiedStateEligibility": True,
    },
)
_OFFICIAL: tuple[dict[str, str], ...] = (
    {
        "claim": (
            "CPU kernels are compiled into onnxruntime_providers and linked into the main "
            "library. On Unix, onnxruntime_providers_shared is not directly linked; it is "
            "loaded with RTLD_GLOBAL for shared providers."
        ),
        "evidenceId": "cpu-provider-link",
        "locator": "cmake/onnxruntime_providers_cpu.cmake",
        "revision": "v1.31.1",
        "sourceName": "microsoft/onnxruntime",
    },
    {
        "claim": (
            "The official CMake import target and pkg-config link line name only "
            "libonnxruntime.so.1.31.1."
        ),
        "evidenceId": "package-link-interface",
        "locator": "lib/cmake/onnxruntime/onnxruntimeTargets-release.cmake",
        "revision": "6af1a932e2286d5c58166085d24c68783033edee",
        "sourceName": "onnxruntime-linux-x64-1.31.1",
    },
    {
        "claim": (
            "DT_NEEDED does not include libonnxruntime_providers_shared.so. "
            "OrtSessionOptionsAppendExecutionProvider_CPU is defined in the verified library. "
            "The shared object exports Provider_GetHost and Provider_SetHost."
        ),
        "evidenceId": "verified-elf-interface",
        "locator": "dynamic-section",
        "revision": "a96f132e5eb5ca04e23a7d2fc1078fb95aa591e8d71d0f237702ece3a1e0f4ea",
        "sourceName": "libonnxruntime.so.1.31.1",
    },
)


class EvidenceError(ValueError):
    """Track 8A evidence failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def provider_disposition() -> str:
    """The single CPU-only disposition for libonnxruntime_providers_shared.so."""
    return _DISPOSITION


def digest_document(document: dict[str, Any]) -> dict[str, Any]:
    """Attach the identity digest and validate the evidence record."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    payload["identityDigest"] = sha256_text(canonical_dumps(payload))
    reject_sensitive(payload)
    validate("track8a-acquisition-evidence", payload)
    return payload


def build_acquisition_evidence() -> dict[str, Any]:
    """Build the redacted observed-acquisition record and seal its digest."""
    _require_boundaries()
    attempts = [dict(item) for item in _ATTEMPTS]
    reclaimed = sum(int(item["reclaimedBytes"]) for item in attempts)
    document: dict[str, Any] = {
        "allowlistDigest": _ALLOWLIST_DIGEST,
        "attemptDecisions": attempts,
        "calibrationApprovalStatus": "not-approved",
        "candidateAcquisition": "acquired-and-verified",
        "candidateFiles": _candidate_files(),
        "copyFallbackUsed": False,
        "corpusExecuted": False,
        "evidenceClass": "track8a-observed-acquisition",
        "excludedSharedLibrary": {
            "disposition": _DISPOSITION,
            "executableEligibility": False,
            "fileName": "libonnxruntime_providers_shared.so",
            "localSha256": "086ec1d5388f64153d9c63470d126693db9a182c8ce236d3a1119068471b8a0d",
            "logicalBytes": 14632,
            "payloadRetained": False,
            "promoted": False,
            "verifiedStateEligibility": False,
        },
        "generationPerformed": False,
        "gitTrackedArtifact": False,
        "hardenedOfflineLoad": "passed",
        "historicalAcquisitionAuthorization": "not-authorized",
        "inferencePerformed": False,
        "installationAuthorized": False,
        "longContextMeasurementPerformed": False,
        "measurementPerformed": False,
        "networkDenial": "passed",
        "officialProviderEvidence": [dict(item) for item in _OFFICIAL],
        "operatorApproval": "accepted",
        "planDigest": _PLAN_DIGEST,
        "processCleanup": "passed",
        "productionReady": False,
        "providerSharedLibraryDisposition": _DISPOSITION,
        "realModelExecuted": False,
        "retainedIdentities": [dict(item) for item in _RETAINED],
        "runtimeAcquisition": "acquired-and-verified",
        "runtimeArchive": {
            "fileName": _ARCHIVE_NAME,
            "localSha256": RUNTIME_LISTED_SHA256,
            "logicalBytes": RUNTIME_LISTED_BYTES,
            "upstreamSha256": RUNTIME_LISTED_SHA256,
        },
        "runtimeFiles": [dict(item) for item in _RUNTIME_FILES],
        "sameFilesystemPromotion": True,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "storageReclaimedBytes": reclaimed,
        "track8bMeasurementAuthorization": "not-authorized",
    }
    return digest_document(document)


def load_acquisition_evidence(root: Path | None = None) -> dict[str, Any]:
    """Load the committed evidence and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise EvidenceError("record-type")
    reject_sensitive(loaded)
    validate("track8a-acquisition-evidence", loaded)
    if loaded != build_acquisition_evidence():
        raise EvidenceError("record-drift")
    return loaded


def compare_promoted_digests(runtime_root: Path, model_root: Path) -> None:
    """Recompute promoted payload digests. A mismatch fails closed."""
    evidence = build_acquisition_evidence()
    retained = {str(item["attemptClass"]): str(item["attemptId"]) for item in _RETAINED}
    _compare_directory(
        runtime_root / "verified" / retained["verified-runtime"],
        evidence["runtimeFiles"],
    )
    _compare_directory(
        model_root / "verified" / retained["verified-candidate"],
        evidence["candidateFiles"],
    )
    archive = runtime_root / "quarantine" / retained["runtime-archive"] / _ARCHIVE_NAME
    _require_file(archive, evidence["runtimeArchive"])
    _refuse_shared_library(runtime_root)
    _refuse_shared_library(model_root)


def _candidate_files() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    selected = chosen_files()
    if len(selected) != len(_LOCAL_CANDIDATE):
        raise EvidenceError("inventory")
    for item in selected:
        local = _LOCAL_CANDIDATE.get(item.path)
        if local is None:
            raise EvidenceError("missing-file")
        if item.published_sha256 is not None and local != item.published_sha256:
            raise EvidenceError("digest-mismatch")
        if item.quantized or item.reduced_precision or not item.selected:
            raise EvidenceError("unexpected-file")
        role = _candidate_role(item.role, item.path)
        rows.append(
            {
                "fileName": item.path,
                "logicalBytes": item.listed_byte_count,
                "localSha256": local,
                "role": role,
                "upstreamSha256": item.published_sha256,
            }
        )
    return rows


def _candidate_role(role: str, path: str) -> str:
    if path == "LICENSE":
        return "license"
    if path == "README.md":
        return "readme"
    if role == "tokenizer":
        return "tokenizer"
    if role == "configuration":
        return "configuration"
    if role == "graph":
        return "graph"
    if role == "external-data":
        return "external-data"
    raise EvidenceError("inventory")


def _require_boundaries() -> None:
    plan = load_acquisition_plan()
    allowlist = load_acquisition_allowlist()
    if plan["planDigest"] != _PLAN_DIGEST or plan["acquisitionStatus"] != "not-acquired":
        raise EvidenceError("plan-digest")
    if plan["operatorApproval"] != "required":
        raise EvidenceError("historical-record")
    if allowlist["allowlistDigest"] != _ALLOWLIST_DIGEST:
        raise EvidenceError("plan-digest")
    if allowlist["acquisitionStatus"] != "not-acquired":
        raise EvidenceError("historical-record")
    if load_digest_template()["acquisitionStatus"] != "not-acquired":
        raise EvidenceError("historical-record")
    if load_closeout_template()["closeoutState"] != "not-closed":
        raise EvidenceError("historical-record")
    if load_attestation_template()["loadStatus"] != "not-performed":
        raise EvidenceError("historical-record")
    if load_runtime_manifest_template()["manifestState"] != "not-acquired":
        raise EvidenceError("historical-record")
    if load_candidate_manifest_template()["manifestState"] != "not-acquired":
        raise EvidenceError("historical-record")
    authorization = load_track8_authorization()
    if authorization["authorizationOutcome"] != "not-authorized":
        raise EvidenceError("historical-record")
    if authorization["acquisitionStatus"] != "not-acquired":
        raise EvidenceError("historical-record")
    readiness = load_track8a_readiness()
    if readiness["readinessOutcome"] != "not-ready":
        raise EvidenceError("historical-record")
    if readiness["acquisitionAuthorization"] != "not-authorized":
        raise EvidenceError("historical-record")
    measurement = load_track8b_readiness()
    if measurement["acquisitionStatus"] != "not-acquired":
        raise EvidenceError("historical-record")
    if measurement["acquisitionAuthorization"] != "not-authorized":
        raise EvidenceError("historical-record")
    if RUNTIME_LISTED_BYTES != 11_413_655 or len(RUNTIME_LISTED_SHA256) != 64:
        raise EvidenceError("digest-mismatch")


def _compare_directory(directory: Path, expected: list[dict[str, Any]]) -> None:
    if directory.is_symlink() or not directory.is_dir():
        raise EvidenceError("missing-file")
    expected_names = {str(item["fileName"]) for item in expected}
    found: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(directory, followlinks=False):
        current = Path(dirpath)
        if current.is_symlink():
            raise EvidenceError("symlink")
        for name in dirnames:
            path = current / name
            if path.is_symlink():
                raise EvidenceError("symlink")
        for name in filenames:
            path = current / name
            if path.is_symlink():
                raise EvidenceError("symlink")
            relative = path.relative_to(directory).as_posix()
            if relative in _METADATA:
                continue
            if relative not in expected_names:
                raise EvidenceError("unexpected-file")
            found.add(relative)
    if found != expected_names:
        raise EvidenceError("missing-file")
    for item in expected:
        _require_file(directory / str(item["fileName"]), item)


def _require_file(path: Path, expected: dict[str, Any]) -> None:
    if path.is_symlink() or not path.is_file():
        raise EvidenceError("missing-file")
    if path.stat().st_size != int(expected["logicalBytes"]):
        raise EvidenceError("size-mismatch")
    if _sha256(path) != str(expected["localSha256"]):
        raise EvidenceError("digest-mismatch")
    upstream = expected.get("upstreamSha256")
    if isinstance(upstream, str) and upstream != str(expected["localSha256"]):
        raise EvidenceError("digest-mismatch")


def _refuse_shared_library(root: Path) -> None:
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        if current.is_symlink() or any((current / name).is_symlink() for name in dirnames):
            raise EvidenceError("symlink")
        if "libonnxruntime_providers_shared.so" in filenames:
            raise EvidenceError("unexpected-file")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
