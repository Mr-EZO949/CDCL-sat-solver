# satsolver

> Started in 2025 as a final project for a Computational Logic course; polished and published now.

A CDCL SAT solver in pure Python with encoders for classic NP problems,
a DRAT proof producer, an incremental API, a preprocessor, and a
deletion-based MUS extractor.

No external dependencies. Verified against a brute-force oracle on 500
random formulas and a 85-test suite covering propagation, learning,
backjumping, proofs, deletion, incremental solving, minimization, and MUS.

## Features

- **Two-watched-literal** unit propagation with blocker literals
- **1-UIP** conflict analysis with non-chronological backjumping
- **VSIDS** branching with activity decay and phase saving
- **Luby** restart schedule plus **Glucose-style adaptive restart** on the LBD window
- **Recursive clause minimization** (Sörensson–Biere) — shortens learnt clauses by 25% on random 3-SAT
- **LBD-based clause deletion** with locked-clause preservation
- **DRAT proof emission** (additions and deletions) for UNSAT certificates
- **Incremental solving** — `add_clause` between `solve` calls, IPASIR-style assumptions
- **Preprocessor** — subsumption, self-subsuming resolution, unit-propagation fixpoint
- **Deletion-based MUS extraction** via selector variables and assumptions
- **Encoders** — Sudoku, N-Queens, graph k-coloring, pigeonhole (with Sinz sequential counter for at-most-one)

## Running

```
python -m satsolver demo
python -m satsolver sudoku examples/hardest.sudoku
python -m satsolver queens 40
python -m satsolver color examples/petersen.edges 3
python -m satsolver pigeon 6
python -m satsolver dimacs some_file.cnf
python -m satsolver mus some_file.cnf
```

Any command accepts `--proof <path>` to emit a DRAT proof of UNSAT.

## Layout

```
satsolver/
  solver.py           CDCL core
  preprocess.py       subsumption, self-subsuming resolution, unit propagation
  mus.py              minimal-unsatisfiable-subset extraction
  cardinality.py      at-least/most-k helpers (Sinz, totalizer)
  dimacs.py           DIMACS CNF parser and dumper
  cli.py              command-line entry point
  demo.py             self-verifying demo suite
  encoders/           sudoku, queens, coloring, pigeonhole
benchmarks/           ablation, scaling, minimization study, plots
examples/             sample inputs
tests/                85 tests
```

## Benchmarks

See [benchmarks/README.md](benchmarks/README.md) for the full writeup.
Headline numbers on random 3-SAT at the phase transition (ratio 4.26):

| claim | number |
|---|---|
| VSIDS speedup vs naive branching (n=140) | **20.9× geomean** |
| Clause-minimization reduction in learnt length | **25.1%** |
| Luby restart speedup | 26% |

## Tests

```
python -m pytest -q
```

Includes a brute-force equivalence check: 500 random formulas, each
solved by the CDCL solver and a DPLL-free enumeration oracle, asserted
equal on every instance.
