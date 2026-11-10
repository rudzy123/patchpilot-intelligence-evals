"""Emit a response for a different request id."""

from __future__ import annotations

import sys

from patchpilot_intelligence_evals.corpus import canonical_dumps

sys.stdin.buffer.read()
sys.stdout.write(
    canonical_dumps(
        {
            "protocolVersion": "1.0.0",
            "requestId": "b" * 64,
            "candidateId": "fixture-conforming",
            "candidateVersion": "1",
        }
    )
)
