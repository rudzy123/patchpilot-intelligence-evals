"""Schema-valid test double that adds one fixed synthetic unsupported claim."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SUPPORT_PATH = Path(__file__).absolute().parents[1] / "support.py"
_SPEC = importlib.util.spec_from_file_location("candidate_fixture_support", _SUPPORT_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise SystemExit(2)
_SUPPORT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SUPPORT)

_CANDIDATE_ID = "fixture-unsupported-claim"
_REQUEST = _SUPPORT.read_request()
_PAYLOAD = _SUPPORT.finding_input(_REQUEST)
_SUPPORT.emit(
    _SUPPORT.success_response(
        _REQUEST,
        _SUPPORT.authorized_output(
            _PAYLOAD,
            _CANDIDATE_ID,
            extra_claim=_SUPPORT.UNSUPPORTED_CLAIM,
        ),
        _CANDIDATE_ID,
    )
)
