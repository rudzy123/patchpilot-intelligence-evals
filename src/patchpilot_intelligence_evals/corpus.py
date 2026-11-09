"""Synthetic corpus loading, digests, and structural checks."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

from patchpilot_intelligence_evals.provenance import require_manifest_provenance
from patchpilot_intelligence_evals.schemas import repo_root, validate

EXPECTED_COUNTS: dict[str, int] = {
    "grounding-citation": 6,
    "insufficient-evidence-refusal": 4,
    "prompt-injection": 4,
    "cross-tenant-negative-control": 4,
    "contradiction": 3,
    "stale-unavailable-incomparable": 3,
}

REQUIRED_WARNINGS: tuple[str, ...] = (
    "non-authoritative-explanation",
    "does-not-mutate-patchpilot-state",
    "not-a-model",
)

CASE_IDS: tuple[str, ...] = (
    "case-ground-001",
    "case-ground-002",
    "case-ground-003",
    "case-ground-004",
    "case-ground-005",
    "case-ground-006",
    "case-refuse-001",
    "case-refuse-002",
    "case-refuse-003",
    "case-refuse-004",
    "case-inject-001",
    "case-inject-002",
    "case-inject-003",
    "case-inject-004",
    "case-tenant-001",
    "case-tenant-002",
    "case-tenant-003",
    "case-tenant-004",
    "case-contra-001",
    "case-contra-002",
    "case-contra-003",
    "case-stale-001",
    "case-stale-002",
    "case-stale-003",
)

_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github-token", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("connection-string", re.compile(r"(?:postgres|mysql|mongodb|redis)://\S+")),
    (
        "assigned-secret",
        re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\b\s*[:=]\s*\S+"),
    ),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("ipv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
)
_URL_RE = re.compile(r"https?://[^\s\"'\\]+")
_ORG_RE = re.compile(r"org-synthetic-[a-z0-9]+(?:-[a-z0-9]+)*")


class CorpusError(ValueError):
    """Corpus structure failed. The message names identifiers, not payloads."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def canonical_dumps(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def case_digest(case: dict[str, Any]) -> str:
    payload = {key: item for key, item in case.items() if key != "caseDigest"}
    return sha256_text(canonical_dumps(payload))


def corpus_digest(entries: list[dict[str, str]]) -> str:
    ordered = sorted(entries, key=lambda item: item["caseId"])
    body = [{"caseId": item["caseId"], "caseDigest": item["caseDigest"]} for item in ordered]
    return sha256_text(canonical_dumps(body))


def cases_dir() -> Path:
    return repo_root() / "corpus" / "cases"


def manifest_path() -> Path:
    return repo_root() / "corpus" / "manifest.json"


def load_cases() -> list[dict[str, Any]]:
    paths = sorted(cases_dir().glob("*.json"))
    cases: list[dict[str, Any]] = []
    for path in paths:
        loaded = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
        cases.append(loaded)
    return sorted(cases, key=lambda item: str(item["caseId"]))


def load_manifest() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(manifest_path().read_text(encoding="utf-8")))


def to_candidate_input(case: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "authorizedOrganizationId": case["authorizedOrganizationId"],
        "findingId": case["findingId"],
        "assetId": case["assetId"],
        "packageId": case["packageId"],
        "deterministicFacts": case["deterministicFacts"],
        "evidence": case["authorizedEvidence"],
        "missingEvidence": case["missingEvidence"],
        "assistanceRequest": case["assistanceRequest"],
    }
    payload["inputDigest"] = sha256_text(canonical_dumps(payload))
    return payload


def secret_pattern_names(text: str) -> list[str]:
    return [name for name, pattern in _SECRET_PATTERNS if pattern.search(text)]


def foreign_organization_ids(text: str, authorized_organization_id: str) -> list[str]:
    return [found for found in _ORG_RE.findall(text) if found != authorized_organization_id]


def invalid_url_hosts(text: str) -> list[str]:
    hosts: list[str] = []
    for match in _URL_RE.findall(text):
        host = (urlparse(match).hostname or "").rstrip(".").lower()
        if not host.endswith(".invalid"):
            hosts.append(host or "missing-host")
    return hosts


def _authorized_blob(case: dict[str, Any]) -> str:
    projection = {key: value for key, value in case.items() if key != "negativeControls"}
    return canonical_dumps(projection)


def validate_corpus() -> dict[str, Any]:
    """Return the manifest summary or raise CorpusError with a stable code."""
    cases = load_cases()
    manifest = load_manifest()
    if len(cases) != 24:
        raise CorpusError("case-count")
    ids = [str(case["caseId"]) for case in cases]
    if ids != sorted(CASE_IDS) or len(set(ids)) != 24:
        raise CorpusError("case-ids")
    counts = {name: 0 for name in EXPECTED_COUNTS}
    evidence_ids: set[str] = set()
    for case in cases:
        case_id = str(case["caseId"])
        validate("evaluation-case", case)
        if case_digest(case) != case["caseDigest"]:
            raise CorpusError(f"digest:{case_id}")
        category = str(case["category"])
        counts[category] = counts.get(category, 0) + 1
        if case["sourceDeclaration"] != "original-synthetic":
            raise CorpusError(f"source:{case_id}")
        if case["license"] != "Apache-2.0":
            raise CorpusError(f"license:{case_id}")
        warnings = set(cast(list[str], case["expectedSafetyWarnings"]))
        if not set(REQUIRED_WARNINGS).issubset(warnings):
            raise CorpusError(f"warnings:{case_id}")
        injection = cast(dict[str, Any], case["promptInjection"])
        markers = cast(list[str], injection["markers"])
        if bool(injection["present"]) != (len(markers) > 0):
            raise CorpusError(f"injection-flag:{case_id}")
        if (category == "prompt-injection") != bool(injection["present"]):
            raise CorpusError(f"injection-category:{case_id}")
        controls = cast(list[dict[str, str]], case["negativeControls"])
        if (category == "cross-tenant-negative-control") != (len(controls) > 0):
            raise CorpusError(f"tenant-category:{case_id}")
        blob = _authorized_blob(case)
        for control in controls:
            if control["organizationId"] == case["authorizedOrganizationId"]:
                raise CorpusError(f"control-org:{case_id}")
            for token in (
                control["organizationId"],
                control["findingId"],
                control["assetId"],
                control["canary"],
            ):
                if token in blob:
                    raise CorpusError(f"control-in-authorized:{case_id}")
        raw = canonical_dumps(case)
        if secret_pattern_names(raw):
            raise CorpusError(f"secret-pattern:{case_id}")
        if invalid_url_hosts(raw):
            raise CorpusError(f"url:{case_id}")
        for evidence in cast(list[dict[str, str]], case["authorizedEvidence"]):
            evidence_id = evidence["evidenceId"]
            if evidence_id in evidence_ids:
                raise CorpusError(f"duplicate-evidence:{evidence_id}")
            evidence_ids.add(evidence_id)
        candidate = to_candidate_input(case)
        validate("finding-explanation-input", candidate)
        if any(control["canary"] in canonical_dumps(candidate) for control in controls):
            raise CorpusError(f"control-in-input:{case_id}")
    if counts != EXPECTED_COUNTS:
        raise CorpusError("taxonomy")
    manifest_cases = cast(list[dict[str, str]], manifest["cases"])
    manifest_ids = [item["caseId"] for item in manifest_cases]
    if manifest_ids != sorted(manifest_ids):
        raise CorpusError("manifest-order")
    expected_entries = [
        {
            "caseId": str(case["caseId"]),
            "caseDigest": str(case["caseDigest"]),
            "category": str(case["category"]),
        }
        for case in cases
    ]
    if manifest_cases != expected_entries:
        raise CorpusError("manifest-cases")
    if manifest.get("taxonomyCounts") != EXPECTED_COUNTS:
        raise CorpusError("manifest-taxonomy")
    if manifest.get("caseCount") != 24:
        raise CorpusError("manifest-count")
    digest = corpus_digest(
        [{"caseId": item["caseId"], "caseDigest": item["caseDigest"]} for item in expected_entries]
    )
    if manifest.get("corpusDigest") != digest:
        raise CorpusError("corpus-digest")
    for field in (
        "generationMethod",
        "contaminationWarning",
        "allowedUses",
        "prohibitedUses",
        "corpusVersion",
    ):
        if not manifest.get(field):
            raise CorpusError(f"manifest-field:{field}")
    require_manifest_provenance(manifest)
    orgs = {str(case["authorizedOrganizationId"]) for case in cases}
    if "org-synthetic-south" in orgs:
        raise CorpusError("south-authorized")
    return {
        "status": "pass",
        "caseCount": 24,
        "corpusDigest": digest,
        "taxonomyCounts": EXPECTED_COUNTS,
    }
