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


def build_pdf(docx):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("  LibreOffice not found; PDF preview skipped")
        return
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", HERE, docx], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("  wrote", os.path.relpath(os.path.splitext(docx)[0] + ".pdf", ROOT))


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
        build_pdf(build_docx(md))
        build_pdf(build_docx(sup))
