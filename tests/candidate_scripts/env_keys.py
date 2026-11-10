"""Report child environment names without values."""

from __future__ import annotations

import json
import os
import sys

sys.stdout.write(json.dumps(sorted(os.environ), separators=(",", ":")))
