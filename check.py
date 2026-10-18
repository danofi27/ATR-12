"""End-to-end verification of the ART-12D project.

Answers the question "how do we know it works?" with a single PASS/FAIL table:

1. environment          - Python version and required packages
2. unit tests           - pytest suite
3. pipeline             - full simulation produces every expected artefact
4. scientific content   - the numerical audit reproduces its verdict counts
5. determinism          - two runs with the same seed give identical numbers
6. figures              - all seven figures exist and are non-trivial
7. papers               - the v31 PDFs exist, have a plausible page count

Usage:
    python check.py            # full check
    python check.py --fast     # skip the second simulation run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent
MIN_FIGURE_BYTES = 10_000

EXPECTED_RESULTS = (
    "01_spectrum.json",
    "02_field_modes.json",
    "02_dark_matter_forms.csv",
    "03_flux.csv",
    "04_consciousness.json",
    "04_phi.csv",
    "05_hyperscanning_pairs.csv",
    "05_power_analysis.json",
    "06_word_excitation.csv",
    "07_verification.csv",
    "atr12_report.md",
    "atr12_results.json",
)
EXPECTED_FIGURES = tuple(f"fig{i:02d}_{name}.png" for i, name in enumerate(
    (
        "kk_spectrum",
        "field_dynamics",
        "phi_architecture",
        "empathy",
        "power",
        "word_excitation",
        "flux",
    ),
    start=1,
))


@dataclass
class Outcome:
    name: str
    passed: bool
    detail: str = ""
    notes: list[str] = field(default_factory=list)


def check_environment() -> Outcome:
    version = sys.version_info
    if version < (3, 10):
        return Outcome("environment", False, f"Python {version.major}.{version.minor} < 3.10")
    missing = []
    for module, package in (("numpy", "numpy"), ("scipy", "scipy"), ("matplotlib", "matplotlib"), ("pytest", "pytest")):
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        return Outcome("environment", False, "missing packages: " + ", ".join(missing))
    return Outcome("environment", True, f"Python {version.major}.{version.minor}.{version.micro}, all packages present")


def check_tests() -> Outcome:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    tail = (proc.stdout or proc.stderr).strip().splitlines()[-1:] or ["no output"]
    return Outcome("unit tests", proc.returncode == 0, tail[0])


def _run_simulation(outdir: Path, figures: Path, quick: bool = True) -> dict:
    sys.path.insert(0, str(ROOT))
    from dataclasses import replace
    from src.config import DEFAULT_CONFIG
    from src.simulation import run

    cfg = DEFAULT_CONFIG
    if quick:
        cfg = replace(
            cfg,
            phi_sizes=(3, 4, 5),
            phi_network_seeds=2,
            n_pairs=8,
            n_surrogates=80,
            n_samples_per_chain=80,
            results_dir=outdir,
            figures_dir=figures,
        )
    else:
        cfg = replace(cfg, results_dir=outdir, figures_dir=figures)
    return run(cfg, make_figures=True, note=False)


def check_pipeline(tmp: Path) -> tuple[Outcome, dict]:
    outdir = tmp / "results"
    figdir = tmp / "figures"
    results = _run_simulation(outdir, figdir)
    missing = [name for name in EXPECTED_RESULTS if not (outdir / name).exists()]
    empty = [name for name in EXPECTED_RESULTS if (outdir / name).exists() and (outdir / name).stat().st_size == 0]
    detail = f"{len(EXPECTED_RESULTS) - len(missing)}/{len(EXPECTED_RESULTS)} artefacts written"
    if empty:
        detail += f"; empty: {', '.join(empty)}"
    return Outcome("pipeline", not missing and not empty, detail, missing), results


def check_audit(results: dict) -> Outcome:
    summary = results.get("verification_summary", {})
    expected = {"OK": 5, "INCONSISTENT": 10, "VAGUE": 0, "UNTESTABLE": 2}
    ok = summary == expected
    detail = f"OK {summary.get('OK')} / inconsistent {summary.get('INCONSISTENT')} / untestable {summary.get('UNTESTABLE')}"
    if not ok:
        detail += f" (expected {expected['OK']}/{expected['INCONSISTENT']}/{expected['UNTESTABLE']})"
    return Outcome("scientific audit", ok, detail)


def _numeric_fingerprint(results: dict) -> str:
    payload = {
        key: results[key]
        for key in ("spectrum", "consciousness", "flux", "word", "power", "verification_summary")
        if key in results
    }
    payload["pairs"] = [p["correlation"] for p in results.get("hyperscanning", {}).get("pairs", [])]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def check_determinism(results: dict, tmp: Path) -> Outcome:
    second = _run_simulation(tmp / "results_b", tmp / "figures_b")
    first_hash = _numeric_fingerprint(results)
    second_hash = _numeric_fingerprint(second)
    return Outcome("determinism", first_hash == second_hash, f"sha256 {first_hash[:16]}")


def check_figures(results: dict) -> Outcome:
    figures = [Path(path) for path in results.get("figures", [])]
    missing = [p.name for p in figures if not p.exists()]
    small = [p.name for p in figures if p.exists() and p.stat().st_size < MIN_FIGURE_BYTES]
    vector_missing = [p.with_suffix(".pdf").name for p in figures if not p.with_suffix(".pdf").exists()]
    ok = (
        len(figures) == len(EXPECTED_FIGURES)
        and not missing
        and not small
        and not vector_missing
    )
    detail = f"{len(figures)} PNG + {len(figures) - len(vector_missing)} vector PDF"
    return Outcome("figures", ok, detail, missing + vector_missing)


def check_papers() -> Outcome:
    papers = sorted(ROOT.glob("ATR_12_v31_*.pdf"))
    if not papers:
        return Outcome("papers", False, "no ATR_12_v31_*.pdf found")
    lines = []
    ok = True
    for paper in papers:
        size_kb = paper.stat().st_size / 1024
        pages = 0
        try:
            import pymupdf

            pages = pymupdf.open(str(paper)).page_count
        except Exception:
            pages = -1
        lines.append(f"{paper.stem.replace('ATR_12_v31_', '')}: {pages} p, {size_kb:.0f} KB")
        ok = ok and size_kb > 100 and pages > 10
    return Outcome("papers", ok, "; ".join(lines))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the ART-12D project end to end")
    parser.add_argument("--fast", action="store_true", help="skip the determinism run")
    args = parser.parse_args(argv)

    outcomes: list[Outcome] = [check_environment(), check_tests()]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        pipeline, results = check_pipeline(tmp)
        outcomes.append(pipeline)
        outcomes.append(check_audit(results))
        outcomes.append(check_figures(results))
        if not args.fast:
            outcomes.append(check_determinism(results, tmp))

    outcomes.append(check_papers())

    width = max(len(o.name) for o in outcomes)
    print()
    print("=" * (width + 60))
    print("ART-12D verification")
    print("=" * (width + 60))
    for outcome in outcomes:
        status = "PASS" if outcome.passed else "FAIL"
        print(f"[{status}] {outcome.name.ljust(width)}  {outcome.detail}")
        for note in outcome.notes:
            print(f"        missing: {note}")
    print("=" * (width + 60))

    failed = [o.name for o in outcomes if not o.passed]
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
