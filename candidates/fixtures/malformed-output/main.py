"""Emit a response frame that is not JSON. This is not a model."""

from __future__ import annotations

import sys

sys.stdout.write("not-json")
