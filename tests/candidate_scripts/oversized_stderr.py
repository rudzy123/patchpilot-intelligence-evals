"""Exceed the 16 KiB standard-error limit."""

from __future__ import annotations

import sys

sys.stderr.buffer.write(b"y" * 16385)
sys.stdout.write("{}")
