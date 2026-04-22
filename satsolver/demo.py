from __future__ import annotations

import random
import time

from satsolver.encoders import coloring, pigeonhole, queens, sudoku
from satsolver.solver import Solver


HARDEST_SUDOKU = (
    "8........"
    "..36....."
    ".7..9.2.."
    ".5...7..."
    "....457.."
    "...1...3."
    "..1....68"
    "..85...1."
    ".9....4.."
)

PETERSEN_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
    (5, 7), (7, 9), (9, 6), (6, 8), (8, 5),
    (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
]

K4_EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def _solve(label: str, clauses: list[list[int]]) -> tuple[Solver, bool, float]:
    s = Solver()
    for cl in clauses:
        s.add_clause(cl)
    t0 = time.perf_counter()
    sat = s.solve()
    dt = time.perf_counter() - t0
    verdict = "SAT" if sat else "UNSAT"
    print(f"  {label}: {verdict} in {dt*1000:.1f} ms  [{s.stats_line()}]")
    return s, sat, dt


def _header(title: str) -> None:
    print("=" * 68)
    print(title)
    print("=" * 68)


def run() -> int:
    failures = 0

    _header("Sudoku (Arto Inkala's 'hardest', 2012)")
    puzzle = sudoku.parse(HARDEST_SUDOKU)
    print(sudoku.pretty(puzzle))
    s, sat, _ = _solve("sudoku", sudoku.encode(puzzle))
    solved = sudoku.decode(s.model())
    print(sudoku.pretty(solved))
    if not (sat and sudoku.verify(solved)):
        print("  FAIL: sudoku solution did not verify")
        failures += 1
    else:
        print("  verified by independent checker")
    print()

    _header("N-queens")
    for n in (8, 20, 40):
        s, sat, _ = _solve(f"queens N={n}", queens.encode(n))
        placement = queens.decode(n, s.model())
        if not (sat and queens.verify(placement)):
            print(f"  FAIL: invalid placement for N={n}")
            failures += 1
        elif n == 8:
            print(queens.pretty(placement))
    print()

    _header("Graph 3-coloring")
    s, sat, _ = _solve("Petersen, k=3", coloring.encode(10, PETERSEN_EDGES, 3))
    colors = coloring.decode(10, 3, s.model())
    if sat and coloring.verify(10, PETERSEN_EDGES, colors):
        print(f"  node colors: {colors}")
    else:
        print("  FAIL: coloring violates an edge")
        failures += 1

    s, sat, _ = _solve("K4, k=3", coloring.encode(4, K4_EDGES, 3))
    if sat:
        print("  FAIL: K4 was falsely reported SAT with 3 colors")
        failures += 1
    print()

    _header("Pigeonhole (UNSAT, resolution-hard)")
    for n in (4, 5, 6):
        _, sat, _ = _solve(f"PHP n={n} ({n+1} pigeons, {n} holes)", pigeonhole.encode(n))
        if sat:
            print(f"  FAIL: PHP n={n} should be UNSAT")
            failures += 1
    print()

    _header("Random 3-SAT near phase transition (ratio 4.26)")
    random.seed(1234)
    for n_vars in (60, 100, 150):
        n_clauses = int(n_vars * 4.26)
        clauses: list[list[int]] = []
        while len(clauses) < n_clauses:
            vs = random.sample(range(1, n_vars + 1), 3)
            clauses.append([v if random.random() < 0.5 else -v for v in vs])
        _solve(f"random 3-SAT n={n_vars} m={n_clauses}", clauses)
    print()

    _header("result")
    if failures == 0:
        print("ALL DEMOS PASSED — every SAT result independently verified.")
    else:
        print(f"DEMO FAILURES: {failures}")
    return 0 if failures == 0 else 1
