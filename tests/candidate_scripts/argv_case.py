"""Report the script argument vector."""

from __future__ import annotations

import sys

from patchpilot_intelligence_evals.corpus import canonical_dumps

sys.stdout.write(canonical_dumps(sys.argv))
