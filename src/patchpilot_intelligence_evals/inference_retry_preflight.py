"""No-Run preflight and template compatibility for the inference retry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.corpus import canonical_dumps
from patchpilot_intelligence_evals.inference_retry_plan import (
    PHASE_ORDER,
    frozen_flags,
    load_inference_plan,
    validate_inference_result_root,
)
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    MeasurementError,
    bind_verified_roots,
    digest_document,
)
from patchpilot_intelligence_evals.measurement_retry_preflight import (
    observe_template,
    prove_template,
    read_publisher_template,
)
from patchpilot_intelligence_evals.measurement_retry_preflight import (
    utc_timestamp as utc_timestamp,
)
from patchpilot_intelligence_evals.schemas import repo_root

_PREFLIGHT = Path("candidates/templates/inference-retry-preflight-template.json")
SYNTHETIC_RENDERED_DIGEST = "5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d"
PHASE_FILES = {
    "preflight": "preflight.json",
    "template-compatibility": "template-compatibility.json",
    "dynamic-link-precheck": "dynamic-link-precheck.json",
    "one-token-smoke": "one-token-smoke.json",
    "short-generation": "short-generation.json",
    "context-4096": "context-4096.json",
    "context-8192": "context-8192.json",
    "corpus-evaluation": "corpus-summary.json",
}


def build_preflight_template() -> dict[str, Any]:
    """Committed preflight. It has not touched a verified root."""
    plan = load_inference_plan()
    return digest_document(
        _preflight_body(plan, status="not-executed", timestamp="not-executed"),
        "inference-retry-preflight",
        "identityDigest",
    )


def build_compatibility_template() -> dict[str, Any]:
    """Prove the committed fixture. This does not create a session or call Run."""
    plan = load_inference_plan()
    template = (repo_root() / "tests/fixtures/verified-chat-template.jinja").read_text(
        encoding="utf-8"
    )
    proved = prove_template(template)
    return digest_document(
        _compatibility_body(plan, proved, timestamp="not-executed"),
        "inference-retry-preflight",
        "identityDigest",
    )


def load_preflight_template() -> dict[str, Any]:
    """Load the committed preflight and require it to match the builder."""
    return _load(_PREFLIGHT, build_preflight_template)


def load_compatibility_template() -> dict[str, Any]:
    """Load the committed compatibility proof from the same preflight schema."""
    path = repo_root() / "candidates/templates/inference-retry-compatibility-template.json"
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_compatibility_template():
        raise MeasurementError("record-drift")
    return loaded


def run_preflight(runtime_root: Path, model_root: Path, result_root: Path) -> dict[str, Any]:
    """Recompute promoted digests and prove the publisher template. No session is created."""
    binding = bind_verified_roots(runtime_root, model_root)
    root = validate_inference_result_root(result_root, resume=False)
    plan = load_inference_plan()
    sealed = digest_document(
        _preflight_body(plan, status="ok", timestamp=utc_timestamp()),
        "inference-retry-preflight",
        "identityDigest",
    )
    if sealed["archiveAttemptId"] != binding["archiveAttemptId"]:
        raise MeasurementError("digest-mismatch")
    if sealed["candidateAttemptId"] != binding["candidateAttemptId"]:
        raise MeasurementError("digest-mismatch")
    if sealed["runtimeAttemptId"] != binding["runtimeAttemptId"]:
        raise MeasurementError("digest-mismatch")
    if sealed["runInvoked"] is not False or sealed["modelSessionCreated"] is not False:
        raise MeasurementError("compatibility-failure")
    reject_sensitive(sealed)
    write_new(root, PHASE_FILES["preflight"], sealed)
    run_compatibility(model_root, root)
    return sealed


def run_compatibility(model_root: Path, result_root: Path) -> dict[str, Any]:
    """Validate the mounted template before any model session."""
    root = validate_inference_result_root(result_root, resume=True)
    require_prior(root, "template-compatibility")
    plan = load_inference_plan()
    proved = observe_template(read_publisher_template(model_root))
    sealed = digest_document(
        _compatibility_body(plan, proved, timestamp=utc_timestamp()),
        "inference-retry-preflight",
        "identityDigest",
    )
    if sealed["runInvoked"] is not False or sealed["sessionCreated"] is not False:
        raise MeasurementError("compatibility-failure")
    reject_sensitive(sealed)
    write_new(root, PHASE_FILES["template-compatibility"], sealed)
    if sealed["compatibility"] != "supported":
        if sealed["compatibility"] == "identity-mismatch":
            raise MeasurementError("digest-mismatch")
        raise MeasurementError("compatibility-failure")
    return sealed


def load_phase(result_root: Path, phase_name: str) -> dict[str, Any]:
    """Load one external inference-retry phase record."""
    if phase_name not in PHASE_ORDER:
        raise MeasurementError("phase")
    path = result_root / PHASE_FILES[phase_name]
    if path.is_symlink() or not path.is_file():
        raise MeasurementError("missing-root")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise MeasurementError("record-type")
    return document


def require_prior(result_root: Path, phase_name: str) -> None:
    """Refuse a phase whose prerequisite is missing or unsuccessful."""
    previous = None
    if phase_name in PHASE_ORDER:
        index = PHASE_ORDER.index(phase_name)
        if index:
            previous = PHASE_ORDER[index - 1]
    if previous is None:
        return
    path = result_root / PHASE_FILES[previous]
    if path.is_symlink() or not path.is_file():
        raise MeasurementError("prior-phase-failed")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not passed(previous, document):
        raise MeasurementError("prior-phase-failed")


def require_passed_precheck(result_root: Path) -> dict[str, Any]:
    """Require the exact-sandbox precheck before a model session."""
    document = load_phase(result_root, "dynamic-link-precheck")
    if not passed("dynamic-link-precheck", document):
        raise MeasurementError("precheck-failed")
    return document


def passed(phase_name: str, document: dict[str, Any]) -> bool:
    """Return whether one phase record allows the next phase."""
    if phase_name == "preflight":
        return (
            document.get("recordKind") == "preflight"
            and document.get("status") == "ok"
            and document.get("runInvoked") is False
        )
    if phase_name == "template-compatibility":
        return (
            document.get("recordKind") == "template-compatibility"
            and document.get("compatibility") == "supported"
            and document.get("renderedDigest") == SYNTHETIC_RENDERED_DIGEST
            and document.get("runInvoked") is False
            and document.get("sessionCreated") is False
        )
    if phase_name == "dynamic-link-precheck":
        return (
            document.get("status") == "passed"
            and document.get("symbolBoundary") == "held"
            and document.get("createSessionCalled") is False
            and document.get("getApiCalled") is False
            and document.get("runInvoked") is False
            and document.get("modelSessionCreated") is False
            and document.get("providerLoaded") is False
            and document.get("unexpectedPath") is False
            and document.get("broadHostLibraryMounted") is False
            and document.get("libraryClosed") is True
            and document.get("networkResult") == "denied"
            and document.get("processCleanup") == "reaped"
        )
    return document.get("exitClassification") == "success" and document.get("stopCause") is None


def write_new(root: Path, name: str, document: dict[str, Any]) -> None:
    """Write one new result file. An existing path is reuse."""
    destination = root / name
    if destination.exists() or destination.is_symlink():
        raise MeasurementError("result-root-reuse")
    destination.write_text(canonical_dumps(document) + "\n", encoding="utf-8")


def _preflight_body(plan: dict[str, Any], *, status: str, timestamp: str) -> dict[str, Any]:
    return {
        **frozen_flags(),
        "archiveAttemptId": "rt-e791f1518ae46ead",
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateClass": "verified-candidate",
        "compatibility": None,
        "contentClass": "synthetic-user",
        "planDigest": plan["planDigest"],
        "recordKind": "preflight",
        "renderedDigest": None,
        "renderedShape": None,
        "runtimeAttemptId": "rp-c2fe1c88f694fc1e",
        "runtimeClass": "verified-runtime",
        "sessionCreated": False,
        "status": status,
        "templateDigest": None,
        "timestamp": timestamp,
    }


def _compatibility_body(
    plan: dict[str, Any],
    proved: dict[str, Any],
    *,
    timestamp: str,
) -> dict[str, Any]:
    compatibility = str(proved.get("compatibility"))
    status = "supported" if compatibility == "supported" else compatibility
    return {
        **frozen_flags(),
        "archiveAttemptId": "rt-e791f1518ae46ead",
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateClass": "verified-candidate",
        "compatibility": compatibility,
        "contentClass": "synthetic-user",
        "planDigest": plan["planDigest"],
        "recordKind": "template-compatibility",
        "renderedDigest": proved.get("renderedDigest"),
        "renderedShape": proved.get("renderedShape"),
        "runtimeAttemptId": "rp-c2fe1c88f694fc1e",
        "runtimeClass": "verified-runtime",
        "sessionCreated": False,
        "status": status,
        "templateDigest": proved.get("templateDigest"),
        "timestamp": timestamp,
    }


def _load(relative: Path, builder: Any) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
