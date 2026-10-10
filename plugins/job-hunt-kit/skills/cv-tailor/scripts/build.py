#!/usr/bin/env python3
"""Build and check the CV and cover letter in one application folder.

For each of cv.tex and cover-letter.tex present in FOLDER:
  1. run pdflatex twice (the second pass resolves the "1 / 2" page counter);
  2. parse the log for errors, the page count and Overfull \\vbox warnings;
  3. count extracted words (pypdf, pdfminer.six or pdftotext — whichever exists);
  4. optionally rename the PDF to its final name (--name-prefix);
  5. delete .aux/.log/.out.

Exit code is non-zero if any document failed to build or missed its page
budget, so a batch driver can stop on it.

Usage:
    python build.py "applications/20261010 - Acme - Engineer"
    python build.py FOLDER --name-prefix "20261010 - Acme - Engineer" --cv-pages 2
Standard library only; word counting uses an optional tool if available.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

PAGES_RE = re.compile(r"Output written on .*?\((\d+) pages?")


def run_pdflatex(folder: Path, tex: str) -> tuple[bool, str]:
    for _ in range(2):
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex],
            cwd=folder, capture_output=True, text=True, errors="replace",
        )
    log_path = folder / (Path(tex).stem + ".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else proc.stdout
    return proc.returncode == 0, log


def word_count(pdf: Path) -> int | None:
    try:
        from pypdf import PdfReader  # type: ignore
        return sum(len((p.extract_text() or "").split()) for p in PdfReader(str(pdf)).pages)
    except Exception:
        pass
    try:
        from pdfminer.high_level import extract_text  # type: ignore
        return len(extract_text(str(pdf)).split())
    except Exception:
        pass
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, errors="replace")
        if out.returncode == 0:
            return len(out.stdout.split())
    return None


def copy_with_retry(src: Path, dst: Path, attempts: int = 5) -> None:
    # Synced folders (OneDrive, Dropbox) sometimes lock files briefly.
    for i in range(attempts):
        try:
            shutil.copy2(src, dst)
            return
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(1.5)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build and check an application folder.")
    ap.add_argument("folder", type=Path)
    ap.add_argument("--name-prefix", help='e.g. "20261010 - Acme - Engineer"; PDFs are copied to "<prefix> - CV.pdf" / "- CL.pdf" in the folder')
    ap.add_argument("--cv-pages", type=int, default=2)
    ap.add_argument("--cl-pages", type=int, default=1)
    ap.add_argument("--keep-aux", action="store_true")
    args = ap.parse_args()

    if not shutil.which("pdflatex"):
        print("error: pdflatex not found on PATH (install TeX Live or MiKTeX)", file=sys.stderr)
        return 2

    folder = args.folder.resolve()
    ok_all = True
    for tex, budget, suffix in (("cv.tex", args.cv_pages, "CV"), ("cover-letter.tex", args.cl_pages, "CL")):
        if not (folder / tex).exists():
            continue
        ok, log = run_pdflatex(folder, tex)
        errors = [l for l in log.splitlines() if l.startswith("!")]
        m = PAGES_RE.search(log)
        pages = int(m.group(1)) if m else None
        overfull_v = len(re.findall(r"Overfull \\vbox", log))
        pdf = folder / (Path(tex).stem + ".pdf")
        words = word_count(pdf) if pdf.exists() else None

        status = "OK"
        if not ok or errors or pages is None:
            status = "FAILED"
        elif pages != budget:
            status = f"PAGE BUDGET MISSED ({pages} != {budget})"
        if status != "OK":
            ok_all = False

        print(f"{tex}: {status} - pages={pages} words={words if words is not None else 'n/a'} overfull_vbox={overfull_v}")
        for e in errors[:5]:
            print(f"    {e}")

        if status == "OK" and args.name_prefix:
            dst = folder / f"{args.name_prefix} - {suffix}.pdf"
            copy_with_retry(pdf, dst)
            try:
                pdf.unlink()  # keep only the final-named PDF
            except OSError:
                pass
            print(f"    -> {dst.name}")

    if not args.keep_aux:
        for ext in (".aux", ".log", ".out"):
            for f in folder.glob(f"*{ext}"):
                try:
                    f.unlink()
                except OSError:
                    pass

    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
