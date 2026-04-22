from __future__ import annotations

import random
import time
from dataclasses import dataclass

from satsolver import Solver


def random_3sat(n: int, ratio: float, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    m = int(n * ratio)
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return clauses


@dataclass
class Run:
    solved: bool
    sat: bool
    seconds: float
    conflicts: int
    decisions: int
    propagations: int
    restarts: int
    deletions: int
    learned_units: int


def run_once(
    clauses: list[list[int]],
    config: str = "full",
    time_budget_s: float = 60.0,
) -> Run:
    s = Solver()

    if config == "no_minimize":
        s._minimize = lambda learnt: learnt
    elif config == "no_vsids":
        def first_unassigned() -> int | None:
            for v in sorted(s.vars):
                if v not in s.assigns:
                    return v
            return None
        s.pick_branching_var = first_unassigned
    elif config == "no_restart":
        s.luby = staticmethod(lambda i: 10**18)
        s._glucose_trigger = lambda recent_required=50: False
    elif config == "no_glucose":
        s._glucose_trigger = lambda recent_required=50: False
    elif config == "no_deletion":
        s.reduce_limit = 10**18
    elif config == "full":
        pass
    else:
        raise ValueError(f"unknown config {config}")

    for cl in clauses:
        s.add_clause(cl)

    t0 = time.perf_counter()
    try:
        sat = s.solve()
        dt = time.perf_counter() - t0
        return Run(
            solved=True,
            sat=bool(sat),
            seconds=dt,
            conflicts=s.conflicts,
            decisions=s.decisions,
            propagations=s.propagations,
            restarts=s.restarts,
            deletions=s.deletions,
            learned_units=s.learned_units,
        )
    except RecursionError:
        dt = time.perf_counter() - t0
        return Run(
            solved=False, sat=False, seconds=dt,
            conflicts=s.conflicts, decisions=s.decisions,
            propagations=s.propagations, restarts=s.restarts,
            deletions=s.deletions, learned_units=s.learned_units,
        )
