"""Temporal modes: KK spectrum, tachyons, reference clocks, time as vibration.

Relations implemented (v30.md, Part II):

    m_n^2 = n^2 / R^2                      ordinary KK modes
    m_n^2 = n^2 / R^2 - mu_A^2             tachyonic modes (n < mu_A R)
    omega_n = (1/R) * sqrt(n^2 + mu_A^2 R^2)   acoustic spectrum
    tau = hbar / Gamma,  Gamma = g^2 m / (8 pi)  mode lifetime
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .config import HZ_PER_EV, REFERENCE_CLOCKS_HZ, ATR12Config

HBAR_EV_S = 6.582119569e-16
AGE_OF_UNIVERSE_S = 4.35e17


def kk_masses_ev(n_max: int, inv_r_ev: float) -> np.ndarray:
    """m_n = n / R, with 1/R given in eV."""
    if n_max < 1:
        raise ValueError("n_max must be >= 1")
    if inv_r_ev <= 0:
        raise ValueError("1/R must be positive")
    n = np.arange(1, n_max + 1, dtype=float)
    return n * inv_r_ev


def kk_frequencies_hz(n_max: int, inv_r_ev: float) -> np.ndarray:
    return kk_masses_ev(n_max, inv_r_ev) * HZ_PER_EV


def tachyon_spectrum_ev(n_max: int, inv_r_ev: float, mu_a_ev: float) -> np.ndarray:
    """m_n^2 = n^2/R^2 - mu_A^2. Negative values mean a tachyonic mode."""
    n = np.arange(1, n_max + 1, dtype=float)
    return (n * inv_r_ev) ** 2 - mu_a_ev**2


def critical_mode(mu_a_ev: float, inv_r_ev: float) -> float:
    """Mode number below which the spectrum becomes tachyonic: n_crit = mu_A * R."""
    return mu_a_ev / inv_r_ev


def acoustic_spectrum_hz(n_max: int, inv_r_ev: float, mu_a_ev: float) -> np.ndarray:
    """omega_n = (1/R) sqrt(n^2 + (mu_A R)^2), expressed in Hz."""
    n = np.arange(1, n_max + 1, dtype=float)
    return np.sqrt(n**2 + (mu_a_ev / inv_r_ev) ** 2) * inv_r_ev * HZ_PER_EV


def mode_lifetime_s(mass_ev: float, coupling: float) -> float:
    """Lifetime of a scalar mode decaying into two fermions.

    Gamma = g^2 m / (8 pi) in natural units, tau = hbar / Gamma.
    """
    if mass_ev <= 0:
        return float("inf")
    if coupling <= 0:
        return float("inf")
    gamma_ev = coupling**2 * mass_ev / (8.0 * np.pi)
    return HBAR_EV_S / gamma_ev


def max_stable_coupling(mass_ev: float, lifetime_s: float = AGE_OF_UNIVERSE_S) -> float:
    """Largest coupling for which the mode survives the given time."""
    if mass_ev <= 0 or lifetime_s <= 0:
        return float("inf")
    return float(np.sqrt(8.0 * np.pi * HBAR_EV_S / (mass_ev * lifetime_s)))


def reality_ratio(change_hz: float, reference_hz: float) -> float:
    """The ratio 'Reality = Change / Reference' from v30.md."""
    if reference_hz <= 0:
        raise ValueError("reference must be positive")
    return change_hz / reference_hz


def reference_clocks() -> list[dict[str, Any]]:
    """Clock table used as a relative, not absolute, reference frame."""
    rows = [{"clock": name, "frequency_hz": f} for name, f in REFERENCE_CLOCKS_HZ.items()]
    caesium = REFERENCE_CLOCKS_HZ["caesium-133"]
    for row in rows:
        row["relative_to_caesium"] = row["frequency_hz"] / caesium
    return rows


def schumann_harmonics(n_max: int = 5, base_hz: float = 7.83) -> list[float]:
    """Schumann resonance harmonics, for comparison with the acoustic bands."""
    return [base_hz * (k + 1) for k in range(n_max)]


def spectrum_summary(cfg: ATR12Config, n_max: int = 6) -> dict[str, Any]:
    """Numeric summary of the spectrum used in the report."""
    masses = kk_masses_ev(n_max, cfg.inv_r_ev)
    freqs = masses * HZ_PER_EV
    tach = tachyon_spectrum_ev(n_max, cfg.inv_r_ev, cfg.tachyon_demo_mu_ev)
    return {
        "inv_r_ev": cfg.inv_r_ev,
        "masses_ev": masses.tolist(),
        "frequencies_ghz": (freqs / 1e9).tolist(),
        "compton_wavelengths_m": (1.239841984e-6 / masses).tolist(),
        "tachyon_mass_squared_ev2": tach.tolist(),
        "tachyon_modes": [int(n + 1) for n, m2 in enumerate(tach) if m2 < 0],
        "critical_mode": critical_mode(cfg.tachyon_demo_mu_ev, cfg.inv_r_ev),
        "acoustic_frequencies_ghz": (
            acoustic_spectrum_hz(n_max, cfg.inv_r_ev, cfg.tachyon_demo_mu_ev) / 1e9
        ).tolist(),
    }
