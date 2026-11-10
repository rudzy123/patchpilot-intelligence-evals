"""Emit a success envelope whose explanation is not schema-valid."""

from __future__ import annotations

import json
import sys

from patchpilot_intelligence_evals.corpus import canonical_dumps

request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
sys.stdout.write(
    canonical_dumps(
        {
            "schemaVersion": "1.0.0",
            "protocolVersion": "1.0.0",
            "requestId": request["requestId"],
            "candidateId": "fixture-conforming",
            "candidateVersion": "1",
            "status": "success",
            "findingExplanationOutput": {},
        }
    )
)
