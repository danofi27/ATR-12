# Project specification — ART-12D simulation code

**Status:** active · **Version:** 1.0.0 · **Owner:** Daniel Ofiteru · **Target:** preprint (GitHub + Zenodo)

---

## 1. Purpose

Provide a reproducible, testable implementation of the relations in the
ART-12D v30 paper, so that

1. every quantitative statement in the paper can be recomputed,
2. the proposed experiments can be designed with a known statistical power,
3. the inconsistencies between the text and the mathematics are visible and
   traceable before publication.

The code is a *support artefact* for the paper, not evidence for the theory.

## 2. Scope

**In scope**

- Kaluza-Klein spectrum and its projection to 4D (`m_n = n/R`, tachyonic branch).
- Scalar-field dynamics: mode superposition, energy density, equation of state.
- Dark-matter number density, flux through a body, Yukawa and fifth-force bounds.
- Consciousness field `C(t)` and an integrated-information proxy `Φ`.
- Cortex (recurrent) vs cerebellum (feedforward) comparison at equal unit count.
- EEG hyperscanning model, surrogate testing and power analysis.
- Word–field acoustic coupling and its scale audit.
- Automated numerical audit of the paper's claims.

**Out of scope**

- Derivation of the KK spectrum from 12D geometry (taken as an axiom).
- General relativity, cosmology, structure formation.
- Any claim of experimental evidence; all data are synthetic.
- Medical or therapeutic claims.

## 3. Repository layout

```
ATR-12/
├── run_atr12.py            # CLI launcher (python run_atr12.py)
├── conftest.py             # makes the project root importable under pytest
├── requirements.txt        # numpy, scipy, matplotlib, pytest
├── CITATION.cff
├── README.md
├── proiect_ATR-12.MD       # this file
├── src/
│   ├── __init__.py
│   ├── config.py           # dataclass of parameters + paper tables
│   ├── akashic_field.py    # KK modes, A(t), equation of state
│   ├── temporal_modes.py   # KK/tachyon spectra, clocks, lifetimes
│   ├── fermions.py         # flux, Yukawa, Debye, Compton/de Broglie
│   ├── consciousness.py    # Φ proxy, Glauber dynamics, C(t)
│   ├── empathy.py          # frequency coupling, hyperscanning, power
│   ├── word_excitation.py  # word-field coupling
│   ├── verification.py     # numeric audit of v30.md
│   └── simulation.py       # orchestrator, figures, report
├── tests/
│   └── test_atr12.py       # 31 tests
├── figures/                # generated
└── results/                # generated, git-ignored
```

## 4. Data flow

```
config ─┬─ temporal_modes ── spectrum ───────────────┐
        ├─ akashic_field  ── modes, w(delta) ───────┤
        ├─ fermions       ── flux, couplings ───────┤
        ├─ consciousness  ── Phi table, C(t) ───────┼─> simulation.run()
        ├─ empathy        ── pairs, power ──────────┤      ├─ results/*.json|csv
        ├─ word_excitation── excitation table ──────┤      ├─ results/atr12_report.md
        └─ verification   ── 16 checks ─────────────┘      └─ figures/*.png
```

Everything is seeded (`cfg.seed`, default 12). Two runs with the same
configuration produce identical numbers.

## 5. Model assumptions and free parameters

| Parameter | Default | Origin | Status |
|---|---|---|---|
| `inv_r_ev` (1/R) | 1e-5 eV | paper: m₁ = 1e-5 eV | derived from the paper's axion mass |
| `mu_a_ev` | 0 | not given in the paper | **free**; tachyon demo uses 1.5e-5 eV |
| `lambda_a` | 0.1 | not given | free |
| `m4_gev`, `m12_gev` | 1e3, 1e19 GeV | paper (Yukawa estimate) | paper values |
| `yukawa_overlap` | 1 | paper mentions overlap factors | free, bounded to ≤ 1 |
| `rho_dm_gev_cm3` | 0.3 | Read (2014) | literature |
| `alpha_c`, `beta_noise` | 0.15 s⁻¹, 0.02 | not given | free (phenomenological) |
| `eeg_field_gain` | 0.55 | model choice | **free**, sets the effect size |
| `empathy_gamma_hz` | 2 Hz | not given | free |
| `g_sound` | 1e-3 | not given | **free**, prediction 67 has no numbers without it |

Free parameters are declared in docstrings. No result is reported as data.

## 6. Validation

| Level | Command | Criterion |
|---|---|---|
| Unit | `pytest -q` | 31 tests pass |
| Analytic limits | included in tests | w(δ→0)=0, w(δ→∞)=1/3, w(δ=0)=−1; Φ=0 for disconnected networks; E(Δω=0)=1 |
| End-to-end | `python run_atr12.py --quick` | report + JSON + CSVs written |
| Audit stability | `python run_atr12.py` | verdict counts reproduced (5 OK / 10 INCONSISTENT / 2 UNTESTABLE) |
| Timing | full run | < 10 s on the NAS share (see note in README) |

## 7. Audit findings (summary)

Nine statements in v30.md contradict their own definitions; two are untestable
as written. They are listed with the exact section and recomputed value in
`results/atr12_report.md`. The three that affect the theory's core:

1. **KK masses** — the table (1e-5, 1e-4, 1e-3 eV) is not compatible with
   `m_n = n/R` (which gives 1, 2, 3 × 1e-5 eV).
2. **Compactification radius** — `m_1 = 1e-5 eV` implies `R ≈ 2 cm`, excluded by
   sub-millimetre tests of Newton's law (`R < 38 µm`, i.e. `m_1 > 5e-3 eV`).
3. **Coupling** — `g_eff = 1e-3` is excluded by fifth-force tests (α ≈ 1.7e32)
   and would make the mode decay in 1.6 ms. `g_A ≈ 1e-80` is the consistent value.
4. **Acoustic scale** — 150–800 Hz modes require `1/R ≈ 1e-12 eV`, seven orders
   of magnitude away from the dark-matter scale.

## 8. Roadmap

| Priority | Task | Output |
|---|---|---|
| P0 | Fix the 9 numeric inconsistencies in v30 | v31 draft |
| P0 | Redesign Prediction 1 with the power analysis (group test, ≥ 30 pairs or ≥ 90 s/pair) | pre-registered protocol |
| P1 | Add a "Numerical results" section to the paper using this report | paper section |
| P1 | Publish code on GitHub, archive a release on Zenodo (DOI) | citable artefact |
| P2 | Second compactification scale (or drop the word mechanism) | decision note |
| P2 | Replace the Φ proxy with IIT 3.0 on small networks | optional module |

## 9. Decisions log

| Date | Decision | Rationale |
|---|---|---|
| 2026-10-17 | Python 3.10 + numpy/scipy/matplotlib only | runs on any machine without a heavy stack |
| 2026-10-17 | `src/` flat modules, no packaging metadata | matches the structure proposed in `exp.md` |
| 2026-10-17 | Φ implemented as minimum-cut KL on Glauber dynamics | tractable; exact IIT 3.0 is intractable at this scale |
| 2026-10-17 | Fisher z for the pair test, surrogate shifts as a cross-check | surrogates cannot resolve p < 1/N |
| 2026-10-17 | Equation of state computed by phase-space quadrature | time-domain averaging has a phase bias near the separatrix |
| 2026-10-17 | English for code and documentation | target is an international preprint |
| 2026-10-17 | Results and figures regenerated, not versioned (`results/` ignored) | avoids stale artefacts |

## 10. Open items

- [x] License file (MIT) committed.
- [x] Corrected paper v31 in RO, EN, DE and FR, with figures, in `paper/`.
- [x] `check.py` verification harness and `PUBLISHING.md`.
- [ ] Translations ES, IT, RU, JP, CN rebuilt from the v31 master.
- [ ] Language of the final paper (v31 exists in RO and EN).
- [ ] Whether the 313 predictions are listed in full or the claim is reformulated.
- [ ] Remote repository and Zenodo DOI.
