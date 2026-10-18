# ART-12D — Akashic Resonance Theory in 12 Dimensions

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23457100.svg)](https://doi.org/10.5281/zenodo.23457100)
[![CI](https://github.com/danofi27/ATR-12/actions/workflows/ci.yml/badge.svg)](https://github.com/danofi27/ATR-12/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

**Archived DOI (v1.0.0):** [10.5281/zenodo.23457100](https://doi.org/10.5281/zenodo.23457100) ·
concept DOI for all versions: [10.5281/zenodo.23457099](https://doi.org/10.5281/zenodo.23457099)

Simulation code accompanying the **ART-12D** paper. The package implements the
relations of Part II of the paper, runs the experiments proposed in Part V on
synthetic data, and produces a **numerical audit** of the paper's quantitative
claims.

**Current paper: version 31.0**

- **Romanian (complete):** [ATR_12_v31_RO.pdf](./ATR_12_v31_RO.pdf) — 42 pages, built from
  [ATR_12_v31_RO.tex](./ATR_12_v31_RO.tex), which is the full v30 text with the ten
  corrections, the new sections and the seven figures (vector PDF, print quality).
  Ready to edit on Overleaf.
- **English (complete):** [ATR_12_v31_EN.pdf](./ATR_12_v31_EN.pdf) — 41 pages, a
  section-by-section translation of the Romanian master, built from
  [ATR_12_v31_EN.tex](./ATR_12_v31_EN.tex). The source is assembled from the
  per-part files in [`paper/en/`](./paper/en) by `paper/build_lang.py`, so the
  prose can be revised part by part.
- **German (complete):** [ATR_12_v31_DE.pdf](./ATR_12_v31_DE.pdf) — 43 pages,
  section-by-section translation, assembled from [`paper/de/`](./paper/de).
- **French (complete):** [ATR_12_v31_FR.pdf](./ATR_12_v31_FR.pdf) — 41 pages,
  section-by-section translation, assembled from [`paper/fr/`](./paper/fr).
- **Spanish (complete):** [ATR_12_v31_ES.pdf](./ATR_12_v31_ES.pdf) — 42 pages,
  section-by-section translation, assembled from [`paper/es/`](./paper/es).
- **Italian (complete):** [ATR_12_v31_IT.pdf](./ATR_12_v31_IT.pdf) — 42 pages,
  section-by-section translation, assembled from [`paper/it/`](./paper/it).

Every edition is built from the same twelve-part structure by
`paper/build_lang.py`, so a correction to the Romanian master can be carried
across one part at a time.

- The previous versions (v3, v7, v30) are **not published**. They remain on the
  author's disk for reference, but are untracked and listed in `.gitignore`.

Version 31 applies the audit: ten numerical statements of v30 are corrected,
two are downgraded to untestable conjectures, and a structural tension with
sub-millimetre gravity tests is stated openly (Section 5.3). See
[PUBLISHING.md](./PUBLISHING.md) for how to rebuild the PDFs and publish.

> **Epistemic status.** The theory is speculative and untested. The code does
> not provide evidence for it; it provides (1) a reproducible model, (2) concrete
> numerical predictions, and (3) a list of inconsistencies to fix before the
> final version. Where the model makes a choice (for example the EEG coupling),
> the choice is declared in the docstring, not presented as experimental data.

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Tested with Python 3.10, numpy 2.2, scipy 1.15, matplotlib 3.10.

## Running

```bash
python run_atr12.py                 # full run (~8 s)
python run_atr12.py --quick         # reduced variant
python run_atr12.py --no-figures    # tables and report only
python -m src.simulation --seed 7   # alternative entry point
python check.py                     # end-to-end PASS/FAIL verification
pytest -q                           # tests
```

Results are written to [`results/`](./results) (Markdown report, JSON, CSV) and
figures to [`figures/`](./figures). Both directories are fully regenerated on
every run; `results/` is git-ignored, while `figures/` may be committed (the
figures are useful directly in the paper).

> **Note for running directly from the NAS share (W:).** If the working
> directory is on the network share, writes to `__pycache__` can be blocked by
> antivirus/indexer and the Python process is terminated without a message.
> Run with `set PYTHONDONTWRITEBYTECODE=1` (Windows) or
> `export PYTHONDONTWRITEBYTECODE=1` (Linux/macOS), or copy the project locally.

## What it computes

Each figure is written twice: a vector `.pdf` for the paper (used by the LaTeX
source) and a `.png` at 200 dpi for the README and the web.

| Module | Content | Relations |
|---|---|---|
| [`src/config.py`](./src/config.py) | parameters, constants, paper tables | m_1, rho_DM, acoustic bands |
| [`src/akashic_field.py`](./src/akashic_field.py) | KK modes, A(t), equation of state | `A = Σ A_n cos(ω_n t + φ_n)`, `V = -μ²A²/2 + λA⁴/4` |
| [`src/temporal_modes.py`](./src/temporal_modes.py) | KK and tachyonic spectrum, clocks | `m_n² = n²/R² - μ_A²`, `τ = ħ/Γ` |
| [`src/fermions.py`](./src/fermions.py) | dark-matter flux, Yukawa, Debye | `n = ρ/m`, `Φ = nv`, `g_A ~ (M_4/M_12)^5` |
| [`src/consciousness.py`](./src/consciousness.py) | C(t) field, Φ as integrated information | `dC/dt = αC(1-C/C_max) + βη(t)` |
| [`src/empathy.py`](./src/empathy.py) | frequency coupling, hyperscanning, statistical power | `E = 1/(1+(Δω/Γ)²)` |
| [`src/word_excitation.py`](./src/word_excitation.py) | word–field coupling | `ω_n = (1/R)√(n²+μ²R²)` |
| [`src/verification.py`](./src/verification.py) | numerical audit of the paper | 17 checks with verdicts |
| [`src/simulation.py`](./src/simulation.py) | orchestrator, figures, report | — |

## Results (seed = 12)

**Spectrum.** With `1/R = 1e-5 eV`: m_n = 1, 2, 3, 4, 5, 6 × 10⁻⁵ eV, i.e.
2.42, 4.84, 7.25 GHz. Mode n = 1 is tachyonic only if μ_A > 1/R.

**Φ — cortex vs cerebellum.** Over 4 random networks per size, the recurrent
network has 2–20× more Φ than the feedforward one at equal unit count
(n = 6: 0.259 ± 0.049 vs 0.045 ± 0.015). The proxy is a minimum cut of the
Glauber dynamics, not exact IIT 3.0 Φ.

**Hyperscanning.** The model gives r ≈ 0.27 for high-empathy pairs and
r ≈ 0.09 for low-empathy pairs. The power analysis shows that **the paper's
literal criterion (r > 0.1 per pair, p < 0.05 Bonferroni) is underpowered**:
6 s of EEG at ±5 Hz gives only ~60 independent samples, and r = 0.1 would
require ~91 s per pair. The group test (high vs low empathy) reaches 80%
power with ~30 pairs.

**The word.** KK modes sit at GHz; 150–800 Hz bands would require
`1/R ≈ 1.2e-12 eV`, about 7 orders of magnitude away.

## Numerical audit of the paper

`src/verification.py` recomputes the claims of v30.md: **5 OK, 10
inconsistent, 2 untestable**. The most important:

| Check | Claim in v30 | Recomputed |
|---|---|---|
| `kk-mass-ratio` | masses 1e-5, 1e-4, 1e-3 eV | m_n = n/R gives ratios 2 and 3, not 10 and 100 |
| `compactification-radius` | 1e-5 eV KK mode | R ≈ 2 cm, excluded by sub-mm gravity tests (R < 38 µm) |
| `resonance-masses` | 16 / 36.8 / 57.6 GHz | 16 GHz ↔ 6.6e-5 eV; 1e-5 eV = 2.42 GHz |
| `dm-number-density` | 3000 particles/m³ | 3e19 /m³ for 1e-5 eV (3000/m³ ↔ ~100 GeV) |
| `body-crossing-rate` | 1e8 vs 6e8 particles/s | both far below 6e24 /s |
| `yukawa-coupling` | g_A can rise to 1e-3 | would need an overlap factor of 1e77 and give a 1.6 ms lifetime |
| `yukawa-fifth-force` | g_eff = 1e-3 is allowed | α ≈ 1.7e32, excluded by fifth-force tests; g < 2e-20 |
| `compton-wavelengths` | axion 1e19 m, ratio 1e28 | 0.124 m, ratio 5e10 |
| `acoustic-scale` | acoustic modes 150–800 Hz | modes sit at GHz (7 orders of magnitude apart) |
| `equation-of-state` | A ≫ μ_A → w = 1 | w = 1/3 (quartic); w = 1 is kination |

Full details, with the paper section for every verdict, are in
[`results/atr12_report.md`](./results/atr12_report.md).

## Structure

```
ATR-12/
├── run_atr12.py            # launcher
├── check.py                # end-to-end verification (PASS/FAIL)
├── conftest.py             # pytest: adds the project root to sys.path
├── requirements.txt
├── CITATION.cff
├── LICENSE                 # MIT
├── PUBLISHING.md           # run, verify, publish
├── proiect_ATR-12.MD       # project specification
├── .github/workflows/ci.yml# CI: pytest + check.py on every push
├── docs/                   # supporting notes
├── paper/                  # v31 sources (RO, EN) + build_paper.py
├── src/                    # simulation package
├── tests/                  # 31 tests
├── figures/                # generated on every run
├── results/                # generated, git-ignored
├── ATR_12_v31_RO.tex       # full Romanian LaTeX source (Overleaf)
├── ATR_12_v31_*.pdf        # current papers (only version published)
```

## Limitations

- Φ is a tractable proxy, not full IIT 3.0 (see the module docstring).
- The EEG coupling (`eeg_field_gain`) and `g_sound` are free parameters; the
  statistical-power results depend on the assumed effect size.
- The model contains no gravity, no cosmology and no derivation of the KK
  spectrum from 12D geometry; it uses the paper's relations as axioms.

## Citation

See [CITATION.cff](./CITATION.cff). Paper: Ofiteru, D. (2026),
*Akashic Resonance Theory in 12 Dimensions*, version 30.0, speculative preprint.
