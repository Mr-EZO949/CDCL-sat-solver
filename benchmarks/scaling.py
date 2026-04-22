"""Scaling curve: solve time vs problem size on random 3-SAT at ratio 4.26.

Reports median solve time over K instances at each N, so one bad instance
does not dominate. Random 3-SAT at ratio 4.26 sits near the SAT/UNSAT phase
transition where instances are hardest.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks._common import random_3sat, run_once


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=str, default="30,50,70,90,110,130,150")
    ap.add_argument("--instances", type=int, default=10)
    ap.add_argument("--ratio", type=float, default=4.26)
    ap.add_argument("--out", type=str, default="benchmarks/results_scaling.json")
    args = ap.parse_args()

    sizes = [int(s) for s in args.sizes.split(",")]

    def median(xs):
        xs = sorted(xs)
        k = len(xs)
        if k == 0:
            return 0.0
        return (xs[k//2] if k % 2 else (xs[k//2 - 1] + xs[k//2]) / 2)

    rows = []
    print(f"{'n':>5s} {'m':>6s} {'median_ms':>12s} {'median_conf':>12s} {'sat_frac':>9s}")
    print("-" * 50)
    for n in sizes:
        times = []
        confs = []
        sat_count = 0
        for i in range(args.instances):
            cl = random_3sat(n, args.ratio, seed=1000 + n * 100 + i)
            t0 = time.perf_counter()
            r = run_once(cl, "full")
            times.append(r.seconds)
            confs.append(r.conflicts)
            if r.sat:
                sat_count += 1
        row = {
            "n": n,
            "m": int(n * args.ratio),
            "median_seconds": median(times),
            "median_conflicts": median(confs),
            "sat_fraction": sat_count / args.instances,
            "all_seconds": times,
        }
        rows.append(row)
        print(
            f"{n:>5d} {int(n*args.ratio):>6d} "
            f"{median(times)*1000:>12.1f} "
            f"{int(median(confs)):>12d} "
            f"{sat_count/args.instances:>9.2f}"
        )

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"ratio": args.ratio, "instances": args.instances, "rows": rows}, f, indent=2)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
