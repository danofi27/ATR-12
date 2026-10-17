"""The akashic field: Kaluza-Klein spectrum, modes, energy density, equations of state.

Base model (v30.md, Part II):

    A(x, y) = sum_n A_n(x) Y_n(y)          KK decomposition on M_4 x K_8
    m_n^2   = n^2 / R^2                    mass spectrum
    L_A     = 1/2 g^{MN} d_M A* d_N A + 1/2 mu_A^2 |A|^2 - lambda_A/4 |A|^4

KK modes are treated as independent oscillators; each mode has its own
frequency f_n = m_n / h (mode at rest).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

from .config import (
    HZ_PER_EV,
    HC_EV_M,
    PAPER_DARK_MATTER_FORMS,
    ATR12Config,
)


@dataclass(frozen=True)
class FieldMode:
    """A single Kaluza-Klein mode of the akashic field."""

    n: int
    mass_ev: float
    amplitude: float
    phase: float

    @property
    def frequency_hz(self) -> float:
        return self.mass_ev * HZ_PER_EV

    @property
    def angular_frequency(self) -> float:
        return 2.0 * np.pi * self.frequency_hz

    @property
    def compton_wavelength_m(self) -> float:
        if self.mass_ev <= 0:
            return float("inf")
        return HC_EV_M / self.mass_ev

    def as_dict(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "mass_ev": self.mass_ev,
            "frequency_ghz": self.frequency_hz / 1e9,
            "amplitude": self.amplitude,
            "phase_rad": self.phase,
            "compton_wavelength_m": self.compton_wavelength_m,
        }


class AkashicField:
    """Sum of KK modes approximating the field A(x, y) projected to 4D."""

    def __init__(self, modes: Iterable[FieldMode], mu_ev: float = 0.0, lambda_a: float = 0.1) -> None:
        self.modes: tuple[FieldMode, ...] = tuple(modes)
        self.mu_ev = mu_ev
        self.lambda_a = lambda_a

    # ------------------------------------------------------------------
    @classmethod
    def from_config(cls, cfg: ATR12Config, n_modes: int = 6, amplitude0: float = 1.0) -> "AkashicField":
        rng = np.random.default_rng(cfg.seed)
        modes = [
            FieldMode(
                n=n,
                mass_ev=n * cfg.inv_r_ev,
                amplitude=amplitude0 / n,
                phase=float(rng.uniform(0.0, 2.0 * np.pi)),
            )
            for n in range(1, n_modes + 1)
        ]
        return cls(modes, mu_ev=cfg.mu_a_ev, lambda_a=cfg.lambda_a)

    # ------------------------------------------------------------------
    def sample(self, t: np.ndarray, real: bool = True) -> np.ndarray:
        """Sample A(t) = sum_n A_n cos(omega_n t + phi_n)."""
        t = np.asarray(t, dtype=float)
        acc = np.zeros(t.shape, dtype=complex)
        for m in self.modes:
            acc = acc + m.amplitude * np.exp(1j * (m.angular_frequency * t + m.phase))
        return np.real(acc) if real else acc

    def power_spectrum(self, freqs_hz: np.ndarray, linewidth_hz: float | None = None) -> np.ndarray:
        """Power spectrum as a sum of Lorentzian lines centred on f_n."""
        freqs = np.asarray(freqs_hz, dtype=float)
        out = np.zeros(freqs.shape, dtype=float)
        for m in self.modes:
            gamma = linewidth_hz if linewidth_hz is not None else max(m.frequency_hz * 1e-4, 1.0)
            out += (m.amplitude**2) * (gamma / (2.0 * np.pi)) / ((freqs - m.frequency_hz) ** 2 + (gamma / 2.0) ** 2)
        return out

    def mode_table(self) -> list[dict[str, Any]]:
        return [m.as_dict() for m in self.modes]

    def total_energy_density(self, amplitudes: np.ndarray | None = None) -> float:
        """Energy density in arbitrary units: V(A) = -1/2 mu^2 A^2 + lambda/4 A^4."""
        amps = np.array([m.amplitude for m in self.modes]) if amplitudes is None else np.asarray(amplitudes, float)
        # the sign depends on the position relative to the minimum; use the modulus
        return float(np.sum(np.abs(-0.5 * self.mu_ev**2 * amps**2 + 0.25 * self.lambda_a * amps**4)))


# ---------------------------------------------------------------------------
# Equation of state of an oscillating scalar field
# ---------------------------------------------------------------------------
def _eos_curves(deltas: np.ndarray, n_theta: int = 4000) -> np.ndarray:
    """w for several amplitudes, computed exactly on the orbit.

    The time average is transformed into a phase integral,
    ``<F> = oint F dphi / |phidot| / oint dphi / |phidot|``, and the
    singularities at the turning points are regularized with
    ``phi = a + (b - a)(1 - cos(theta))/2``.

    The result therefore does not depend on a period estimate and carries no
    phase error (the problem that time-domain averaging has at intermediate
    amplitudes).
    """
    deltas = np.asarray(deltas, dtype=float)
    if np.any(deltas < 0):
        raise ValueError("delta must be non-negative")

    energy = 0.25 * (deltas * (2.0 + deltas)) ** 2      # V(1 + delta)
    root_energy = np.sqrt(energy)
    b = np.sqrt(1.0 + 2.0 * root_energy)                # outer turning point
    a_squared = 1.0 - 2.0 * root_energy                 # negative => orbit crosses the barrier
    a_phi = np.where(a_squared > 0.0, np.sqrt(np.maximum(a_squared, 0.0)), -b)

    theta = (np.arange(n_theta, dtype=float) + 0.5) * np.pi / n_theta
    phi = a_phi[None, :] + (b - a_phi)[None, :] * (1.0 - np.cos(theta))[:, None] / 2.0
    dphi = (b - a_phi)[None, :] * np.sin(theta)[:, None] / 2.0

    # E - V(phi) = (b^2 - phi^2)(phi^2 - a^2)/4, numerically stable form
    kinetic_energy = np.maximum(
        (b[None, :] ** 2 - phi**2) * (phi**2 - a_squared[None, :]) / 4.0, 0.0
    )
    sqrt_term = np.sqrt(2.0 * kinetic_energy)
    potential = 0.25 * (phi**2 - 1.0) ** 2

    safe = np.maximum(sqrt_term, 1e-300)
    ratio = dphi / safe                       # dphi / |phidot|, common d(theta) factor
    denominator = np.sum(ratio, axis=0)
    # K/|phidot| = (E - V)/sqrt(2(E - V)) = sqrt((E - V)/2) = sqrt_term / 2
    mean_k = np.sum(0.5 * sqrt_term * dphi, axis=0) / denominator
    mean_v = np.sum(potential * ratio, axis=0) / denominator
    return (mean_k - mean_v) / (mean_k + mean_v)


def equation_of_state(delta: float) -> float:
    """w = <p>/<rho> for a scalar oscillating in V = -mu^2 A^2/2 + lambda A^4/4.

    ``delta`` is the oscillation amplitude relative to the minimum
    A_min = mu/sqrt(lambda). Known limits:

    * ``delta -> 0``  : effective quadratic potential -> w = 0   (matter)
    * ``delta >> 1``  : quartic-dominated potential   -> w = 1/3 (radiation)
    * ``delta == 0``  : field frozen at the minimum   -> w = -1  (cosmological constant)

    Energy is measured from the potential minimum, so w is well defined even
    for the potential with V_min < 0 used in the paper.
    """
    if delta < 0:
        raise ValueError("delta must be non-negative")
    if delta == 0.0:
        return -1.0
    return float(_eos_curves(np.array([delta]))[0])


def equation_of_state_curve(deltas: Iterable[float]) -> list[dict[str, float]]:
    deltas_arr = np.asarray(list(deltas), dtype=float)
    mask = deltas_arr > 0
    values = np.full(deltas_arr.shape, -1.0)
    if np.any(mask):
        values[mask] = _eos_curves(deltas_arr[mask])
    return [{"delta": float(d), "w": float(w)} for d, w in zip(deltas_arr, values)]


# ---------------------------------------------------------------------------
# Multiverse and vacua
# ---------------------------------------------------------------------------
def multiverse_state(n_vacua: int, seed: int = 0) -> np.ndarray:
    """Product state |Psi> = prod_k |A_k>, with normalised complex amplitudes."""
    if n_vacua < 1:
        raise ValueError("n_vacua must be >= 1")
    rng = np.random.default_rng(seed)
    amps = rng.normal(size=n_vacua) + 1j * rng.normal(size=n_vacua)
    return amps / np.linalg.norm(amps)


def intersection_overlap(psi_a: np.ndarray, psi_b: np.ndarray) -> float:
    """Overlap |<a|b>|^2 between two multiverse states."""
    a = np.asarray(psi_a, complex)
    b = np.asarray(psi_b, complex)
    overlap = abs(np.vdot(a, b)) ** 2 / (np.vdot(a, a).real * np.vdot(b, b).real)
    return float(np.clip(overlap, 0.0, 1.0))


def dark_matter_forms() -> list[dict[str, Any]]:
    """The six dark-matter forms of v30.md, with the implied frequency."""
    rows: list[dict[str, Any]] = []
    for entry in PAPER_DARK_MATTER_FORMS:
        row = dict(entry)
        mass = float(row["mass_ev"])
        row["frequency_hz"] = mass * HZ_PER_EV if mass > 0 else float("nan")
        row["compton_wavelength_m"] = HC_EV_M / mass if mass > 0 else float("nan")
        rows.append(row)
    return rows
