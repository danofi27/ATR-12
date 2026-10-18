"""Assemble and build the English translation from paper/en/*.tex.

Usage:  python paper/build_en.py [--no-compile]

Concatenates the numbered parts in order, writes ATR_12_v31_EN.tex next to the
Romanian master, then compiles it with tectonic (if available) and reports the
page count and the LaTeX warnings that matter.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = sorted((ROOT / "paper" / "en").glob("*.tex"))
TARGET = ROOT / "ATR_12_v31_EN.tex"


def assemble() -> str:
    if not PARTS:
        raise SystemExit("no parts found in paper/en/")
    body = "\n".join(p.read_text(encoding="utf-8").rstrip("\n") for p in PARTS)
    if "\\end{document}" not in body:
        body += "\n\\end{document}\n"
        complete = False
    else:
        complete = True
    TARGET.write_text(body, encoding="utf-8")
    print(f"assembled {len(PARTS)} parts -> {TARGET.name} ({len(body):,} chars)")
    print(f"  complete: {complete}")
    for p in PARTS:
        print(f"    {p.name}")
    return body


def find_tectonic() -> str | None:
    candidates = [
        os.environ.get("TECTONIC"),
        str(Path(tempfile.gettempdir()) / "tectonic" / "tectonic.exe"),
        shutil.which("tectonic"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def build() -> int:
    tectonic = find_tectonic()
    if tectonic is None:
        print("tectonic not found; skipping the build")
        return 0
    work = Path(tempfile.gettempdir()) / "atr12_en_build"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    shutil.copy2(TARGET, work / TARGET.name)
    shutil.copytree(ROOT / "figures", work / "figures")
    proc = subprocess.run(
        [tectonic, "-X", "compile", "--keep-logs", TARGET.name],
        cwd=work,
        capture_output=True,
        text=True,
    )
    log_path = work / (TARGET.stem + ".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    errors = log.count("\n! ")
    over = log.count("Overfull \\hbox")
    under = log.count("Underfull \\hbox")
    print(f"  errors: {errors}")
    print(f"  missing characters: {log.count('Missing character')}")
    print(f"  overfull hbox: {over}")
    print(f"  underfull hbox: {under}")
    print(f"  undefined refs: {log.count('undefined')}")
    if proc.returncode != 0:
        tail = [ln for ln in (proc.stdout + proc.stderr).splitlines() if ln.strip()][-25:]
        print("BUILD FAILED")
        print("\n".join(tail))
        return 1
    pdf = work / (TARGET.stem + ".pdf")
    if pdf.exists():
        try:
            import pymupdf

            doc = pymupdf.open(str(pdf))
            print(f"  pages: {doc.page_count}")
            print(f"  raster images: {sum(len(p.get_images(full=True)) for p in doc)}")
        except Exception as exc:  # pragma: no cover
            print(f"  (could not inspect the PDF: {exc})")
        shutil.copy2(pdf, ROOT / pdf.name)
        print(f"  copied {pdf.name} back to the repository")
    return 0


if __name__ == "__main__":
    assemble()
    if "--no-compile" not in sys.argv:
        sys.exit(build())
