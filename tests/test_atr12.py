"""Tests for the ART-12D package.

Run with: pytest -q
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from src import akashic_field, consciousness, empathy, fermions, temporal_modes, verification, word_excitation
from src.config import HZ_PER_EV, ATR12Config


@pytest.fixture()
def cfg() -> ATR12Config:
    return ATR12Config()


# ---------------------------------------------------------------------------
# Configuration and spectrum
# ---------------------------------------------------------------------------
def test_dimensions(cfg: ATR12Config) -> None:
    assert cfg.n_dim_total == 12
    assert cfg.n_dim_compact == 8


def test_kk_spectrum(cfg: ATR12Config) -> None:
    masses = temporal_modes.kk_masses_ev(3, cfg.inv_r_ev)
    assert masses[0] == pytest.approx(1e-5)
    assert masses[1] == pytest.approx(2e-5)
    assert masses[2] == pytest.approx(3e-5)


def test_kk_frequency_of_first_mode(cfg: ATR12Config) -> None:
    freqs = temporal_modes.kk_frequencies_hz(1, cfg.inv_r_ev)
    assert freqs[0] == pytest.approx(1e-5 * HZ_PER_EV)
    assert freqs[0] / 1e9 == pytest.approx(2.418, rel=1e-2)


def test_tachyon_mode(cfg: ATR12Config) -> None:
    m2 = temporal_modes.tachyon_spectrum_ev(3, cfg.inv_r_ev, cfg.tachyon_demo_mu_ev)
    assert m2[0] < 0
    assert m2[1] > 0
    assert temporal_modes.critical_mode(cfg.tachyon_demo_mu_ev, cfg.inv_r_ev) == pytest.approx(1.5)


def test_acoustic_spectrum_reduces_to_kk(cfg: ATR12Config) -> None:
    acoustic = temporal_modes.acoustic_spectrum_hz(3, cfg.inv_r_ev, 0.0)
    kk = temporal_modes.kk_frequencies_hz(3, cfg.inv_r_ev)
    np.testing.assert_allclose(acoustic, kk)


@pytest.mark.parametrize("delta,expected", [(0.01, 0.0), (100.0, 1.0 / 3.0)])
def test_equation_of_state_limits(delta: float, expected: float) -> None:
    assert akashic_field.equation_of_state(delta) == pytest.approx(expected, abs=2e-3)


def test_frozen_field_is_cosmological_constant() -> None:
    assert akashic_field.equation_of_state(0.0) == -1.0


def test_multiverse_overlap() -> None:
    psi = akashic_field.multiverse_state(4, seed=1)
    assert akashic_field.intersection_overlap(psi, psi) == pytest.approx(1.0)
    other = akashic_field.multiverse_state(4, seed=2)
    assert 0.0 <= akashic_field.intersection_overlap(psi, other) < 1.0


# ---------------------------------------------------------------------------
# Fermions
# ---------------------------------------------------------------------------
def test_number_density(cfg: ATR12Config) -> None:
    n = fermions.dark_matter_number_density_per_m3(1e-5, cfg.rho_dm_gev_cm3)
    assert n == pytest.approx(3e19, rel=1e-6)


def test_flux_scales_inversely_with_mass(cfg: ATR12Config) -> None:
    f1 = fermions.flux_per_m2_s(1e-5, 0.3, 300.0)
    f2 = fermions.flux_per_m2_s(1e-4, 0.3, 300.0)
    assert f1 / f2 == pytest.approx(10.0)


def test_body_crossing_matches_flux(cfg: ATR12Config) -> None:
    rate = fermions.body_crossings_per_s(1e-5, 0.3, 300.0, cfg.body_area_m2)
    flux = fermions.flux_per_m2_s(1e-5, 0.3, 300.0)
    assert rate == pytest.approx(flux * cfg.body_area_m2)


def test_yukawa_coupling(cfg: ATR12Config) -> None:
    assert fermions.yukawa_coupling(cfg.m4_gev, cfg.m12_gev, 5) == pytest.approx(1e-80, rel=1e-12)


def test_compton_wavelength_axion() -> None:
    assert fermions.compton_wavelength_m(1e-5) == pytest.approx(0.12398, rel=1e-3)


def test_debye_length_tissue() -> None:
    length_nm = fermions.debye_length_m(310.0, 0.15) * 1e9
    assert 0.5 < length_nm < 1.2


def test_mode_lifetime_scales_with_coupling() -> None:
    long_lived = temporal_modes.mode_lifetime_s(1e-5, 1e-10)
    short_lived = temporal_modes.mode_lifetime_s(1e-5, 1e-3)
    assert long_lived > short_lived
    assert temporal_modes.max_stable_coupling(1e-5) < 1e-12


# ---------------------------------------------------------------------------
# Consciousness
# ---------------------------------------------------------------------------
def test_phi_zero_for_disconnected_network() -> None:
    weights = np.zeros((3, 3))
    bias = np.zeros(3)
    samples = consciousness.glauber_sample(weights, bias, 1.0, 8, 40, 20, seed=0)
    result = consciousness.phi_cut(weights, bias, 1.0, samples)
    assert result.phi == pytest.approx(0.0, abs=1e-12)


def test_phi_positive_and_partition_valid(cfg: ATR12Config) -> None:
    result = consciousness.measure_phi(cfg, "cortex", n_nodes=5)
    assert result.phi > 0.0
    assert 0 < len(result.min_partition) < 5


def test_cortex_integrates_more_than_cerebellum(cfg: ATR12Config) -> None:
    comparison = consciousness.architecture_comparison(replace(cfg, phi_sizes=(6,), phi_network_seeds=2))
    row = comparison["rows"][0]
    assert row["phi_cortex_mean"] > row["phi_cerebellum_mean"]


def test_consciousness_field_bounded(cfg: ATR12Config) -> None:
    trajectory = consciousness.simulate_consciousness_field(cfg)
    assert trajectory.c.min() >= 0.0
    assert trajectory.c.max() <= 1.5 * cfg.c_max
    assert trajectory.final > cfg.c_initial


def test_consciousness_total_and_heart() -> None:
    assert consciousness.consciousness_total(2.0, 0.5) == pytest.approx(1.0)
    assert consciousness.heart_modulation(1.0, 0.2, 0.5) == pytest.approx(1.1)
    assert consciousness.receptor_gain(1e9) == pytest.approx(1.0, abs=1e-6)


def test_relaxation_time_positive(cfg: ATR12Config) -> None:
    assert consciousness.relaxation_time_s(cfg) > 0


# ---------------------------------------------------------------------------
# Empathy
# ---------------------------------------------------------------------------
def test_empathy_coupling_peaks_at_zero_detuning() -> None:
    assert empathy.empathy_coupling(40.0, 40.0, 2.0) == pytest.approx(1.0)
    assert empathy.empathy_coupling(40.0, 42.0, 2.0) == pytest.approx(0.5)
    assert empathy.empathy_coupling(40.0, 60.0, 2.0) < 0.01


def test_empathy_matrix_symmetric() -> None:
    matrix = empathy.empathy_matrix(np.array([40.0, 41.0, 44.0]), 2.0)
    np.testing.assert_allclose(matrix, matrix.T)
    np.testing.assert_allclose(np.diag(matrix), 1.0)


def test_required_duration_grows_for_small_effects(cfg: ATR12Config) -> None:
    small = empathy.required_duration_s(0.1, cfg.band_halfwidth_hz, 0.05)
    large = empathy.required_duration_s(0.4, cfg.band_halfwidth_hz, 0.05)
    assert small > large


def test_power_analysis_consistency(cfg: ATR12Config) -> None:
    power = empathy.power_analysis(cfg)
    assert power["effective_samples"] == pytest.approx(2 * cfg.band_halfwidth_hz * cfg.eeg_duration_s)
    assert 0.0 <= power["group_power"][0]["power_r0.1_vs_0.0"] <= 1.0


# ---------------------------------------------------------------------------
# Word coupling
# ---------------------------------------------------------------------------
def test_audio_scale_mismatch(cfg: ATR12Config) -> None:
    inv_r = word_excitation.required_inv_r_for_audio(300.0)
    assert inv_r == pytest.approx(1.24e-12, rel=1e-2)
    assert np.log10(cfg.inv_r_ev / inv_r) == pytest.approx(6.9, abs=0.2)


def test_word_analysis_shapes(cfg: ATR12Config) -> None:
    analysis = word_excitation.run_word_analysis(cfg)
    assert len(analysis["modes"]) == len(word_excitation.PAPER_EMOTION_BANDS_HZ)
    assert len(analysis["solfeggio"]) == 6


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------
def test_verification_checks(cfg: ATR12Config) -> None:
    checks = verification.run_checks(cfg)
    assert len(checks) >= 12
    verdicts = {c.ident: c.verdict for c in checks}
    assert verdicts["planck-fractions"] == verification.OK
    assert verdicts["kk-mass-ratio"] == verification.INCONSISTENT
    assert verdicts["compton-wavelengths"] == verification.INCONSISTENT
    assert verdicts["prediction-count"] == verification.UNTESTABLE


def test_verification_markdown(cfg: ATR12Config) -> None:
    markdown = verification.to_markdown(verification.run_checks(cfg))
    assert markdown.startswith("| # |")
    assert "INCONSISTENT" in markdown


# ---------------------------------------------------------------------------
# End-to-end
# ---------------------------------------------------------------------------
def test_full_pipeline_quick(tmp_path: Path, cfg: ATR12Config) -> None:
    from src.simulation import run

    quick = replace(
        cfg,
        phi_sizes=(3, 4),
        phi_network_seeds=2,
        n_pairs=6,
        n_surrogates=40,
        n_samples_per_chain=60,
        figures_dir=tmp_path / "figures",
        results_dir=tmp_path / "results",
    )
    results = run(quick, make_figures=False, note=False)

    assert (tmp_path / "results" / "atr12_report.md").exists()
    assert (tmp_path / "results" / "atr12_results.json").exists()
    assert results["verification_summary"]["OK"] >= 1
    assert len(results["hyperscanning"]["pairs"]) == 6
