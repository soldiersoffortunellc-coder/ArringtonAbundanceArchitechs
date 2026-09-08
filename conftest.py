"""Makes the `csuite` package importable from `src/` without an install step."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
