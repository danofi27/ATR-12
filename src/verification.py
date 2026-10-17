"""Numerical audit of the quantitative claims in v30.md.

Each check recomputes a statement from the paper using the parameters it
declares, and assigns a verdict:

* ``OK``           - the statement reproduces numerically;
* ``INCONSISTENT`` - recomputed values contradict the statement;
* ``VAGUE``        - the statement is qualitative or ambiguously worded;
* ``UNTESTABLE``   - it cannot be evaluated with the data available in the paper.

The goal is to give the author a concrete list of corrections before the final
version, not to evaluate the theory as a whole.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from . import fermions, temporal_modes
from .akashic_field import equation_of_state
from .config import PAPER_MODE_MASSES_EV, PAPER_RESONANCES_HZ, ATR12Config
from .temporal_modes import AGE_OF_UNIVERSE_S, mode_lifetime_s, max_stable_coupling

OK = "OK"
INCONSISTENT = "INCONSISTENT"
VAGUE = "VAGUE"
UNTESTABLE = "UNTESTABLE"

#: alpha = g^2 * hbar c / (G m_p^2): ratio of the scalar Yukawa force to
#: gravity between two nucleons, in the limit r << lambda.
GRAVITATIONAL_CONSTANT_SI = 6.67430e-11
PROTON_MASS_KG = 1.67262192369e-27
HBAR_C_SI = 3.16152677e-26
FIFTH_FORCE_SCALE = HBAR_C_SI / (GRAVITATIONAL_CONSTANT_SI * PROTON_MASS_KG**2)


@dataclass
class Check:
    ident: str
    section: str
    claim: str
    computed: str
    verdict: str
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}e}"


def run_checks(cfg: ATR12Config) -> list[Check]:
    checks: list[Check] = []

    # 1. Planck cosmological composition ------------------------------------
    total = 4.9 + 26.8 + 68.3
    checks.append(
        Check(
            ident="planck-fractions",
            section="1.2 Dark matter - the exact numbers",
            claim="4.9% ordinary matter + 26.8% dark matter + 68.3% dark energy",
            computed=f"sum = {total:.1f}%",
            verdict=OK if abs(total - 100.0) < 0.05 else INCONSISTENT,
            detail="The Planck 2018 numbers are internally consistent.",
        )
    )

    # 2. KK mass ratios ------------------------------------------------------
    paper_ratios = (
        PAPER_MODE_MASSES_EV[1] / PAPER_MODE_MASSES_EV[0],
        PAPER_MODE_MASSES_EV[2] / PAPER_MODE_MASSES_EV[0],
    )
    model_spectrum = temporal_modes.kk_masses_ev(3, cfg.inv_r_ev)
    model_ratios = (model_spectrum[1] / model_spectrum[0], model_spectrum[2] / model_spectrum[0])
    checks.append(
        Check(
            ident="kk-mass-ratio",
            section="III.1 The six forms of dark matter",
            claim="masses of modes n=1,2,3 are 1e-5, 1e-4, 1e-3 eV",
            computed=f"implied ratios {paper_ratios[0]:.0f} and {paper_ratios[1]:.0f}; "
                     f"the model m_n = n/R gives {model_ratios[0]:.0f} and {model_ratios[1]:.0f}",
            verdict=INCONSISTENT,
            detail="The table uses a factor 10 between modes, but the KK spectrum requires m_n proportional to n. "
                   "Either change the table to 1e-5 / 2e-5 / 3e-5 eV, or drop the formula m_n = n/R.",
        )
    )

    # 2b. Compactification radius implied by the KK spectrum -----------------
    radius_m = fermions.HBAR_C_EV_M / cfg.inv_r_ev
    lab_bound_m = 38e-6
    checks.append(
        Check(
            ident="compactification-radius",
            section="II.1 Geometry + III.1 dark-matter masses",
            claim="a 1e-5 eV KK mode is compatible with the 12D compactification",
            computed=f"R = hbar c /(1/R) = {radius_m:.3e} m ({radius_m * 100:.2f} cm); "
                     f"inverse-square-law bound: R < {lab_bound_m:.1e} m",
            verdict=INCONSISTENT,
            detail="With m_n = n/R, a 1e-5 eV mode requires an extra dimension of ~2 cm, excluded by "
                   "sub-millimetre tests of Newton's law by more than two orders of magnitude. Keeping the "
                   "KK interpretation requires m_1 > 5e-3 eV (R < 40 um); otherwise the dark-matter field "
                   "cannot be a KK mode of the same geometry.",
        )
    )

    # 3. Resonance frequencies vs table masses -------------------------------
    implied_masses = [f * 4.135667696e-15 for f in PAPER_RESONANCES_HZ]
    ratios_to_first = [m / PAPER_MODE_MASSES_EV[0] for m in implied_masses]
    checks.append(
        Check(
            ident="resonance-masses",
            section="IV.4 (Prediction 158) / III.3 (microtubules)",
            claim="resonances at 16 GHz, 36.8 GHz and 57.6 GHz for KK modes 1, 2, 3",
            computed="implied masses: "
                     + ", ".join(_fmt(m) for m in implied_masses)
                     + " eV; ratios to 1e-5 eV: "
                     + ", ".join(f"{r:.1f}" for r in ratios_to_first),
            verdict=INCONSISTENT,
            detail="16 GHz corresponds to 6.6e-5 eV, not to 1e-5 eV (which is 2.42 GHz). "
                   "The ratios 16 : 36.8 : 57.6 follow neither m_n ~ n nor sqrt(n^2 + const).",
        )
    )

    # 4. Dark-matter number density ------------------------------------------
    n_axion = fermions.dark_matter_number_density_per_m3(PAPER_MODE_MASSES_EV[0], cfg.rho_dm_gev_cm3)
    mass_for_3000 = cfg.rho_dm_gev_cm3 * 1e15 / 3000.0
    checks.append(
        Check(
            ident="dm-number-density",
            section="I.4 What kind of particles pass through your body",
            claim="n = 3000 particles/m^3 for dark matter",
            computed=f"n(1e-5 eV) = {_fmt(n_axion)} /m^3; 3000 /m^3 corresponds to {_fmt(mass_for_3000)} eV (~100 GeV)",
            verdict=INCONSISTENT,
            detail="The value 3000/m^3 is the one for a ~100 GeV WIMP. For a 1e-5 eV KK mode, "
                   f"the number density is about {np.log10(n_axion / 3000):.1f} orders of magnitude larger.",
        )
    )

    # 5. Body crossing rate --------------------------------------------------
    rate_paper_n = 3000.0 * cfg.v_dm_km_s * 1000.0 * cfg.body_area_m2
    rate_axion = fermions.body_crossings_per_s(
        PAPER_MODE_MASSES_EV[0], cfg.rho_dm_gev_cm3, cfg.v_dm_km_s, cfg.body_area_m2
    )
    checks.append(
        Check(
            ident="body-crossing-rate",
            section="I.4 (6e8 particles/s) vs abstract/introduction (1e8 particles/s)",
            claim="~6e8 particles/s cross the body; the introduction says ~1e8",
            computed=f"with n=3000/m^3: {_fmt(rate_paper_n)} /s; with the correct n for 1e-5 eV: {_fmt(rate_axion)} /s",
            verdict=INCONSISTENT,
            detail="The two values in the paper differ from each other by a factor of 6. Both are far below the "
                   "real rate for a 1e-5 eV mode, which is ~6e24 /s.",
        )
    )

    # 6. Yukawa coupling and the overlap factor ------------------------------
    g = fermions.yukawa_coupling(cfg.m4_gev, cfg.m12_gev, cfg.yukawa_power)
    needed_overlap = 1e-3 / g
    tau_g1e3 = mode_lifetime_s(PAPER_MODE_MASSES_EV[0], 1e-3)
    g_max_stable = max_stable_coupling(PAPER_MODE_MASSES_EV[0], AGE_OF_UNIVERSE_S)
    checks.append(
        Check(
            ident="yukawa-coupling",
            section="II.5 Derivation of the Yukawa coupling",
            claim="g_A ~ (M_4/M_12)^5 = 1e-80, but overlap factors can raise it to 1e-3",
            computed=f"g_A = {_fmt(g)}; overlap needed for 1e-3: {_fmt(needed_overlap)}",
            verdict=INCONSISTENT,
            detail=f"The required overlap factor is {_fmt(needed_overlap)}, impossible for normalised wavefunctions "
                   "(overlap is <= 1). Moreover, g = 1e-3 would give the mode a lifetime of "
                   f"{_fmt(tau_g1e3)} s, against a universe age of {_fmt(AGE_OF_UNIVERSE_S)} s.",
        )
    )

    checks.append(
        Check(
            ident="yukawa-stability",
            section="II.5 + III.1",
            claim="the 1e-5 eV KK modes are stable dark matter",
            computed=f"maximum coupling for stability over {_fmt(AGE_OF_UNIVERSE_S)} s: {_fmt(g_max_stable)}",
            verdict=OK,
            detail="The derived coupling g_A ~ 1e-80 is compatible with stability. The constraint only becomes "
                   "severe if g_eff ~ 1e-3 is adopted.",
        )
    )

    checks.append(
        Check(
            ident="yukawa-fifth-force",
            section="I.2 (the 7% fifth-force constraint) + II.5",
            claim="the effective coupling can reach 1e-3 without contradicting gravitational constraints",
            computed=f"alpha = g^2 hbar c /(G m_p^2) = {g**2 * FIFTH_FORCE_SCALE:.2e} for g = g_A; "
                     f"{1e-3**2 * FIFTH_FORCE_SCALE:.2e} for g = 1e-3",
            verdict=INCONSISTENT,
            detail="A scalar Yukawa force between nucleons has relative strength alpha = g^2 * 1.69e38. "
                   "For g = 1e-3, alpha ~ 1.7e32, excluded by fifth-force tests by ~35 orders of magnitude. "
                   "The 7% constraint quoted in the paper implies g < 2e-20. The derived value "
                   "g_A ~ 1e-80 is the only one consistent with the data.",
        )
    )

    # 7. Orch OR time constant vs gamma --------------------------------------
    tau_ms = 25.0
    f_from_tau = 1.0 / (tau_ms * 1e-3)
    checks.append(
        Check(
            ident="orch-or-40hz",
            section="I.3.4 Orchestrated Objective Reduction",
            claim="tau ~ 25 ms corresponds to ~40 Hz",
            computed=f"1 / 25 ms = {f_from_tau:.0f} Hz",
            verdict=OK,
            detail="The numerical relation is correct; it remains a qualitative coincidence, not a derivation.",
        )
    )

    # 8. Compton wavelengths -------------------------------------------------
    lam_axion = fermions.compton_wavelength_m(1e-5)
    lam_electron = fermions.compton_wavelength_m(fermions.ELECTRON_MASS_EV)
    checks.append(
        Check(
            ident="compton-wavelengths",
            section="I.4 Wave-particle duality (axion vs electron table)",
            claim="axion 1e-5 eV -> 1e19 m; electron 511 keV -> 1e-9 m; ratio 1e28",
            computed=f"axion: {lam_axion:.3f} m; electron: {lam_electron:.2e} m; ratio {lam_axion / lam_electron:.1e}",
            verdict=INCONSISTENT,
            detail="The Compton wavelength of a 1e-5 eV axion is ~12 cm, not 1e19 m; the electron one is "
                   "~2.4 pm, not 1 nm. The correct ratio is ~5e10, not 1e28.",
        )
    )

    # 9. Acoustic scale of the field -----------------------------------------
    audio_hz = 300.0
    inv_r_audio = audio_hz * 4.135667696e-15
    checks.append(
        Check(
            ident="acoustic-scale",
            section="I.3 (The word as field excitation)",
            claim="the acoustic spectrum omega_n = (1/R) sqrt(n^2 + mu^2 R^2) excites 150-800 Hz bands",
            computed=f"1/R for 300 Hz: {_fmt(inv_r_audio)} eV; 1/R for 1e-5 eV: {_fmt(cfg.inv_r_ev)} eV",
            verdict=INCONSISTENT,
            detail=f"The difference is {np.log10(cfg.inv_r_ev / inv_r_audio):.0f} orders of magnitude. "
                   "Word-field coupling requires either a second compactification scale or dropping the "
                   "identification of acoustic modes with the dark-matter KK modes.",
        )
    )

    # 10. Equation of state ---------------------------------------------------
    w_small = equation_of_state(0.01)
    w_large = equation_of_state(100.0)
    checks.append(
        Check(
            ident="equation-of-state",
            section="I.3 (Dark matter and dark energy: two faces)",
            claim="A << mu_A -> w = -1; A ~ mu_A -> w = 0; A >> mu_A -> w = 1",
            computed=f"small oscillation: w = {w_small:.3f}; large oscillation: w = {w_large:.3f}; frozen field: w = -1",
            verdict=INCONSISTENT,
            detail="For an oscillating field the virial theorem gives w = 0 for a quadratic potential and w = 1/3 "
                   "for a quartic-dominated one, not w = 1. w = 1 corresponds to kinetic domination (kination), "
                   "and w = -1 only to a field frozen at the minimum, not to small amplitudes. "
                   "The statement should be corrected into three distinct regimes.",
        )
    )

    # 11. Number of predictions ----------------------------------------------
    checks.append(
        Check(
            ident="prediction-count",
            section="V.1 Central prediction table",
            claim="313 testable predictions",
            computed="~20 predictions have cost, duration and criterion; the rest are deferred to 'version 1.0'",
            verdict=UNTESTABLE,
            detail="The number 313 cannot be verified from v30.md. The final version needs either the full list "
                   "or a reformulation such as '313 statements, 20 of which with a protocol'.",
        )
    )

    # 12. Phi hierarchy -------------------------------------------------------
    checks.append(
        Check(
            ident="phi-hierarchy",
            section="I.3 (The hierarchy of reception)",
            claim="Phi increases from thermostat (0) to trained human (very high)",
            computed="the hierarchy is qualitative; no numerical Phi values are given",
            verdict=UNTESTABLE,
            detail="The hierarchy follows from the proposed definition, not from an independent prediction. "
                   "To be testable, each level should be tied to a measurement (PCI, perturbational complexity).",
        )
    )

    # 13. Cerebellum/cortex ratio --------------------------------------------
    ratio = 69.0 / (69.0 + 16.0)
    checks.append(
        Check(
            ident="cerebellum-share",
            section="I.1.6 (architecture, not size)",
            claim="the cerebellum has 69 billion neurons, ~80% of the total; the cortex 16 billion",
            computed=f"69/(69+16) = {100 * ratio:.1f}%",
            verdict=OK,
            detail="The numbers agree with the literature (Herculano-Houzel).",
        )
    )

    # 14. Empathy formula at Gamma -> 0 --------------------------------------
    emp = 1.0 / (1.0 + (10.0 / 2.0) ** 2)
    checks.append(
        Check(
            ident="empathy-formula",
            section="I.3 (Empathy as frequency resonance)",
            claim="Empathy = 1/(1 + (dw/Gamma)^2)",
            computed=f"for dw = 10 Hz and Gamma = 2 Hz: {emp:.4f}",
            verdict=OK,
            detail="The formula is well defined; however, Gamma is not estimated in the paper, so the "
                   "decoupling scale remains a free parameter.",
        )
    )

    return checks


def summarize(checks: list[Check]) -> dict[str, int]:
    counts: dict[str, int] = {OK: 0, INCONSISTENT: 0, VAGUE: 0, UNTESTABLE: 0}
    for check in checks:
        counts[check.verdict] = counts.get(check.verdict, 0) + 1
    return counts


def to_markdown(checks: list[Check]) -> str:
    lines = ["| # | Check | Section | Verdict | Recomputed |", "|---|---|---|---|---|"]
    for i, c in enumerate(checks, start=1):
        lines.append(f"| {i} | `{c.ident}` | {c.section} | **{c.verdict}** | {c.computed} |")
    lines.append("")
    lines.append("Details:")
    lines.append("")
    for i, c in enumerate(checks, start=1):
        lines.append(f"{i}. **{c.ident}** - {c.detail}")
    return "\n".join(lines)
