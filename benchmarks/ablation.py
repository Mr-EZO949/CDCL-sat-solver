"""Ablation study: how much does each CDCL feature contribute?

Runs N random 3-SAT instances at the phase transition (ratio 4.26) with
each feature individually disabled, and reports the geometric-mean slowdown
vs the full solver. Geometric mean is the right average for ratios.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks._common import random_3sat, run_once


CONFIGS = ["full", "no_minimize", "no_vsids", "no_glucose", "no_restart", "no_deletion"]

LABELS = {
    "full": "full solver",
    "no_minimize": "no clause minimization",
    "no_vsids": "no VSIDS (lowest-index branching)",
    "no_glucose": "no Glucose LBD restart (Luby only)",
    "no_restart": "no restarts at all",
    "no_deletion": "no LBD-based clause deletion",
}


def geomean(xs: list[float]) -> float:
    xs = [x for x in xs if x > 0]
    if not xs:
        return 0.0
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=80, help="variables per instance")
    ap.add_argument("--instances", type=int, default=20)
    ap.add_argument("--ratio", type=float, default=4.26)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", type=str, default="benchmarks/results_ablation.json")
    args = ap.parse_args()

    seeds = list(range(args.seed, args.seed + args.instances))
    formulas = [random_3sat(args.n, args.ratio, s) for s in seeds]

    results: dict[str, list[dict]] = {cfg: [] for cfg in CONFIGS}

    for idx, clauses in enumerate(formulas):
        print(f"instance {idx+1}/{len(formulas)} (seed={seeds[idx]}, n={args.n}, m={len(clauses)})")
        baseline = None
        for cfg in CONFIGS:
            r = run_once(clauses, cfg)
            row = {
                "seed": seeds[idx],
                "config": cfg,
                "sat": r.sat,
                "seconds": r.seconds,
                "conflicts": r.conflicts,
                "decisions": r.decisions,
                "propagations": r.propagations,
                "restarts": r.restarts,
                "deletions": r.deletions,
                "solved": r.solved,
            }
            results[cfg].append(row)
            if cfg == "full":
                baseline = r
            marker = "" if r.solved else "  (TIMEOUT/ERROR)"
            print(f"  {cfg:<14s} t={r.seconds*1000:8.1f}ms  conflicts={r.conflicts:6d}{marker}")

    print()
    print("=" * 78)
    print(f"{'config':<34s} {'median t (ms)':>14s} {'median conflicts':>18s} {'slowdown (gmean)':>18s}")
    print("-" * 78)

    summary: list[dict] = []
    n_inst = len(formulas)

    def median(xs):
        xs = sorted(xs)
        k = len(xs)
        if k == 0:
            return 0.0
        return (xs[k//2] if k % 2 else (xs[k//2 - 1] + xs[k//2]) / 2)

    for cfg in CONFIGS:
        rows = results[cfg]
        times = [r["seconds"] for r in rows]
        confs = [r["conflicts"] for r in rows]
        full_times = [r["seconds"] for r in results["full"]]
        ratios = []
        for a, b in zip(times, full_times):
            if b > 0:
                ratios.append(a / b)
        slowdown = geomean(ratios) if cfg != "full" else 1.0
        entry = {
            "config": cfg,
            "label": LABELS[cfg],
            "median_seconds": median(times),
            "median_conflicts": median(confs),
            "geomean_slowdown_vs_full": slowdown,
        }
        summary.append(entry)
        print(
            f"{LABELS[cfg]:<34s} {median(times)*1000:>14.1f} {int(median(confs)):>18d} {slowdown:>17.2f}x"
        )

    print("=" * 78)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({
            "params": {"n": args.n, "instances": args.instances, "ratio": args.ratio, "seed": args.seed},
            "summary": summary,
            "per_instance": results,
        }, f, indent=2)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
