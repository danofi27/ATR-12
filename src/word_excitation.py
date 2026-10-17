"""The word as an excitation of the akashic field (Prediction 3 / 67).

Model (v30.md):

    A(x, t) = sum_n A_n cos(omega_n t + phi_n)
    omega_n = (1/R) * sqrt(n^2 + mu_A^2 R^2)
    L_int   = g_sound * A * Phi_sound

A word is described by its dominant band (150-800 Hz). The coupling depends
on the overlap between the word's acoustic spectrum and the field's mode
spectrum. The module also audits the scale: KK modes sit at GHz for the R
that puts dark matter at 1e-5 eV, not at hundreds of Hz.
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from .config import (
    HZ_PER_EV,
    PAPER_EMOTION_BANDS_HZ,
    REFERENCE_CLOCKS_HZ,
    SOLFEGGIO_HZ,
    ATR12Config,
)


def lorentzian_overlap(f_hz: float, f0_hz: float, gamma_hz: float) -> float:
    """Overlap of a mode at f0 with a component at f (maximum at f = f0)."""
    if gamma_hz <= 0:
        raise ValueError("gamma must be positive")
    half = gamma_hz / 2.0
    return float(half**2 / ((f_hz - f0_hz) ** 2 + half**2))


def band_center(band: tuple[float, float]) -> float:
    return 0.5 * (band[0] + band[1])


def excitation_amplitude(
    band: tuple[float, float],
    mode_frequencies_hz: Iterable[float],
    amplitudes: Iterable[float],
    g_sound: float,
    gamma_hz: float,
) -> float:
    """Amplitude excited in each mode: g * A_n * L(f_band, f_n)."""
    center = band_center(band)
    total = 0.0
    for f_n, a_n in zip(mode_frequencies_hz, amplitudes):
        total += g_sound * a_n * lorentzian_overlap(center, f_n, gamma_hz)
    return float(total)


def mode_excitation_table(cfg: ATR12Config, n_modes: int = 6) -> list[dict[str, Any]]:
    freqs = [(n * cfg.inv_r_ev) * HZ_PER_EV for n in range(1, n_modes + 1)]
    amps = [1.0 / n for n in range(1, n_modes + 1)]
    rows = []
    for word, band in PAPER_EMOTION_BANDS_HZ.items():
        amp = excitation_amplitude(band, freqs, amps, cfg.g_sound, cfg.word_gamma_hz)
        rows.append(
            {
                "word": word,
                "band_hz": list(band),
                "excitation_amplitude": amp,
                "energy_proxy": amp**2,
            }
        )
    return rows


def required_inv_r_for_audio(f_hz: float, mu_a_ev: float = 0.0) -> float:
    """1/R needed for a mode to sit at frequency f (in eV)."""
    if f_hz <= 0:
        raise ValueError("frequency must be positive")
    energy = f_hz * 4.135667696e-15
    return float(np.sqrt(max(energy**2 - mu_a_ev**2, 0.0)))


def solfeggio_table() -> list[dict[str, Any]]:
    schumann = REFERENCE_CLOCKS_HZ["Schumann (historic)"]
    rows = []
    for f in SOLFEGGIO_HZ:
        harmonic = f / schumann
        rows.append(
            {
                "frequency_hz": f,
                "ratio_to_432": f / 432.0,
                "schumann_harmonic_index": harmonic,
                "nearest_schumann_harmonic": int(round(harmonic)),
                "deviation_from_harmonic": f - round(harmonic) * schumann,
            }
        )
    return rows


def detectable_effect(excitation: float, noise_floor: float = 1e-3) -> bool:
    """The effect is detectable only if it exceeds the measurement noise."""
    return bool(excitation**2 > noise_floor**2)


def required_coupling_for_effect(target_relative_effect: float, excitation_per_g: float) -> float:
    """g needed for a target relative effect, in the energy_proxy = (g * X)^2 model."""
    if target_relative_effect <= 0 or excitation_per_g <= 0:
        return float("inf")
    return float(np.sqrt(target_relative_effect) / excitation_per_g)


def run_word_analysis(cfg: ATR12Config) -> dict[str, Any]:
    modes = mode_excitation_table(cfg)
    freqs = [(n * cfg.inv_r_ev) * HZ_PER_EV for n in range(1, 7)]
    amps = [1.0 / n for n in range(1, 7)]
    love_band = PAPER_EMOTION_BANDS_HZ["love"]
    per_unit_g = excitation_amplitude(love_band, freqs, amps, 1.0, cfg.word_gamma_hz)

    audio_inv_r = required_inv_r_for_audio(300.0)
    return {
        "modes": modes,
        "g_sound": cfg.g_sound,
        "excitation_per_unit_g": per_unit_g,
        "g_sound_for_1pct_effect": required_coupling_for_effect(0.01, per_unit_g),
        "field_mode_frequencies_ghz": [f / 1e9 for f in freqs],
        "audio_inv_r_ev": audio_inv_r,
        "dm_inv_r_ev": cfg.inv_r_ev,
        "scale_mismatch_orders": float(abs(np.log10(audio_inv_r / cfg.inv_r_ev))),
        "solfeggio": solfeggio_table(),
        "note": (
            "The acoustic spectrum of the KK modes sits at GHz for the compactification "
            "scale that gives dark matter at 1e-5 eV. A resonance at 150-800 Hz would need "
            "1/R ~ 1e-12 eV, about 7 orders of magnitude away. Prediction 67 has no "
            "numerical content until g_sound is fixed independently."
        ),
    }
