"""Report the child working directory."""

from __future__ import annotations

import os
import sys

sys.stdout.write(os.getcwd())
