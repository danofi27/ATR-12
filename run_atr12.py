"""Lansator: python run_atr12.py [--quick] [--no-figures]"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.simulation import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
