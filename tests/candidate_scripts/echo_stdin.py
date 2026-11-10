"""Copy standard input to standard output without interpretation."""

from __future__ import annotations

import sys

sys.stdout.buffer.write(sys.stdin.buffer.read())
