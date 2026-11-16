"""No-Run preflight and template compatibility for the retry plan."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    MeasurementError,
    bind_verified_roots,
    digest_document,
)
from patchpilot_intelligence_evals.measurement_retry_plan import (
    PHASE_ORDER,
    SYNTHETIC_CONTENT,
    SYNTHETIC_RENDERED_DIGEST,
    frozen_flags,
    load_retry_plan,
    validate_retry_result_root,
)
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.template_compatibility import (
    CHAT_TEMPLATE_SHA256,
    TemplateCompatibilityError,
    validate_chat_template,
)

_PREFLIGHT = Path("candidates/templates/measurement-retry-preflight-template.json")
_COMPATIBILITY = Path("candidates/templates/template-compatibility-result-template.json")
_FIXTURE = Path("tests/fixtures/verified-chat-template.jinja")
PHASE_FILES = {
    "preflight": "preflight.json",
    "template-compatibility": "template-compatibility.json",
    "one-token-smoke": "one-token-smoke.json",
    "short-generation": "short-generation.json",
    "context-4096": "context-4096.json",
    "context-8192": "context-8192.json",
    "corpus-evaluation": "corpus-summary.json",
}


def utc_timestamp() -> str:
    """Return a UTC timestamp short enough for the closed records."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_preflight_template() -> dict[str, Any]:
    """Committed preflight. It has not touched a verified root."""
    plan = load_retry_plan()
    return digest_document(
        {
            **frozen_flags(),
            "archiveAttemptId": "rt-e791f1518ae46ead",
            "candidateAttemptId": "cd-20b7ceee37a62cba",
            "candidateClass": "verified-candidate",
            "planDigest": plan["planDigest"],
            "runtimeAttemptId": "rp-c2fe1c88f694fc1e",
            "runtimeClass": "verified-runtime",
            "status": "not-executed",
        },
        "measurement-retry-preflight",
        "identityDigest",
    )


def build_compatibility_template() -> dict[str, Any]:
    """Prove the committed fixture. This does not create a session or call Run."""
    plan = load_retry_plan()
    template = (repo_root() / _FIXTURE).read_text(encoding="utf-8")
    proved = prove_template(template)
    return digest_document(
        _compatibility_body(plan, proved, timestamp="not-executed"),
        "template-compatibility-result",
        "identityDigest",
    )


def load_preflight_template() -> dict[str, Any]:
    """Load the committed preflight and require it to match the builder."""
    return _load(_PREFLIGHT, build_preflight_template)


def load_compatibility_template() -> dict[str, Any]:
    """Load the committed compatibility proof and require it to match the builder."""
    return _load(_COMPATIBILITY, build_compatibility_template)


def observe_template(template: str) -> dict[str, Any]:
    """Render the synthetic fixture. This does not create a session or call Run."""
    observed = sha256_text(template)
    rejected = {
        "compatibility": "identity-mismatch",
        "renderedDigest": None,
        "renderedShape": "not-rendered",
        "templateDigest": observed,
    }
    if observed != CHAT_TEMPLATE_SHA256:
        return rejected
    try:
        record = validate_chat_template(
            template,
            expected_digest=CHAT_TEMPLATE_SHA256,
            content=SYNTHETIC_CONTENT,
        )
    except TemplateCompatibilityError as exc:
        rejected["compatibility"] = exc.code
        return rejected
    if (
        record["renderedDigest"] != SYNTHETIC_RENDERED_DIGEST
        or record["runInvoked"] is not False
        or record["sessionCreated"] is not False
        or record["compatibility"] != "supported"
    ):
        rejected["compatibility"] = "invalid-rendered-prompt"
        return rejected
    return record


def prove_template(template: str) -> dict[str, Any]:
    """Require the supported synthetic proof."""
    record = observe_template(template)
    if record["compatibility"] != "supported":
        code = (
            "digest-mismatch"
            if record["compatibility"] == "identity-mismatch"
            else ("compatibility-failure")
        )
        raise MeasurementError(code)
    return record


def read_publisher_template(model_root: Path) -> str:
    """Read the mounted publisher template. The bytes are not rewritten."""
    path = model_root / "verified" / CANDIDATE_ATTEMPT / "chat_template.jinja"
    if path.is_symlink() or not path.is_file():
        raise MeasurementError("missing-root")
    return path.read_text(encoding="utf-8")


def run_preflight(runtime_root: Path, model_root: Path, result_root: Path) -> dict[str, Any]:
    """Recompute promoted digests and prove the publisher template. No session is created."""
    binding = bind_verified_roots(runtime_root, model_root)
    root = validate_retry_result_root(result_root, resume=False)
    plan = load_retry_plan()
    document = build_preflight_template()
    document = {
        **document,
        "planDigest": plan["planDigest"],
        "status": "ok",
    }
    document.pop("identityDigest", None)
    sealed = digest_document(document, "measurement-retry-preflight", "identityDigest")
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
    plan = load_retry_plan()
    template = read_publisher_template(model_root)
    proved = observe_template(template)
    sealed = digest_document(
        _compatibility_body(plan, proved, timestamp=utc_timestamp()),
        "template-compatibility-result",
        "identityDigest",
    )
    if sealed["runInvoked"] is not False or sealed["sessionCreated"] is not False:
        raise MeasurementError("compatibility-failure")
    reject_sensitive(sealed)
    write_new(result_root, PHASE_FILES["template-compatibility"], sealed)
    if sealed["compatibility"] != "supported":
        if sealed["compatibility"] == "identity-mismatch":
            raise MeasurementError("digest-mismatch")
        raise MeasurementError("compatibility-failure")
    return sealed


def load_phase(result_root: Path, phase_name: str) -> dict[str, Any]:
    """Load one external retry phase record."""
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


def passed(phase_name: str, document: dict[str, Any]) -> bool:
    """Return whether one phase record allows the next phase."""
    if phase_name == "preflight":
        return document.get("status") == "ok" and document.get("runInvoked") is False
    if phase_name == "template-compatibility":
        return (
            document.get("compatibility") == "supported"
            and document.get("renderedDigest") == SYNTHETIC_RENDERED_DIGEST
            and document.get("runInvoked") is False
            and document.get("sessionCreated") is False
        )
    return document.get("exitClassification") == "success" and document.get("stopCause") is None


def write_new(root: Path, name: str, document: dict[str, Any]) -> None:
    """Write one new result file. An existing path is reuse."""
    destination = root / name
    if destination.exists() or destination.is_symlink():
        raise MeasurementError("result-root-reuse")
    destination.write_text(canonical_dumps(document) + "\n", encoding="utf-8")


def _compatibility_body(
    plan: dict[str, Any],
    proved: dict[str, Any],
    *,
    timestamp: str,
) -> dict[str, Any]:
    return {
        **frozen_flags(),
        "compatibility": proved["compatibility"],
        "contentClass": "synthetic-user",
        "planDigest": plan["planDigest"],
        "renderedDigest": proved["renderedDigest"],
        "renderedShape": proved["renderedShape"],
        "sessionCreated": False,
        "templateDigest": proved["templateDigest"],
        "timestamp": timestamp,
    }


def _load(relative: Path, builder: Any) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
