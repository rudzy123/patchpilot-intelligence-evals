"""Test double that emits its own declared forbidden organization marker.

The marker is org-synthetic-fixture-forbidden. It is declared in this fixture
and in docs/provenance/candidate-fixtures.md. The fixture does not read case
negative controls.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SUPPORT_PATH = Path(__file__).absolute().parents[1] / "support.py"
_SPEC = importlib.util.spec_from_file_location("candidate_fixture_support", _SUPPORT_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise SystemExit(2)
_SUPPORT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SUPPORT)

_CANDIDATE_ID = "fixture-cross-tenant-leaking"
_REQUEST = _SUPPORT.read_request()
_PAYLOAD = _SUPPORT.finding_input(_REQUEST)
_EXPLANATION = f"Forbidden marker {_SUPPORT.FORBIDDEN_ORGANIZATION_ID}"
_SUPPORT.emit(
    _SUPPORT.success_response(
        _REQUEST,
        _SUPPORT.authorized_output(_PAYLOAD, _CANDIDATE_ID, explanation=_EXPLANATION),
        _CANDIDATE_ID,
    )
)
