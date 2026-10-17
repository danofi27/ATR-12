# AKASHIC RESONANCE THEORY IN 12 DIMENSIONS

## Dark matter as the quantum substrate of consciousness (ART-12D)

**Daniel Ofiteru** — Independent Researcher

Version 31.0 — October 2026 — Speculative preprint

<div class="pagebreak"></div>

## Abstract

This paper proposes a framework in which consciousness is not produced by the brain but received by it. What would be received is a scalar field associated with dark matter, existing in twelve dimensions and projecting into four.

Compared with version 30, this version applies a systematic numerical audit. Ten quantitative statements have been corrected and two have been explicitly downgraded to untestable conjectures. The main changes are: the Kaluza–Klein spectrum is equidistant (m_n = n/R), the resonance frequencies become 2.42, 4.84 and 7.25 GHz, the dark-matter flux through the human body is of order 10^24 particles per second, the effective coupling cannot exceed 10^-20, and the equation of state has three distinct regimes (0, 1/3, −1).

The paper also records a structural tension that the previous version did not signal: for the fundamental mode to have 10^-5 eV, the compactification radius would have to be of order 2 cm, which is excluded by sub-millimetre tests of Newton's law. This tension is treated openly in Section 5.3 and Section 14.

There is no experimental evidence. There is a formalisation, a central test feasible with 50,000 dollars, and a statistical protocol with the correct sample size.

<div class="pagebreak"></div>

## Reader's guide

- **Physicist:** Part II (Sections 5–8) and Section 14 (numerical audit). There you can see what is derived, what is postulated, and what conflicts with data.
- **Neurobiologist:** Section 8 (cortex–cerebellum architecture) and Section 9 (EEG protocol).
- **Philosopher:** Section 3 and Appendix A.
- **Curious reader:** Section 9.3 (how many pairs and how long to measure) and Section 12 (what would refute the theory).

<div class="pagebreak"></div>

# Part I — Foundations

## 1. Introduction

### 1.1 The problem that does not go away

Why do you feel pain? Nociceptors send signals to the thalamus, the cortex processes them, endorphins are released. All of this is a functional description: it tells us what the brain does, not why experience exists. A computer can recognise an image and play chess, but it feels nothing. This is the hard problem of consciousness, formulated by Chalmers (1995).

In 1998, Christof Koch bet Chalmers that a neural correlate of consciousness would be identified within 25 years. In 2023 he acknowledged that the bet was lost.

### 1.2 Dark matter: the exact numbers

The Planck mission (2018) gives the composition of the universe: 4.9% ordinary matter, 26.8% dark matter, 68.3% dark energy. Dark matter neither emits nor absorbs light and crosses ordinary matter without interacting.

The local density is about 0.3 GeV/cm³ (Read, 2014). Number density and flux depend on the mass:

$$n = \frac{\rho}{m}, \qquad \Phi = n\,v$$

For a 10^-5 eV mode and v = 300 km/s this gives n = 3.0×10^19 m^-3 and Φ = 9.0×10^24 m^-2 s^-1. For a body of 0.7 m², the crossing rate is about 6×10^24 particles per second. (Version 30 stated 3000 m^-3 and 6×10^8 s^-1; those values correspond to a WIMP of about 100 GeV, not to a 10^-5 eV mode. See Section 14.)

![Dark-matter flux as a function of mass. The red point marks the claim of version 30; the curve is the correct value for ρ = 0.3 GeV/cm³ and v = 300 km/s.](../../figures/fig07_flux.png)

*Figure 1. Dark-matter flux through the human body. At 10^-5 eV the two differ by 16 orders of magnitude.*

The Bonvin et al. (2025) constraint shows that dark matter falls into gravitational wells like ordinary matter; any additional force cannot exceed 7% of gravity.

### 1.3 What ART-12D is

The universe has more dimensions than the four we perceive. The extra dimensions are compact. Dark matter exists in all twelve; projected into 4D it appears as a field filling the universe. The brain would receive this field.

The name comes from *Akashic* (universal information field), *Resonance* (the interaction is a resonance), *Theory* and *12D*.

### 1.4 Why twelve dimensions

Kaluza–Klein (5 dimensions, 1919–1926), superstrings (10), M-theory (11, Witten, 1995), F-theory (12, Vafa, 1996). Twelve is the maximum number of dimensions in which string theory is mathematically consistent. The choice is inherited, not derived in this paper.

## 2. Methodology

The paper was built in four steps: formulating the hypothesis, formalising it with existing tools (Kaluza–Klein, F-theory, field theory, IIT), deriving predictions, and designing experiments.

Four criteria were used: internal coherence, falsifiability, convergence with established physics, and honesty. The last one forced the numerical audit in Section 14, which invalidated ten statements of the previous version.

**Declared limitations:** no experimental evidence, no peer review, no academic affiliation, no funding.

## 3. Theoretical background

### 3.1 The hard problem

Chalmers (1995): no combination of physical quantities logically entails the existence of subjective experience. Every physical description tells what the brain does, not what it is like to be the brain.

### 3.2 Russellian monism

Russell (1927) observes that physics describes the structural properties of matter — mass, charge, spin, position — but not the intrinsic nature of what carries them. If the intrinsic properties are proto-experiential, the hard problem becomes a problem of access, not of emergence.

### 3.3 Integrated information theory

Tononi (2004) proposes a measure of integration:

$$\Phi = \min_{P}\; D_{KL}\left( p(X_{t+1}\mid X_t) \,\|\, \prod_i p(x_i^{t+1}\mid x_i^{t}) \right)$$

Appendix B contains the values computed for small networks, together with the approximation used (see Section 8.2).

### 3.4 Orchestrated objective reduction

Penrose (1996) proposes spontaneous gravitational collapse with time constant τ ≈ ħ/E_G. For cortical microtubules, τ ≈ 25 ms, i.e. 40 Hz — the frequency of gamma oscillations. The correspondence is numerical, not a derivation.

### 3.5 Kaluza–Klein

Kaluza (1919) unified gravity with electromagnetism through a fifth dimension; Einstein worked on the idea between 1938 and 1943. The extended metric is:

$$dS^2 = g_{\mu\nu}\,dx^{\mu}dx^{\nu} + \varphi^2\left(dx^5 + A_{\mu}dx^{\mu}\right)^2$$

## 4. The three postulates

1. Dark matter is a fundamental scalar field with Kaluza–Klein modes.
2. The brain is a geometric receiver: the architecture of the network, not the number of neurons, determines its reception capacity.
3. The coupling between field and fermions is of Yukawa type, with the constant estimated in Section 7.

These postulates are not demonstrated; they are the frame in which the predictions are made.

<div class="pagebreak"></div>

# Part II — Mathematical formulation

## 5. Geometry and the Kaluza–Klein spectrum

### 5.1 The total manifold

$$M_{12} = M_4 \times K_8, \qquad ds^2 = g_{MN}\,dx^{M}dx^{N}$$

The akashic field decomposes into modes:

$$A(x,y) = \sum_n A_n(x)\,Y_n(y), \qquad m_n^2 = \frac{n^2}{R^2}$$

### 5.2 The numerical spectrum

The scale is fixed by the mass of the fundamental mode, m₁ = 10^-5 eV, the value used throughout the paper. Then 1/R = 10^-5 eV and

| n | mass (eV) | frequency (GHz) | λ_C (m) |
|---|---|---|---|
| 1 | 1.00×10^-5 | 2.42 | 0.124 |
| 2 | 2.00×10^-5 | 4.84 | 0.062 |
| 3 | 3.00×10^-5 | 7.25 | 0.041 |
| 4 | 4.00×10^-5 | 9.67 | 0.031 |

The spectrum is **equidistant**. This is the distinctive signature of the theory: a test that measures two lines at 2.42 and 4.84 GHz confirms or refutes the structure, independently of any other prediction.

![Kaluza–Klein spectrum: the model m_n = n/R compared with the version 30 table and with the masses implied by 16/36.8/57.6 GHz.](../../figures/fig01_kk_spectrum.png)

*Figure 2. The KK spectrum. The version 30 table (orange) and the declared resonance frequencies (green) are compatible neither with each other nor with m_n = n/R (blue).*

### 5.3 The compactification radius

From m₁ = 1/R it follows that R = 1.97×10^-2 m, about 2 cm. Sub-millimetre tests of Newton's law constrain an extra dimension to R < 38 µm, which implies m₁ > 5×10^-3 eV.

This is a structural tension, not an arithmetic error: identifying the dark-matter field with a KK mode of the same geometry is incompatible with the data at the chosen mass scale. Two honest exits remain:

- **Option A:** the akashic field is not a KK mode; the equidistant spectrum follows from another structure, and the frequency predictions are recomputed.
- **Option B:** the fundamental mode mass is m₁ > 5×10^-3 eV, and the "dark matter" of the paper is not the fundamental mode but an excited one.

The paper does not choose between them. The predictions of Part III are formulated so that they hold in both cases, with the frequencies treated as a parameter.

## 6. The akashic field

### 6.1 The Lagrangian

$$\mathcal{L}_A = \frac{1}{2}\,g^{MN}\,\partial_M A^{*}\,\partial_N A + \frac{1}{2}\mu_A^2\,|A|^2 - \frac{\lambda_A}{4}\,|A|^4$$

The potential has two minima at A = ±μ_A/√λ_A and a local maximum at A = 0. Modes with n < μ_A R have m_n² < 0 and are tachyonic.

### 6.2 The equation of state

For an oscillating field, the time average of the pressure-to-density ratio is computed exactly on the orbit (phase-space quadrature, Appendix C). The results are:

| regime | condition | w |
|---|---|---|
| small oscillation about the minimum | δ ≪ 1 | 0 (matter) |
| quartic-dominated oscillation | δ ≫ 1 | 1/3 (radiation) |
| field frozen at the minimum | δ = 0 | −1 (cosmological constant) |

Here δ = A_osc/A_min. Version 30 stated that the large-amplitude regime gives w = 1; the correct value is 1/3. w = 1 corresponds to kinetic domination (kination), which quartic oscillations do not reach.

![Left: dynamics of the consciousness field with noise. Right: equation of state w(δ), with the separatrix at δ = √2 − 1.](../../figures/fig02_field_dynamics.png)

*Figure 3. Dynamics of C(t) and the equation of state of the akashic field.*

### 6.3 The acoustic spectrum

$$\omega_n = \frac{1}{R}\sqrt{n^2 + \mu_A^2 R^2}$$

For the dark-matter mass scale these frequencies are of order GHz. The consequence matters for Section 11: an acoustic mechanism at 150–800 Hz would require a different compactification scale, by about seven orders of magnitude.

## 7. Coupling to fermions

### 7.1 Estimating the coupling

$$g_A \sim \left(\frac{M_4}{M_{12}}\right)^5 = \left(\frac{10^3}{10^{19}}\right)^5 = 10^{-80}$$

The value is extremely small. Version 30 suggested that overlap factors could raise the effective value to 10^-3; that would require a factor of 10^77, impossible for normalised wavefunctions (overlap is at most 1).

### 7.2 Debye screening

In tissue, the Debye length is

$$\lambda_D = \sqrt{\frac{\varepsilon_0 \varepsilon_r k_B T}{2 N_A e^2 I}} \approx 0.81\ \mathrm{nm}$$

for T = 310 K and I = 0.15 mol/L. Screening suppresses the coupling at long distances but does not cancel it.

### 7.3 The fifth-force constraint

If the field couples to nucleons via Yukawa, the strength relative to gravity is

$$\alpha = \frac{g^2 \hbar c}{G m_p^2} = g^2 \times 1.69\times10^{38}$$

For g = 10^-3 this gives α ≈ 1.7×10^32, excluded by laboratory tests by about 35 orders of magnitude. The 7% constraint quoted in the introduction implies g < 2×10^-20. The derived value, g_A ≈ 10^-80, is the only one compatible with the data.

This conclusion has a cost: the coupling is so weak that no direct interaction with matter will be detectable in the near future.

## 8. The neural receiver

### 8.1 Cortex versus cerebellum

The cerebellum has about 69 billion neurons (81% of the total) but a predominantly feedforward architecture. The cortex has about 16 billion, with a recurrent architecture. Postulate 2 states that the geometry of the network, not the number of neurons, determines reception.

### 8.2 Measuring Φ

To make the claim numerically testable, a tractable proxy of Φ was implemented: the KL divergence between the full model and the model in which links across a cut are removed, minimised over all bipartitions, on Glauber dynamics. It is not exact IIT 3.0 Φ; it is an approximation with the same ordinal signature.

The result, averaged over four random networks per size:

| units | Φ cortex | Φ cerebellum | ratio |
|---|---|---|---|
| 4 | 0.243 ± 0.063 | 0.012 ± 0.014 | 20.6 |
| 6 | 0.259 ± 0.049 | 0.045 ± 0.015 | 5.8 |
| 8 | 0.245 ± 0.042 | 0.036 ± 0.030 | 6.9 |

The recurrent network integrates 2–20 times more than the feedforward one at equal unit count. The qualitative conclusion of version 30 is therefore supported numerically, within the limits of the proxy.

![Φ for recurrent and feedforward networks, with standard deviation over four random networks.](../../figures/fig03_phi_architecture.png)

*Figure 4. Integrated information for the two architectures.*

### 8.3 The heart as a modulator

The heart has its own electrical system (the sinoatrial node) and generates electromagnetic fields of much larger amplitude than cortical ones, with a mechanical power of 1–1.3 W. The proposed model is

$$C_{\mathrm{coherent}} = C_0\left(1 + \beta\,HRV\right)$$

The relation is phenomenological. HRV correlates with the stability of access rather than with the level of access — a prediction that can be tested with PCI during guided respiratory variation.

### 8.4 Dynamics of the consciousness field

$$dC/dt = \alpha\,C\left(1 - C/C_{\max}\right) + \beta\,\eta(t)$$

The equation is logistic with noise; it is an **axiom of the model**, not a consequence of the Lagrangian. With α = 0.15 s^-1, the 95% relaxation time is 50 s, the value used in the simulations.

<div class="pagebreak"></div>

# Part III — Predictions and experiments

## 9. Prediction 1: non-local EEG correlations

### 9.1 The model

Empathy is formalised as frequency resonance:

$$\mathrm{Empathy}(A,B) = \frac{1}{1 + \left(\omega_A - \omega_B\right)^2/\Gamma^2}$$

Two brains with close frequencies would be coupled more strongly to the common field. In the simulation each brain produces narrowband noise in the gamma range, and the common component has an amplitude proportional to empathy.

![Left: frequency coupling for three values of Γ. Right: in-band correlation for the simulated pairs.](../../figures/fig04_empathy.png)

*Figure 5. Frequency coupling and the result of the hyperscanning simulation (20 pairs, 6 s, 250 Hz).*

### 9.2 The version 30 criterion and its problem

The criterion was: correlation r > 0.1 at 40 Hz, with p < 0.05 after Bonferroni correction. For a 6 s signal filtered at ±5 Hz, the number of independent samples is about 2·B·T = 60. The Fisher test shows that, for r = 0.1 and α = 0.0025 (Bonferroni for 20 pairs), about 91 seconds of recording are needed **per pair**. At 6 s the criterion cannot be met even if the effect exists.

![Left: duration needed for significance as a function of r. Right: power of the group test.](../../figures/fig05_power.png)

*Figure 6. Power analysis. The red line marks the current protocol duration (6 s); r = 0.1 would need ~91 s.*

### 9.3 The proposed protocol

| Element | Value | Rationale |
|---|---|---|
| Design | group test: high vs low empathy | far more powerful than the per-pair test |
| Pairs | ≥ 30 (15 + 15) | 80% power for r = 0.3 at 6 s |
| Duration | 6 s per epoch, ≥ 20 epochs per pair | increases the effective sample size |
| Band | 35–45 Hz, fs ≥ 250 Hz | low gamma, robust to muscle artefacts |
| Primary statistic | pooled Fisher z, two-group test | α = 0.05 two-sided |
| Secondary | Hilbert-envelope correlation | phase-independent |
| Control 1 | shuffled pairs (A from session 1 with B from session 2) | rules out pipeline artefacts |
| Control 2 | Faraday cage, separate rooms | rules out electromagnetic coupling |
| Control 3 | randomised order, analyst blind to group | rules out analysis bias |

With this design a negative result is informative: it excludes r > 0.3 at 80% power.

### 9.4 What a positive result would mean

An effect at 40 Hz, absent in the control pairs and absent in low-empathy pairs, would be compatible with coupling through a field. It would not demonstrate dark matter: it would eliminate electromagnetic explanations and demand a mechanism analysis.

## 10. Other predictions

| # | Prediction | Value in v31 | Cost | Falsifiable |
|---|---|---|---|---|
| 2 | cardiac coherence (HRV–PCI) | positive correlation, not level dependence | 100k $ | yes |
| 3 | word effect on DNA | no numerical value until g_sound is fixed | 200k $ | not yet |
| 4 | equidistant KK ladder | 2.42 / 4.84 / 7.25 GHz | 500k $ | yes |
| 5 | akashic Casimir effect | deviation at 10^-11 m | 500k $ | yes |
| 6 | microtubule resonances | 2.42 / 4.84 / 7.25 GHz (not 16/36.8/57.6) | 300k $ | yes |
| 7 | three dark-matter forms | 1, 2, 3 ×10^-5 eV | 10M $ | yes |

Predictions 4 and 6 are the most valuable: they have precise numerical values, and a negative result refutes the KK identification.

## 11. Speculative extensions (separate from the body of the theory)

The following ideas from version 30 are kept as research directions, explicitly marked as untestable at the present stage.

### 11.1 The word as excitation

The hypothesis is that dark matter has an acoustic manifestation that can be excited by sound waves. The scale problem, however, is decisive: KK modes are at GHz, while acoustic bands at 150–800 Hz would require 1/R ≈ 1.24×10^-12 eV, seven orders of magnitude below the mass scale. Until a second compactification scale is introduced, the prediction has no numerical content.

![Left: relative word–field coupling. Right: scale separation between KK modes and acoustic bands.](../../figures/fig06_word_excitation.png)

*Figure 7. Scale separation between KK modes (~GHz) and sound (~Hz).*

### 11.2 Hyper-civilisations, non-carbon life, the multiverse

These sections remain philosophical conjectures. They are not derived from the equations of the paper and make no numerical predictions. The reader is asked to treat them as such; they are placed in Appendix A, not in the body of the theory.

## 12. Falsifiability statement

The theory is refuted if any of the following conditions holds:

1. **The central test:** hyperscanning with the design of 9.3 shows no difference between high- and low-empathy pairs (r < 0.1, p > 0.05).
2. **The KK spectrum:** two lines fail to appear at 2.42 and 4.84 GHz in any resonance experiment (microtubules, cavities, clusters).
3. **The Casimir effect:** no deviation from the standard formula at 10^-11 m.
4. **The gravitational constraint:** if R < 38 µm is confirmed, the KK identification with m₁ = 10^-5 eV is excluded and the theory must be reformulated (Option A or B in 5.3).

If any of these tests fails, the theory is revised or abandoned. That is the only condition under which a speculative theory deserves attention.

<div class="pagebreak"></div>

# Part IV — Discussion

## 13. Strengths and limitations

**Strengths.** It is the first framework that explicitly links consciousness to dark matter and makes a precise numerical prediction about the spectrum. The coupling is derived, not chosen. The central prediction is feasible on a modest budget. The methodology includes an audit that invalidates its own statements.

**Limitations.** There is no experimental evidence. The coupling mechanism is estimated with approximations. Akashic frequencies are technologically inaccessible today. The combination problem remains open. There is a structural tension with gravitational tests (5.3). The speculative extensions are not testable.

## 14. Numerical audit

Every quantitative statement was recomputed with the code of Appendix C. The result: 5 correct, 10 inconsistent, 2 untestable.

| # | Statement (v30) | Recomputed | Verdict |
|---|---|---|---|
| 1 | masses 1e-5 / 1e-4 / 1e-3 eV | m_n = n/R gives ratios 2 and 3 | inconsistent |
| 2 | 1e-5 eV KK mode | R ≈ 2 cm; the bound is 38 µm | inconsistent |
| 3 | resonances 16 / 36.8 / 57.6 GHz | 2.42 / 4.84 / 7.25 GHz | inconsistent |
| 4 | 3000 particles/m³ | 3.0×10^19 m^-3 | inconsistent |
| 5 | 10^8 or 6×10^8 particles/s | 6×10^24 s^-1 | inconsistent |
| 6 | g_eff can reach 1e-3 | needs overlap 1e77; lifetime 1.6 ms | inconsistent |
| 7 | g_eff = 1e-3 is allowed | α ≈ 1.7×10^32, excluded | inconsistent |
| 8 | axion 1e19 m, ratio 1e28 | 0.124 m, ratio 5×10^10 | inconsistent |
| 9 | acoustic modes 150–800 Hz | modes sit at GHz | inconsistent |
| 10 | A ≫ μ_A gives w = 1 | w = 1/3 | inconsistent |

Correct checks: Planck composition, τ = 25 ms ↔ 40 Hz, cerebellum share (81%), the empathy formula, mode stability with g_A ≈ 10^-80. Untestable: the count of 313 predictions and the Φ hierarchy.

The full audit, with the exact section and the recomputed value for every verdict, is generated automatically in `results/atr12_report.md`.

## 15. What would change the conclusion

One result would change everything: a reproducible 40 Hz correlation between electromagnetically isolated brains, with adequate statistical power. The second would be the detection of a resonance at 2.42 GHz in isolated microtubules. The third would be a Casimir deviation at 10^-11 m.

In their absence, the theory remains a coherent conjecture with clear predictions.

# Part V — Conclusions

ART-12D starts from a simple intuition: the brain does not produce consciousness, it receives it. The formalisation leads to an equidistant mode spectrum, a derived coupling of order 10^-80, and a test feasible with 50,000 dollars.

This version of the paper takes a step that version 30 did not: it checks its own numbers. Ten statements fell, two were downgraded, and a structural tension was brought into the open. What remains is less spectacular but more solid: a bold hypothesis, with precise numerical predictions and a protocol that can produce a publishable negative result.

<div class="pagebreak"></div>

# Appendix A — Philosophical speculations

This appendix contains speculations that are **not derived** from the equations of the paper. They are included for transparency, not as support for the theory.

**Death as transition.** If consciousness is received, death dissolves the receiver, not the content. The statement is metaphysical; no protocol tests it.

**The split soul.** The tripartite model (body–soul–spirit, analogous to states of matter) is a metaphor, not a formalisation.

**Hyper-civilisations.** Defined as stable structures in the field, with minimal intervention. Prediction 85 (absence of technological signatures) is compatible with any observation, hence not falsifiable.

**God.** Four hypotheses are stated in version 30; none has testable consequences. This appendix takes no position.

<div class="pagebreak"></div>

# Appendix B — Constants, symbols, numerical results

## B.1 Constants

| Symbol | Value | Unit |
|---|---|---|
| h | 4.135667696×10^-15 | eV·s |
| ħc | 1.973269804×10^-7 | eV·m |
| hc | 1.239841984×10^-6 | eV·m |
| m_e | 510998.95 | eV |
| ρ_DM | 0.3 | GeV/cm³ |
| v_DM | 300 | km/s |

## B.2 Statistical power (6 s, ±5 Hz, Bonferroni α = 0.0025)

| true r | required duration (s) |
|---|---|
| 0.1 | 91.1 |
| 0.2 | 22.5 |
| 0.3 | 9.8 |
| 0.4 | 5.4 |
| 0.5 | 3.3 |

| pairs | power r = 0.3 | power r = 0.2 | power r = 0.1 |
|---|---|---|---|
| 10 | 1.00 | 0.93 | 0.40 |
| 20 | 1.00 | 1.00 | 0.67 |
| 40 | 1.00 | 1.00 | 0.92 |
| 80 | 1.00 | 1.00 | 1.00 |

# Appendix C — Code and reproducibility

The code that produces every number in this paper is published with it.

```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python run_atr12.py        # report + 7 figures, ~8 s
pytest -q                  # 31 tests
python check.py            # full PASS/FAIL verification
```

The modules are: `config`, `akashic_field`, `temporal_modes`, `fermions`, `consciousness`, `empathy`, `word_excitation`, `verification`, `simulation`. Every relation in Part II has a dedicated test. Results are deterministic for a given configuration (seed = 12).

# Appendix D — Declarations

**Contribution:** the author conceived all central ideas. AI tools were used as drafting and verification support; all conceptual contributions are the author's.

**Conflicts of interest:** none.

**Funding:** none.

**Epistemic status:** speculative preprint. The central ideas are original but have not been tested experimentally. The sections of Appendix A are philosophical speculations.

---

*Author: Daniel Ofiteru — October 2026 — Speculative preprint*
