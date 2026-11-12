"""In-place verification seals for synthetic quarantine trees.

Streaming SHA-256 runs twice. Size, mtime, inode, device, file type, and link
count are compared around the reads. A matching first digest does not survive a
change in that window. The seal does not make the tree executable.
"""

from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import stat
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.filesystem_identity import (
    IdentityError,
    fsync_directory,
    fsync_file,
    rename_noreplace,
    write_new_file,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root, validate

APPROVED_SUFFIXES: tuple[str, ...] = (".onnx", ".json", ".jinja", ".md", ".txt", ".safetensors")
APPROVED_EXACT_NAMES: tuple[str, ...] = ("LICENSE", "README.md")
SEAL_FILENAME = "verification-seal.json"
JOURNAL_FILENAME = "promotion-journal.json"
SEAL_TEMPORARY = ".verification-seal.json.tmp"
JOURNAL_TEMPORARY = ".promotion-journal.json.tmp"
METADATA_FILENAMES = frozenset({SEAL_FILENAME, JOURNAL_FILENAME, SEAL_TEMPORARY, JOURNAL_TEMPORARY})
_ATTEMPT_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_ONNX_DATA = re.compile(r"^.+\.onnx_data(?:_[0-9]+)?$")
_DOMAIN_MAX = 2**63 - 1
_CHUNK = 65536
_PRIORITY = (
    "non-utf8-path",
    "absolute-path",
    "path-traversal",
    "duplicate-path",
    "case-collision",
    "unsupported-name",
    "symlink",
    "dangling-symlink",
    "fifo",
    "socket",
    "device-file",
    "special-file",
    "hard-link-uniqueness",
    "unexpected-file",
    "missing-file",
    "mutated-during-verification",
    "size-mismatch",
    "digest-mismatch",
    "unknown-size",
    "integer-overflow",
    "repository-root",
    "sibling-root",
)


class SealError(ValueError):
    """A quarantine tree failed sealing. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def document_digest(document: Mapping[str, Any]) -> str:
    """SHA-256 of the canonical document without its identity digest."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    return sha256_text(canonical_dumps(payload))


def inventory_identity(files: list[dict[str, Any]]) -> str:
    """SHA-256 of sorted relative name, logical size, and content digest."""
    rows = [
        {
            "logicalBytes": item["logicalBytes"],
            "relativeName": item["relativeName"],
            "sha256": item["sha256"],
        }
        for item in files
    ]
    ordered = sorted(rows, key=lambda item: str(item["relativeName"]))
    return sha256_text(canonical_dumps(ordered))


def classify_mode(mode: int, nlink: int) -> str | None:
    """Classify an lstat mode. A regular unique file returns None."""
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
        return "device-file"
    if stat.S_ISDIR(mode):
        return None
    if not stat.S_ISREG(mode):
        return "special-file"
    if nlink != 1:
        return "hard-link-uniqueness"
    return None


def classify_filesystem_entry(path: Path) -> str | None:
    """Classify one path from lstat. Dangling links are distinguished."""
    info = os.lstat(path)
    kind = classify_mode(info.st_mode, info.st_nlink)
    if kind == "symlink" and not path.exists():
        return "dangling-symlink"
    return kind


def check_relative_name(name: object) -> str:
    """Accept one normalized relative artifact name."""
    if not isinstance(name, str):
        raise SealError("path-traversal")
    try:
        name.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise SealError("non-utf8-path") from exc
    if "\\" in name or "\x00" in name or name.startswith("/"):
        code = "absolute-path" if name.startswith("/") else "path-traversal"
        raise SealError(code)
    if posixpath.normpath(name) != name:
        raise SealError("path-traversal")
    parts = name.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise SealError("path-traversal")
    if name in METADATA_FILENAMES or not _approved(name):
        raise SealError("unsupported-name")
    return name


def confinement_problems(directory: Path) -> set[str]:
    """Return hazard codes for a tree whose expected inventory is not known yet."""
    problems: set[str] = set()
    if directory.is_symlink():
        return {"symlink"}
    if not directory.is_dir():
        return {"missing-file"}
    for relative in _walk(directory, problems):
        path = directory.joinpath(*relative.split("/"))
        kind = classify_filesystem_entry(path)
        if kind is not None:
            problems.add(kind)
        try:
            check_relative_name(relative)
        except SealError as exc:
            problems.add(exc.code)
    return problems


def not_acquired_seal() -> dict[str, Any]:
    """Build the committed seal template. It records no artifact bytes."""
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        **_disabled(),
        "sealState": "not-acquired",
        "attemptId": None,
        "executionEligibility": "prohibited",
        "laterSessionEligibility": "none",
        "logicalInventoryBytes": 0,
        "allocatedInventoryBytes": None,
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "sameFilesystem": None,
        "syncSteps": [],
        "failureCategory": None,
        "inventoryIdentity": None,
        "files": [],
    }
    document["identityDigest"] = document_digest(document)
    return validate_seal(document)


def validate_seal(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one seal and its identity digest."""
    validate("artifact-verification-seal", document)
    if document["identityDigest"] != document_digest(document):
        raise SealError("invalid-seal")
    if document["locallyObservedArtifactDigests"] != []:
        raise SealError("local-digest")
    if document["executionEligibility"] != "prohibited":
        raise SealError("quarantine-execution")
    if document["executionStatus"] != "not-executed":
        raise SealError("execution-status")
    return document


def load_seal_template(root: Path | None = None) -> dict[str, Any]:
    """Load the committed seal template and require it to match the builder."""
    base = root if root is not None else repo_root()
    loaded = json.loads(
        (base / "candidates/templates/artifact-verification-seal-template.json").read_text(
            encoding="utf-8"
        )
    )
    if not isinstance(loaded, dict):
        raise SealError("record-type")
    document = validate_seal(loaded)
    if document != not_acquired_seal():
        raise SealError("record-drift")
    return document


def load_seal(directory: Path) -> dict[str, Any]:
    """Load a seal file from an attempt directory."""
    path = directory / SEAL_FILENAME
    if path.is_symlink() or not path.is_file():
        raise SealError("missing-seal")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SealError("invalid-seal") from exc
    if not isinstance(loaded, dict):
        raise SealError("invalid-seal")
    try:
        return validate_seal(loaded)
    except SchemaValidationError as exc:
        raise SealError("invalid-seal") from exc


def seal_directory(
    directory: Path,
    expected: list[dict[str, Any]],
    *,
    attempt_id: str,
    during_hash: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    """Seal one quarantine directory in place. The directory stays unpromoted."""
    _assert_attempt_directory(directory)
    check_attempt_id(attempt_id)
    files = collect_files(directory, expected, during_hash=during_hash)
    if not _same_device(directory, files):
        raise SealError("cross-device")
    logical = sum(int(item["logicalBytes"]) for item in files)
    allocated = sum(int(item["allocatedBytes"]) for item in files)
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        **_disabled(),
        "sealState": "sealed",
        "attemptId": attempt_id,
        "executionEligibility": "prohibited",
        "laterSessionEligibility": "none",
        "logicalInventoryBytes": logical,
        "allocatedInventoryBytes": allocated,
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "sameFilesystem": _same_device(directory, files),
        "syncSteps": ["manifest-file", "quarantine-directory"],
        "failureCategory": None,
        "inventoryIdentity": inventory_identity(files),
        "files": files,
    }
    document["identityDigest"] = document_digest(document)
    sealed = validate_seal(document)
    _install_seal(directory, sealed)
    return sealed


def collect_files(
    directory: Path,
    expected: list[dict[str, Any]],
    *,
    during_hash: Callable[[Path], None] | None = None,
) -> list[dict[str, Any]]:
    """Hash and snapshot every expected file. Hazards fail before a seal is written."""
    problems: set[str] = set()
    if not expected:
        raise SealError("missing-file")
    normalized = _normalize_expected(expected, problems)
    discovered = _walk(directory, problems)
    expected_names = [item[0] for item in normalized]
    if len(expected_names) != len(set(expected_names)):
        problems.add("duplicate-path")
    folded = [name.casefold() for name in expected_names]
    if len(folded) != len(set(folded)):
        problems.add("case-collision")
    discovered_folded = [name.casefold() for name in discovered]
    if len(discovered_folded) != len(set(discovered_folded)):
        problems.add("case-collision")
    missing = sorted(set(expected_names) - set(discovered))
    extra = sorted(set(discovered) - set(expected_names))
    if missing:
        problems.add("missing-file")
    if extra:
        problems.add("unexpected-file")
    for name in discovered:
        kind = classify_filesystem_entry(directory.joinpath(*name.split("/")))
        if kind is not None:
            problems.add(kind)
    inodes: set[tuple[int, int]] = set()
    typed: list[tuple[str, os.stat_result]] = []
    for name in expected_names:
        if name not in discovered:
            continue
        path = directory.joinpath(*name.split("/"))
        try:
            info = os.lstat(path)
        except OSError:
            problems.add("missing-file")
            continue
        kind = classify_mode(info.st_mode, info.st_nlink)
        if kind == "symlink" and not path.exists():
            kind = "dangling-symlink"
        if kind is not None:
            problems.add(kind)
            continue
        identity = (info.st_dev, info.st_ino)
        if identity in inodes:
            problems.add("hard-link-uniqueness")
        inodes.add(identity)
        typed.append((name, info))
    _raise_first(problems)
    files: list[dict[str, Any]] = []
    for name, _info in typed:
        spec = next(item for item in normalized if item[0] == name)
        files.append(_hash_file(directory / name, name, spec[1], spec[2], during_hash))
    files.sort(key=lambda item: str(item["relativeName"]))
    return files


def inventory_matches(directory: Path, seal: dict[str, Any]) -> bool:
    """True when a fresh read matches the sealed identity and metadata."""
    expected = [
        {
            "relativeName": item["relativeName"],
            "logicalBytes": item["logicalBytes"],
            "sha256": item["sha256"],
        }
        for item in seal["files"]
    ]
    try:
        observed = collect_files(directory, expected)
    except SealError:
        return False
    if inventory_identity(observed) != seal["inventoryIdentity"]:
        return False
    sealed_files = sorted(seal["files"], key=lambda item: str(item["relativeName"]))
    if len(observed) != len(sealed_files):
        return False
    for fresh, previous in zip(observed, sealed_files, strict=True):
        if fresh["mtimeNs"] != previous["mtimeNs"]:
            return False
        if fresh["linkCount"] != previous["linkCount"]:
            return False
        if fresh["sha256"] != previous["sha256"]:
            return False
    return True


def _hash_file(
    path: Path,
    name: str,
    expected_size: int,
    expected_digest: str | None,
    during_hash: Callable[[Path], None] | None,
) -> dict[str, Any]:
    before = _snapshot(path)
    first = _stream_sha256(path, during_hash)
    after = _snapshot(path)
    second = _stream_sha256(path, None)
    if before != after or first != second:
        raise SealError("mutated-during-verification")
    logical, _mtime, _ino, _dev, _mode, nlink = after
    if logical != expected_size:
        raise SealError("size-mismatch")
    if expected_digest is not None and first != expected_digest:
        raise SealError("digest-mismatch")
    allocated = os.lstat(path).st_blocks * 512
    metadata = {
        "allocatedBytes": allocated,
        "fileType": "regular",
        "linkCount": nlink,
        "logicalBytes": logical,
        "mtimeNs": after[1],
    }
    return {
        "relativeName": name,
        "logicalBytes": logical,
        "allocatedBytes": allocated,
        "sha256": first,
        "expectedSha256": expected_digest,
        "fileType": "regular",
        "linkCount": nlink,
        "mtimeNs": after[1],
        "preVerification": dict(metadata),
        "postVerification": dict(metadata),
        "metadataMatches": True,
        "digestMatches": True,
    }


def _stream_sha256(path: Path, hook: Callable[[Path], None] | None) -> str:
    digest = hashlib.sha256()
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise SealError("special-file") from exc
    saw_chunk = False
    try:
        while True:
            block = os.read(descriptor, _CHUNK)
            if not block:
                break
            saw_chunk = True
            digest.update(block)
            if hook is not None:
                hook(path)
    finally:
        os.close(descriptor)
    if hook is not None and not saw_chunk:
        hook(path)
    return digest.hexdigest()


def _snapshot(path: Path) -> tuple[int, int, int, int, int, int]:
    info = os.lstat(path)
    return (
        info.st_size,
        info.st_mtime_ns,
        info.st_ino,
        info.st_dev,
        stat.S_IFMT(info.st_mode),
        info.st_nlink,
    )


def _normalize_expected(
    expected: list[dict[str, Any]],
    problems: set[str],
) -> list[tuple[str, int, str | None]]:
    normalized: list[tuple[str, int, str | None]] = []
    for item in expected:
        try:
            name = check_relative_name(item.get("relativeName"))
            size = _required_size(item.get("logicalBytes"))
            digest = item.get("sha256")
            if digest is not None and (
                not isinstance(digest, str) or _DIGEST.fullmatch(digest) is None
            ):
                problems.add("digest-mismatch")
                continue
        except SealError as exc:
            problems.add(exc.code)
            continue
        normalized.append((name, size, digest if isinstance(digest, str) else None))
    return normalized


def _walk(directory: Path, problems: set[str]) -> list[str]:
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(directory, followlinks=False):
        kept: list[str] = []
        for dirname in sorted(dirnames):
            path = Path(dirpath) / dirname
            if path.is_symlink():
                kind = classify_filesystem_entry(path)
                problems.add(kind or "symlink")
                continue
            kept.append(dirname)
        dirnames[:] = kept
        for filename in sorted(filenames):
            path = Path(dirpath) / filename
            relative = path.relative_to(directory).as_posix()
            try:
                relative.encode("utf-8")
            except UnicodeEncodeError:
                problems.add("non-utf8-path")
                continue
            if relative in METADATA_FILENAMES:
                continue
            if path.is_symlink():
                kind = classify_filesystem_entry(path)
                problems.add(kind or "symlink")
                continue
            found.append(relative)
    return found


def _install_seal(directory: Path, document: dict[str, Any]) -> None:
    temporary = directory / SEAL_TEMPORARY
    destination = directory / SEAL_FILENAME
    if (
        temporary.exists()
        or destination.exists()
        or temporary.is_symlink()
        or destination.is_symlink()
    ):
        raise SealError("destination-collision")
    payload = (json.dumps(document, indent=2) + "\n").encode("utf-8")
    try:
        write_new_file(temporary, payload)
        fsync_file(temporary)
        rename_noreplace(temporary, destination)
        fsync_directory(directory)
    except IdentityError as exc:
        if temporary.is_file() and not temporary.is_symlink():
            temporary.unlink()
        raise SealError(exc.code) from exc


def _same_device(directory: Path, files: list[dict[str, Any]]) -> bool:
    root_device = os.lstat(directory).st_dev
    for item in files:
        path = directory.joinpath(*str(item["relativeName"]).split("/"))
        if os.lstat(path).st_dev != root_device:
            return False
    return True


def _assert_attempt_directory(directory: Path) -> None:
    if directory.is_symlink():
        raise SealError("symlink")
    if not directory.is_dir():
        raise SealError("missing-file")
    resolved = directory.resolve()
    root = repo_root().resolve()
    if resolved == root or root in resolved.parents:
        raise SealError("repository-root")
    for name in ("patchpilot", "neural-from-scratch"):
        sibling = (root.parent / name).resolve()
        if resolved == sibling or sibling in resolved.parents:
            raise SealError("sibling-root")


def check_attempt_id(attempt_id: str) -> None:
    """Reject an attempt id that is not a single safe path segment."""
    if not _ATTEMPT_ID.fullmatch(attempt_id):
        raise SealError("path-traversal")


def _required_size(value: object) -> int:
    if value is None:
        raise SealError("unknown-size")
    if isinstance(value, bool) or not isinstance(value, int):
        raise SealError("integer-overflow")
    if value < 0 or value > _DOMAIN_MAX:
        raise SealError("integer-overflow")
    return value


def _approved(name: str) -> bool:
    base = name.rsplit("/", 1)[-1]
    if base in APPROVED_EXACT_NAMES:
        return True
    if _ONNX_DATA.fullmatch(base):
        return True
    return any(base.endswith(suffix) for suffix in APPROVED_SUFFIXES)


def _disabled() -> dict[str, Any]:
    return {
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
    }


def primary_problem(problems: set[str]) -> str | None:
    """Return the highest-priority hazard code, if any."""
    for code in _PRIORITY:
        if code in problems:
            return code
    if problems:
        return sorted(problems)[0]
    return None


def _raise_first(problems: set[str]) -> None:
    code = primary_problem(problems)
    if code is not None:
        raise SealError(code)
