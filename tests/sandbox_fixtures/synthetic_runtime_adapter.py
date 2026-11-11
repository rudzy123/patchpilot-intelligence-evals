"""Synthetic runtime adapter fixture.

This file is the only executable the Track 6B adapter may launch. It does not
load ONNX Runtime, a model, or a tokenizer. It prints one canonical response.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _fail(category: str) -> None:
    sys.stdout.write(_canonical({"status": "fail", "failureCategory": category}))


def main() -> None:
    execution_path = Path("/config/execution.json")
    request_path = Path("/config/request.json")
    if not execution_path.is_file() or not request_path.is_file():
        _fail("protocol-malformed")
        return
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if not isinstance(execution, dict) or not isinstance(request, dict):
        _fail("protocol-malformed")
        return
    if execution.get("offline") is not True:
        _fail("offline-required")
        return
    telemetry_disabled = execution.get("telemetryDisabled") is True
    if not telemetry_disabled or os.environ.get("ORT_DISABLE_TELEMETRY") != "1":
        _fail("telemetry-enabled")
        return
    if execution.get("automaticRetrieval") is not False:
        _fail("retrieval-attempt")
        return
    if execution.get("automaticConversion") is not False:
        _fail("conversion-attempt")
        return
    if request.get("protocolVersion") != "1.0.0" or not isinstance(request.get("requestId"), str):
        _fail("protocol-malformed")
        return
    response = {
        "candidateId": "fixture-synthetic-runtime",
        "candidateVersion": "1.0.0",
        "failure": {"category": "unavailable", "message": "synthetic runtime fixture"},
        "protocolVersion": "1.0.0",
        "requestId": request["requestId"],
        "schemaVersion": "1.0.0",
        "status": "unavailable",
    }
    Path("/results/report.json").write_text(
        _canonical({"realModelExecuted": False, "status": "ok"}) + "\n",
        encoding="utf-8",
    )
    sys.stdout.write(_canonical(response))


if __name__ == "__main__":
    main()
