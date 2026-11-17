"""Corpus-continuation preflight. It does not create a model session or call Run."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus_continuation_plan import (
    PROFILE_ID,
    artifact_pins,
    identity_fields,
    load_corpus_plan,
    validate_continuation_root,
)
from patchpilot_intelligence_evals.hardened_execution import (
    HardenedExecutionError,
    execute_hardened,
)
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    RUNTIME_ATTEMPT,
    MeasurementError,
    bind_verified_roots,
    digest_document,
)
from patchpilot_intelligence_evals.measurement_retry_preflight import (
    observe_template,
    read_publisher_template,
    utc_timestamp,
)
from patchpilot_intelligence_evals.runtime_dependency_closure import (
    INTERPRETER_NAME,
    LIBRARY_NAME,
    ClosureError,
    approved_public_closure,
    approved_runtime_mounts,
)
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/corpus-continuation-preflight-template.json")
_CHILD = Path(__file__).with_name("dynamic_link_precheck_main.py")
Probe = Callable[[Path], str]


def build_preflight_template() -> dict[str, Any]:
    """Committed preflight. It has not touched a verified root."""
    return digest_document(
        _body(
            load_corpus_plan(),
            artifact="not-checked",
            template_status="not-executed",
            link_status="not-executed",
            preflight_status="not-executed",
            validated=False,
            timestamp="not-executed",
        ),
        "corpus-continuation-preflight",
        "identityDigest",
    )


def load_preflight_template() -> dict[str, Any]:
    """Load the committed preflight and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_preflight_template():
        raise MeasurementError("record-drift")
    return loaded


def run_continuation_preflight(
    runtime_root: Path,
    model_root: Path,
    result_root: Path,
    *,
    bind: bool = True,
    probe: Probe | None = None,
) -> dict[str, Any]:
    """Recompute identities and the no-session checks. This does not call Run."""
    validate_continuation_root(result_root, resume=True)
    plan = load_corpus_plan()
    artifact = "not-checked"
    template_status = "not-executed"
    if bind:
        binding = bind_verified_roots(runtime_root, model_root)
        if binding["runtimeAttemptId"] != RUNTIME_ATTEMPT:
            raise MeasurementError("digest-mismatch")
        if binding["candidateAttemptId"] != CANDIDATE_ATTEMPT:
            raise MeasurementError("digest-mismatch")
        artifact = "matched"
        observed = observe_template(read_publisher_template(model_root))
        template_status = str(observed["compatibility"])
        if template_status != "supported":
            template_status = "failed"
    chosen = probe if probe is not None else observe_dynamic_link
    link_status = chosen(runtime_root) if bind or probe is not None else "not-executed"
    if link_status not in {"not-executed", "passed", "failed", "unavailable"}:
        raise MeasurementError("precheck-failed")
    if template_status == "failed" or link_status in {"failed", "unavailable"}:
        status = "failed"
    elif artifact == "matched" and template_status == "supported" and link_status == "passed":
        status = "passed"
    else:
        status = "not-executed"
    return digest_document(
        _body(
            plan,
            artifact=artifact,
            template_status=template_status if template_status != "supported" else "supported",
            link_status=link_status,
            preflight_status=status,
            validated=True,
            timestamp=utc_timestamp(),
        ),
        "corpus-continuation-preflight",
        "identityDigest",
    )


def observe_dynamic_link(runtime_root: Path) -> str:
    """Load the runtime library inside the sandbox and exit before Run."""
    runtime_dir = runtime_root / "verified" / RUNTIME_ATTEMPT
    library = runtime_dir / LIBRARY_NAME
    try:
        mounts = approved_runtime_mounts(library)
    except ClosureError:
        return "failed"
    if not runtime_dir.is_dir() or library.is_symlink() or not _individual(mounts):
        return "failed"
    from patchpilot_intelligence_evals.candidate_inference import measurement_limits
    from patchpilot_intelligence_evals.filesystem_policy import Mount

    try:
        result = execute_hardened(
            _CHILD,
            (),
            limits=measurement_limits(load_corpus_plan()),
            environment=(("ORT_DISABLE_TELEMETRY", "1"),),
            extra_mounts=(Mount(str(runtime_dir), "/verified-runtime", True), *mounts),
        )
    except HardenedExecutionError:
        return "failed"
    if not result.report:
        return "failed"
    try:
        report = json.loads(result.report.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "failed"
    if not isinstance(report, dict):
        return "failed"
    names = report.get("mappedBasenames")
    present = {str(item) for item in names} if isinstance(names, list) else set()
    required = {row["basename"] for row in approved_public_closure()}
    required.add(LIBRARY_NAME)
    held = (
        result.return_code == 0
        and report.get("symbolBoundary") == "held"
        and report.get("createSessionCalled") is False
        and report.get("getApiCalled") is False
        and report.get("runInvoked") is False
        and report.get("modelSessionCreated") is False
        and report.get("providerLoaded") is False
        and report.get("unexpectedPath") is False
        and report.get("libraryClosed") is True
        and INTERPRETER_NAME in present
        and required.issubset(present)
        and result.cleanup == "reaped"
    )
    return "passed" if held else "failed"


def _individual(mounts: tuple[Any, ...]) -> bool:
    broad = {"/lib", "/lib64", "/usr/lib", "/usr/lib64", "/usr/lib/x86_64-linux-gnu"}
    for mount in mounts:
        destination = str(mount.destination).rstrip("/")
        source = Path(mount.source)
        if destination in broad or not mount.read_only or source.is_dir() or not source.is_file():
            return False
    return True


def _body(
    plan: dict[str, Any],
    *,
    artifact: str,
    template_status: str,
    link_status: str,
    preflight_status: str,
    validated: bool,
    timestamp: str,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "artifactIdentity": artifact,
        "cleanupEvidence": "not-observed",
        "dynamicLinkStatus": link_status,
        "failureAuthority": None,
        "failureEvidence": "not-executed",
        "measurementCompleted": False,
        "measurementPerformed": False,
        "memoryEvidence": "not-observed",
        "modelSessionCreated": False,
        "outputLimitStatus": "not-retained",
        "preflightStatus": preflight_status,
        "profileId": PROFILE_ID,
        "realModelExecuted": False,
        "recordKind": "preflight",
        "resultRootValidated": validated,
        "runInvoked": False,
        "stderrTruncated": False,
        "stdoutTruncated": False,
        "templateStatus": template_status,
        "timestamp": timestamp,
    }
