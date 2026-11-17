"""Extraction classifies stdout without rewriting the retained bytes."""

from __future__ import annotations

from patchpilot_intelligence_evals.corpus import canonical_dumps
from patchpilot_intelligence_evals.output_extraction import extract_envelope


def test_empty_and_encoding_failures_leave_bytes_intact() -> None:
    empty = b""
    assert extract_envelope(empty)["extractionStatus"] == "empty"
    binary = b"\xff\xfe"
    observed = extract_envelope(binary)
    assert observed["extractionStatus"] == "encoding-failure"
    assert binary == b"\xff\xfe"


def test_prose_around_json_is_not_rewritten() -> None:
    leading = b'note {"schemaVersion":"1.0.0"}'
    trailing = b'{"schemaVersion":"1.0.0"} note'
    assert extract_envelope(leading)["extractionStatus"] == "malformed-output"
    assert extract_envelope(trailing)["extractionStatus"] == "multiple-outputs"
    assert leading.startswith(b"note ")
    assert trailing.endswith(b" note")


def test_one_canonical_object_is_extracted() -> None:
    payload = {"schemaVersion": "1.0.0", "status": "success"}
    raw = canonical_dumps(payload).encode("utf-8")
    observed = extract_envelope(raw)
    assert observed["extractionStatus"] == "extracted"
    assert observed["parsed"] == payload
    assert observed["extractedDigest"] is None
    assert raw == canonical_dumps(payload).encode("utf-8")
