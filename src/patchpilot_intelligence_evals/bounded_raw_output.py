"""Bounded immutable stdout and stderr retention. Later runs cannot read it."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus_continuation_plan import (
    artifact_pins,
    identity_fields,
    load_corpus_plan,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.protocol import MAX_STDERR_BYTES, MAX_STDOUT_BYTES
from patchpilot_intelligence_evals.result_store import ResultStoreError, write_canonical

_TEMPLATE = Path("candidates/templates/bounded-raw-output-template.json")


def build_raw_template() -> dict[str, Any]:
    """Committed raw-output record. No candidate bytes are stored."""
    return digest_document(
        _body(
            load_corpus_plan(),
            case_id="not-executed",
            repetition=0,
            run_id="not-executed",
            stdout=b"",
            stderr=b"",
            limit_status="not-retained",
            retained=False,
        ),
        "bounded-raw-output",
        "identityDigest",
    )


def load_raw_template() -> dict[str, Any]:
    """Load the committed template and require it to match the builder."""
    from patchpilot_intelligence_evals.corpus_continuation_plan import _load

    return _load(None, _TEMPLATE, lambda _root: build_raw_template())


def retain_bounded_output(
    root: Path,
    *,
    case_id: str,
    repetition: int,
    run_id: str,
    stdout: bytes,
    stderr: bytes,
    limit_status: str,
) -> dict[str, Any]:
    """Seal raw bytes before extraction. A later stage cannot replace them."""
    if len(stdout) > MAX_STDOUT_BYTES or len(stderr) > MAX_STDERR_BYTES:
        raise MeasurementError("excessive-output")
    if limit_status not in {"within-limit", "stdout-limit-exceeded", "stderr-limit-exceeded"}:
        raise MeasurementError("raw-output-unretained")
    run_dir = root / "runs" / run_id
    if run_dir.exists():
        raise MeasurementError("result-root-reuse")
    runs = root / "runs"
    try:
        if not runs.exists():
            runs.mkdir(mode=0o700)
        os.chmod(runs, 0o700)
        run_dir.mkdir(mode=0o700)
        os.chmod(run_dir, 0o700)
    except OSError as exc:
        raise MeasurementError("raw-output-unretained") from exc
    stdout_path = run_dir / "stdout.bin"
    stderr_path = run_dir / "stderr.bin"
    try:
        stdout_path.write_bytes(stdout)
        stderr_path.write_bytes(stderr)
        os.chmod(stdout_path, 0o400)
        os.chmod(stderr_path, 0o400)
        if stdout_path.read_bytes() != stdout or stderr_path.read_bytes() != stderr:
            raise MeasurementError("raw-output-unretained")
    except OSError as exc:
        raise MeasurementError("raw-output-unretained") from exc
    plan = load_corpus_plan()
    sealed = digest_document(
        _body(
            plan,
            case_id=case_id,
            repetition=repetition,
            run_id=run_id,
            stdout=stdout,
            stderr=stderr,
            limit_status=limit_status,
            retained=True,
        ),
        "bounded-raw-output",
        "identityDigest",
    )
    try:
        write_canonical(
            f"runs/{run_id}/raw-output.json",
            sealed,
            schema_name="bounded-raw-output",
            root=root,
        )
    except ResultStoreError as exc:
        raise MeasurementError("raw-output-unretained") from exc
    os.chmod(root / "runs" / run_id / "raw-output.json", 0o400)
    return sealed


def _body(
    plan: dict[str, Any],
    *,
    case_id: str,
    repetition: int,
    run_id: str,
    stdout: bytes,
    stderr: bytes,
    limit_status: str,
    retained: bool,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "availableToCandidate": False,
        "availableToLaterRuns": False,
        "caseId": case_id,
        "cleanupEvidence": "not-observed",
        "failureAuthority": None,
        "failureEvidence": "not-executed",
        "freeOfGold": True,
        "hostIdentityExcluded": True,
        "immutable": retained,
        "memoryEvidence": "not-observed",
        "outputLimitStatus": limit_status,
        "recordKind": "raw-output",
        "repetition": repetition,
        "retentionStatus": "retained" if retained else "not-retained",
        "runId": run_id,
        "stderrBytes": len(stderr) if retained else 0,
        "stderrDigest": _digest(stderr) if retained else None,
        "stderrTruncated": limit_status == "stderr-limit-exceeded",
        "stdoutBytes": len(stdout) if retained else 0,
        "stdoutDigest": _digest(stdout) if retained else None,
        "stdoutTruncated": limit_status == "stdout-limit-exceeded",
    }


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
