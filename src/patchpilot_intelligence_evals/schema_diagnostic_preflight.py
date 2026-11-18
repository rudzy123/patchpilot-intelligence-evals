"""Schema-diagnostic preflight. It does not create a model session or call Run."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus_continuation_plan import PROFILE_ID
from patchpilot_intelligence_evals.corpus_continuation_preflight import observe_dynamic_link
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
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    artifact_pins,
    identity_fields,
    load_schema_diagnostic_plan,
    validate_diagnostic_root,
)
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/schema-diagnostic-preflight-template.json")
Probe = Callable[[Path], str]


def build_preflight_template() -> dict[str, Any]:
    """Committed preflight. It has not touched a verified root."""
    return digest_document(
        _body(
            load_schema_diagnostic_plan(),
            artifact="not-checked",
            template_status="not-executed",
            link_status="not-executed",
            preflight_status="not-executed",
            validated=False,
            timestamp="not-executed",
            evidence="not-executed",
        ),
        "schema-diagnostic-preflight",
        "identityDigest",
    )


def load_preflight_template() -> dict[str, Any]:
    """Load the committed preflight and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_preflight_template():
        raise MeasurementError("record-drift")
    return loaded


def run_schema_diagnostic_preflight(
    runtime_root: Path,
    model_root: Path,
    result_root: Path,
    *,
    bind: bool = True,
    probe: Probe | None = None,
) -> dict[str, Any]:
    """Recompute identities and the no-session checks. This does not call Run."""
    validate_diagnostic_root(result_root, resume=True)
    plan = load_schema_diagnostic_plan()
    artifact = "not-checked"
    template_status = "not-executed"
    evidence = "not-executed"
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
            evidence = "compatibility-failure"
    chosen = probe if probe is not None else observe_dynamic_link
    link_status = chosen(runtime_root) if bind or probe is not None else "not-executed"
    if link_status not in {"not-executed", "passed", "failed", "unavailable"}:
        raise MeasurementError("precheck-failed")
    if template_status == "failed" or link_status in {"failed", "unavailable"}:
        status = "failed"
        if evidence == "not-executed":
            evidence = "precheck-failed"
    elif artifact == "matched" and template_status == "supported" and link_status == "passed":
        status = "passed"
        evidence = "preflight"
    else:
        status = "not-executed"
    return digest_document(
        _body(
            plan,
            artifact=artifact,
            template_status=template_status,
            link_status=link_status,
            preflight_status=status,
            validated=True,
            timestamp=utc_timestamp(),
            evidence=evidence,
        ),
        "schema-diagnostic-preflight",
        "identityDigest",
    )


def _body(
    plan: dict[str, Any],
    *,
    artifact: str,
    template_status: str,
    link_status: str,
    preflight_status: str,
    validated: bool,
    timestamp: str,
    evidence: str,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "artifactIdentity": artifact,
        "cleanupEvidence": "not-observed",
        "dynamicLinkStatus": link_status,
        "failureAuthority": None,
        "failureEvidence": evidence,
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
        "runs": plan["runs"],
        "stderrTruncated": False,
        "stdoutTruncated": False,
        "systematicThreshold": plan["systematicThreshold"],
        "templateStatus": template_status,
        "timestamp": timestamp,
    }
