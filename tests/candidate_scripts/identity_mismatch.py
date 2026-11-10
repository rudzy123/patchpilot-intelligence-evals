"""Emit a response that names a different candidate."""

from __future__ import annotations

import json
import sys

from patchpilot_intelligence_evals.corpus import canonical_dumps

request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
sys.stdout.write(
    canonical_dumps(
        {
            "protocolVersion": "1.0.0",
            "requestId": request["requestId"],
            "candidateId": "fixture-other",
            "candidateVersion": "1",
        }
    )
)
