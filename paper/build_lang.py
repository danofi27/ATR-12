"""Assemble and build one language edition of the paper.

Usage:  python paper/build_lang.py de [--no-compile]

Reads paper/<lang>/*.tex in filename order, writes ATR_12_v31_<LANG>.tex next to
the Romanian master, then compiles it with tectonic and reports the page count,
missing glyphs and overfull boxes.

The NAS share kills processes that run longer than about fifteen seconds, so on
the share run the assembly with --no-compile and invoke the TeX engine yourself,
or copy the project to a local disk first.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def assemble(lang: str) -> Path:
    parts = sorted((ROOT / "paper" / lang).glob("*.tex"))
    if not parts:
        raise SystemExit(f"no parts found in paper/{lang}/")
    body = "\n".join(p.read_text(encoding="utf-8").rstrip("\n") for p in parts)
    complete = "\\end{document}" in body
    if not complete:
        body += "\n\\end{document}\n"
    target = ROOT / f"ATR_12_v31_{lang.upper()}.tex"
    target.write_text(body, encoding="utf-8")
    print(f"assembled {len(parts)} parts -> {target.name} ({len(body):,} chars)")
    print(f"  complete: {complete}")
    for p in parts:
        print(f"    {p.name}")
    return target


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


def build(target: Path) -> int:
    tectonic = find_tectonic()
    if tectonic is None:
        print("tectonic not found; skipping the build")
        return 0
    work = Path(tempfile.gettempdir()) / f"atr12_{target.stem}_build"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    shutil.copy2(target, work / target.name)
    shutil.copytree(ROOT / "figures", work / "figures")
    proc = subprocess.run(
        [tectonic, "-X", "compile", "--keep-logs", target.name],
        cwd=work,
        capture_output=True,
        text=True,
    )
    log_path = work / (target.stem + ".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    print(f"  errors: {log.count(chr(10) + '! ')}")
    print(f"  missing characters: {log.count('Missing character')}")
    print(f"  overfull hbox: {log.count('Overfull ' + chr(92) + 'hbox')}")
    print(f"  underfull hbox: {log.count('Underfull ' + chr(92) + 'hbox')}")
    print(f"  undefined references: {log.count('undefined')}")
    if proc.returncode != 0:
        tail = [ln for ln in (proc.stdout + proc.stderr).splitlines() if ln.strip()][-25:]
        print("BUILD FAILED")
        print("\n".join(tail))
        return 1
    pdf = work / (target.stem + ".pdf")
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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("usage: python paper/build_lang.py <lang> [--no-compile]")
    lang = args[0].lower()
    target = assemble(lang)
    if "--no-compile" not in sys.argv:
        sys.exit(build(target))
