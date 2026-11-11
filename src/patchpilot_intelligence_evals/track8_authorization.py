"""Track 8 acquisition authorization. Empty digest arrays stay empty.

No-selection withholds authorization. This module does not acquire artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import contains_private_marker
from patchpilot_intelligence_evals.candidate_eligibility import RETRIEVED_ON
from patchpilot_intelligence_evals.finalist_budget import decide_finalist_budget
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.track7_selection import (
    blocker_codes,
    decide_track7_selection,
)

_RECORD = Path("candidates/authorization/track8-acquisition-authorization.json")
_VERDICTS = {
    "authorized": "TRACK 8 CONTROLLED ACQUISITION AUTHORIZED",
    "authorized-with-documented-residuals": (
        "TRACK 8 CONTROLLED ACQUISITION AUTHORIZED WITH DOCUMENTED RESIDUALS"
    ),
    "not-authorized": "TRACK 8 CONTROLLED ACQUISITION NOT AUTHORIZED",
    "blocked-by-unresolved-authority": "BLOCKED BY UNRESOLVED AUTHORITY",
}


class Track8AuthorizationError(ValueError):
    """An authorization record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_track8_authorization() -> dict[str, Any]:
    """Withhold Track 8 when Track 7 selects nobody."""
    selection = decide_track7_selection()
    budget = decide_finalist_budget()["finalists"][0]
    blockers = blocker_codes(selection["candidates"][0], budget)
    outcome = _outcome(selection["selectionOutcome"], blockers)
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "retrievedOn": RETRIEVED_ON,
        "selectionOutcome": selection["selectionOutcome"],
        "selectedModelId": selection["selectedModelId"],
        "authorizationOutcome": outcome,
        "verdict": _VERDICTS[outcome],
        "installationAuthorized": False,
        "conversionAuthorized": False,
        "quantizationApproved": False,
        "blockers": blockers,
        "finalistCount": selection["finalistCount"],
        "finalistModelIds": selection["finalistModelIds"],
        "locallyObservedRuntimeDigests": [],
        "locallyObservedModelDigests": [],
        "locallyObservedTokenizerDigests": [],
        "locallyObservedConfigurationDigests": [],
    }
    return validate_track8_authorization(document)


def validate_track8_authorization(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one Track 8 authorization record."""
    validate("track8-acquisition-authorization", document)
    if contains_private_marker(document):
        raise Track8AuthorizationError("identity")
    for name in (
        "locallyObservedRuntimeDigests",
        "locallyObservedModelDigests",
        "locallyObservedTokenizerDigests",
        "locallyObservedConfigurationDigests",
    ):
        if document[name] != []:
            raise Track8AuthorizationError("local-digest")
    if document["installationAuthorized"] is not False:
        raise Track8AuthorizationError("installation")
    if (
        document["conversionAuthorized"] is not False
        or document["quantizationApproved"] is not False
    ):
        raise Track8AuthorizationError("conversion")
    selection = decide_track7_selection()
    budget = decide_finalist_budget()["finalists"][0]
    blockers = blocker_codes(selection["candidates"][0], budget)
    outcome = _outcome(selection["selectionOutcome"], blockers)
    if document["blockers"] != blockers:
        raise Track8AuthorizationError("blockers")
    if document["authorizationOutcome"] != outcome or document["verdict"] != _VERDICTS[outcome]:
        raise Track8AuthorizationError("verdict")
    if document["selectionOutcome"] != selection["selectionOutcome"]:
        raise Track8AuthorizationError("selection")
    if document["selectedModelId"] != selection["selectedModelId"]:
        raise Track8AuthorizationError("selection")
    if document["finalistModelIds"] != selection["finalistModelIds"]:
        raise Track8AuthorizationError("finalist-boundary")
    if outcome != "not-authorized" and document["selectedModelId"] is None:
        raise Track8AuthorizationError("authorization")
    return document


def load_track8_authorization(root: Path | None = None) -> dict[str, Any]:
    """Load the committed authorization and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track8AuthorizationError("record-type")
    document = validate_track8_authorization(loaded)
    if document != decide_track8_authorization():
        raise Track8AuthorizationError("authorization-drift")
    return document


def _outcome(selection_outcome: str, blockers: list[str]) -> str:
    if "unresolved-authority" in blockers:
        return "blocked-by-unresolved-authority"
    if selection_outcome == "selected" and not blockers:
        return "authorized"
    return "not-authorized"
