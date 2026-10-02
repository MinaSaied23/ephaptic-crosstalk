"""Shared helpers for the experiment scripts: parallel execution and CSV output."""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
DATA = os.path.join(ROOT, "results", "data")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ephaptic.params import as_dict  # noqa: E402


def workers():
    return int(os.environ.get("EPHAPTIC_WORKERS", os.cpu_count() or 1))


def pmap(fn, jobs, nproc=None):
    """Run fn(job) for each job (in parallel) and return results in order."""
    nproc = nproc or workers()
    t0 = time.time()
    if nproc <= 1 or len(jobs) <= 1:
        out = [fn(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=nproc) as ex:
            out = list(ex.map(fn, jobs, chunksize=1))
    print(f"  {len(jobs)} runs in {time.time() - t0:.1f} s", flush=True)
    return out


def write_csv(name, rows, meta=None):
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, name)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: _fmt(r.get(k, "")) for k in keys})
    if meta is not None:
        with open(path.replace(".csv", ".meta.json"), "w") as f:
            json.dump(meta, f, indent=1, default=str)
    print(f"  wrote {os.path.relpath(path, ROOT)} ({len(rows)} rows)")
    return path


def _fmt(v):
    if isinstance(v, float):
        return f"{v:.6g}"
    return v


def read_csv(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


# ----------------------------------------------------------------------------
# Generic single-run job
# ----------------------------------------------------------------------------
def run_case(job):
    """job = dict(c=<C-fiber params>, proto={...Protocol kwargs}, cleft={...CleftParams kwargs},
    tags={...columns copied to the output row}).  Returns one summary row."""
    from ephaptic import CoupledModel, Protocol, CleftParams
    from ephaptic.metrics import summarize
    pr = Protocol(**job.get("proto", {}))
    cl = CleftParams(**job.get("cleft", {}))
    m = CoupledModel(job["c"], pr, cl)
    r = m.run()
    s = summarize(r)
    row = dict(job.get("tags", {}))
    row.update(s)
    return row
