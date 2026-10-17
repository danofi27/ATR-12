"""Empathy as frequency resonance and the EEG hyperscanning test (Prediction 1).

Model (v30.md):

    Empathy(A, B) = 1 / (1 + (omega_A - omega_B)^2 / Gamma^2)

Two brains with close frequencies are coupled more strongly to the common
field. The central test of the paper is the cross-correlation of EEG signals
at 40 Hz, with the criterion r > 0.1 and p < 0.05 after Bonferroni correction.

This module implements:
* pair simulation (own narrowband signal + common field component + noise),
* in-band correlation and a circular-shift surrogate test,
* power analysis via the Fisher transform, which shows how many independent
  samples the paper's criterion actually requires.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal
from scipy.stats import norm

from .config import ATR12Config


# ---------------------------------------------------------------------------
# Frequency coupling
# ---------------------------------------------------------------------------
def empathy_coupling(omega_a: float, omega_b: float, gamma: float) -> float:
    """1 / (1 + (dw/Gamma)^2), with values in (0, 1]."""
    if gamma <= 0:
        raise ValueError("Gamma must be positive")
    return float(1.0 / (1.0 + ((omega_a - omega_b) / gamma) ** 2))


def empathy_matrix(omegas: np.ndarray, gamma: float) -> np.ndarray:
    omegas = np.asarray(omegas, float)
    diff = omegas[:, None] - omegas[None, :]
    return 1.0 / (1.0 + (diff / gamma) ** 2)


# ---------------------------------------------------------------------------
# Synthetic EEG signals
# ---------------------------------------------------------------------------
def narrowband_source(
    t: np.ndarray,
    fs_hz: float,
    f0_hz: float,
    halfwidth_hz: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """White noise filtered in the band of interest: the standard EEG oscillation model."""
    white = rng.normal(size=t.shape)
    return bandpass(white, fs_hz, f0_hz, halfwidth_hz)


def bandpass(x: np.ndarray, fs_hz: float, f0_hz: float, halfwidth_hz: float, order: int = 4) -> np.ndarray:
    nyquist = 0.5 * fs_hz
    low = max(f0_hz - halfwidth_hz, 0.5)
    high = min(f0_hz + halfwidth_hz, nyquist * 0.95)
    if low >= high:
        raise ValueError("invalid band for the given sampling rate")
    b, a = signal.butter(order, [low / nyquist, high / nyquist], btype="band")
    return signal.filtfilt(b, a, x)


def band_correlation(a: np.ndarray, b: np.ndarray, fs_hz: float, f0_hz: float, halfwidth_hz: float) -> float:
    """Pearson correlation in the band of interest (proxy for the '40 Hz cross-correlation')."""
    fa = bandpass(a, fs_hz, f0_hz, halfwidth_hz)
    fb = bandpass(b, fs_hz, f0_hz, halfwidth_hz)
    if np.std(fa) < 1e-15 or np.std(fb) < 1e-15:
        return 0.0
    return float(np.corrcoef(fa, fb)[0, 1])


def envelope_correlation(a: np.ndarray, b: np.ndarray, fs_hz: float, f0_hz: float, halfwidth_hz: float) -> float:
    """Hilbert-envelope correlation, the measure most often used in hyperscanning."""
    ea = np.abs(signal.hilbert(bandpass(a, fs_hz, f0_hz, halfwidth_hz)))
    eb = np.abs(signal.hilbert(bandpass(b, fs_hz, f0_hz, halfwidth_hz)))
    if np.std(ea) < 1e-15 or np.std(eb) < 1e-15:
        return 0.0
    return float(np.corrcoef(ea, eb)[0, 1])


def surrogate_p_value(
    a: np.ndarray,
    b: np.ndarray,
    fs_hz: float,
    f0_hz: float,
    halfwidth_hz: float,
    n_surrogates: int,
    rng: np.random.Generator,
    min_shift_s: float = 0.5,
) -> float:
    """p-value from circular shifts of b (keeps the spectrum, breaks synchrony).

    Both signals are filtered once, then the surrogates are circular shifts of
    the filtered signal - much faster than re-filtering on every permutation.
    """
    fa = bandpass(a, fs_hz, f0_hz, halfwidth_hz)
    fb = bandpass(b, fs_hz, f0_hz, halfwidth_hz)
    fa_centered = fa - fa.mean()
    fb_centered = fb - fb.mean()
    norm_a = np.linalg.norm(fa_centered)
    norm_b = np.linalg.norm(fb_centered)
    if norm_a < 1e-15 or norm_b < 1e-15:
        return 1.0
    observed = float(np.dot(fa_centered, fb_centered) / (norm_a * norm_b))

    n = len(fb_centered)
    min_shift = int(min_shift_s * fs_hz)
    if 2 * min_shift >= n:
        min_shift = max(1, n // 10)
    count = 0
    for _ in range(n_surrogates):
        shift = int(rng.integers(min_shift, n - min_shift))
        shifted = np.roll(fb_centered, shift)
        r = float(np.dot(fa_centered, shifted) / (norm_a * norm_b))
        if abs(r) >= abs(observed):
            count += 1
    return float((1 + count) / (1 + n_surrogates))


# ---------------------------------------------------------------------------
# Pair simulation
# ---------------------------------------------------------------------------
@dataclass
class PairResult:
    empathy: float
    delta_f_hz: float
    correlation: float
    envelope_correlation: float
    p_value: float
    is_high_empathy: bool
    p_surrogate: float = float("nan")

    def as_dict(self) -> dict[str, Any]:
        return {
            "empathy": self.empathy,
            "delta_f_hz": self.delta_f_hz,
            "correlation": self.correlation,
            "envelope_correlation": self.envelope_correlation,
            "p_value_fisher": self.p_value,
            "p_value_surrogate": self.p_surrogate,
            "high_empathy": self.is_high_empathy,
        }


def simulate_pair(cfg: ATR12Config, high_empathy: bool, rng: np.random.Generator) -> PairResult:
    """Simulate one pair; coupling depends on frequency matching (empathy).

    Each brain produces narrowband noise in the gamma range. The common
    component is the field received by both; its amplitude is proportional to
    empathy. The model gives E[r] = g^2 for the in-band correlation, with
    g = gain * empathy.
    """
    duration = cfg.eeg_duration_s
    fs = cfg.eeg_fs_hz
    t = np.arange(int(duration * fs)) / fs

    sigma = 0.4 if high_empathy else 3.0
    delta_f = float(rng.normal(scale=sigma))
    f_center = cfg.f_gamma_hz
    empathy = empathy_coupling(f_center, f_center + delta_f, cfg.empathy_gamma_hz)

    gain = float(np.clip(cfg.eeg_field_gain * empathy, 0.0, 0.999))

    common = narrowband_source(t, fs, f_center, cfg.band_halfwidth_hz, rng)
    own_a = narrowband_source(t, fs, f_center, cfg.band_halfwidth_hz, rng)
    own_b = narrowband_source(t, fs, f_center, cfg.band_halfwidth_hz, rng)

    own_scale = np.sqrt(max(1.0 - gain**2, 0.0))
    a = own_scale * own_a + gain * common
    b = own_scale * own_b + gain * common

    corr = band_correlation(a, b, fs, f_center, cfg.band_halfwidth_hz)
    env_corr = envelope_correlation(a, b, fs, f_center, cfg.band_halfwidth_hz)
    n_eff = effective_sample_size(duration, cfg.band_halfwidth_hz)
    p_fisher = fisher_p_value(corr, n_eff)
    p_surrogate = surrogate_p_value(
        a, b, fs, f_center, cfg.band_halfwidth_hz, cfg.n_surrogates, rng
    )
    return PairResult(
        empathy=empathy,
        delta_f_hz=delta_f,
        correlation=corr,
        envelope_correlation=env_corr,
        p_value=p_fisher,
        is_high_empathy=high_empathy,
        p_surrogate=p_surrogate,
    )


def run_hyperscanning(cfg: ATR12Config) -> dict[str, Any]:
    """Run all pairs and apply a Bonferroni correction at the pair level."""
    rng = np.random.default_rng(cfg.seed + 101)
    n_high = int(round(cfg.n_pairs * cfg.high_empathy_fraction))
    flags = [True] * n_high + [False] * (cfg.n_pairs - n_high)
    rng.shuffle(flags)
    pairs = [simulate_pair(cfg, bool(flag), rng) for flag in flags]

    alpha = 0.05
    alpha_bonferroni = alpha / max(len(pairs), 1)

    high = [p for p in pairs if p.is_high_empathy]
    low = [p for p in pairs if not p.is_high_empathy]

    def _mean_stat(group: list[PairResult]) -> dict[str, float]:
        if not group:
            return {"n": 0, "mean_r": float("nan"), "mean_env_r": float("nan"), "max_r": float("nan")}
        return {
            "n": len(group),
            "mean_r": float(np.mean([g.correlation for g in group])),
            "mean_env_r": float(np.mean([g.envelope_correlation for g in group])),
            "max_r": float(np.max([g.correlation for g in group])),
        }

    n_pass = sum(
        1 for p in pairs
        if p.correlation > 0.1 and p.p_value < alpha_bonferroni
    )
    return {
        "n_pairs": len(pairs),
        "alpha_bonferroni": alpha_bonferroni,
        "pairs": [p.as_dict() for p in pairs],
        "high_empathy": _mean_stat(high),
        "low_empathy": _mean_stat(low),
        "pairs_passing_literal_criterion": n_pass,
        "criterion": "r > 0.1 and p < 0.05 after Bonferroni (v30.md, Prediction 1); p is analytic (Fisher)",
    }


# ---------------------------------------------------------------------------
# Statistical power
# ---------------------------------------------------------------------------
def effective_sample_size(duration_s: float, halfwidth_hz: float) -> float:
    """Approximate number of independent samples in a band of width 2*B.

    For a band-limited process the number of degrees of freedom is
    approximately 2 * B * T (band-limited sampling theorem).
    """
    return float(2.0 * halfwidth_hz * duration_s)


def fisher_p_value(r: float, n_eff: float) -> float:
    if n_eff <= 3:
        return 1.0
    r = float(np.clip(r, -0.999999, 0.999999))
    z = np.arctanh(r) * np.sqrt(n_eff - 3.0)
    return float(2.0 * (1.0 - norm.cdf(abs(z))))


def required_n_eff(r: float, alpha: float) -> float:
    """Degrees of freedom needed to detect r at level alpha (two-sided)."""
    if not 0.0 < abs(r) < 1.0:
        raise ValueError("r must be in (-1, 1) and non-zero")
    z_crit = norm.ppf(1.0 - alpha / 2.0)
    return float((z_crit / np.arctanh(abs(r))) ** 2 + 3.0)


def required_duration_s(r: float, halfwidth_hz: float, alpha: float) -> float:
    n_eff = required_n_eff(r, alpha)
    return float(n_eff / (2.0 * halfwidth_hz))


def group_power(r_signal: float, r_null: float, n_pairs: int, n_eff: float, alpha: float) -> float:
    """Power of a two-group test using the aggregated Fisher z statistic."""
    if n_eff <= 3 or n_pairs < 2:
        return 0.0
    se = np.sqrt(1.0 / (n_pairs * (n_eff - 3.0))) * np.sqrt(2.0)
    delta = abs(np.arctanh(np.clip(r_signal, -0.999, 0.999)) - np.arctanh(np.clip(r_null, -0.999, 0.999)))
    z_crit = norm.ppf(1.0 - alpha / 2.0)
    return float(norm.cdf(delta / se - z_crit) + norm.cdf(-delta / se - z_crit))


def power_analysis(cfg: ATR12Config) -> dict[str, Any]:
    """How many pairs / seconds are needed for the criterion in the paper."""
    n_eff = effective_sample_size(cfg.eeg_duration_s, cfg.band_halfwidth_hz)
    alpha_bonf = 0.05 / cfg.n_pairs

    literal_duration = required_duration_s(0.1, cfg.band_halfwidth_hz, alpha_bonf)
    literal_duration_uncorrected = required_duration_s(0.1, cfg.band_halfwidth_hz, 0.05)

    grid = []
    for r in (0.1, 0.2, 0.3, 0.4, 0.5):
        grid.append(
            {
                "r": r,
                "required_duration_s_bonferroni": required_duration_s(r, cfg.band_halfwidth_hz, alpha_bonf),
                "required_duration_s_uncorrected": required_duration_s(r, cfg.band_halfwidth_hz, 0.05),
            }
        )

    power_rows = []
    for n_pairs in (10, 20, 40, 80, 120, 160):
        power_rows.append(
            {
                "n_pairs": n_pairs,
                "power_r0.3_vs_0.0": group_power(0.30, 0.0, n_pairs, n_eff, 0.05),
                "power_r0.2_vs_0.0": group_power(0.20, 0.0, n_pairs, n_eff, 0.05),
                "power_r0.1_vs_0.0": group_power(0.10, 0.0, n_pairs, n_eff, 0.05),
            }
        )

    return {
        "eeg_duration_s": cfg.eeg_duration_s,
        "band_halfwidth_hz": cfg.band_halfwidth_hz,
        "effective_samples": n_eff,
        "alpha_bonferroni": alpha_bonf,
        "literal_criterion_r0.1_duration_s": literal_duration,
        "literal_criterion_r0.1_duration_uncorrected_s": literal_duration_uncorrected,
        "required_n_eff": grid,
        "group_power": power_rows,
        "note": (
            "The literal criterion of v30.md (r > 0.1 per pair, Bonferroni) requires "
            "far longer recordings than 6 s; the group test (high vs low empathy) is "
            "substantially more powerful at the same number of pairs."
        ),
    }
