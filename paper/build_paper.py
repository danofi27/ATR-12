"""Build a print-ready PDF from a Markdown paper.

Pipeline: Markdown -> HTML (equations rendered with matplotlib mathtext) ->
headless Microsoft Edge -> PDF.

Usage:
    python paper/build_paper.py paper/paper_v31_ro.md --lang RO
    python paper/build_paper.py paper/paper_v31_en.md --lang EN
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "build"
FIGURES_DIR = ROOT / "figures"
EDGE_CANDIDATES = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)

CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
html { font-size: 10.6pt; }
body {
  font-family: "Charter", "Georgia", "Times New Roman", "Noto Serif", "DejaVu Serif",
               "Segoe UI", "Yu Mincho", "MS Mincho", "SimSun", "Microsoft YaHei", serif;
  line-height: 1.42; color: #111; text-align: justify; hyphens: auto;
}
h1 { font-size: 19pt; line-height: 1.2; margin: 0 0 4mm 0; text-align: left; color: #0d1b2a; }
h1 + h2 { font-size: 12.5pt; font-weight: 600; margin: 0 0 6mm 0; color: #33475b; }
h2 { font-size: 13pt; margin: 7mm 0 2.5mm 0; color: #0d1b2a; text-align: left; }
h3 { font-size: 11pt; margin: 5mm 0 2mm 0; color: #1d3557; text-align: left; }
p { margin: 0 0 2.4mm 0; }
ul, ol { margin: 0 0 3mm 0; padding-left: 6mm; }
li { margin-bottom: 1.2mm; }
table { border-collapse: collapse; width: 100%; margin: 3mm 0 5mm 0; font-size: 9.2pt; }
th, td { border: 0.4pt solid #9aa5b1; padding: 1.2mm 2mm; vertical-align: top; }
th { background: #eef2f6; text-align: left; }
tr { page-break-inside: avoid; }
code { font-family: "Consolas", "DejaVu Sans Mono", monospace; font-size: 9pt; background: #f4f4f4; padding: 0 0.6mm; }
pre { background: #f7f7f7; border-left: 1.2mm solid #8fa3b8; padding: 2.5mm; font-size: 8.8pt; page-break-inside: avoid; }
pre code { background: none; }
img { display: block; margin: 3.5mm auto 1.5mm auto; max-width: 88%; height: auto; }
figure { margin: 4mm 0 5mm 0; page-break-inside: avoid; }
figure img { margin: 0 auto 2mm auto; }
figure figcaption { font-size: 9.2pt; font-style: italic; text-align: center; color: #333; }
p.eq { text-align: center; margin: 3mm 0 3.5mm 0; page-break-inside: avoid; }
p.eq img { margin: 0 auto; max-width: 100%; }
em { color: #333; }
.pagebreak { page-break-after: always; }
blockquote { margin: 3mm 5mm; padding-left: 4mm; border-left: 1mm solid #c9d3dd; color: #333; }
hr { border: none; border-top: 0.4pt solid #9aa5b1; margin: 6mm 0; }
a { color: #1d3557; text-decoration: none; }
"""

HTML_TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def find_edge() -> Path:
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise SystemExit("Microsoft Edge not found; install it or pass --edge")


def render_equations(markdown_text: str, workdir: Path, dpi: int = 300) -> str:
    """Replace $$...$$ blocks with PNG images rendered by matplotlib mathtext."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pattern = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)

    def replace(match: re.Match[str]) -> str:
        latex = " ".join(match.group(1).split())
        digest = hashlib.sha1(latex.encode("utf-8")).hexdigest()[:12]
        png = workdir / f"eq_{digest}.png"
        if not png.exists():
            fig = plt.figure(figsize=(0.01, 0.01))
            try:
                fig.text(0, 0, f"${latex}$", fontsize=12, color="black")
                fig.savefig(png, dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0.02)
            except Exception as exc:  # pragma: no cover - fallback for unsupported mathtext
                print(f"  ! mathtext failed ({exc}); writing plain text instead", file=sys.stderr)
                fig.text(0, 0, latex, fontsize=11)
                fig.savefig(png, dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0.02)
            plt.close(fig)
        return f'\n\n<p class="eq"><img src="{png.as_uri()}" alt="equation"></p>\n\n'

    return pattern.sub(replace, markdown_text)


def absolutize_images(markdown_text: str) -> str:
    """Turn relative image paths into file:// URIs so the build is location independent."""
    pattern = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")

    def replace(match: re.Match[str]) -> str:
        target = match.group(2).strip()
        if target.startswith(("http://", "https://", "file://", "data:")):
            return match.group(0)
        resolved = (ROOT / "paper" / target).resolve()
        if not resolved.exists():
            resolved = (ROOT / target).resolve()
        if not resolved.exists():
            resolved = FIGURES_DIR / Path(target).name
        return f"{match.group(1)}{resolved.as_uri()}{match.group(3)}"

    return pattern.sub(replace, markdown_text)


def group_figures(html: str) -> str:
    """Wrap <p><img></p> plus the following italic caption into one <figure>."""
    pattern = re.compile(
        r"<p>\s*(<img[^>]*>)\s*</p>\s*<p>\s*(<em>.*?</em>)\s*</p>",
        re.DOTALL,
    )
    return pattern.sub(lambda m: f"<figure>{m.group(1)}<figcaption>{m.group(2)}</figcaption></figure>", html)


def build(markdown_path: Path, lang: str, edge: Path, keep_html: bool = False) -> Path:
    import markdown as md

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    text = markdown_path.read_text(encoding="utf-8")
    text = absolutize_images(text)
    text = render_equations(text, BUILD_DIR)

    html_body = md.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        output_format="html5",
    )
    html_body = group_figures(html_body)

    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else markdown_path.stem

    html = HTML_TEMPLATE.format(lang=lang.lower(), title=title, css=CSS, body=html_body)
    html_path = BUILD_DIR / f"paper_v31_{lang.lower()}.html"
    html_path.write_text(html, encoding="utf-8")

    pdf_path = ROOT / f"ATR_12_v31_{lang.upper()}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

    with tempfile.TemporaryDirectory() as profile:
        command = [
            str(edge),
            "--headless",
            "--disable-gpu",
            "--no-first-run",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0 or not pdf_path.exists():
            sys.stderr.write(result.stderr)
            raise SystemExit(f"Edge failed to produce {pdf_path}")

    if not keep_html:
        html_path.unlink(missing_ok=True)

    pages = 0
    try:
        import pymupdf

        pages = pymupdf.open(str(pdf_path)).page_count
    except Exception:  # pragma: no cover - pymupdf optional
        pass

    size_kb = pdf_path.stat().st_size / 1024
    print(f"  {pdf_path.name}: {pages} pages, {size_kb:.0f} KB")
    return pdf_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an ART-12D paper PDF from Markdown")
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--lang", required=True, help="language code, e.g. RO or EN")
    parser.add_argument("--edge", type=Path, default=None)
    parser.add_argument("--keep-html", action="store_true")
    args = parser.parse_args(argv)

    edge = args.edge or find_edge()
    print(f"Building {args.markdown.name} -> ATR_12_v31_{args.lang.upper()}.pdf")
    build(args.markdown, args.lang, edge, keep_html=args.keep_html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
