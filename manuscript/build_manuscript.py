#!/usr/bin/env python3
"""Assemble the manuscript from manuscript/sections/*.md, substitute every {{key}} with the
value computed by src/build_tables.py (manuscript/generated/numbers.json) and every
{{TABLE:name}} with manuscript/generated/name.md, then build the .docx (pandoc; equations
become native Word equations) and a PDF preview (LibreOffice).

    python manuscript/build_manuscript.py            # manuscript.md, .docx, .pdf
    python manuscript/build_manuscript.py --md-only  # only the assembled markdown

The build fails if a placeholder has no value.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEN = os.path.join(HERE, "generated")
NAME = "ephaptic_crosstalk_manuscript"


def pandoc():
    exe = shutil.which("pandoc")
    if exe:
        return exe
    try:
        import pypandoc
        return pypandoc.get_pandoc_path()
    except Exception:
        sys.exit("pandoc not found (install pandoc or pypandoc_binary)")


TEMPLATES = [  # (template, output): other documents rendered from the same numbers
    (os.path.join(ROOT, "docs", "templates", "README.tmpl.md"), os.path.join(ROOT, "README.md")),
    (os.path.join(ROOT, "docs", "templates", "RESPONSE_TO_REVIEW.tmpl.md"), os.path.join(ROOT, "docs", "RESPONSE_TO_REVIEW.md")),
    (os.path.join(ROOT, "docs", "templates", "cover_letter.tmpl.md"), os.path.join(ROOT, "manuscript", "cover_letter.md")),
]


def substitute(text):
    with open(os.path.join(GEN, "numbers.json")) as f:
        nums = json.load(f)
    missing = set()

    def tab(m):
        path = os.path.join(GEN, m.group(1) + ".md")
        if not os.path.exists(path):
            missing.add("TABLE:" + m.group(1))
            return m.group(0)
        with open(path) as f:
            return f.read()
    text = re.sub(r"\{\{TABLE:([A-Za-z0-9_]+)\}\}", tab, text)

    def num(m):
        k = m.group(1)
        if k not in nums:
            missing.add(k)
            return m.group(0)
        return nums[k]
    text = re.sub(r"\{\{([A-Za-z0-9_.]+)\}\}", num, text)
    if missing:
        sys.exit("unresolved placeholders: " + ", ".join(sorted(missing)))
    return text


def assemble(folder="sections", name=NAME):
    parts = []
    for p in sorted(glob.glob(os.path.join(HERE, folder, "*.md"))):
        with open(p) as f:
            parts.append(f.read().rstrip() + "\n")
    text = substitute("\n".join(parts))
    out = os.path.join(HERE, name + ".md")
    with open(out, "w") as f:
        f.write(text)
    print("  wrote", os.path.relpath(out, ROOT))
    return out


def build_docx(md):
    out = os.path.splitext(md)[0] + ".docx"
    cmd = [pandoc(), md, "-o", out, "--from", "markdown+tex_math_dollars+pipe_tables+subscript+superscript",
           "--resource-path", HERE, "--reference-doc", os.path.join(HERE, "template", "reference.docx")]
    subprocess.run(cmd, check=True, cwd=HERE)
    print("  wrote", os.path.relpath(out, ROOT))
    return out


PRINT_CSS = """
@page { size: A4; margin: 20mm 18mm; }
html { font-size: 10.5pt; }
body { font-family: Georgia, 'Times New Roman', serif; line-height: 1.45; max-width: none;
       margin: 0; color: #000; }
h1 { font-size: 1.5rem; } h2 { font-size: 1.2rem; margin-top: 1.4em; } h3 { font-size: 1.05rem; }
img { max-width: 100%; height: auto; }
figure { margin: 1em 0; page-break-inside: avoid; }
figcaption { font-size: 0.85rem; }
table { border-collapse: collapse; font-size: 0.78rem; width: 100%; page-break-inside: avoid; }
th, td { border: 1px solid #999; padding: 2px 4px; text-align: left; }
pre, code { font-family: 'DejaVu Sans Mono', monospace; font-size: 0.8rem; }
"""


def chromium():
    """Headless Chrome/Chromium, which prints the HTML rendering to PDF."""
    for env in ("CHROME_PATH", "CHROMIUM_PATH"):
        if os.environ.get(env) and os.path.exists(os.environ[env]):
            return os.environ[env]
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        exe = shutil.which(name)
        if exe:
            return exe
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    for pat in ("chromium-*/chrome-linux/chrome", "chromium_headless_shell-*/chrome-linux/headless_shell"):
        hits = sorted(glob.glob(os.path.join(root, pat)))
        if hits:
            return hits[-1]
    return None


def build_pdf(md):
    """PDF preview of the assembled markdown.

    LibreOffice is tried only as a fallback: in some containers it exits 0 without writing
    anything, so the output is always checked for existence before it is reported.
    """
    out = os.path.splitext(md)[0] + ".pdf"
    if os.path.exists(out):
        os.remove(out)
    exe = chromium()
    if exe:
        css = os.path.join(HERE, "generated", "print.css")
        with open(css, "w") as f:
            f.write(PRINT_CSS)
        html = os.path.splitext(md)[0] + ".preview.html"
        subprocess.run([pandoc(), md, "-o", html, "--standalone", "--embed-resources",
                        "--css", css, "--metadata", "title=" + os.path.basename(md),
                        "--from", "markdown+tex_math_dollars+pipe_tables+subscript+superscript",
                        "--mathml", "--resource-path", HERE], check=True, cwd=HERE)
        r = subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu",
                            "--no-pdf-header-footer", "--print-to-pdf=" + out,
                            "file://" + html], capture_output=True, text=True)
        os.remove(html)
        if os.path.exists(out) and os.path.getsize(out) > 5000:
            print("  wrote", os.path.relpath(out, ROOT))
            return out
        print("  PDF preview failed (chromium):", (r.stderr or "").strip().splitlines()[-1:] or "no output")
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        docx = os.path.splitext(md)[0] + ".docx"
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", HERE, docx],
                       capture_output=True, text=True)
        if os.path.exists(out) and os.path.getsize(out) > 5000:
            print("  wrote", os.path.relpath(out, ROOT))
            return out
    print("  PDF preview not produced (no working converter); the .docx is the submission file")
    return None


def render_templates():
    for src, dst in TEMPLATES:
        if not os.path.exists(src):
            continue
        with open(src) as f:
            text = substitute(f.read())
        with open(dst, "w") as f:
            f.write(text)
        print("  wrote", os.path.relpath(dst, ROOT))


if __name__ == "__main__":
    md = assemble()
    sup = assemble("supplement", "supplementary_information")
    render_templates()
    if "--md-only" not in sys.argv:
        for src in (md, sup):
            build_docx(src)
            build_pdf(src)
