"""Exact-sandbox dynamic-link precheck. It loads the runtime and does not call Run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.candidate_inference import measurement_limits
from patchpilot_intelligence_evals.filesystem_policy import Mount
from patchpilot_intelligence_evals.hardened_execution import (
    ExecutionResult,
    HardenedExecutionError,
    execute_hardened,
)
from patchpilot_intelligence_evals.inference_retry_plan import (
    frozen_flags,
    load_inference_plan,
    phase_by_name,
    validate_inference_result_root,
)
from patchpilot_intelligence_evals.inference_retry_preflight import (
    PHASE_FILES,
    require_prior,
    utc_timestamp,
    write_new,
)
from patchpilot_intelligence_evals.measurement_plan import (
    RUNTIME_ATTEMPT,
    MeasurementError,
    digest_document,
)
from patchpilot_intelligence_evals.runtime_dependency_closure import (
    INTERPRETER_NAME,
    LIBRARY_NAME,
    ClosureError,
    approved_public_closure,
    approved_runtime_mounts,
)
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/dynamic-link-precheck-template.json")
_CHILD = Path(__file__).with_name("dynamic_link_precheck_main.py")
_BROAD = {
    "/lib",
    "/lib64",
    "/usr/lib",
    "/usr/lib64",
    "/usr/lib/x86_64-linux-gnu",
}


def build_precheck_template() -> dict[str, Any]:
    """Committed precheck. The sandbox has not loaded the runtime library."""
    plan = load_inference_plan()
    return digest_document(
        _body(
            plan,
            status="not-executed",
            symbol_boundary="not-executed",
            api_version=None,
            dependencies=approved_public_closure(),
            exported=[],
            mapped=[],
            provider=False,
            closed=False,
            unexpected=False,
            broad=False,
            network="not-performed",
            cleanup="not-performed",
            timestamp="not-executed",
            stop=None,
        ),
        "dynamic-link-precheck",
        "identityDigest",
    )


def load_precheck_template() -> dict[str, Any]:
    """Load the committed precheck and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_precheck_template():
        raise MeasurementError("record-drift")
    return loaded


def run_dynamic_link_precheck(runtime_root: Path, result_root: Path) -> dict[str, Any]:
    """Load the runtime inside the measurement sandbox. No model session is created."""
    root = validate_inference_result_root(result_root, resume=True)
    require_prior(root, "dynamic-link-precheck")
    plan = load_inference_plan()
    runtime_dir = runtime_root / "verified" / RUNTIME_ATTEMPT
    library = runtime_dir / LIBRARY_NAME
    try:
        dependency_mounts = approved_runtime_mounts(library)
    except ClosureError as exc:
        _seal(
            root,
            plan,
            status="failed",
            symbol_boundary="violated",
            api_version=None,
            dependencies=[],
            exported=[],
            mapped=[],
            provider=False,
            closed=False,
            unexpected=False,
            broad=False,
            network="not-performed",
            cleanup="not-performed",
            stop="precheck-failed",
        )
        raise MeasurementError("precheck-failed") from exc
    broad = not _individual(dependency_mounts)
    if broad or not runtime_dir.is_dir() or library.is_symlink():
        _seal(
            root,
            plan,
            status="failed",
            symbol_boundary="violated",
            api_version=None,
            dependencies=[],
            exported=[],
            mapped=[],
            provider=False,
            closed=False,
            unexpected=False,
            broad=broad,
            network="not-performed",
            cleanup="not-performed",
            stop="precheck-failed",
        )
        raise MeasurementError("precheck-failed")
    phase = phase_by_name(plan, "dynamic-link-precheck")
    try:
        result = execute_hardened(
            _CHILD,
            (),
            limits=measurement_limits(phase),
            environment=(("ORT_DISABLE_TELEMETRY", "1"),),
            extra_mounts=(Mount(str(runtime_dir), "/verified-runtime", True), *dependency_mounts),
        )
    except HardenedExecutionError as exc:
        _seal(
            root,
            plan,
            status="failed",
            symbol_boundary="violated",
            api_version=None,
            dependencies=[],
            exported=[],
            mapped=[],
            provider=False,
            closed=False,
            unexpected=False,
            broad=broad,
            network="not-performed",
            cleanup="failed",
            stop="precheck-failed",
        )
        raise MeasurementError("precheck-failed") from exc
    report = _report(result)
    mapped = report.get("mappedBasenames")
    names = mapped if isinstance(mapped, list) else []
    dependencies = _observed(names)
    provider = bool(report.get("providerLoaded")) or any("providers" in str(name) for name in names)
    unexpected = bool(report.get("unexpectedPath"))
    closed = bool(report.get("libraryClosed"))
    boundary = report.get("symbolBoundary")
    version = report.get("apiVersion") if isinstance(report.get("apiVersion"), str) else None
    network = _network_result(report)
    cleanup = "reaped" if result.cleanup == "reaped" else "failed"
    held = (
        result.return_code == 0
        and boundary == "held"
        and report.get("createSessionCalled") is False
        and report.get("getApiCalled") is False
        and report.get("runInvoked") is False
        and report.get("modelSessionCreated") is False
        and provider is False
        and unexpected is False
        and broad is False
        and closed is True
        and network == "denied"
        and cleanup == "reaped"
        and _closure_matches(names)
        and isinstance(version, str)
        and "1.31.1" in version
    )
    status = "passed" if held else "failed"
    stop = None if held else "precheck-failed"
    sealed = _seal(
        root,
        plan,
        status=status,
        symbol_boundary="held" if held else "violated",
        api_version=version,
        dependencies=dependencies,
        exported=_strings(report.get("exportedSymbols")),
        mapped=[str(item) for item in names if isinstance(item, str)],
        provider=provider,
        closed=closed,
        unexpected=unexpected,
        broad=broad,
        network=network,
        cleanup=cleanup,
        stop=stop,
    )
    if not held:
        raise MeasurementError("precheck-failed")
    return sealed


def _seal(
    root: Path,
    plan: dict[str, Any],
    **fields: Any,
) -> dict[str, Any]:
    sealed = digest_document(
        _body(plan, timestamp=utc_timestamp(), **fields),
        "dynamic-link-precheck",
        "identityDigest",
    )
    reject_sensitive(sealed)
    write_new(root, PHASE_FILES["dynamic-link-precheck"], sealed)
    return sealed


def _body(
    plan: dict[str, Any],
    *,
    status: str,
    symbol_boundary: str,
    api_version: str | None,
    dependencies: list[dict[str, str]],
    exported: list[str],
    mapped: list[str],
    provider: bool,
    closed: bool,
    unexpected: bool,
    broad: bool,
    network: str,
    cleanup: str,
    timestamp: str,
    stop: str | None,
) -> dict[str, Any]:
    flags = frozen_flags()
    flags.pop("dynamicLinkPrecheckDigest", None)
    return {
        **flags,
        "apiVersion": api_version,
        "broadHostLibraryMounted": broad,
        "createSessionCalled": False,
        "dependencies": dependencies,
        "exportedSymbols": exported,
        "getApiCalled": False,
        "libraryClosed": closed,
        "mappedBasenames": mapped,
        "networkResult": network,
        "planDigest": plan["planDigest"],
        "processCleanup": cleanup,
        "profileId": plan["profileId"],
        "providerLoaded": provider,
        "status": status,
        "stopCause": stop,
        "symbolBoundary": symbol_boundary,
        "timestamp": timestamp,
        "unexpectedPath": unexpected,
    }


def _individual(mounts: tuple[Mount, ...]) -> bool:
    for mount in mounts:
        destination = mount.destination.rstrip("/")
        source = Path(mount.source)
        if destination in _BROAD or not mount.read_only or source.is_dir() or not source.is_file():
            return False
    return True


def _observed(names: list[object]) -> list[dict[str, str]]:
    present = {str(item) for item in names}
    return [row for row in approved_public_closure() if row["basename"] in present]


def _closure_matches(names: list[object]) -> bool:
    present = {str(item) for item in names}
    required = {row["basename"] for row in approved_public_closure()}
    required.add(LIBRARY_NAME)
    if INTERPRETER_NAME not in present:
        return False
    return required.issubset(present)


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _report(result: ExecutionResult) -> dict[str, Any]:
    if not result.report:
        return {}
    try:
        loaded = json.loads(result.report.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _network_result(report: dict[str, Any]) -> str:
    network = report.get("network")
    if not isinstance(network, dict):
        return "failed"
    if network.get("ipv4") == "reached" or network.get("dns") == "reached":
        return "failed"
    return "denied"
