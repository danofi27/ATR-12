"""ART-12D - Akashic Resonance Theory in 12 Dimensions.

Simulation package accompanying the v30.md paper. Modules follow the
structure of the theory:

* :mod:`src.config`          - parameters, constants, paper tables
* :mod:`src.akashic_field`   - KK spectrum, field A(t), equation of state
* :mod:`src.temporal_modes`  - KK and tachyonic modes, reference clocks
* :mod:`src.fermions`        - dark-matter flux, Yukawa coupling
* :mod:`src.consciousness`   - C(t) field, Phi as integrated information
* :mod:`src.empathy`         - frequency coupling, hyperscanning, statistical power
* :mod:`src.word_excitation` - word-field coupling
* :mod:`src.verification`    - numerical audit of the paper's claims
* :mod:`src.simulation`      - orchestrator that produces the report and figures

Run: ``python -m src.simulation`` or ``python run_atr12.py``.
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = ["__version__"]
