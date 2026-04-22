from __future__ import annotations

import sys
import time

from satsolver import dimacs
from satsolver import mus as mus_mod
from satsolver.encoders import coloring, pigeonhole, queens, sudoku
from satsolver.solver import Solver


USAGE = """usage:
  python -m satsolver demo
  python -m satsolver sudoku <puzzle-file>
  python -m satsolver queens <N>
  python -m satsolver color <edges-file> <k>
  python -m satsolver pigeon <n>
  python -m satsolver dimacs <file.cnf>
  python -m satsolver mus <file.cnf>

global options:
  --proof <path>    emit DRAT proof to <path> (append mode)
"""


def _pop_proof(argv: list[str]) -> tuple[list[str], str | None]:
    path: str | None = None
    out: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == "--proof" and i + 1 < len(argv):
            path = argv[i + 1]
            i += 2
            continue
        out.append(argv[i])
        i += 1
    return out, path


def _make_solver(proof_path: str | None) -> tuple[Solver, object]:
    if proof_path is None:
        return Solver(), None
    f = open(proof_path, "w")
    return Solver(proof=f), f


def solve_and_report(
    label: str, clauses: list[list[int]], proof_path: str | None = None
) -> Solver:
    s, f = _make_solver(proof_path)
    for cl in clauses:
        s.add_clause(cl)
    t0 = time.perf_counter()
    sat = s.solve()
    dt = time.perf_counter() - t0
    if f is not None:
        f.close()
    verdict = "SAT" if sat else "UNSAT"
    print(f"  {label}: {verdict} in {dt*1000:.1f} ms  [{s.stats_line()}]")
    if proof_path is not None and not sat:
        print(f"  proof written to {proof_path}")
    return s


def cmd_sudoku(path: str, proof: str | None) -> int:
    with open(path) as f:
        puzzle = sudoku.parse(f.read())
    print("puzzle:")
    print(sudoku.pretty(puzzle))
    s = solve_and_report("sudoku", sudoku.encode(puzzle), proof)
    solved = sudoku.decode(s.model())
    print("solution:")
    print(sudoku.pretty(solved))
    return 0 if sudoku.verify(solved) else 1


def cmd_queens(n: int, proof: str | None) -> int:
    s = solve_and_report(f"queens N={n}", queens.encode(n), proof)
    placement = queens.decode(n, s.model())
    if n <= 20:
        print(queens.pretty(placement))
    else:
        print(f"placement: {placement}")
    return 0 if queens.verify(placement) else 1


def cmd_color(path: str, k: int, proof: str | None) -> int:
    with open(path) as f:
        num_nodes, edges = coloring.parse_edges(f.read())
    s = solve_and_report(f"k-color k={k}", coloring.encode(num_nodes, edges, k), proof)
    if len(s.assigns) != len(s.vars):
        print(f"no {k}-coloring exists")
        return 0
    colors = coloring.decode(num_nodes, k, s.model())
    print(f"colors: {colors}")
    return 0 if coloring.verify(num_nodes, edges, colors) else 1


def cmd_pigeon(n: int, proof: str | None) -> int:
    solve_and_report(f"PHP n={n}", pigeonhole.encode(n), proof)
    return 0


def cmd_dimacs(path: str, proof: str | None) -> int:
    with open(path) as f:
        clauses = dimacs.parse(f.read())
    solve_and_report(f"dimacs {path}", clauses, proof)
    return 0


def cmd_mus(path: str) -> int:
    with open(path) as f:
        clauses = dimacs.parse(f.read())
    print(f"input: {len(clauses)} clauses")
    result = mus_mod.extract(clauses)
    if result is None:
        print("formula is SATISFIABLE; no MUS exists")
        return 0
    print(f"MUS: {len(result)} clauses")
    print(dimacs.dump(result))
    return 0


def cmd_demo() -> int:
    from satsolver import demo as demo_mod
    return demo_mod.run()


def main(argv: list[str]) -> int:
    argv, proof = _pop_proof(list(argv))
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    cmd = argv[1]
    try:
        if cmd == "demo":
            return cmd_demo()
        if cmd == "sudoku":
            return cmd_sudoku(argv[2], proof)
        if cmd == "queens":
            return cmd_queens(int(argv[2]), proof)
        if cmd == "color":
            return cmd_color(argv[2], int(argv[3]), proof)
        if cmd == "pigeon":
            return cmd_pigeon(int(argv[2]), proof)
        if cmd == "dimacs":
            return cmd_dimacs(argv[2], proof)
        if cmd == "mus":
            return cmd_mus(argv[2])
    except (IndexError, FileNotFoundError, ValueError) as e:
        print(f"error: {e}")
        print(USAGE)
        return 2
    print(f"unknown command: {cmd}")
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    sys.exit(main(sys.argv))
