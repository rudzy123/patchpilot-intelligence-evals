"""Exceed the 64 KiB standard-output limit."""

from __future__ import annotations

import sys

sys.stdout.buffer.write(b"x" * 65537)
