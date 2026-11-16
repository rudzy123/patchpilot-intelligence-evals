"""Closed Track 8A acquisition plan and source allowlist.

The plan is derived from the committed finalist and runtime records. It does
not transfer bytes. Operator approval is the plan digest, supplied later on
the command line.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any
from urllib.parse import SplitResult, urlsplit

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP, MEMORY_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
)
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.filesystem_identity import device_equal
from patchpilot_intelligence_evals.finalist_budget import (
    PROFILE_ID,
    PROFILE_VERSION,
    RUNTIME_LISTED_BYTES,
    RUNTIME_LISTED_SHA256,
    RUNTIME_PACKAGE,
    RUNTIME_REVISION,
    RUNTIME_TAG,
)
from patchpilot_intelligence_evals.finalist_onnx import SELECTED_FILES
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.storage_budget import verification_overhead_bytes

_PLAN = Path("candidates/authorization/acquisition-plan.json")
_ALLOWLIST = Path("candidates/authorization/acquisition-allowlist.json")
_RUNTIME_POLICY = Path("candidates/authorization/external-runtime-cache-policy.json")
_ONNX_RECORD = Path("candidates/authorization/finalist-direct-onnx.json")
_BUDGET = Path("candidates/authorization/finalist-artifact-budget.json")
_SELECTED_BYTES = 4_717_588_977
_UNPACK_ALLOWANCE = 268_435_456
_CANDIDATE_FILESYSTEM_MINIMUM = 6_442_450_944
_LOGICAL_CEILING = 8_589_934_592
_DELIVERY_SCOPE = "track8a-acquisition-plan"
_LIBRARY = "libonnxruntime.so.1.31.1"
_ONNX_REPO = "LiquidAI/LFM2.5-1.2B-Instruct-ONNX"
_NOTICE = "ThirdPartyNotices.txt"
_CONNECT_TIMEOUT = 30
_STALL_TIMEOUT = 120
_RUNTIME_TRANSFER_TIMEOUT = 600
_CANDIDATE_TRANSFER_TIMEOUT = 2700
_RETRY_LIMIT = 2
_MAX_REDIRECTS = 2
_HOSTS = ("github.com", "huggingface.co")
_PROHIBITED_REDIRECT_HOSTS = (
    "cas-bridge.xethub.hf.co",
    "cdn-lfs.huggingface.co",
    "objects.githubusercontent.com",
)
_DELIVERY_HOSTS: tuple[dict[str, Any], ...] = (
    {
        "artifacts": ["onnxruntime-linux-x64-1.31.1.tgz"],
        "host": "release-assets.githubusercontent.com",
        "scope": _DELIVERY_SCOPE,
    },
    {
        "artifacts": [
            "onnx/model.onnx",
            "onnx/model.onnx_data",
            "onnx/model.onnx_data_1",
            "onnx/model.onnx_data_2",
        ],
        "host": "us.aws.cdn.hf.co",
        "scope": _DELIVERY_SCOPE,
    },
)
_OBSERVED_REDIRECTS: tuple[tuple[str, tuple[tuple[str, int], ...], str], ...] = (
    (
        "onnxruntime-linux-x64-1.31.1.tgz",
        (("github.com", 302), ("release-assets.githubusercontent.com", 200)),
        "release-assets.githubusercontent.com",
    ),
    (
        "onnx/model.onnx",
        (("huggingface.co", 302), ("us.aws.cdn.hf.co", 200)),
        "us.aws.cdn.hf.co",
    ),
    (
        "onnx/model.onnx_data",
        (("huggingface.co", 302), ("us.aws.cdn.hf.co", 200)),
        "us.aws.cdn.hf.co",
    ),
    (
        "onnx/model.onnx_data_1",
        (("huggingface.co", 302), ("us.aws.cdn.hf.co", 200)),
        "us.aws.cdn.hf.co",
    ),
    (
        "onnx/model.onnx_data_2",
        (("huggingface.co", 302), ("us.aws.cdn.hf.co", 200)),
        "us.aws.cdn.hf.co",
    ),
    (
        "tokenizer.json",
        (("huggingface.co", 307), ("huggingface.co", 200)),
        "huggingface.co",
    ),
    (
        "config.json",
        (("huggingface.co", 307), ("huggingface.co", 200)),
        "huggingface.co",
    ),
    (
        "generation_config.json",
        (("huggingface.co", 307), ("huggingface.co", 200)),
        "huggingface.co",
    ),
    (
        "tokenizer_config.json",
        (("huggingface.co", 307), ("huggingface.co", 200)),
        "huggingface.co",
    ),
    (
        "chat_template.jinja",
        (("huggingface.co", 307), ("huggingface.co", 200)),
        "huggingface.co",
    ),
    (
        "LICENSE",
        (("huggingface.co", 307), ("huggingface.co", 200)),
        "huggingface.co",
    ),
    (
        "README.md",
        (("huggingface.co", 307), ("huggingface.co", 200)),
        "huggingface.co",
    ),
)
_ROOT_CLASSES = (
    "model-quarantine",
    "model-verified",
    "runtime-quarantine",
    "runtime-verified",
)
_SECRET_MARKERS = ("AKIA", "PRIVATE KEY", "ghp_", "hf_")


class PlanError(ValueError):
    """The acquisition plan failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def runtime_transfer_url() -> str:
    """Return the single official runtime archive URL."""
    return (
        "https://github.com/microsoft/onnxruntime/releases/download/"
        f"{RUNTIME_TAG}/{RUNTIME_PACKAGE}"
    )


def runtime_release_page_url() -> str:
    """Return the official release page. It is not a transfer URL."""
    return f"https://github.com/microsoft/onnxruntime/releases/tag/{RUNTIME_TAG}"


def candidate_transfer_url(relative_path: str) -> str:
    """Return one official resolve URL for a selected relative path."""
    return f"https://huggingface.co/{_ONNX_REPO}/resolve/{LFM_ONNX_REVISION}/{relative_path}"


def reject_sensitive(document: object) -> None:
    """Reject home paths, addresses, and credential markers."""
    text = json.dumps(document)
    if not isinstance(document, dict):
        raise PlanError("identity")
    if contains_private_marker(document) or "/Users/" in text:
        raise PlanError("identity")
    if any(marker in text for marker in _SECRET_MARKERS):
        raise PlanError("identity")


def chosen_files() -> tuple[Any, ...]:
    """Return the eleven selected files. Reduced-precision rows stay out."""
    return tuple(
        item
        for item in SELECTED_FILES
        if item.selected and not item.quantized and not item.reduced_precision
    )


def free_space_minimum_bytes() -> int:
    """Bytes required on the destination filesystem before a transfer."""
    overhead = verification_overhead_bytes(len(chosen_files()))
    return _SELECTED_BYTES + RUNTIME_LISTED_BYTES + overhead + _UNPACK_ALLOWANCE


def build_acquisition_plan() -> dict[str, Any]:
    """Build the preflight plan from committed authority."""
    _require_authorities()
    files = [
        {
            "expectedBytes": item.listed_byte_count,
            "localDigestRequired": item.published_sha256 is None,
            "path": item.path,
            "quantized": False,
            "reducedPrecision": False,
            "role": item.role,
            "upstreamSha256": item.published_sha256,
        }
        for item in chosen_files()
    ]
    document: dict[str, Any] = {
        "acquisitionStatus": "not-acquired",
        "artifactBytesSaved": 0,
        "calibrationStatus": "not-approved",
        "candidateFiles": files,
        "candidateFilesystemMinimumBytes": _CANDIDATE_FILESYSTEM_MINIMUM,
        "candidateLicenseName": "LFM Open License v1.0",
        "candidateNoticeFileName": None,
        "connectTimeoutSeconds": _CONNECT_TIMEOUT,
        "conversionStatus": "not-performed",
        "copyFallback": False,
        "executionStatus": "not-executed",
        "freeSpaceMinimumBytes": free_space_minimum_bytes(),
        "installationAuthorized": False,
        "logicalArtifactCeilingBytes": _LOGICAL_CEILING,
        "maxRedirects": _MAX_REDIRECTS,
        "measurementPerformed": False,
        "modelId": LFM_MODEL_ID,
        "networkPhase": "preflight",
        "onnxRepository": _ONNX_REPO,
        "onnxRevision": LFM_ONNX_REVISION,
        "operatorApproval": "required",
        "processMemoryCeilingBytes": MEMORY_CAP,
        "productionReady": False,
        "profileId": PROFILE_ID,
        "profileVersion": PROFILE_VERSION,
        "promotion": "rename-noreplace",
        "quantizationApproved": False,
        "realModelExecuted": False,
        "redirectDiscovery": "metadata-only",
        "retryConditions": ["connection-reset", "timeout"],
        "retryLimit": _RETRY_LIMIT,
        "rootClasses": list(_ROOT_CLASSES),
        "runtimeId": "onnxruntime",
        "runtimeInstallationStatus": "not-installed",
        "runtimeLicenseName": "MIT",
        "runtimeNoticeFileName": _NOTICE,
        "runtimePackageBytes": RUNTIME_LISTED_BYTES,
        "runtimePackageFileName": RUNTIME_PACKAGE,
        "runtimePackagePublishedSha256": RUNTIME_LISTED_SHA256,
        "runtimeReleasePageUrl": runtime_release_page_url(),
        "runtimeRevision": RUNTIME_REVISION,
        "runtimeSharedLibrary": _LIBRARY,
        "runtimeTransferTimeoutSeconds": _RUNTIME_TRANSFER_TIMEOUT,
        "runtimeTransferUrl": runtime_transfer_url(),
        "runtimeVersionTag": RUNTIME_TAG,
        "schemaVersion": "1.0.0",
        "selectedInventoryBytes": _SELECTED_BYTES,
        "selectionOutcome": "no-selection",
        "sourceRevision": LFM_SOURCE_REVISION,
        "stallTimeoutSeconds": _STALL_TIMEOUT,
        "candidateTransferTimeoutSeconds": _CANDIDATE_TRANSFER_TIMEOUT,
        "unpackAllowanceBytes": _UNPACK_ALLOWANCE,
        "verificationOverheadBytes": verification_overhead_bytes(len(chosen_files())),
    }
    document["planDigest"] = sha256_text(canonical_dumps(document))
    reject_sensitive(document)
    validate("acquisition-plan", document)
    return document


def build_acquisition_allowlist(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build the host allowlist for the plan's exact transfer URLs."""
    source = plan if plan is not None else build_acquisition_plan()
    urls = [str(source["runtimeTransferUrl"])]
    urls.extend(candidate_transfer_url(str(item["path"])) for item in source["candidateFiles"])
    document: dict[str, Any] = {
        "acquisitionStatus": "not-acquired",
        "allowedHosts": list(_HOSTS),
        "allowedUrls": urls,
        "calibrationStatus": "not-approved",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "followRedirects": "plan-scoped-delivery-hosts",
        "installationAuthorized": False,
        "maxRedirects": _MAX_REDIRECTS,
        "measurementPerformed": False,
        "networkPhase": "preflight",
        "planScopedDeliveryHosts": [
            {
                "artifacts": list(item["artifacts"]),
                "host": item["host"],
                "scope": item["scope"],
            }
            for item in _DELIVERY_HOSTS
        ],
        "productionReady": False,
        "prohibitedRedirectHosts": list(_PROHIBITED_REDIRECT_HOSTS),
        "redirectObservations": _redirect_observations(source),
        "quantizationApproved": False,
        "realModelExecuted": False,
        "referenceUrls": [str(source["runtimeReleasePageUrl"])],
        "runtimeInstallationStatus": "not-installed",
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
    }
    document["allowlistDigest"] = sha256_text(canonical_dumps(document))
    reject_sensitive(document)
    _require_urls(document)
    validate("acquisition-allowlist", document)
    return document


def load_acquisition_plan(root: Path | None = None) -> dict[str, Any]:
    """Load the committed plan and require it to match the builder."""
    loaded = _read_json(_PLAN, root)
    validate("acquisition-plan", loaded)
    if loaded != build_acquisition_plan():
        raise PlanError("record-drift")
    return loaded


def load_acquisition_allowlist(root: Path | None = None) -> dict[str, Any]:
    """Load the committed allowlist and require it to match the builder."""
    loaded = _read_json(_ALLOWLIST, root)
    validate("acquisition-allowlist", loaded)
    if loaded != build_acquisition_allowlist():
        raise PlanError("record-drift")
    return loaded


def require_operator_approval(supplied: str, plan: dict[str, Any] | None = None) -> None:
    """Accept only the digest of the committed plan."""
    document = plan if plan is not None else load_acquisition_plan()
    if supplied != document["planDigest"]:
        raise PlanError("approval-required")


def host_allowed(url: str, allowlist: dict[str, Any]) -> bool:
    """Return whether a URL's host is on the allowlist and the URL is exact."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme != "https" or parts.username or parts.password:
        return False
    if parts.port not in (None, 443):
        return False
    host = parts.hostname
    if host not in allowlist["allowedHosts"]:
        return False
    if host in allowlist["prohibitedRedirectHosts"]:
        return False
    return url in allowlist["allowedUrls"] or url in allowlist["referenceUrls"]


def transfer_allowed(url: str, allowlist: dict[str, Any]) -> bool:
    """Return whether a URL may be fetched. Reference pages are not transfers."""
    return url in allowlist["allowedUrls"] and host_allowed(url, allowlist)


def redirect_allowed(start_url: str, next_url: str, allowlist: dict[str, Any]) -> bool:
    """Accept one HTTPS redirect that preserves the artifact and the plan scope."""
    artifact = _artifact_name(start_url)
    nxt = _https_parts(next_url)
    if artifact is None or nxt is None:
        return False
    host = nxt.hostname
    if host is None or host in allowlist["prohibitedRedirectHosts"]:
        return False
    if _names_other_artifact(nxt.path, artifact):
        return False
    if host in _HOSTS:
        return _origin_identity(artifact, host, nxt.path)
    return _scoped_delivery(artifact, host, allowlist)


def validate_external_root(root: Path, *, repository: Path | None = None) -> Path:
    """Accept an absolute external cache root."""
    from patchpilot_intelligence_evals.artifact_cache import CacheError, validate_cache_root

    try:
        resolved = validate_cache_root(root, repository=repository)
    except CacheError as exc:
        raise PlanError(exc.code) from exc
    text = resolved.as_posix()
    if (
        text == "/home"
        or text.startswith("/home/")
        or "/Users/" in text
        or text.startswith("/Users")
    ):
        raise PlanError("home-root")
    parts = set(resolved.parts)
    if ".venv" in parts or "build" in parts or "dist" in parts:
        raise PlanError("workspace-root")
    if "actions-runner" in parts or "workspace" in parts and "github" in parts:
        raise PlanError("ci-workspace")
    return resolved


def available_bytes(root: Path) -> int:
    """Return free bytes on the filesystem that holds ``root``."""
    info = os.statvfs(root)
    return int(info.f_bavail) * int(info.f_frsize)


def preflight_report(
    runtime_root: Path | None = None,
    model_root: Path | None = None,
) -> dict[str, Any]:
    """Describe the plan without transferring and without recording host paths."""
    plan = load_acquisition_plan()
    allowlist = load_acquisition_allowlist()
    report: dict[str, Any] = {
        "allowlistDigest": allowlist["allowlistDigest"],
        "availableBytes": None,
        "candidateAvailableBytes": None,
        "candidateFileCount": len(plan["candidateFiles"]),
        "candidateFilesystemMinimumBytes": plan["candidateFilesystemMinimumBytes"],
        "commandTemplates": command_templates(str(plan["planDigest"])),
        "copyFallback": False,
        "freeSpaceMinimumBytes": plan["freeSpaceMinimumBytes"],
        "freeSpaceSufficient": None,
        "logicalArtifactCeilingBytes": plan["logicalArtifactCeilingBytes"],
        "modelDevice": None,
        "networkPhase": "preflight",
        "noCopyFallback": "pass",
        "ownershipSuitable": None,
        "permissionSuitable": None,
        "planDigest": plan["planDigest"],
        "prohibitedRoot": None,
        "requiredBytes": plan["candidateFilesystemMinimumBytes"],
        "rootClasses": list(plan["rootClasses"]),
        "rootsSupplied": runtime_root is not None and model_root is not None,
        "runtimeAvailableBytes": None,
        "runtimeDevice": None,
        "runtimeSharedLibrary": plan["runtimeSharedLibrary"],
        "sameFilesystem": None,
        "selectedInventoryBytes": plan["selectedInventoryBytes"],
        "status": "ok",
        "symlinkResult": None,
        "transfer": "not-started",
    }
    if runtime_root is None and model_root is None:
        return report
    if runtime_root is None or model_root is None:
        raise PlanError("missing-root")
    if runtime_root.is_symlink() or model_root.is_symlink():
        raise PlanError("symlink-escape")
    runtime = validate_external_root(runtime_root)
    model = validate_external_root(model_root)
    if runtime == model:
        raise PlanError("root-collision")
    if runtime in model.parents or model in runtime.parents:
        raise PlanError("root-collision")
    runtime_free = available_bytes(runtime)
    model_free = available_bytes(model)
    report["runtimeAvailableBytes"] = runtime_free
    report["candidateAvailableBytes"] = model_free
    report["availableBytes"] = min(runtime_free, model_free)
    report["freeSpaceSufficient"] = model_free >= int(
        plan["candidateFilesystemMinimumBytes"]
    ) and min(runtime_free, model_free) >= int(plan["freeSpaceMinimumBytes"])
    report["sameFilesystem"] = device_equal(runtime, model)
    report["runtimeDevice"] = os.lstat(runtime).st_dev
    report["modelDevice"] = os.lstat(model).st_dev
    report["prohibitedRoot"] = "pass"
    report["symlinkResult"] = "absent"
    report["permissionSuitable"] = _permission_suitable(runtime) and _permission_suitable(model)
    report["ownershipSuitable"] = _ownership_suitable(runtime) and _ownership_suitable(model)
    return report


def command_templates(plan_digest: str) -> list[str]:
    """Return the operator commands with root placeholders, not host paths."""
    return [
        "uv run patchpilot-evals acquisition-preflight "
        "--runtime-cache <runtime-root> --model-cache <model-root>",
        "uv run patchpilot-evals acquire-runtime --runtime-cache <runtime-root> "
        f"--operator-approval {plan_digest}",
        "uv run patchpilot-evals acquire-candidate --runtime-cache <runtime-root> "
        "--model-cache <model-root> "
        f"--operator-approval {plan_digest}",
    ]


def _redirect_observations(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the metadata-only hops. Query strings and bodies are omitted."""
    expected = {str(plan["runtimePackageFileName"]): int(plan["runtimePackageBytes"])}
    expected.update(
        {str(item["path"]): int(item["expectedBytes"]) for item in plan["candidateFiles"]}
    )
    if [item[0] for item in _OBSERVED_REDIRECTS] != [
        str(plan["runtimePackageFileName"]),
        *[str(item["path"]) for item in plan["candidateFiles"]],
    ]:
        raise PlanError("identity-mismatch")
    rows: list[dict[str, Any]] = []
    for artifact, hops, final_host in _OBSERVED_REDIRECTS:
        if artifact not in expected or len(hops) < 2 or len(hops) > 3:
            raise PlanError("identity-mismatch")
        if hops[-1] != (final_host, 200):
            raise PlanError("identity-mismatch")
        if sum(status in {301, 302, 303, 307, 308} for _host, status in hops) > _MAX_REDIRECTS:
            raise PlanError("unauthorized-redirect")
        rows.append(
            {
                "artifact": artifact,
                "bodyBytesSaved": 0,
                "finalHost": final_host,
                "hops": [{"host": host, "status": status} for host, status in hops],
                "identityPreserved": True,
                "observedBytes": expected[artifact],
            }
        )
    return rows


def _https_parts(url: str) -> SplitResult | None:
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if parts.scheme != "https" or parts.username or parts.password or parts.fragment:
        return None
    if parts.port not in (None, 443) or parts.hostname is None:
        return None
    return parts


def _artifact_name(url: str) -> str | None:
    parts = _https_parts(url)
    if parts is None or parts.query:
        return None
    if parts.hostname == "github.com" and parts.path.endswith(f"/{RUNTIME_TAG}/{RUNTIME_PACKAGE}"):
        return RUNTIME_PACKAGE
    prefix = f"/{_ONNX_REPO}/resolve/{LFM_ONNX_REVISION}/"
    if parts.hostname != "huggingface.co" or not parts.path.startswith(prefix):
        return None
    relative = parts.path[len(prefix) :]
    if relative in {item.path for item in chosen_files()}:
        return relative
    return None


def _origin_identity(artifact: str, host: str, path: str) -> bool:
    if artifact == RUNTIME_PACKAGE:
        return host == "github.com" and path.endswith(f"/{RUNTIME_TAG}/{RUNTIME_PACKAGE}")
    if host != "huggingface.co":
        return False
    resolve = f"/{_ONNX_REPO}/resolve/{LFM_ONNX_REVISION}/{artifact}"
    cached = f"/models/{_ONNX_REPO}/{LFM_ONNX_REVISION}/{artifact}"
    return path.endswith(resolve) or path.endswith(cached)


def _names_other_artifact(path: str, artifact: str) -> bool:
    names = [RUNTIME_PACKAGE, *[item.path for item in chosen_files()]]
    for other in names:
        if other == artifact:
            continue
        if path.endswith(f"/{other}") or f"/{other}/" in path:
            return True
    return False


def _scoped_delivery(artifact: str, host: str, allowlist: dict[str, Any]) -> bool:
    matches = [
        row
        for row in allowlist["planScopedDeliveryHosts"]
        if row["host"] == host and artifact in row["artifacts"]
    ]
    if len(matches) != 1:
        return False
    return str(matches[0]["scope"]) == _DELIVERY_SCOPE


def _permission_suitable(root: Path) -> bool:
    info = root.lstat()
    mode = stat.S_IMODE(info.st_mode)
    private = mode & 0o022 == 0 and mode & 0o700 == 0o700
    return private and os.access(root, os.W_OK | os.X_OK) and not root.is_symlink()


def _ownership_suitable(root: Path) -> bool:
    return root.lstat().st_uid == os.geteuid() and not root.is_symlink()


def _require_authorities() -> None:
    chosen = chosen_files()
    if len(chosen) != 11:
        raise PlanError("identity-mismatch")
    total = sum(item.listed_byte_count for item in chosen)
    if total != _SELECTED_BYTES:
        raise PlanError("identity-mismatch")
    base = repo_root()
    policy = _read_json(_RUNTIME_POLICY, base)
    onnx = _read_json(_ONNX_RECORD, base)
    budget = _read_json(_BUDGET, base)
    if policy.get("approvedSharedLibraries") != [_LIBRARY]:
        raise PlanError("identity-mismatch")
    if policy.get("immutableRevision") != RUNTIME_REVISION:
        raise PlanError("identity-mismatch")
    if policy.get("packageFileName") != RUNTIME_PACKAGE:
        raise PlanError("identity-mismatch")
    if policy.get("versionTag") != RUNTIME_TAG or policy.get("licenseName") != "MIT":
        raise PlanError("identity-mismatch")
    if budget.get("runtimePackagePublishedSha256") != RUNTIME_LISTED_SHA256:
        raise PlanError("identity-mismatch")
    if budget.get("runtimeStagingListedBytes") != RUNTIME_LISTED_BYTES:
        raise PlanError("identity-mismatch")
    if budget.get("runtimeRevision") != RUNTIME_REVISION:
        raise PlanError("identity-mismatch")
    finalists = onnx.get("finalists")
    if not isinstance(finalists, list) or not finalists:
        raise PlanError("identity-mismatch")
    finalist = finalists[0]
    if not isinstance(finalist, dict):
        raise PlanError("identity-mismatch")
    if finalist.get("sourceRevision") != LFM_SOURCE_REVISION:
        raise PlanError("identity-mismatch")
    if finalist.get("onnxRevision") != LFM_ONNX_REVISION:
        raise PlanError("identity-mismatch")
    if finalist.get("onnxRepository") != _ONNX_REPO:
        raise PlanError("identity-mismatch")
    if finalist.get("licenseName") != "LFM Open License v1.0":
        raise PlanError("identity-mismatch")
    rows = finalist.get("files")
    if not isinstance(rows, list):
        raise PlanError("identity-mismatch")
    selected = [item for item in rows if isinstance(item, dict) and item.get("selected") is True]
    if len(selected) != len(chosen):
        raise PlanError("identity-mismatch")
    for row, item in zip(selected, chosen, strict=True):
        if row.get("path") != item.path or row.get("listedByteCount") != item.listed_byte_count:
            raise PlanError("identity-mismatch")
        if row.get("publishedSha256") != item.published_sha256:
            raise PlanError("identity-mismatch")
        if row.get("quantized") is not False or row.get("reducedPrecision") is not False:
            raise PlanError("identity-mismatch")
    overhead = verification_overhead_bytes(11)
    if overhead != 1_228_800:
        raise PlanError("identity-mismatch")
    if free_space_minimum_bytes() != 4_998_666_888:
        raise PlanError("identity-mismatch")
    if _CANDIDATE_FILESYSTEM_MINIMUM != 6_442_450_944:
        raise PlanError("identity-mismatch")
    if ARTIFACT_CAP != _LOGICAL_CEILING or _LOGICAL_CEILING != 8_589_934_592:
        raise PlanError("identity-mismatch")


def _require_urls(document: dict[str, Any]) -> None:
    for url in [*document["allowedUrls"], *document["referenceUrls"]]:
        if not isinstance(url, str):
            raise PlanError("unauthorized-source")
        parts = urlsplit(url)
        if parts.scheme != "https" or parts.hostname not in _HOSTS:
            raise PlanError("unauthorized-source")
        if parts.username or parts.password or parts.port not in (None, 443):
            raise PlanError("unauthorized-source")
        if any(host in url for host in _PROHIBITED_REDIRECT_HOSTS):
            raise PlanError("unauthorized-redirect")


def _read_json(relative: Path, root: Path | None) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise PlanError("record-type")
    return loaded
