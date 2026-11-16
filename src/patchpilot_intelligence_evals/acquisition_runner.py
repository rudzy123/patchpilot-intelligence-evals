"""Transfer coordinator. Quarantine bytes are never executed."""

from __future__ import annotations

import hashlib
import http.client
import os
import shutil
import subprocess
import tarfile
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

from patchpilot_intelligence_evals.acquired_artifact_validation import (
    ArtifactValidationError,
    close_and_promote,
    reject_attempt,
)
from patchpilot_intelligence_evals.acquisition_plan import (
    PlanError,
    load_acquisition_allowlist,
    load_acquisition_plan,
    redirect_allowed,
    require_operator_approval,
    transfer_allowed,
    validate_external_root,
)
from patchpilot_intelligence_evals.cache_cleanup import CleanupError, cleanup_attempt
from patchpilot_intelligence_evals.candidate_staging import (
    CandidateStagingError,
    compare_selected_file,
    require_license_text,
)
from patchpilot_intelligence_evals.runtime_artifact_verification import (
    RuntimeVerificationError,
    inspect_runtime,
)
from patchpilot_intelligence_evals.runtime_staging import (
    RuntimeStagingError,
    logging_level_error,
    member_disposition,
    ort_api_indices,
    ort_api_version,
    require_library,
    require_license,
    require_notice,
    runtime_identity_bytes,
)
from patchpilot_intelligence_evals.verification_seal import SealError, check_attempt_id

_CONNECT_TIMEOUT = 30
_STALL_TIMEOUT = 120
_MAX_REDIRECTS = 2
_CHUNK = 65_536
_RETRYABLE = frozenset({"connection-reset", "timeout"})
Exchange = Callable[[str, str], tuple[int, Mapping[str, str], Any]]
Hasher = Callable[[Path, list[str]], dict[str, str]]


class TransferError(ValueError):
    """A transfer stopped. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _namespace_prefix(bwrap: str) -> list[str]:
    """Bubblewrap prefix with network denied and the dynamic linker visible."""
    prefix = [bwrap, "--unshare-net", "--die-with-parent", "--ro-bind", "/usr", "/usr"]
    linker = Path("/lib64")
    if linker.is_symlink() and os.readlink(linker) in {"usr/lib64", "/usr/lib64"}:
        prefix.extend(["--symlink", "usr/lib64", "/lib64"])
    elif linker.is_dir():
        prefix.extend(["--ro-bind", "/lib64", "/lib64"])
    return prefix


def assert_network_disabled() -> None:
    """Require bubblewrap to create a network namespace before hashing."""
    bwrap = shutil.which("bwrap")
    binary = shutil.which("sha256sum")
    if bwrap is None or binary is None:
        raise TransferError("network-not-disabled")
    true_path = "/usr/bin/true" if Path("/usr/bin/true").is_file() else "/bin/true"
    completed = subprocess.run(
        [*_namespace_prefix(bwrap), "--", true_path],
        check=False,
        shell=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise TransferError("network-not-disabled")


def hash_with_network_namespace(directory: Path, names: list[str]) -> dict[str, str]:
    """Hash named files inside a bubblewrap network namespace."""
    bwrap = shutil.which("bwrap")
    if bwrap is None or shutil.which("sha256sum") is None:
        raise TransferError("network-not-disabled")
    for name in names:
        if name.startswith("-") or ".." in name.split("/") or name.startswith("/"):
            raise TransferError("unexpected-file")
    arguments = [
        *_namespace_prefix(bwrap),
        "--ro-bind",
        str(directory),
        "/inventory",
        "--",
        "/usr/bin/sha256sum",
        "--",
        *[f"/inventory/{name}" for name in names],
    ]
    if any(Path(item).name in {"sh", "bash", "dash"} for item in arguments):
        raise TransferError("shell")
    completed = subprocess.run(
        arguments,
        check=False,
        shell=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise TransferError("digest-mismatch")
    return _parse_sha256sum(completed.stdout, names)


def https_exchange(host: str, path: str) -> tuple[int, Mapping[str, str], http.client.HTTPResponse]:
    """Fetch one HTTPS response. The caller decides whether the body is kept."""
    connection = http.client.HTTPSConnection(host, timeout=_CONNECT_TIMEOUT)
    try:
        connection.request(
            "GET",
            path,
            headers={"User-Agent": "patchpilot-intelligence-evals/track8a"},
        )
        if connection.sock is not None:
            connection.sock.settimeout(_STALL_TIMEOUT)
        response = connection.getresponse()
    except TimeoutError as exc:
        connection.close()
        raise TransferError("timeout") from exc
    except ConnectionError as exc:
        connection.close()
        raise TransferError("connection-reset") from exc
    except OSError as exc:
        connection.close()
        raise TransferError("transfer-failed") from exc
    headers = {key.lower(): value for key, value in response.getheaders()}
    return response.status, headers, response


def transfer_file(
    url: str,
    destination: Path,
    *,
    expected_bytes: int,
    allowlist: dict[str, Any],
    overall_seconds: int,
    exchange: Exchange | None = None,
) -> str:
    """Stream one allowlisted URL into a new file and return its SHA-256."""
    if not transfer_allowed(url, allowlist):
        raise TransferError("unauthorized-source")
    opener = exchange if exchange is not None else https_exchange
    current = url
    deadline = time.monotonic() + overall_seconds
    for _hop in range(_MAX_REDIRECTS + 1):
        if time.monotonic() > deadline:
            raise TransferError("timeout")
        parts = urlsplit(current)
        host = parts.hostname or ""
        path = parts.path or "/"
        if parts.query:
            path = f"{path}?{parts.query}"
        status, headers, body = opener(host, path)
        if status in {301, 302, 303, 307, 308}:
            _discard(body)
            location = headers.get("location")
            if not location:
                raise TransferError("unauthorized-redirect")
            nxt = urljoin(current, location)
            if not redirect_allowed(url, nxt, allowlist):
                raise TransferError("unauthorized-redirect")
            current = nxt
            continue
        if status != 200:
            _discard(body)
            raise TransferError("http-status")
        length = headers.get("content-length")
        if length is not None and length != str(expected_bytes):
            _discard(body)
            raise TransferError("size-mismatch")
        return _write_body(body, destination, expected_bytes, deadline)
    raise TransferError("unauthorized-redirect")


def acquire_runtime(
    runtime_root: Path,
    approval: str,
    *,
    repository: Path | None = None,
    exchange: Exchange | None = None,
    network_barrier: Callable[[], None] | None = None,
    hasher: Hasher | None = None,
) -> dict[str, Any]:
    """Download the runtime archive into a new quarantine attempt."""
    plan = load_acquisition_plan()
    allowlist = load_acquisition_allowlist()
    try:
        require_operator_approval(approval, plan)
    except PlanError as exc:
        raise TransferError(exc.code) from exc
    root = validate_external_root(runtime_root, repository=repository)
    attempt_id = _attempt_id("rt")
    directory = _create_attempt(root, attempt_id)
    destination = directory / str(plan["runtimePackageFileName"])
    try:
        digest = transfer_file(
            str(plan["runtimeTransferUrl"]),
            destination,
            expected_bytes=int(plan["runtimePackageBytes"]),
            allowlist=allowlist,
            overall_seconds=int(plan["runtimeTransferTimeoutSeconds"]),
            exchange=exchange,
        )
        (network_barrier or assert_network_disabled)()
        observed = (hasher or hash_with_network_namespace)(
            directory,
            [str(plan["runtimePackageFileName"])],
        )
    except TransferError as exc:
        _fail_attempt(root, attempt_id, exc.code)
        raise
    if observed.get(str(plan["runtimePackageFileName"])) != digest:
        _fail_attempt(root, attempt_id, "digest-mismatch")
        raise TransferError("digest-mismatch")
    if digest != plan["runtimePackagePublishedSha256"]:
        _fail_attempt(root, attempt_id, "digest-mismatch")
        raise TransferError("digest-mismatch")
    return {
        "attemptId": attempt_id,
        "digest": digest,
        "executed": False,
        "status": "quarantined",
    }


def acquire_candidate(
    model_root: Path,
    runtime_root: Path,
    approval: str,
    *,
    repository: Path | None = None,
    exchange: Exchange | None = None,
    network_barrier: Callable[[], None] | None = None,
    hasher: Hasher | None = None,
) -> dict[str, Any]:
    """Download the eleven selected files after a verified runtime receipt exists."""
    plan = load_acquisition_plan()
    allowlist = load_acquisition_allowlist()
    try:
        require_operator_approval(approval, plan)
    except PlanError as exc:
        raise TransferError(exc.code) from exc
    runtime = validate_external_root(runtime_root, repository=repository)
    model = validate_external_root(model_root, repository=repository)
    if not any((runtime / "verified").glob("*.promotion-receipt.json")):
        raise TransferError("runtime-not-verified")
    attempt_id = _attempt_id("cd")
    directory = _create_attempt(model, attempt_id)
    try:
        for item in plan["candidateFiles"]:
            relative = str(item["path"])
            destination = directory.joinpath(*relative.split("/"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            transfer_file(
                _candidate_url(plan, relative),
                destination,
                expected_bytes=int(item["expectedBytes"]),
                allowlist=allowlist,
                overall_seconds=int(plan["candidateTransferTimeoutSeconds"]),
                exchange=exchange,
            )
        (network_barrier or assert_network_disabled)()
        names = [str(item["path"]) for item in plan["candidateFiles"]]
        observed = (hasher or hash_with_network_namespace)(directory, names)
        for item in plan["candidateFiles"]:
            relative = str(item["path"])
            file_path = directory.joinpath(*relative.split("/"))
            digest = observed[relative]
            compare_selected_file(relative, file_path.stat().st_size, digest)
            if relative == "LICENSE":
                require_license_text(file_path.read_bytes())
        sealed = close_and_promote(
            model, attempt_id, _seal_expected(directory), repository=repository
        )
    except (TransferError, CandidateStagingError, ArtifactValidationError) as exc:
        _fail_attempt(model, attempt_id, exc.code)
        if exc.code not in _RETRYABLE:
            reject_attempt(model, attempt_id, exc.code)
        raise TransferError(exc.code) from exc
    return {
        "attemptId": attempt_id,
        "executed": False,
        "receiptState": sealed["receipt"]["receiptState"],
        "status": "verified",
    }


def _candidate_url(plan: dict[str, Any], relative: str) -> str:
    prefix = f"https://huggingface.co/{plan['onnxRepository']}/resolve/{plan['onnxRevision']}/"
    return prefix + relative


def promote_runtime_archive(
    runtime_root: Path,
    archive_attempt_id: str,
    *,
    repository: Path | None = None,
    network_barrier: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Unpack a quarantined archive offline and promote the closed runtime set."""
    root = validate_external_root(runtime_root, repository=repository)
    plan = load_acquisition_plan()
    archive = root / "quarantine" / archive_attempt_id / str(plan["runtimePackageFileName"])
    if archive.is_symlink() or not archive.is_file():
        raise TransferError("missing-file")
    (network_barrier or assert_network_disabled)()
    promotion_id = _attempt_id("rp")
    members_id = _attempt_id("rm")
    promotion = _create_attempt(root, promotion_id)
    members = _create_attempt(root, members_id)
    try:
        inventory = _unpack_runtime(archive, promotion, members, int(plan["unpackAllowanceBytes"]))
        header_name = next(
            (
                item["fileName"]
                for item in inventory
                if item["fileName"].endswith("onnxruntime_c_api.h")
            ),
            None,
        )
        if header_name is None:
            raise TransferError("missing-file")
        header = (members / header_name).read_text(encoding="utf-8")
        version = ort_api_version(header)
        logging_level_error(header)
        ort_api_indices(header)
        identity = runtime_identity_bytes(version)
        identity_path = promotion / "runtime-identity.json"
        identity_path.write_bytes(identity)
        os.chmod(identity_path, 0o444)
        expected = _promotion_expected(promotion)
        inspected = inspect_runtime(promotion, expected, attempt_id=promotion_id)
        if inspected["verificationState"] != "verified":
            raise TransferError("unexpected-file")
        sealed = close_and_promote(
            root,
            promotion_id,
            _seal_expected(promotion),
            repository=repository,
        )
    except (
        TransferError,
        RuntimeStagingError,
        RuntimeVerificationError,
        ArtifactValidationError,
    ) as exc:
        reject_attempt(root, promotion_id, exc.code)
        raise TransferError(exc.code) from exc
    return {
        "archiveAttemptId": archive_attempt_id,
        "executed": False,
        "membersAttemptId": members_id,
        "promotionAttemptId": promotion_id,
        "receiptState": sealed["receipt"]["receiptState"],
        "status": "verified",
    }


def _unpack_runtime(
    archive: Path,
    promotion: Path,
    members: Path,
    allowance: int,
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    total = 0
    seen = {"library": 0, "license": 0, "notice": 0}
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            kind = (
                "symlink"
                if member.issym() or member.islnk()
                else "regular"
                if member.isfile()
                else "directory"
                if member.isdir()
                else "other"
            )
            disposition = member_disposition(member.name, kind)
            if disposition == "rejected":
                raise TransferError("unexpected-file")
            if kind != "regular":
                inventory.append(
                    {
                        "disposition": disposition,
                        "fileName": member.name,
                        "kind": "symlink" if kind == "symlink" else "other",
                        "logicalBytes": 0,
                        "sha256": None,
                    }
                )
                continue
            total += member.size
            if total > allowance or member.size < 0:
                raise TransferError("size-mismatch")
            payload = _read_member(tar, member)
            if disposition == "promotion-library":
                require_library(payload)
                _write_named(promotion / "libonnxruntime.so.1.31.1", payload)
                seen["library"] += 1
            elif disposition == "promotion-license":
                require_license(payload)
                _write_named(promotion / "LICENSE", payload)
                seen["license"] += 1
            elif disposition == "promotion-notice":
                require_notice(payload)
                _write_named(promotion / "ThirdPartyNotices.txt", payload)
                seen["notice"] += 1
            else:
                destination = members.joinpath(*member.name.split("/"))
                if destination.is_symlink() or ".." in destination.parts:
                    raise TransferError("unexpected-file")
                destination.parent.mkdir(parents=True, exist_ok=True)
                _write_named(destination, payload)
            inventory.append(
                {
                    "disposition": disposition,
                    "fileName": member.name,
                    "kind": "regular",
                    "logicalBytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
    if seen != {"library": 1, "license": 1, "notice": 1}:
        raise TransferError("missing-file")
    return inventory


def _read_member(tar: tarfile.TarFile, member: tarfile.TarInfo) -> bytes:
    extracted = tar.extractfile(member)
    if extracted is None:
        raise TransferError("missing-file")
    return extracted.read()


def _write_named(path: Path, payload: bytes) -> None:
    path.write_bytes(payload)
    os.chmod(path, 0o444)


def _promotion_expected(directory: Path) -> list[dict[str, Any]]:
    roles = {
        "libonnxruntime.so.1.31.1": ("shared-library", "elf"),
        "LICENSE": ("license", "not-executable"),
        "ThirdPartyNotices.txt": ("notice", "not-executable"),
        "runtime-identity.json": ("configuration", "not-executable"),
    }
    expected: list[dict[str, Any]] = []
    for name, (role, executable_format) in roles.items():
        payload = (directory / name).read_bytes()
        expected.append(
            {
                "executableFormat": executable_format,
                "expectedBytes": len(payload),
                "fileName": name,
                "role": role,
                "upstreamSha256": None,
            }
        )
    return expected


def _seal_expected(directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_dir():
            continue
        if path.is_symlink() or not path.is_file():
            raise TransferError("unexpected-file")
        size, digest = _stream_sha256(path)
        rows.append(
            {
                "logicalBytes": size,
                "relativeName": path.relative_to(directory).as_posix(),
                "sha256": digest,
            }
        )
    return rows


def _stream_sha256(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(_CHUNK)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def _write_body(body: Any, destination: Path, expected_bytes: int, deadline: float) -> str:
    digest = hashlib.sha256()
    written = 0
    complete = False
    descriptor = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o644)
    try:
        while written < expected_bytes:
            if time.monotonic() > deadline:
                raise TransferError("timeout")
            chunk = body.read(_CHUNK)
            if not isinstance(chunk, bytes):
                raise TransferError("transfer-failed")
            if chunk == b"":
                break
            if written + len(chunk) > expected_bytes:
                raise TransferError("size-mismatch")
            os.write(descriptor, chunk)
            digest.update(chunk)
            written += len(chunk)
        complete = written == expected_bytes
    finally:
        os.close(descriptor)
        if not complete and destination.exists():
            destination.unlink()
    if not complete:
        raise TransferError("size-mismatch")
    os.chmod(destination, 0o444)
    return digest.hexdigest()


def _discard(body: Any) -> None:
    try:
        leftover = body.read(65_536)
        if isinstance(leftover, bytes) and len(leftover) == 65_536:
            raise TransferError("unauthorized-redirect")
    except TransferError:
        raise
    except OSError as exc:
        raise TransferError("transfer-failed") from exc
    closer = getattr(body, "close", None)
    if closer is not None:
        closer()


def _parse_sha256sum(payload: bytes, names: list[str]) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in payload.decode("utf-8").splitlines():
        digest, _separator, raw_path = line.partition(" ")
        relative = raw_path.strip().removeprefix("/inventory/").lstrip()
        if relative.startswith("*"):
            relative = relative[1:]
        found[relative] = digest
    if set(found) != set(names):
        raise TransferError("digest-mismatch")
    return found


def _attempt_id(prefix: str) -> str:
    from secrets import token_hex

    attempt_id = f"{prefix}-{token_hex(8)}"
    try:
        check_attempt_id(attempt_id)
    except SealError as exc:
        raise TransferError(exc.code) from exc
    return attempt_id


def _create_attempt(root: Path, attempt_id: str) -> Path:
    directory = root / "quarantine" / attempt_id
    directory.mkdir(parents=True)
    return directory


def _fail_attempt(root: Path, attempt_id: str, code: str) -> None:
    if code not in _RETRYABLE:
        return
    try:
        cleanup_attempt(root, attempt_id, state="quarantine")
    except CleanupError as exc:
        raise TransferError(exc.code) from exc
