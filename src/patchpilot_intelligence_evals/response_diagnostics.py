"""JSON, schema, and evidence-ID diagnostics. Earlier stages stay intact."""

from __future__ import annotations

import json
import re
from typing import Any

from patchpilot_intelligence_evals.schemas import validator

_NAME = re.compile(r"'([^']+)'")
_EVIDENCE = re.compile(r"evidenceId")


def generation_facts(payload: bytes) -> dict[str, Any]:
    """Read the adapter side file. A missing file does not invent a parse."""
    if not payload:
        return _absent()
    try:
        loaded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _absent()
    if not isinstance(loaded, dict):
        return _absent()
    facts = {
        "adapterFallback": bool(loaded.get("adapterFallback")),
        "adapterTruncated": bool(loaded.get("adapterTruncated")),
        "generationObserved": True,
        "parseCategory": str(loaded.get("parseCategory", "not-performed")),
        "parseColumn": _optional_int(loaded.get("parseColumn")),
        "parseLine": _optional_int(loaded.get("parseLine")),
        "parsePosition": _optional_int(loaded.get("parsePosition")),
        "trailingBytes": _int(loaded.get("trailingBytes")),
        "utf8": bool(loaded.get("utf8")),
    }
    names = _field_names(loaded.get("innerFieldNames"))
    if names is not None:
        facts["innerFieldNames"] = names
    return facts


def diagnose_response(
    extraction: dict[str, Any],
    side: dict[str, Any],
) -> dict[str, Any]:
    """Validate the extracted envelope and explanation without erasing extraction."""
    parsed = extraction.get("parsed")
    envelope_findings = _schema_findings("candidate-response", parsed)
    explanation = None
    if isinstance(parsed, dict):
        candidate = parsed.get("findingExplanationOutput")
        if isinstance(candidate, dict):
            explanation = candidate
    explanation_findings = _schema_findings("finding-explanation-output", explanation)
    missing = _unique(envelope_findings["missing"] + explanation_findings["missing"])
    unexpected = _unique(envelope_findings["unexpected"] + explanation_findings["unexpected"])
    evidence = _unique(envelope_findings["evidence"] + explanation_findings["evidence"])
    if extraction["extractionStatus"] in {"empty", "encoding-failure", "malformed-output"}:
        parse_status = "empty" if extraction["extractionStatus"] == "empty" else "malformed-json"
    elif extraction["extractionStatus"] == "multiple-outputs":
        parse_status = "malformed-json"
    elif isinstance(parsed, dict):
        parse_status = "parsed"
    else:
        parse_status = "not-object"
    schema_status = "not-performed"
    if extraction["extractionStatus"] == "extracted" and isinstance(parsed, dict):
        schema_status = (
            "valid" if envelope_findings["valid"] and explanation_findings["valid"] else "invalid"
        )
    category = str(side.get("parseCategory", "not-performed"))
    if category == "not-performed" and parse_status != "not-performed":
        category = parse_status
    return {
        "adapterFallback": bool(side.get("adapterFallback")),
        "adapterTruncated": bool(side.get("adapterTruncated")),
        "evidenceIdFindings": evidence,
        "generationObserved": bool(side.get("generationObserved")),
        "missingRequired": missing,
        "parseCategory": category,
        "parseColumn": side.get("parseColumn"),
        "parseLine": side.get("parseLine"),
        "parsePosition": side.get("parsePosition"),
        "parseStatus": parse_status,
        "schemaStatus": schema_status,
        "trailingBytes": _int(side.get("trailingBytes")),
        "unexpectedFields": unexpected,
        "utf8": bool(side.get("utf8"))
        or extraction["extractionStatus"] not in {"encoding-failure"},
    }


def _schema_findings(schema_name: str, instance: object) -> dict[str, Any]:
    if not isinstance(instance, dict):
        return {"valid": False, "missing": [], "unexpected": [], "evidence": []}
    missing: list[str] = []
    unexpected: list[str] = []
    evidence: list[str] = []
    valid = True
    for error in validator(schema_name).iter_errors(instance):
        valid = False
        pointer = "/".join(str(part) for part in error.path)
        if error.validator == "required":
            for name in _NAME.findall(error.message):
                if name.isidentifier():
                    missing.append(name)
        elif error.validator == "additionalProperties":
            for name in _NAME.findall(error.message):
                if _safe(name):
                    unexpected.append(name)
        elif _EVIDENCE.search(pointer) or _EVIDENCE.search(error.message):
            if pointer and _safe(pointer):
                evidence.append(pointer)
        elif error.validator == "pattern" and _EVIDENCE.search(str(error.schema_path)):
            if pointer and _safe(pointer):
                evidence.append(pointer)
    return {
        "valid": valid,
        "missing": missing,
        "unexpected": unexpected,
        "evidence": evidence,
    }


def _absent() -> dict[str, Any]:
    return {
        "adapterFallback": False,
        "adapterTruncated": False,
        "generationObserved": False,
        "parseCategory": "not-performed",
        "parseColumn": None,
        "parseLine": None,
        "parsePosition": None,
        "trailingBytes": 0,
        "utf8": False,
    }


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value


def _unique(values: list[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value not in seen and _safe(value):
            seen.append(value)
    return seen


def _safe(value: str) -> bool:
    return 0 < len(value) <= 120 and all(char.isalnum() or char in "._/-" for char in value)


def _field_names(value: object) -> list[str] | None:
    """Accept a sorted list of pre-wrap key names. Values are never stored."""
    if not isinstance(value, list) or len(value) > 40:
        return None
    names: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.isidentifier() or len(item) > 64:
            return None
        names.append(item)
    if names != sorted(names) or len(set(names)) != len(names):
        return None
    return names
