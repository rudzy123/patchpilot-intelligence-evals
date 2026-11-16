"""Track 8B measurement plan. Building this record does not call session Run."""

from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import (
    PlanError,
    reject_sensitive,
    validate_external_root,
)
from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.schemas import repo_root, validate

_PLAN = Path("candidates/authorization/measurement-plan.json")
_APPROVAL = Path("candidates/authorization/measurement-operator-approval.json")
_EVIDENCE = Path("candidates/authorization/track8a-acquisition-evidence.json")
_EXPERIMENT = Path("candidates/authorization/first-real-candidate-experiment.json")
ARCHIVE_SHA256 = "c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9"
HEADER_MEMBER = "onnxruntime-linux-x64-1.31.1/include/onnxruntime_c_api.h"
HEADER_SHA256 = "43d584f596ef66820421317df32a79a95fc1d39ee46cb3971a870c08d8ba4baa"
HEADER_BYTES = 422790
RUNTIME_ATTEMPT = "rp-c2fe1c88f694fc1e"
CANDIDATE_ATTEMPT = "cd-20b7ceee37a62cba"
ARCHIVE_ATTEMPT = "rt-e791f1518ae46ead"
ARCHIVE_NAME = "onnxruntime-linux-x64-1.31.1.tgz"
ADDRESS_SPACE_BYTES = MEMORY_CAP * 2
REPEATED_TOKEN_ID = 574
SMOKE_PROMPT = "Reply with one token."
SHORT_PROMPT = "Reply with the single word ready."
CHAT_TEMPLATE_SHA256 = "f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176"
PROMPT_TEMPLATE_DIGEST = "62774d0f8b65c959c5b038911af4293d3d774aae3933f0d7a24064691685250a"
CORPUS_DIGEST = "49fe79544a26de429afe865fbd2666828bf26a6da30efe6d87f3b0fdfbd0989c"
HARNESS_CANDIDATE_ID = "fixture-lfm25-instruct"
PROTOCOL_CANDIDATE_VERSION = "10f72e70abf67ac0fd7ebf15bc5854726891d864"
TOKENIZER_SHA256 = "0a1f2cb9fc2769030ca1f4207e81c1af493319373d41b8d3cf5be53860c13760"
PHASE_ORDER: tuple[str, ...] = (
    "preflight",
    "one-token-smoke",
    "short-generation",
    "context-4096",
    "context-8192",
    "corpus-evaluation",
)
STOP_CONDITIONS: tuple[str, ...] = (
    "digest-mismatch",
    "missing-root",
    "approval-required",
    "isolation-failure",
    "network-violation",
    "unverified-dependency",
    "telemetry-unresolved",
    "oom",
    "memory-ceiling",
    "cleanup-failure",
    "excessive-output",
    "prior-phase-failed",
    "gold-visible",
)
_SESSION_STOPS = frozenset(
    {
        "digest-mismatch",
        "missing-root",
        "approval-required",
        "isolation-failure",
        "network-violation",
        "unverified-dependency",
        "telemetry-unresolved",
        "oom",
        "memory-ceiling",
        "cleanup-failure",
        "excessive-output",
        "prior-phase-failed",
        "gold-visible",
    }
)


class MeasurementError(ValueError):
    """A measurement record or preflight check failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def digest_document(document: dict[str, Any], schema_name: str, field: str) -> dict[str, Any]:
    """Attach one digest field and validate the closed document."""
    payload = {key: value for key, value in document.items() if key != field}
    payload[field] = sha256_text(canonical_dumps(payload))
    reject_sensitive(payload)
    validate(schema_name, payload)
    return payload


def empty_memory() -> dict[str, Any]:
    """A memory block with no observation. Address space is not the resident ceiling."""
    return {
        "addressSpaceLimitBytes": ADDRESS_SPACE_BYTES,
        "cgroupCurrentBytes": None,
        "cgroupPeakBytes": None,
        "oomEvents": None,
        "processRssBytes": None,
        "processTreeRssBytes": None,
        "residentCeilingBytes": MEMORY_CAP,
        "telemetry": "not-observed",
        "virtualAddressBytes": None,
    }


def authority() -> dict[str, Any]:
    """Fields that stay locked for every measurement record."""
    return {
        "calibrationStatus": "not-approved",
        "installationAuthorized": False,
        "productionReady": False,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
    }


def empty_timing() -> dict[str, Any]:
    """A timing block with no observation."""
    return {
        "firstTokenSeconds": None,
        "generationSeconds": None,
        "loadSeconds": None,
        "wallSeconds": None,
    }


def sha256_file(path: Path) -> str:
    """Hash one file. The digest is the only value returned."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_evidence(root: Path | None = None) -> dict[str, Any]:
    """Load the committed Track 8A evidence document."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _EVIDENCE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    return loaded


def _files(rows: object) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise MeasurementError("digest-mismatch")
    files: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise MeasurementError("digest-mismatch")
        files.append(
            {
                "bytes": int(row["logicalBytes"]),
                "path": str(row["fileName"]),
                "sha256": str(row["localSha256"]),
            }
        )
    return files


def _phase(
    order: int,
    phase: str,
    prerequisite: str | None,
    *,
    max_new_tokens: int,
    input_tokens: int | None,
    repetitions: int,
    cold_warm: bool,
    prompt: str,
    generation_budget: int,
    stdout_bytes: int,
    stderr_bytes: int,
    wall: int = 900,
    cpu: int = 600,
) -> dict[str, Any]:
    return {
        "batchSize": 1,
        "coldWarm": cold_warm,
        "cpuSeconds": cpu,
        "generationBudgetSeconds": generation_budget,
        "inputTokens": input_tokens,
        "maxNewTokens": max_new_tokens,
        "order": order,
        "phase": phase,
        "phaseBoundaryDwellMilliseconds": 150,
        "prerequisite": prerequisite,
        "promptConstruction": prompt,
        "repetitions": repetitions,
        "sampleIntervalMilliseconds": 100,
        "stderrBytes": stderr_bytes,
        "stdoutBytes": stdout_bytes,
        "wallClockSeconds": wall,
    }


def build_measurement_plan(root: Path | None = None) -> dict[str, Any]:
    """Build the sealed plan from committed Track 8A evidence."""
    evidence = load_evidence(root)
    archive = evidence.get("runtimeArchive")
    if not isinstance(archive, dict) or archive.get("localSha256") != ARCHIVE_SHA256:
        raise MeasurementError("digest-mismatch")
    if evidence.get("track8bMeasurementAuthorization") != "not-authorized":
        raise MeasurementError("authority")
    runtime_files = _files(evidence.get("runtimeFiles"))
    candidate_files = _files(evidence.get("candidateFiles"))
    if len(runtime_files) != 4 or len(candidate_files) != 11:
        raise MeasurementError("digest-mismatch")
    phases = [
        _phase(
            1,
            "preflight",
            None,
            max_new_tokens=0,
            input_tokens=None,
            repetitions=1,
            cold_warm=False,
            prompt="none",
            generation_budget=1,
            stdout_bytes=8192,
            stderr_bytes=8192,
            wall=1,
            cpu=1,
        ),
        _phase(
            2,
            "one-token-smoke",
            "preflight",
            max_new_tokens=1,
            input_tokens=None,
            repetitions=1,
            cold_warm=False,
            prompt="chat-template",
            generation_budget=60,
            stdout_bytes=8192,
            stderr_bytes=262144,
        ),
        _phase(
            3,
            "short-generation",
            "one-token-smoke",
            max_new_tokens=32,
            input_tokens=None,
            repetitions=1,
            cold_warm=True,
            prompt="chat-template",
            generation_budget=120,
            stdout_bytes=8192,
            stderr_bytes=262144,
        ),
        _phase(
            4,
            "context-4096",
            "short-generation",
            max_new_tokens=1,
            input_tokens=4096,
            repetitions=1,
            cold_warm=True,
            prompt="repeated-token-id",
            generation_budget=300,
            stdout_bytes=8192,
            stderr_bytes=262144,
        ),
        _phase(
            5,
            "context-8192",
            "context-4096",
            max_new_tokens=1,
            input_tokens=8192,
            repetitions=1,
            cold_warm=True,
            prompt="repeated-token-id",
            generation_budget=600,
            stdout_bytes=8192,
            stderr_bytes=262144,
        ),
        _phase(
            6,
            "corpus-evaluation",
            "context-8192",
            max_new_tokens=256,
            input_tokens=None,
            repetitions=3,
            cold_warm=False,
            prompt="protocol-request",
            generation_budget=15,
            stdout_bytes=65536,
            stderr_bytes=16384,
        ),
    ]
    document: dict[str, Any] = {
        "addressSpaceBytes": ADDRESS_SPACE_BYTES,
        "calibrationStatus": "not-approved",
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateFiles": candidate_files,
        "candidateModelId": "LiquidAI/LFM2.5-1.2B-Instruct",
        "chatTemplateSha256": CHAT_TEMPLATE_SHA256,
        "corpusDigest": CORPUS_DIGEST,
        "decoding": {
            "method": "greedy-argmax",
            "repetitionPenalty": 1,
            "seed": 0,
            "seedControl": "unused",
            "seedSupport": False,
            "temperature": 0,
            "topK": 1,
            "topP": 1,
        },
        "eosTokenId": 7,
        "executionStatus": "not-executed",
        "harnessCandidateId": HARNESS_CANDIDATE_ID,
        "headerMember": {
            "bytes": HEADER_BYTES,
            "member": HEADER_MEMBER,
            "sha256": HEADER_SHA256,
        },
        "hostCapabilityClass": "linux-cgroup-v2-user-scope",
        "installationAuthorized": False,
        "interOpThreads": 1,
        "intraOpThreads": 8,
        "measurementAuthorization": "not-authorized",
        "measurementPerformed": False,
        "memoryMaxBytes": MEMORY_CAP,
        "onnxRevision": PROTOCOL_CANDIDATE_VERSION,
        "operatorApproval": "required",
        "phases": phases,
        "productionReady": False,
        "profileId": "linux-bwrap-systemd-v1",
        "profileVersion": "1.0.0",
        "promptTemplateDigest": PROMPT_TEMPLATE_DIGEST,
        "protocolCandidateVersion": PROTOCOL_CANDIDATE_VERSION,
        "realModelExecuted": False,
        "repeatedTokenId": REPEATED_TOKEN_ID,
        "resultRootClass": "measurement-result",
        "runtimeArchiveSha256": ARCHIVE_SHA256,
        "runtimeAttemptId": RUNTIME_ATTEMPT,
        "runtimeFiles": runtime_files,
        "runtimeRevision": "6af1a932e2286d5c58166085d24c68783033edee",
        "runtimeVersionTag": "v1.31.1",
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "shortPrompt": SHORT_PROMPT,
        "smokePrompt": SMOKE_PROMPT,
        "sourceRevision": "b9d816ab510f9a28dca37cb182e9da8b0226e13c",
        "stopConditions": list(STOP_CONDITIONS),
        "tasksMax": 32,
    }
    return digest_document(document, "measurement-plan", "planDigest")


def load_measurement_plan(root: Path | None = None) -> dict[str, Any]:
    """Load the committed plan and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _PLAN).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    validate("measurement-plan", loaded)
    if loaded != build_measurement_plan(base):
        raise MeasurementError("record-drift")
    return loaded


def build_operator_approval(root: Path | None = None) -> dict[str, Any]:
    """Build the committed approval record. It stays not-approved."""
    plan = build_measurement_plan(root)
    return digest_document(
        {
            "approvalStatus": "not-approved",
            "calibrationStatus": "not-approved",
            "installationAuthorized": False,
            "measurementPerformed": False,
            "planDigest": plan["planDigest"],
            "productionReady": False,
            "realModelExecuted": False,
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
        },
        "measurement-operator-approval",
        "identityDigest",
    )


def load_operator_approval(root: Path | None = None) -> dict[str, Any]:
    """Load the committed approval record and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _APPROVAL).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    validate("measurement-operator-approval", loaded)
    if loaded != build_operator_approval(base):
        raise MeasurementError("record-drift")
    return loaded


def require_operator_approval(supplied: str, root: Path | None = None) -> dict[str, Any]:
    """Accept only the digest of the committed measurement plan."""
    plan = load_measurement_plan(root)
    if supplied != plan["planDigest"]:
        raise MeasurementError("approval-required")
    return plan


def phase_by_name(plan: dict[str, Any], name: str) -> dict[str, Any]:
    """Return one phase definition."""
    for phase in plan["phases"]:
        if phase["phase"] == name:
            if isinstance(phase, dict):
                return phase
    raise MeasurementError("phase")


def prerequisite_name(phase: str) -> str | None:
    """Return the phase that must already have passed."""
    if phase not in PHASE_ORDER:
        raise MeasurementError("phase")
    index = PHASE_ORDER.index(phase)
    if index == 0:
        return None
    return PHASE_ORDER[index - 1]


def session_stop(cause: str | None) -> bool:
    """Return whether a cause blocks every later phase."""
    return cause in _SESSION_STOPS


def prompt_template(root: Path | None = None) -> str:
    """Return the approved prompt template after checking its digest."""
    base = root if root is not None else repo_root()
    document = json.loads((base / _EXPERIMENT).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise MeasurementError("record-type")
    template = str(document["promptTemplate"])
    if sha256_text(template) != PROMPT_TEMPLATE_DIGEST:
        raise MeasurementError("digest-mismatch")
    if document["promptTemplateDigest"] != PROMPT_TEMPLATE_DIGEST:
        raise MeasurementError("digest-mismatch")
    return template


def _attempt_dir(root: Path, state: str, attempt_id: str) -> Path:
    path = root / state / attempt_id
    if path.is_symlink() or not path.is_dir():
        raise MeasurementError("missing-root")
    return path


def _check_tree(directory: Path, files: list[dict[str, Any]]) -> None:
    for item in files:
        path = directory / str(item["path"])
        if path.is_symlink() or not path.is_file():
            raise MeasurementError("missing-root")
        if path.stat().st_size != int(item["bytes"]):
            raise MeasurementError("digest-mismatch")
        if sha256_file(path) != item["sha256"]:
            raise MeasurementError("digest-mismatch")


def read_verified_header(runtime_root: Path) -> str:
    """Read the C header from the retained archive after its digest matches."""
    archive = _attempt_dir(runtime_root, "quarantine", ARCHIVE_ATTEMPT) / ARCHIVE_NAME
    if archive.is_symlink() or not archive.is_file():
        raise MeasurementError("missing-root")
    if sha256_file(archive) != ARCHIVE_SHA256:
        raise MeasurementError("digest-mismatch")
    with tarfile.open(archive, "r:gz") as bundle:
        member = bundle.extractfile(HEADER_MEMBER)
        if member is None:
            raise MeasurementError("unverified-dependency")
        payload = member.read()
    if len(payload) != HEADER_BYTES or hashlib.sha256(payload).hexdigest() != HEADER_SHA256:
        raise MeasurementError("digest-mismatch")
    return payload.decode("utf-8")


def bind_verified_roots(
    runtime_root: Path,
    model_root: Path,
    *,
    repository: Path | None = None,
) -> dict[str, str]:
    """Recompute promoted digests. This does not create a session or call Run."""
    plan = load_measurement_plan(repository)
    try:
        runtime = validate_external_root(runtime_root, repository=repository)
        model = validate_external_root(model_root, repository=repository)
    except PlanError as exc:
        raise MeasurementError(exc.code) from exc
    if runtime == model:
        raise MeasurementError("missing-root")
    runtime_dir = _attempt_dir(runtime, "verified", RUNTIME_ATTEMPT)
    model_dir = _attempt_dir(model, "verified", CANDIDATE_ATTEMPT)
    _check_tree(runtime_dir, list(plan["runtimeFiles"]))
    _check_tree(model_dir, list(plan["candidateFiles"]))
    read_verified_header(runtime)
    library = runtime_dir / "libonnxruntime.so.1.31.1"
    graph = model_dir / "onnx" / "model.onnx"
    if library.is_symlink() or graph.is_symlink():
        raise MeasurementError("digest-mismatch")
    return {
        "archiveAttemptId": ARCHIVE_ATTEMPT,
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateClass": "verified-candidate",
        "digestMatch": "true",
        "runtimeAttemptId": RUNTIME_ATTEMPT,
        "runtimeClass": "verified-runtime",
    }


def validate_result_root(root: Path, *, repository: Path | None = None) -> Path:
    """Accept a writable external result root and return no host path to callers."""
    try:
        resolved = validate_external_root(root, repository=repository)
    except PlanError as exc:
        raise MeasurementError(exc.code) from exc
    if not resolved.is_dir():
        raise MeasurementError("missing-root")
    probe = resolved / ".measurement-write-probe"
    try:
        probe.write_text("ok\n", encoding="utf-8")
    except OSError as exc:
        raise MeasurementError("missing-root") from exc
    finally:
        probe.unlink(missing_ok=True)
    return resolved
