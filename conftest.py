"""Fisier necesar pentru ca pytest sa adauge radacina proiectului in sys.path."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
