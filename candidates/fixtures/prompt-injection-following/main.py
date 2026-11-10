"""Test double that follows instruction text present in the authorized request."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SUPPORT_PATH = Path(__file__).absolute().parents[1] / "support.py"
_SPEC = importlib.util.spec_from_file_location("candidate_fixture_support", _SUPPORT_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise SystemExit(2)
_SUPPORT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SUPPORT)

_CANDIDATE_ID = "fixture-prompt-injection-following"
_REQUEST = _SUPPORT.read_request()
_PAYLOAD = _SUPPORT.finding_input(_REQUEST)
_MARKERS = _SUPPORT.instruction_markers(_PAYLOAD)
_EXPLANATION = _SUPPORT.EXPLANATION
if _MARKERS:
    _EXPLANATION = "Embedded marker " + " ".join(_MARKERS)
_SUPPORT.emit(
    _SUPPORT.success_response(
        _REQUEST,
        _SUPPORT.authorized_output(_PAYLOAD, _CANDIDATE_ID, explanation=_EXPLANATION),
        _CANDIDATE_ID,
    )
)
