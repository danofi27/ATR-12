# Publishing guide — ART-12D

Everything needed to run, verify and publish the project.

---

## 1. Quick start

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python check.py          :: full verification (PASS/FAIL table)
python run_atr12.py      :: regenerate report + figures
pytest -q                :: unit tests only
```

Requirements: Python ≥ 3.10, numpy, scipy, matplotlib, pytest, pymupdf (PDF checks), Microsoft Edge (PDF builds).

> On the NAS share (`W:`) run `set PYTHONDONTWRITEBYTECODE=1` first. Writing
> `__pycache__` on the share can be blocked by antivirus/indexer and the Python
> process is then killed without a message.

## 2. How do we know it works?

`python check.py` prints seven checks. All must be PASS:

| Check | What it proves | Expected |
|---|---|---|
| environment | the interpreter has the required packages | Python 3.10+, 4 packages |
| unit tests | every formula has a dedicated test | 31 passed |
| pipeline | one run produces all 12 result files | 12/12 artefacts |
| scientific audit | the audit reproduces its own verdicts | OK 5 / inconsistent 10 / untestable 2 |
| figures | all seven figures exist as PNG and vector PDF | 7 PNG + 7 PDF |
| determinism | two runs with the same seed agree bit for bit | identical sha256 |
| papers | the v31 PDFs are real documents | > 10 pages, > 100 KB |

The determinism check is the strongest statement the project can make: a reader
who runs the same commands gets the same numbers.

## 3. What the numbers should be

If any of these change, something is wrong:

- m₁ = 1e-5 eV → f₁ = 2.42 GHz, m₂ = 4.84 GHz, m₃ = 7.25 GHz.
- Φ(cortex, n=6) ≈ 0.259 ± 0.049; Φ(cerebellum, n=6) ≈ 0.045 ± 0.015.
- Duration needed for r = 0.1 at ±5 Hz with Bonferroni: 91.1 s.
- Audit: 5 OK, 10 inconsistent, 2 untestable.

## 4. Pre-publication checklist

- [ ] `python check.py` → ALL CHECKS PASSED.
- [ ] `LICENSE` present (MIT).
- [ ] `CITATION.cff` updated with the final version and date.
- [ ] `ATR_12_v31_{RO,EN,DE,FR}.pdf` rebuilt from the current sources.
- [ ] `git status` clean, no secrets, no `results/`.
- [ ] Author identity set: `git config user.name "Daniel Ofiteru"` and the GitHub e-mail.
- [ ] Decide whether `ATR-12_v5.md` (empty file) stays.
- [ ] Read `results/atr12_report.md` once, end to end.

## 5. Publishing on GitHub

```bat
git remote add origin git@github.com:danofi27/ATR-12.git
git push -u origin main
```

Then, on GitHub:

1. **Settings → About:** description "Simulation code and corrected preprint for ART-12D (v31)", topics `consciousness`, `dark-matter`, `kaluza-klein`, `preprint`.
2. **Releases → Draft a new release:** tag `v1.0.0`, title "ART-12D v31.0 + code v1.0.0", attach both PDFs.
3. Only version 31 is published. The superseded versions (v3, v7, v30) are
   untracked and listed in `.gitignore`, so a fresh clone or archive contains
   nothing but v31.

The repository is already initialised with a single commit on `main`.

## 6. Archiving on Zenodo (DOI)

Zenodo only archives releases that are created **after** the repository is enabled
in its settings, so the existing `v1.0.0` release will not receive a DOI. The order
matters:

1. Sign in at <https://zenodo.org> with GitHub.
2. Open <https://zenodo.org/account/settings/github/> and switch `danofi27/ATR-12` to **ON**.
3. Create a **new** release in this repository (for example `v1.0.1`) with the same
   PDF assets. Zenodo archives it within a minute and mints a DOI.
4. Copy the DOI badge from Zenodo and add it to `README.md`:

   ```markdown
   [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
   ```

5. Add the same DOI to `CITATION.cff` (`doi:` field) and to the paper's title page,
   then rebuild the PDFs.

The metadata Zenodo uses comes from [`.zenodo.json`](./.zenodo.json); edit that file
and create a new release to update the record. Only `CITATION.cff` and `.zenodo.json`
are read from the release tag — the PDFs are attached as release assets.

## 7. Rebuilding the PDFs

### Romanian — full LaTeX version (Overleaf)

`ATR_12_v31_RO.tex` is the complete paper: the whole v30 text, the ten
corrections applied, the new sections (numeric spectrum, compactification
tension, power analysis, audit) and the seven figures.

To edit it on Overleaf:

1. **New Project → Upload Project**, and upload `ATR_12_v31_RO.tex` **and** the
   `figures/` folder. The `.tex` references the vector files
   `figures/figXX_*.pdf`; the matching `.png` files are only for the README and
   the web, so the PDFs are the ones that must be present.
2. Set it as the main document (Menu → Main document).
3. **Compiler:** XeLaTeX is recommended (correct Romanian ș/ț). pdfLaTeX also
   works — the preamble switches automatically via the `iftex` package.
4. Compile. The reference build is 41 pages.

### Other languages — Markdown pipeline

The DE/FR/ES/IT versions are currently the condensed Markdown sources in
[`paper/`](./paper), built with Edge:

```bat
python paper\build_paper.py paper\paper_v31_de.md --lang DE
python paper\build_paper.py paper\paper_v31_fr.md --lang FR
python paper\build_paper.py paper\paper_v31_es.md --lang ES
python paper\build_paper.py paper\paper_v31_it.md --lang IT
```

Outputs: `ATR_12_v31_<LANG>.pdf`. They will be regenerated from the full LaTeX
master once the Overleaf edit is final.

To add a language, copy `paper_v31_en.md` to `paper_v31_<lang>.md`, translate the
text (do **not** touch the `$$...$$` blocks or the image paths), and run the
builder with the matching `--lang`. The CSS already provides font fallbacks for
Cyrillic and CJK.

**Why the v30 PDFs for DE/FR/IT/ES/RU/JP/CN were not patched:** their text
layer is not extractable (RU/JP/CN decode as `?`, FR/ES accents are broken), and
their Markdown/LaTeX sources are not in the project. They cannot be corrected
mechanically; they must be re-translated from the v31 master. The originals are
kept in `archive/v30/` for reference.

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| process killed with no output | `__pycache__` write blocked on the NAS | `set PYTHONDONTWRITEBYTECODE=1` |
| `fatal: detected dubious ownership` | SMB share owned by another SID | `git config --global --add safe.directory '%(prefix)///Advance/Advance/Proiecte/ATR-12'` |
| Edge not found | non-standard install | `python paper\build_paper.py ... --edge "C:\path\to\msedge.exe"` |
| equation rendered as plain text | mathtext does not support a command | the builder prints `! mathtext failed`; rewrite the equation with supported commands |
| `pymupdf` missing | optional dependency | `pip install pymupdf` (only needed for page counts) |
