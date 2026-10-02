#!/usr/bin/env python3
"""Regenerate every result, figure and table of the study.

    python run_all.py                 # everything (about 2-3 h on 4 cores)
    python run_all.py --figures       # figures and tables only, from results/data
    python run_all.py --only e03 e05  # selected experiments, then figures and tables

Set EPHAPTIC_WORKERS to control the number of parallel processes.
"""
import argparse
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(ROOT, "src", "experiments")
FIG = os.path.join(ROOT, "src", "figures")


#: Experiments that run faster with one process.  Their systems are large enough (one
#: explicit Abeta cable per onset phase) that every time step streams the whole LU factor
#: from memory, so parallel workers only contend for memory bandwidth.
SERIAL = ("e08",)


def run(script, cwd):
    t0 = time.time()
    print(f"=== {os.path.relpath(script, ROOT)}", flush=True)
    env = dict(os.environ)
    if os.path.basename(script).startswith(SERIAL):
        env["EPHAPTIC_WORKERS"] = "1"
    r = subprocess.run([sys.executable, script], cwd=cwd, env=env)
    if r.returncode != 0:
        sys.exit(f"FAILED: {script}")
    print(f"    ({time.time() - t0:.0f} s)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figures", action="store_true", help="only rebuild figures and tables")
    ap.add_argument("--only", nargs="*", help="experiment prefixes to run (e.g. e03 e05)")
    a = ap.parse_args()
    if not a.figures:
        for s in sorted(glob.glob(os.path.join(EXP, "e[0-9][0-9]*_*.py"))):
            if a.only and not any(os.path.basename(s).startswith(p) for p in a.only):
                continue
            run(s, EXP)
    for s in sorted(glob.glob(os.path.join(FIG, "fig*.py"))):
        run(s, FIG)
    run(os.path.join(ROOT, "src", "build_tables.py"), os.path.join(ROOT, "src"))
    run(os.path.join(ROOT, "src", "build_manifest.py"), os.path.join(ROOT, "src"))


if __name__ == "__main__":
    main()
