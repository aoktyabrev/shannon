"""S0.4: budget and hardware.

Measures what Stage 1 will have to budget against: how fast the verifier walks a
set, how much memory a set and its occupancy bitmap need, and what the GPU adds
over the CPU.  The GPU and CPU verdicts are compared on every set -- a speed-up
that came with a different answer would be worthless.

The benchmark sets are built by products of sets we already have, so nothing here
is a search.  They are written to a scratch directory, not to the repository.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, VERIFY, read_set, write_set  # noqa: E402

TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-bench")
GPU = os.path.join(ROOT, "scripts", "verify_gpu")
os.makedirs(TMP, exist_ok=True)


def run_json(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode not in (0, 1):
        raise RuntimeError(" ".join(cmd) + "\n" + out.stderr)
    return json.loads(out.stdout)


def run_json_timed(cmd):
    """Same, but wrapped in /usr/bin/time -v so the peak RSS is measured, not guessed."""
    import time as _t
    t0 = _t.monotonic()
    out = subprocess.run(["/usr/bin/time", "-v", *cmd], capture_output=True, text=True)
    wall = _t.monotonic() - t0
    if out.returncode not in (0, 1):
        raise RuntimeError(" ".join(cmd) + "\n" + out.stderr)
    m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", out.stderr)
    r = json.loads(out.stdout)
    r["peak_rss_bytes"] = int(m.group(1)) * 1024 if m else None
    r["wall_seconds"] = wall
    return r


def main():
    n5, d5, R = read_set(os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))
    n10, d10, I10 = read_set(os.path.join(ROOT, "sets", "C7_d10_134753_itty_et_al.txt"))
    a1 = [(0,), (2,), (4,)]
    a2 = [tuple(x) for x in run_json([os.path.join(ROOT, "scripts", "mis"), "7", "2", "60", "--json"])["set"]]

    cases = []
    cases.append(("d5", os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt")))
    cases.append(("d10", os.path.join(ROOT, "sets", "C7_d10_134753_itty_et_al.txt")))
    p11 = write_set(os.path.join(TMP, "C7_d11_product.txt"), 7,
                    [x + y for x in I10 for y in a1], ["benchmark set: d10 x alpha(C_7), 404259 vertices"])
    cases.append(("d11", p11))
    p12 = write_set(os.path.join(TMP, "C7_d12_product.txt"), 7,
                    [x + y for x in I10 for y in a2], ["benchmark set: d10 x alpha(C_7^2), 1347530 vertices"])
    cases.append(("d12", p12))

    rep = {"cases": [], "host": {}}
    model = subprocess.run(["bash", "-lc", "lscpu | sed -n 's/^Model name: *//p' | head -1"],
                           capture_output=True, text=True).stdout.strip()
    rep["host"]["cpu"] = model
    rep["host"]["cpu_threads"] = os.cpu_count()
    rep["host"]["ram_bytes"] = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")

    for name, path in cases:
        n, d, rows = read_set(path)
        U = n ** d
        cpu = run_json_timed([VERIFY, path, "--json", "--repeat", "3"])
        entry = {
            "case": name, "n": n, "d": d, "size": len(rows),
            "universe": U,
            "set_bytes_on_disk": os.path.getsize(path),
            "set_bytes_in_core": len(rows) * d,
            "bitmap_bytes": (U + 7) // 8,
            "cpu": {
                "independent": cpu["independent"],
                "seconds": cpu["box_seconds"],
                "vertices_per_second": cpu["vertices_per_second"],
                "cells_per_second": cpu["cells_per_second"],
                "passes": cpu["box_passes"],
                "peak_rss_bytes": cpu["peak_rss_bytes"],
                "wall_seconds_3_repeats": cpu["wall_seconds"],
            },
        }
        if os.path.exists(GPU):
            try:
                g = run_json([GPU, path, "--json", "--repeat", "3"])
                entry["gpu"] = {
                    "device": g["device"], "independent": g["independent"],
                    "kernel_seconds": g["kernel_seconds"],
                    "vertices_per_second": g["vertices_per_second"],
                    "cells_per_second": g["cells_per_second"],
                    "bitmap_bytes": g["bitmap_bytes"],
                }
                entry["gpu_speedup_cells_per_second"] = round(
                    g["cells_per_second"] / cpu["cells_per_second"], 1)
                entry["gpu_agrees_with_cpu"] = g["independent"] == cpu["independent"]
            except Exception as e:                      # out of VRAM, no device, ...
                entry["gpu"] = {"error": str(e)[:300]}
                entry["gpu_agrees_with_cpu"] = None
        rep["cases"].append(entry)

    # the maximality sweep is the expensive one (3^d per vertex instead of 2^d)
    mx = run_json_timed([VERIFY, os.path.join(ROOT, "sets", "C7_d10_134753_itty_et_al.txt"),
                         "--json", "--maximal"])
    rep["maximality_sweep_d10"] = {
        "wall_seconds": mx["wall_seconds"], "independence_sweep_seconds": mx["box_seconds"],
        "addable": mx["addable_vertices"], "peak_rss_bytes": mx["peak_rss_bytes"],
        "neighbourhood_cells": 134753 * 3 ** 10,
        "note": "the maximality pass walks 3^d cells per vertex and dominates the wall clock"}
    rep["gpu_agreement"] = all(c.get("gpu_agrees_with_cpu") in (True, None) for c in rep["cases"])
    with open(os.path.join(ROOT, "results", "json", "bench.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
