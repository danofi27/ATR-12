"""Fermions and the Yukawa coupling: dark-matter flux, screened potential, constants.

Relations implemented (v30.md, Parts I and II):

    n      = rho_DM / m                       number density
    Phi    = n * v                            flux per unit area
    g_A    ~ (M_4 / M_12)^5                   estimated Yukawa coupling
    V(r)   = -g_A^2 * hbar c * exp(-r/lambda_D) / r    Debye-screened potential
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from .config import (
    C_M_S,
    ELECTRON_MASS_EV,
    EPSILON_0,
    EV_J,
    EV_TO_GEV,
    GEV_TO_EV,
    HBAR_C_EV_M,
    ATR12Config,
)

CM2_TO_M2 = 1e-4
AVOGADRO = 6.02214076e23
ELEMENTARY_CHARGE = 1.602176634e-19
K_B_J_K = 1.380649e-23


def dark_matter_number_density_per_m3(mass_ev: float, rho_gev_cm3: float) -> float:
    """n = rho / m. 1 GeV/cm^3 = 1e15 eV/m^3."""
    if mass_ev <= 0:
        raise ValueError("mass must be positive")
    return rho_gev_cm3 * GEV_TO_EV * 1e6 / mass_ev


def flux_per_m2_s(mass_ev: float, rho_gev_cm3: float, v_km_s: float) -> float:
    """Particle flux per unit area: Phi = n * v."""
    return dark_matter_number_density_per_m3(mass_ev, rho_gev_cm3) * v_km_s * 1000.0


def body_crossings_per_s(
    mass_ev: float,
    rho_gev_cm3: float,
    v_km_s: float,
    area_m2: float,
) -> float:
    """Number of particles crossing a body of the given surface area."""
    return flux_per_m2_s(mass_ev, rho_gev_cm3, v_km_s) * area_m2


def expected_interactions(
    flux_m2_s: float,
    sigma_cm2: float,
    area_m2: float,
    years: float,
) -> float:
    """Expected events = flux * sigma * area * time."""
    seconds = years * 365.25 * 24.0 * 3600.0
    return flux_m2_s * sigma_cm2 * CM2_TO_M2 * area_m2 * seconds


def interaction_probability(sigma_cm2: float, column_density_m2: float) -> float:
    """Interaction probability along a column: 1 - exp(-sigma*n)."""
    tau = sigma_cm2 * CM2_TO_M2 * column_density_m2
    return float(1.0 - np.exp(-tau))


def yukawa_coupling(m4_gev: float, m12_gev: float, power: int = 5, overlap: float = 1.0) -> float:
    """g_A ~ (M_4 / M_12)^power, with an optional overlap factor."""
    if m12_gev <= 0:
        raise ValueError("M_12 must be positive")
    return float(overlap * (m4_gev / m12_gev) ** power)


def yukawa_potential(r_m: float, coupling: float, screening_length_m: float) -> float:
    """V(r) = -g^2 * hbar c * exp(-r/lambda) / r, in eV."""
    if r_m <= 0:
        raise ValueError("r must be positive")
    return float(-(coupling**2) * HBAR_C_EV_M * np.exp(-r_m / screening_length_m) / r_m)


def yukawa_force_n(r_m: float, coupling: float, screening_length_m: float) -> float:
    """Force (in newtons) derived from the screened Yukawa potential."""
    if r_m <= 0:
        raise ValueError("r must be positive")
    potential_ev = yukawa_potential(r_m, coupling, screening_length_m)
    magnitude_ev_m = abs(potential_ev) * (1.0 / r_m + 1.0 / screening_length_m)
    return float(magnitude_ev_m * EV_J)


def debye_length_m(temperature_k: float, ionic_strength_mol_l: float, epsilon_r: float = 80.0) -> float:
    """Debye length in tissue: lambda_D = sqrt(eps0 eps_r kT / (2 N_A e^2 I))."""
    if ionic_strength_mol_l <= 0:
        raise ValueError("ionic strength must be positive")
    ionic_mol_m3 = ionic_strength_mol_l * 1000.0
    numerator = EPSILON_0 * epsilon_r * K_B_J_K * temperature_k
    denominator = 2.0 * AVOGADRO * ELEMENTARY_CHARGE**2 * ionic_mol_m3
    return float(np.sqrt(numerator / denominator))


def compton_wavelength_m(mass_ev: float) -> float:
    """lambda_C = h c / (m c^2) = hc / m, in metres."""
    if mass_ev <= 0:
        raise ValueError("mass must be positive")
    return HBAR_C_EV_M * 2.0 * np.pi / mass_ev


def de_broglie_wavelength_m(mass_ev: float, v_km_s: float) -> float:
    """lambda_dB = h / (m v) for a non-relativistic particle."""
    if mass_ev <= 0 or v_km_s <= 0:
        raise ValueError("mass and velocity must be positive")
    return 2.0 * np.pi * HBAR_C_EV_M / (mass_ev * (v_km_s / (C_M_S / 1000.0)))


def flux_table(masses_ev: Iterable[float], cfg: ATR12Config) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mass in masses_ev:
        flux = flux_per_m2_s(mass, cfg.rho_dm_gev_cm3, cfg.v_dm_km_s)
        rows.append(
            {
                "mass_ev": float(mass),
                "number_density_m3": dark_matter_number_density_per_m3(mass, cfg.rho_dm_gev_cm3),
                "flux_m2_s": flux,
                "body_crossings_per_s": flux * cfg.body_area_m2,
                "compton_wavelength_m": compton_wavelength_m(mass),
            }
        )
    return rows


def fermion_reference_table() -> list[dict[str, Any]]:
    """Electron / axion comparison from v30.md, with recomputed values."""
    rows = []
    for name, mass in (("electron", ELECTRON_MASS_EV), ("axion (n=1)", 1e-5)):
        rows.append(
            {
                "particle": name,
                "mass_ev": mass,
                "mass_gev": mass * EV_TO_GEV,
                "compton_wavelength_m": compton_wavelength_m(mass),
                "compton_wavelength_um": compton_wavelength_m(mass) * 1e6,
            }
        )
    rows.append(
        {
            "particle": "electron/axion ratio",
            "mass_ev": ELECTRON_MASS_EV / 1e-5,
            "mass_gev": (ELECTRON_MASS_EV / 1e-5) * EV_TO_GEV,
            "compton_wavelength_m": compton_wavelength_m(1e-5) / compton_wavelength_m(ELECTRON_MASS_EV),
            "compton_wavelength_um": float("nan"),
        }
    )
    return rows
