"""Emit a response whose protocol version is not 1.0.0."""

from __future__ import annotations

import json
import sys

from patchpilot_intelligence_evals.corpus import canonical_dumps

request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
sys.stdout.write(
    canonical_dumps(
        {
            "protocolVersion": "9.9.9",
            "requestId": request["requestId"],
        }
    )
)
