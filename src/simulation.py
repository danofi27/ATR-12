"""ART-12D simulation orchestrator.

A single run produces:

* numeric tables for every module (JSON + CSV),
* the figures in ``figures/``,
* the report ``results/atr12_report.md``, including the numerical audit of the paper.

Usage:
    python -m src.simulation
    python -m src.simulation --quick --no-figures
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import akashic_field, consciousness, empathy, fermions, temporal_modes, verification, word_excitation
from .config import HZ_PER_EV, PAPER_MODE_MASSES_EV, PAPER_RESONANCES_HZ, ATR12Config, DEFAULT_CONFIG  # noqa: E402


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _jsonable(obj.tolist())
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, Path):
        return str(obj)
    return obj


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, ensure_ascii=False), encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def ensure_dirs(cfg: ATR12Config) -> None:
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)


def save_figure(fig: Any, path: Path, png_dpi: int = 200) -> list[str]:
    """Save a figure as vector PDF (for the paper) and as PNG (for the web/README)."""
    path = Path(path)
    fig.savefig(path, dpi=png_dpi)
    pdf_path = path.with_suffix(".pdf")
    fig.savefig(pdf_path)
    return [str(path), str(pdf_path)]


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def plot_kk_spectrum(cfg: ATR12Config, path: Path) -> None:
    n = np.arange(1, 7)
    model = n * cfg.inv_r_ev
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.semilogy(n, model, "o-", label="model: $m_n = n/R$")
    ax.semilogy([1, 2, 3], PAPER_MODE_MASSES_EV, "s--", label="v30.md table")
    implied = [f * 4.135667696e-15 for f in PAPER_RESONANCES_HZ]
    ax.semilogy([1, 2, 3], implied, "^:", label="masses implied by 16/36.8/57.6 GHz")
    for x, y in zip([1, 2, 3], PAPER_MODE_MASSES_EV):
        ax.annotate(f"{y:.0e} eV", (x, y), textcoords="offset points", xytext=(6, 4), fontsize=8)
    ax.set_xlabel("KK mode number (n)")
    ax.set_ylabel("mass (eV)")
    ax.set_title("Kaluza-Klein spectrum: model vs the paper's table")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    save_figure(fig, path)
    plt.close(fig)


def plot_field_dynamics(cfg: ATR12Config, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for k in range(3):
        traj = consciousness.simulate_consciousness_field(cfg, seed=cfg.seed + k)
        axes[0].plot(traj.t, traj.c, lw=1.0, label=f"realisation {k + 1}")
    axes[0].axhline(cfg.c_max, color="k", ls=":", lw=1, label="$C_{max}$")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("C(t)")
    axes[0].set_title("$dC/dt = \\alpha C(1-C/C_{max}) + \\beta\\eta(t)$")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    deltas = np.logspace(-2, 2.5, 24)
    curve = akashic_field.equation_of_state_curve(deltas)
    axes[1].semilogx([c["delta"] for c in curve], [c["w"] for c in curve], "o-")
    axes[1].axhline(0.0, color="gray", ls="--", lw=0.8)
    axes[1].axhline(1.0 / 3.0, color="green", ls="--", lw=0.8, label="1/3 (quartic limit)")
    axes[1].axvline(np.sqrt(2.0) - 1.0, color="crimson", ls=":", lw=1,
                    label="separatrix $\\delta = \\sqrt{2}-1$")
    axes[1].set_xlabel("$\\delta = A_{osc}/A_{min}$")
    axes[1].set_ylabel("w = <p>/<rho>")
    axes[1].set_title("Equation of state of the akashic field")
    axes[1].legend(fontsize=7, loc="lower right")
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, path)
    plt.close(fig)


def plot_phi_architecture(cfg: ATR12Config, comparison: dict[str, Any], path: Path) -> None:
    rows = comparison["rows"]
    sizes = [r["n_units"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].errorbar(
        sizes,
        [r["phi_cortex_mean"] for r in rows],
        yerr=[r["phi_cortex_sd"] for r in rows],
        fmt="o-",
        capsize=3,
        label="cortex (recurrent)",
    )
    axes[0].errorbar(
        sizes,
        [r["phi_cerebellum_mean"] for r in rows],
        yerr=[r["phi_cerebellum_sd"] for r in rows],
        fmt="s-",
        capsize=3,
        label="cerebellum (feedforward)",
    )
    axes[0].set_xlabel("number of units")
    axes[0].set_ylabel("$\\Phi$ (nats)")
    axes[0].set_title("Integrated information across the minimum cut")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    axes[1].bar([str(s) for s in sizes], [r["ratio"] for r in rows], color="steelblue")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("number of units")
    axes[1].set_ylabel("$\\Phi_{cortex} / \\Phi_{cerebellum}$")
    axes[1].set_title("Architecture ratio (network average)")
    axes[1].grid(axis="y", alpha=0.3, which="both")
    fig.tight_layout()
    save_figure(fig, path)
    plt.close(fig)


def plot_empathy(cfg: ATR12Config, hyperscanning: dict[str, Any], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    dw = np.linspace(0, 12, 400)
    for gamma in (1.0, 2.0, 4.0):
        axes[0].plot(dw, 1.0 / (1.0 + (dw / gamma) ** 2), label=f"$\\Gamma$ = {gamma:.0f} Hz")
    axes[0].set_xlabel("$|\\omega_A - \\omega_B|$ (Hz)")
    axes[0].set_ylabel("empathy")
    axes[0].set_title("Frequency coupling")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    pairs = hyperscanning["pairs"]
    highs = [p for p in pairs if p["high_empathy"]]
    lows = [p for p in pairs if not p["high_empathy"]]
    axes[1].scatter([p["empathy"] for p in lows], [p["correlation"] for p in lows], c="gray", label="low empathy")
    axes[1].scatter([p["empathy"] for p in highs], [p["correlation"] for p in highs], c="crimson", label="high empathy")
    axes[1].axhline(0.1, color="k", ls="--", lw=1, label="criterion r = 0.1")
    axes[1].set_xlabel("empathy")
    axes[1].set_ylabel("in-band correlation at 40 Hz")
    axes[1].set_title("Simulated hyperscanning")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, path)
    plt.close(fig)


def plot_power(cfg: ATR12Config, power: dict[str, Any], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    rs = np.linspace(0.05, 0.6, 200)
    durations = [empathy.required_duration_s(float(r), cfg.band_halfwidth_hz, power["alpha_bonferroni"]) for r in rs]
    axes[0].semilogy(rs, durations)
    axes[0].axhline(cfg.eeg_duration_s, color="crimson", ls="--", label=f"current duration ({cfg.eeg_duration_s:.0f} s)")
    axes[0].axvline(0.1, color="k", ls=":", label="criterion r = 0.1")
    axes[0].set_xlabel("true r")
    axes[0].set_ylabel("required duration (s)")
    axes[0].set_title("Duration needed for p < 0.05 (Bonferroni)")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    rows = power["group_power"]
    axes[1].plot([r["n_pairs"] for r in rows], [r["power_r0.3_vs_0.0"] for r in rows], "o-", label="r = 0.3")
    axes[1].plot([r["n_pairs"] for r in rows], [r["power_r0.2_vs_0.0"] for r in rows], "s-", label="r = 0.2")
    axes[1].plot([r["n_pairs"] for r in rows], [r["power_r0.1_vs_0.0"] for r in rows], "^-", label="r = 0.1")
    axes[1].axhline(0.8, color="gray", ls="--", lw=1, label="80% power")
    axes[1].set_xlabel("number of pairs")
    axes[1].set_ylabel("power (group test)")
    axes[1].set_title("Power of the high vs low empathy test")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, path)
    plt.close(fig)


def plot_word(cfg: ATR12Config, analysis: dict[str, Any], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    rows = analysis["modes"]
    amplitudes = np.array([r["excitation_amplitude"] for r in rows], dtype=float)
    relative_db = 20.0 * np.log10(np.maximum(amplitudes, 1e-300) / amplitudes.max())
    axes[0].barh([r["word"] for r in rows], relative_db, color="darkorange")
    axes[0].set_xlabel("excitation relative to the best-coupled word (dB)")
    axes[0].set_title("Word-field coupling at g = %.0e" % cfg.g_sound)
    axes[0].grid(axis="x", alpha=0.3)

    field = akashic_field.AkashicField.from_config(cfg, n_modes=4)
    mode_freqs = [m.frequency_hz for m in field.modes]
    axes[1].vlines(mode_freqs, 1e-6, [m.amplitude for m in field.modes], color="steelblue", lw=2)
    axes[1].scatter(mode_freqs, [m.amplitude for m in field.modes], color="steelblue", zorder=5,
                    label="KK modes")
    for hz in (150.0, 300.0, 800.0):
        axes[1].axvline(hz, color="crimson", ls=":", lw=1.2)
    axes[1].annotate("acoustic bands\n150-800 Hz", (900.0, 1.25), fontsize=8, color="crimson")
    axes[1].set_xscale("log")
    axes[1].set_xlim(1e2, 3e10)
    axes[1].set_ylim(0.0, 2.0)
    axes[1].set_xlabel("frequency (Hz)")
    axes[1].set_ylabel("amplitude (a.u.)")
    axes[1].set_title("Scale separation: KK modes (~GHz) vs sound (~Hz)")
    axes[1].legend(fontsize=8, loc="upper left")
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].xaxis.get_offset_text().set_visible(False)
    axes[0].xaxis.get_offset_text().set_visible(False)
    fig.tight_layout()
    save_figure(fig, path)
    plt.close(fig)


def plot_flux(cfg: ATR12Config, path: Path) -> None:
    masses = np.logspace(-8, 3, 200)
    flux = [fermions.flux_per_m2_s(float(m), cfg.rho_dm_gev_cm3, cfg.v_dm_km_s) for m in masses]
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.loglog(masses, flux, lw=1.6, label="correct flux, $\\Phi = \\rho v / m$")
    ax.scatter([PAPER_MODE_MASSES_EV[0]], [3000.0 * cfg.v_dm_km_s * 1000.0], color="crimson", zorder=5,
               label="paper's claim (3000/m$^3$)")
    ax.set_xlabel("particle mass (eV)")
    ax.set_ylabel("flux (m$^{-2}$ s$^{-1}$)")
    ax.set_title("Dark-matter flux through the human body")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    save_figure(fig, path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def build_report(cfg: ATR12Config, results: dict[str, Any]) -> str:
    spectrum = results["spectrum"]
    consc = results["consciousness"]
    hs = results["hyperscanning"]
    power = results["power"]
    word = results["word"]
    audit = results["verification"]
    counts = results["verification_summary"]

    lines: list[str] = []
    lines.append("# ART-12D - simulation report")
    lines.append("")
    lines.append(f"Configuration: `{cfg.describe()}`")
    lines.append("")

    lines.append("## 1. Kaluza-Klein spectrum")
    lines.append("")
    lines.append(f"- 1/R = {cfg.inv_r_ev:.2e} eV (m_1 = {cfg.m1_ev:.2e} eV)")
    lines.append(f"- masses n=1..6: {', '.join(f'{m:.2e}' for m in spectrum['masses_ev'])} eV")
    lines.append(f"- frequencies: {', '.join(f'{f:.2f}' for f in spectrum['frequencies_ghz'])} GHz")
    lines.append(f"- tachyonic modes (mu_A = {cfg.tachyon_demo_mu_ev:.2e} eV): {spectrum['tachyon_modes'] or 'none'}")
    lines.append("")

    lines.append("## 2. Consciousness field")
    lines.append("")
    lines.append(f"- theoretical fixed point: C* = {consc['steady_state']:.3f}")
    lines.append(f"- relaxation time (95%): {consc['relaxation_time_s']:.1f} s")
    lines.append(f"- simulated final value: {consc['field_final']:.3f} (mean {consc['field_mean']:.3f})")
    lines.append("")
    lines.append("### Phi: cortex vs cerebellum")
    lines.append("")
    lines.append("| units | Phi cortex (mean +/- sd) | Phi cerebellum (mean +/- sd) | ratio |")
    lines.append("|---|---|---|---|")
    for row in consc["cortex_vs_cerebellum"]["rows"]:
        lines.append(
            f"| {row['n_units']} | {row['phi_cortex_mean']:.4f} +/- {row['phi_cortex_sd']:.4f} | "
            f"{row['phi_cerebellum_mean']:.4f} +/- {row['phi_cerebellum_sd']:.4f} | {row['ratio']:.2f} |"
        )
    lines.append("")
    lines.append(f"Averages over {consc['cortex_vs_cerebellum'].get('n_seeds', 1)} random networks per size.")
    lines.append("")
    lines.append(
        "The Phi proxy is defined on a minimum cut of the Glauber dynamics; it is not exact "
        "IIT 3.0 Phi, but it reproduces the ordinal conclusion that a recurrent architecture "
        "integrates more than a feedforward one with the same number of units."
    )
    lines.append("")

    lines.append("## 3. Empathy and hyperscanning")
    lines.append("")
    lines.append(f"- pairs: {hs['n_pairs']}, Bonferroni alpha = {hs['alpha_bonferroni']:.4f}")
    lines.append(f"- high empathy: r = {hs['high_empathy']['mean_r']:.3f}")
    lines.append(f"- low empathy: r = {hs['low_empathy']['mean_r']:.3f}")
    lines.append(f"- pairs passing the literal criterion: {hs['pairs_passing_literal_criterion']}")
    lines.append(f"- mean envelope correlation: high {hs['high_empathy']['mean_env_r']:.3f}, "
                 f"low {hs['low_empathy']['mean_env_r']:.3f}")
    lines.append("")
    lines.append("### Statistical power of the paper's criterion")
    lines.append("")
    lines.append(f"- effective samples at {cfg.eeg_duration_s:.0f} s and +/-{cfg.band_halfwidth_hz:.0f} Hz: "
                 f"{power['effective_samples']:.0f}")
    lines.append(f"- duration needed for r = 0.1, Bonferroni: **{power['literal_criterion_r0.1_duration_s']:.1f} s**")
    lines.append(f"- duration needed for r = 0.1, uncorrected: {power['literal_criterion_r0.1_duration_uncorrected_s']:.1f} s")
    lines.append("")
    lines.append("| r | duration (s), Bonferroni | duration (s), alpha=0.05 |")
    lines.append("|---|---|---|")
    for row in power["required_n_eff"]:
        lines.append(f"| {row['r']:.1f} | {row['required_duration_s_bonferroni']:.1f} | {row['required_duration_s_uncorrected']:.1f} |")
    lines.append("")
    lines.append("| pairs | power r=0.3 | power r=0.2 | power r=0.1 |")
    lines.append("|---|---|---|---|")
    for row in power["group_power"]:
        lines.append(
            f"| {row['n_pairs']} | {row['power_r0.3_vs_0.0']:.2f} | {row['power_r0.2_vs_0.0']:.2f} | "
            f"{row['power_r0.1_vs_0.0']:.2f} |"
        )
    lines.append("")
    lines.append(f"> {power['note']}")
    lines.append("")

    lines.append("## 4. The word as field excitation")
    lines.append("")
    lines.append(f"- g_sound = {word['g_sound']:.1e}")
    lines.append(f"- excitation for g = 1: {word['excitation_per_unit_g']:.3e}")
    lines.append(f"- g needed for a 1% effect: {word['g_sound_for_1pct_effect']:.3e}")
    lines.append(f"- 1/R required for a 300 Hz resonance: {word['audio_inv_r_ev']:.2e} eV")
    lines.append(f"- scale gap to the dark-matter 1/R: {word['scale_mismatch_orders']:.0f} orders of magnitude")
    lines.append("")

    lines.append("## 5. Numerical audit of v30")
    lines.append("")
    lines.append(f"- OK: {counts.get('OK', 0)}")
    lines.append(f"- INCONSISTENT: {counts.get('INCONSISTENT', 0)}")
    lines.append(f"- VAGUE: {counts.get('VAGUE', 0)}")
    lines.append(f"- UNTESTABLE: {counts.get('UNTESTABLE', 0)}")
    lines.append("")
    lines.append(audit)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "This report is generated by `python -m src.simulation`. Values depend on the "
        "parameters in `src/config.py`; where the model makes a choice (for example the "
        "EEG coupling), the choice is declared in the docstring, not presented as data."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def run(cfg: ATR12Config = DEFAULT_CONFIG, make_figures: bool = True, note: bool = True) -> dict[str, Any]:
    ensure_dirs(cfg)
    results: dict[str, Any] = {"config": cfg.to_dict()}

    spectrum = temporal_modes.spectrum_summary(cfg)
    results["spectrum"] = spectrum
    _write_json(Path(cfg.results_dir) / "01_spectrum.json", spectrum)

    field = akashic_field.AkashicField.from_config(cfg)
    results["field_modes"] = field.mode_table()
    results["dark_matter_forms"] = akashic_field.dark_matter_forms()
    _write_json(Path(cfg.results_dir) / "02_field_modes.json", results["field_modes"])
    _write_csv(Path(cfg.results_dir) / "02_dark_matter_forms.csv", results["dark_matter_forms"])

    flux_rows = fermions.flux_table([1e-5, 1e-4, 1e-3, 1.0, 1e4, 1e11], cfg)
    results["flux"] = flux_rows
    _write_csv(Path(cfg.results_dir) / "03_flux.csv", flux_rows)
    results["fermion_reference"] = fermions.fermion_reference_table()

    consc = consciousness.summary(cfg)
    results["consciousness"] = consc
    _write_json(Path(cfg.results_dir) / "04_consciousness.json", consc)
    _write_csv(Path(cfg.results_dir) / "04_phi.csv", consc["cortex_vs_cerebellum"]["rows"])

    hs = empathy.run_hyperscanning(cfg)
    results["hyperscanning"] = hs
    _write_csv(Path(cfg.results_dir) / "05_hyperscanning_pairs.csv", hs["pairs"])

    power = empathy.power_analysis(cfg)
    results["power"] = power
    _write_json(Path(cfg.results_dir) / "05_power_analysis.json", power)

    word = word_excitation.run_word_analysis(cfg)
    results["word"] = word
    _write_csv(Path(cfg.results_dir) / "06_word_excitation.csv", word["modes"])

    checks = verification.run_checks(cfg)
    results["verification_summary"] = verification.summarize(checks)
    results["verification_checks"] = [c.as_dict() for c in checks]
    results["verification"] = verification.to_markdown(checks)
    _write_csv(Path(cfg.results_dir) / "07_verification.csv", [c.as_dict() for c in checks])

    if make_figures:
        figdir = Path(cfg.figures_dir)
        plot_kk_spectrum(cfg, figdir / "fig01_kk_spectrum.png")
        plot_field_dynamics(cfg, figdir / "fig02_field_dynamics.png")
        plot_phi_architecture(cfg, consc["cortex_vs_cerebellum"], figdir / "fig03_phi_architecture.png")
        plot_empathy(cfg, hs, figdir / "fig04_empathy.png")
        plot_power(cfg, power, figdir / "fig05_power.png")
        plot_word(cfg, word, figdir / "fig06_word_excitation.png")
        plot_flux(cfg, figdir / "fig07_flux.png")
        results["figures"] = sorted(str(p) for p in figdir.glob("*.png"))

    _write_json(Path(cfg.results_dir) / "atr12_results.json", results)
    report_path = Path(cfg.results_dir) / "atr12_report.md"
    report_path.write_text(build_report(cfg, results), encoding="utf-8")
    results["report_path"] = str(report_path)

    if note:
        print("ART-12D: run complete.")
        print(f"  spectrum: m1 = {cfg.m1_ev:.2e} eV, f1 = {cfg.m1_ev * HZ_PER_EV / 1e9:.2f} GHz")
        print(f"  Phi cortex/cerebellum (n={cfg.n_nodes}): "
              f"{consc['cortex_vs_cerebellum']['rows'][-1]['ratio']:.2f}x")
        print(f"  hyperscanning: r_high = {hs['high_empathy']['mean_r']:.3f}, "
              f"r_low = {hs['low_empathy']['mean_r']:.3f}")
        print(f"  audit: {results['verification_summary']}")
        print(f"  report: {report_path}")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ART-12D simulation")
    parser.add_argument("--out", type=Path, default=None, help="output directory for results")
    parser.add_argument("--figures", type=Path, default=None, help="output directory for figures")
    parser.add_argument("--seed", type=int, default=DEFAULT_CONFIG.seed)
    parser.add_argument("--quick", action="store_true", help="run a reduced variant")
    parser.add_argument("--no-figures", action="store_true", help="skip figure generation")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parent.parent
    cfg = DEFAULT_CONFIG
    overrides: dict[str, Any] = {
        "seed": args.seed,
        "results_dir": args.out if args.out is not None else project_root / "results",
        "figures_dir": args.figures if args.figures is not None else project_root / "figures",
    }
    if args.quick:
        overrides.update(
            {
                "phi_sizes": (3, 4, 5),
                "phi_network_seeds": 2,
                "n_pairs": 8,
                "n_surrogates": 100,
                "n_samples_per_chain": 80,
            }
        )

    cfg = replace(cfg, **overrides)
    run(cfg, make_figures=not args.no_figures)
    return 0


if __name__ == "__main__":
    sys.exit(main())
