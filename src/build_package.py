#!/usr/bin/env python3
"""Assemble the journal submission package in submission/ from files already built.

    python src/build_package.py

Contents:
    Manuscript/            manuscript .docx (upload this) and .pdf preview
    Figures/               Fig1-8 and FigS1-S2 at 300 dpi
    Supplementary/         supplementary information, all result CSVs and their metadata
    Cover_letter/          cover letter
    Response/              point-by-point response to the pre-submission review
    Code_and_data/         snapshot of the repository (git archive of HEAD)
"""
import os
import shutil
import subprocess
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
OUT = os.path.join(ROOT, "submission")

FIGS = ["fig1_model.png", "fig2_numerics.png", "fig3_controls.png", "fig4_drive.png",
        "fig5_n_sweep.png", "fig6_threshold.png", "fig7_sensitivity.png",
        "fig8_dispersion_trains.png", "figS2_full_length.png", "figS3_lesion_stimulus.png",
        "figS1_membrane_verification.png"]
NUMBERED = {"fig1_model.png": "Fig1.png", "fig2_numerics.png": "Fig2.png",
            "fig3_controls.png": "Fig3.png", "fig4_drive.png": "Fig4.png",
            "fig5_n_sweep.png": "Fig5.png", "fig6_threshold.png": "Fig6.png",
            "fig7_sensitivity.png": "Fig7.png", "fig8_dispersion_trains.png": "Fig8.png",
            "figS2_full_length.png": "FigS1.png", "figS3_lesion_stimulus.png": "FigS2.png",
            "figS1_membrane_verification.png": "FigS3.png"}


def copy(src, dst_dir, name=None):
    if not os.path.exists(src):
        print(f"  MISSING {os.path.relpath(src, ROOT)}")
        return False
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(dst_dir, name or os.path.basename(src)))
    return True


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    ok = True
    for f, ext in (("ephaptic_crosstalk_manuscript", ".docx"), ("ephaptic_crosstalk_manuscript", ".pdf")):
        ok &= copy(os.path.join(ROOT, "manuscript", f + ext), os.path.join(OUT, "Manuscript"))
    for f in FIGS:
        ok &= copy(os.path.join(ROOT, "results", "figures", f), os.path.join(OUT, "Figures"), NUMBERED[f])
    for f, ext in (("supplementary_information", ".docx"), ("supplementary_information", ".pdf")):
        ok &= copy(os.path.join(ROOT, "manuscript", f + ext), os.path.join(OUT, "Supplementary"))
    data_out = os.path.join(OUT, "Supplementary", "data")
    for f in sorted(os.listdir(os.path.join(ROOT, "results", "data"))):
        copy(os.path.join(ROOT, "results", "data", f), data_out)
    ok &= copy(os.path.join(ROOT, "manuscript", "cover_letter.md"), os.path.join(OUT, "Cover_letter"))
    ok &= copy(os.path.join(ROOT, "docs", "RESPONSE_TO_REVIEWERS.md"), os.path.join(OUT, "Response"))
    ok &= copy(os.path.join(ROOT, "docs", "MANIFEST.md"), os.path.join(OUT, "Response"))
    code = os.path.join(OUT, "Code_and_data")
    os.makedirs(code, exist_ok=True)
    try:
        subprocess.run(["git", "archive", "--format=zip", "-o",
                        os.path.join(code, "ephaptic-crosstalk.zip"), "HEAD"], cwd=ROOT, check=True)
        print("  wrote submission/Code_and_data/ephaptic-crosstalk.zip")
    except Exception as e:  # noqa: BLE001
        print("  git archive failed:", e)
        ok = False
    print("submission/ assembled" + ("" if ok else " WITH MISSING FILES"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
