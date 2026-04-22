"""Measures the effect of recursive clause minimization on learned-clause length.

Re-runs the same random 3-SAT formulas with minimization on and off, averages
the learned-clause length, and reports the percentage reduction.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks._common import random_3sat
from satsolver import Solver


def avg_learnt_len(clauses: list[list[int]], minimize: bool) -> tuple[float, int]:
    s = Solver()
    if not minimize:
        s._minimize = lambda learnt: learnt
    for cl in clauses:
        s.add_clause(cl)
    s.solve()
    lens = [
        len(s.clauses[ci])
        for ci in s.learned_indices
        if not s.deleted[ci] and len(s.clauses[ci]) > 0
    ]
    if not lens:
        return 0.0, 0
    return sum(lens) / len(lens), len(lens)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--instances", type=int, default=20)
    ap.add_argument("--ratio", type=float, default=4.26)
    ap.add_argument("--out", type=str, default="benchmarks/results_minimize.json")
    args = ap.parse_args()

    print(f"{'seed':>6s} {'with_min':>10s} {'without':>10s} {'reduction':>10s}")
    print("-" * 44)

    rows = []
    with_sum = without_sum = 0.0
    with_count = without_count = 0

    for i in range(args.instances):
        seed = 2000 + i
        cl = random_3sat(args.n, args.ratio, seed)
        with_avg, with_n = avg_learnt_len(cl, minimize=True)
        without_avg, without_n = avg_learnt_len(cl, minimize=False)
        reduction = (1 - with_avg / without_avg) * 100 if without_avg else 0.0
        rows.append({
            "seed": seed,
            "with_min_avg_len": with_avg,
            "without_min_avg_len": without_avg,
            "reduction_pct": reduction,
        })
        with_sum += with_avg * with_n
        without_sum += without_avg * without_n
        with_count += with_n
        without_count += without_n
        print(f"{seed:>6d} {with_avg:>10.2f} {without_avg:>10.2f} {reduction:>9.1f}%")

    overall_with = with_sum / with_count if with_count else 0.0
    overall_without = without_sum / without_count if without_count else 0.0
    overall_reduction = (1 - overall_with / overall_without) * 100 if overall_without else 0.0

    print("-" * 44)
    print(f"{'all':>6s} {overall_with:>10.2f} {overall_without:>10.2f} {overall_reduction:>9.1f}%")
    print()
    print(f"Overall: minimization shortens learned clauses by {overall_reduction:.1f}% on average")
    print(f"         ({overall_without:.2f} lits → {overall_with:.2f} lits, averaged over "
          f"{with_count} + {without_count} clauses across {args.instances} instances)")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({
            "params": {"n": args.n, "instances": args.instances, "ratio": args.ratio},
            "overall_with": overall_with,
            "overall_without": overall_without,
            "overall_reduction_pct": overall_reduction,
            "per_instance": rows,
        }, f, indent=2)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
