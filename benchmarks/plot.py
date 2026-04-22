"""Render plots from the JSON result files produced by the other benchmark scripts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent


def plot_scaling(data: dict, out: Path) -> None:
    rows = data["rows"]
    ns = [r["n"] for r in rows]
    ts = [r["median_seconds"] * 1000 for r in rows]
    confs = [r["median_conflicts"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    for r in rows:
        xs = [r["n"]] * len(r["all_seconds"])
        ys = [s * 1000 for s in r["all_seconds"]]
        ax1.scatter(xs, ys, color="#3498db", alpha=0.35, s=30, zorder=2)
    ax1.plot(ns, ts, marker="o", linewidth=2, color="#1f618d", zorder=3, label="median")
    ax1.set_yscale("log")
    ax1.set_xlabel("variables (n)")
    ax1.set_ylabel("solve time (ms, log)")
    ax1.set_title(f"Scaling on random 3-SAT, ratio {data['ratio']}")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(loc="upper left")

    ax2.plot(ns, confs, marker="s", color="#c0392b", linewidth=2)
    ax2.set_yscale("log")
    ax2.set_xlabel("variables (n)")
    ax2.set_ylabel("median conflicts (log)")
    ax2.set_title("Conflicts to solve")
    ax2.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


def plot_ablation(data: dict, out: Path) -> None:
    labels_short = {
        "full": "full",
        "no_minimize": "no minimize",
        "no_vsids": "no VSIDS",
        "no_glucose": "no Glucose",
        "no_restart": "no restarts",
        "no_deletion": "no deletion",
    }
    summary = data["summary"]
    cfgs = [s["config"] for s in summary]
    slow = [s["geomean_slowdown_vs_full"] for s in summary]
    labels = [labels_short[c] for c in cfgs]

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    colors = ["#2ecc71" if c == "full" else "#3498db" for c in cfgs]
    bars = ax.bar(labels, slow, color=colors, edgecolor="black")
    ax.axhline(1.0, linestyle="--", color="gray", linewidth=1, label="full solver baseline")
    ax.set_yscale("log")
    ax.set_ylabel("geometric-mean slowdown vs full solver (log)")
    ax.set_title(
        f"Ablation at n={data['params']['n']}, "
        f"{data['params']['instances']} instances, ratio {data['params']['ratio']}"
    )
    for b, v in zip(bars, slow):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v * 1.08,
            f"{v:.2f}x",
            ha="center",
            fontsize=9,
        )
    ax.set_ylim(0.5, max(slow) * 1.6)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


def main() -> int:
    sc = json.loads((ROOT / "results_scaling.json").read_text())
    ab = json.loads((ROOT / "results_ablation.json").read_text())
    plot_scaling(sc, ROOT / "scaling.png")
    plot_ablation(ab, ROOT / "ablation.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
