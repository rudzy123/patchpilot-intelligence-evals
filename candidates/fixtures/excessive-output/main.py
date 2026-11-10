"""Emit more than 64 KiB of standard output. This is not a model."""

from __future__ import annotations

import sys

sys.stdout.buffer.write(b"x" * 65537)
