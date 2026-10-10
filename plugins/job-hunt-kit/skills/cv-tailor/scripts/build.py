#!/usr/bin/env python3
"""Render, build and check the CV and cover letter in one application folder.

  1. render content.json into sources (render.py), unless --no-render;
  2. LaTeX: run pdflatex twice per document (the second pass resolves "1 / 2");
     Word: convert each .docx to PDF with Word, LibreOffice or docx2pdf, if any exists;
  3. check the page count against the budget and count extracted words;
  4. optionally copy outputs to their final names (--name-prefix);
  5. delete .aux/.log/.out.

Exit code: 0 OK, 1 a document failed or missed its page budget, 2 a required tool is
missing (pdflatex for LaTeX, python-docx for Word).

Usage:
    python build.py FOLDER --format docx --name-prefix "20261010 - Acme - Engineer"
    python build.py FOLDER --format latex --cv-pages 2 --templates path/to/workspace/templates
    python build.py FOLDER --format latex --no-render     # build hand-edited .tex as is
"""

from __future__ import annotations

import argparse
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402

PAGES_RE = re.compile(r"Output written on .*?\((\d+) pages?")
DOCS = (("cv", "CV"), ("cover-letter", "CL"))


# ------------------------------------------------------------------ helpers

def pdf_info(pdf: Path) -> tuple[int | None, int | None]:
    """(pages, words) from a PDF, using whichever extractor is installed."""
    try:
        from pypdf import PdfReader  # type: ignore
        r = PdfReader(str(pdf))
        return len(r.pages), sum(len((p.extract_text() or "").split()) for p in r.pages)
    except Exception:
        pass
    pages = words = None
    try:
        from pdfminer.high_level import extract_text  # type: ignore
        words = len(extract_text(str(pdf)).split())
    except Exception:
        pass
    if words is None and shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, errors="replace")
        if out.returncode == 0:
            words = len(out.stdout.split())
            pages = out.stdout.count("\f") or None
    return pages, words


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


def unlink_quietly(p: Path) -> None:
    try:
        p.unlink()
    except OSError:
        pass


# ------------------------------------------------------------------ LaTeX

def run_pdflatex(folder: Path, tex: str) -> tuple[bool, str]:
    for _ in range(2):
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex],
            cwd=folder, capture_output=True, text=True, errors="replace",
        )
    log_path = folder / (Path(tex).stem + ".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else proc.stdout
    return proc.returncode == 0, log


def build_latex(folder: Path, stem: str) -> dict:
    ok, log = run_pdflatex(folder, stem + ".tex")
    errors = [l for l in log.splitlines() if l.startswith("!")]
    m = PAGES_RE.search(log)
    pdf = folder / (stem + ".pdf")
    _, words = pdf_info(pdf) if pdf.exists() else (None, None)
    return {"ok": ok and not errors and m is not None, "pages": int(m.group(1)) if m else None,
            "words": words, "errors": errors, "pdf": pdf,
            "note": f"overfull_vbox={len(re.findall(r'Overfull \\\\vbox', log))}"}


# ------------------------------------------------------------------ Word

def find_soffice() -> str | None:
    for name in ("soffice", "libreoffice"):
        if shutil.which(name):
            return shutil.which(name)
    for p in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if Path(p).exists():
            return p
    return None


def docx_to_pdf(docx: Path) -> tuple[Path | None, str]:
    """Convert with the first converter that works. Returns (pdf or None, how/why).

    Conversion happens in a short temporary folder: Word refuses paths over ~259
    characters, which deep synced folders plus long company names easily exceed. The
    PDF then lands in a subfolder, so it can't overwrite a LaTeX PDF of the same name."""
    outdir = docx.parent / "_word_pdf"
    outdir.mkdir(exist_ok=True)
    pdf = outdir / (docx.stem + ".pdf")
    unlink_quietly(pdf)
    tried = []

    with tempfile.TemporaryDirectory(prefix="jhk") as tmp:
        src = Path(tmp) / "doc.docx"
        out = Path(tmp) / "doc.pdf"
        shutil.copy2(docx, src)

        def done(how: str):
            shutil.move(str(out), str(pdf))
            return pdf, how

        # 1. Microsoft Word on Windows, via COM (no extra Python packages needed).
        if platform.system() == "Windows":
            exe = shutil.which("powershell") or shutil.which("pwsh")
            if exe:
                ps = (f"$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
                      f"try {{ $d = $w.Documents.Open('{src}', $false, $true); "
                      f"$d.ExportAsFixedFormat('{out}', 17); $d.Close($false) }} finally {{ $w.Quit() }}")
                try:
                    subprocess.run([exe, "-NoProfile", "-NonInteractive", "-Command", ps],
                                   capture_output=True, text=True, errors="replace", timeout=180)
                except subprocess.TimeoutExpired:
                    pass
                if out.exists():
                    return done("Microsoft Word")
                tried.append("Word (not installed or failed)")

        # 2. docx2pdf (drives Word on Windows/macOS).
        try:
            from docx2pdf import convert  # type: ignore
            convert(str(src), str(out))
            if out.exists():
                return done("docx2pdf")
        except Exception:
            tried.append("docx2pdf")

        # 3. LibreOffice, any OS.
        soffice = find_soffice()
        if soffice:
            try:
                subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(src)],
                               capture_output=True, text=True, errors="replace", timeout=180)
            except subprocess.TimeoutExpired:
                pass
            if out.exists():
                return done("LibreOffice")
            tried.append("LibreOffice (failed)")
        else:
            tried.append("LibreOffice (not found)")
    return None, "no converter worked: " + ", ".join(tried)


def build_docx(folder: Path, stem: str) -> dict:
    docx = folder / (stem + ".docx")
    pdf, how = docx_to_pdf(docx)
    if pdf is None:
        return {"ok": True, "pages": None, "words": None, "errors": [], "pdf": None, "docx": docx,
                "note": f"PDF not made, pages NOT checked ({how})"}
    pages, words = pdf_info(pdf)
    return {"ok": True, "pages": pages, "words": words, "errors": [], "pdf": pdf, "docx": docx,
            "note": f"pdf via {how}"}


# ------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser(description="Render, build and check an application folder.")
    ap.add_argument("folder", type=Path)
    ap.add_argument("--format", choices=("latex", "docx", "both"), default="docx")
    ap.add_argument("--name-prefix", help='e.g. "20261010 - Acme - Engineer"; outputs are copied to "<prefix> - CV.pdf" etc.')
    ap.add_argument("--templates", type=Path, help="workspace folder holding jobcv.sty / jobcv-template.docx overrides")
    ap.add_argument("--no-render", action="store_true", help="build existing cv.tex / cv.docx as they are")
    ap.add_argument("--cv-pages", type=int, default=2)
    ap.add_argument("--cl-pages", type=int, default=1)
    ap.add_argument("--keep-aux", action="store_true")
    args = ap.parse_args()

    folder = args.folder.resolve()
    want_latex = args.format in ("latex", "both")
    want_docx = args.format in ("docx", "both")

    if want_latex and not shutil.which("pdflatex"):
        print("error: pdflatex not found on PATH (install TeX Live or MiKTeX, or use --format docx)", file=sys.stderr)
        return 2

    if not args.no_render:
        try:
            for p in render.render(folder, args.format, args.templates):
                print(f"rendered {p.name}")
        except render.ContentError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2 if "python-docx" in str(e) else 1

    ok_all = True
    for stem, suffix in DOCS:
        budget = args.cv_pages if stem == "cv" else args.cl_pages
        jobs = []
        if want_latex and (folder / f"{stem}.tex").exists():
            jobs.append(("latex", build_latex))
        if want_docx and (folder / f"{stem}.docx").exists():
            jobs.append(("docx", build_docx))
        for kind, fn in jobs:
            res = fn(folder, stem)
            status = "OK"
            if not res["ok"]:
                status = "FAILED"
            elif res["pages"] is not None and res["pages"] != budget:
                status = f"PAGE BUDGET MISSED ({res['pages']} != {budget})"
            if status != "OK":
                ok_all = False
            words = res["words"] if res["words"] is not None else "n/a"
            print(f"{stem} [{kind}]: {status} - pages={res['pages']} words={words} {res['note']}")
            for e in res["errors"][:5]:
                print(f"    {e}")

            # With --format both, the Word PDF gets a "(Word)" tag so the two don't collide.
            tag = " (Word)" if kind == "docx" and want_latex else ""
            if status == "OK" and args.name_prefix:
                if res["pdf"]:
                    dst = folder / f"{args.name_prefix} - {suffix}{tag}.pdf"
                    copy_with_retry(res["pdf"], dst)
                    unlink_quietly(res["pdf"])  # keep only the final-named file
                    print(f"    -> {dst.name}")
                if kind == "docx":
                    dst = folder / f"{args.name_prefix} - {suffix}.docx"
                    copy_with_retry(res["docx"], dst)
                    unlink_quietly(res["docx"])  # content.json is the source; rebuild to regenerate
                    print(f"    -> {dst.name}")
            elif kind == "docx" and res["pdf"]:
                dst = folder / f"{stem}{tag}.pdf"
                copy_with_retry(res["pdf"], dst)
                print(f"    -> {dst.name}")

    shutil.rmtree(folder / "_word_pdf", ignore_errors=True)
    if not args.keep_aux:
        for ext in (".aux", ".log", ".out"):
            for f in folder.glob(f"*{ext}"):
                unlink_quietly(f)

    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
