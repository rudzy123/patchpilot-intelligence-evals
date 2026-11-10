"""Succeed for one case and sleep for another. This is not a model."""

from __future__ import annotations

import json
import sys
import time

from patchpilot_intelligence_evals.candidate_output import authorized_output
from patchpilot_intelligence_evals.corpus import canonical_dumps

request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
if request["caseId"] == "case-ground-002":
    time.sleep(30)
output = authorized_output(request["findingExplanationInput"], "fixture-conforming")
sys.stdout.write(
    canonical_dumps(
        {
            "schemaVersion": "1.0.0",
            "protocolVersion": "1.0.0",
            "requestId": request["requestId"],
            "candidateId": "fixture-conforming",
            "candidateVersion": "1",
            "status": "success",
            "findingExplanationOutput": output,
        }
    )
)
