"""Emit one schema-valid success response from the authorized request."""

from __future__ import annotations

import json
import sys

from patchpilot_intelligence_evals.candidate_output import authorized_output
from patchpilot_intelligence_evals.corpus import canonical_dumps

request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
payload = request["findingExplanationInput"]
output = authorized_output(payload, "fixture-conforming")
response = {
    "schemaVersion": "1.0.0",
    "protocolVersion": "1.0.0",
    "requestId": request["requestId"],
    "candidateId": "fixture-conforming",
    "candidateVersion": "1",
    "status": "success",
    "findingExplanationOutput": output,
}
sys.stdout.write(canonical_dumps(response))
