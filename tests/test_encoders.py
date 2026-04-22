import pytest

from satsolver import Solver
from satsolver.encoders import coloring, pigeonhole, queens, sudoku


def solve(clauses):
    s = Solver()
    for cl in clauses:
        s.add_clause(cl)
    sat = s.solve()
    return sat, s.model()


EASY = (
    "53..7...."
    "6..195..."
    ".98....6."
    "8...6...3"
    "4..8.3..1"
    "7...2...6"
    ".6....28."
    "...419..5"
    "....8..79"
)

HARDEST = (
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


def test_sudoku_parse_roundtrip():
    g = sudoku.parse(EASY)
    assert len(g) == 9 and all(len(r) == 9 for r in g)
    assert g[0][0] == 5
    assert g[0][2] == 0


def test_sudoku_parse_rejects_wrong_length():
    with pytest.raises(ValueError):
        sudoku.parse("123")


def test_sudoku_easy_solves_and_verifies():
    sat, model = solve(sudoku.encode(sudoku.parse(EASY)))
    assert sat
    solved = sudoku.decode(model)
    assert sudoku.verify(solved)


def test_sudoku_hardest_solves_and_verifies():
    sat, model = solve(sudoku.encode(sudoku.parse(HARDEST)))
    assert sat
    solved = sudoku.decode(model)
    assert sudoku.verify(solved)
    puzzle = sudoku.parse(HARDEST)
    for r in range(9):
        for c in range(9):
            if puzzle[r][c]:
                assert solved[r][c] == puzzle[r][c]


def test_sudoku_unsolvable_is_unsat():
    puzzle = [[0] * 9 for _ in range(9)]
    puzzle[0][0] = 1
    puzzle[0][1] = 1
    sat, _ = solve(sudoku.encode(puzzle))
    assert not sat


@pytest.mark.parametrize("n", [1, 4, 5, 6, 8, 10])
def test_queens_solvable(n):
    sat, model = solve(queens.encode(n))
    assert sat
    assert queens.verify(queens.decode(n, model))


@pytest.mark.parametrize("n", [2, 3])
def test_queens_unsolvable(n):
    sat, _ = solve(queens.encode(n))
    assert not sat


def test_petersen_is_3_colorable():
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
        (5, 7), (7, 9), (9, 6), (6, 8), (8, 5),
        (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
    ]
    sat, model = solve(coloring.encode(10, edges, 3))
    assert sat
    assert coloring.verify(10, edges, coloring.decode(10, 3, model))


def test_petersen_is_not_2_colorable():
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    sat, _ = solve(coloring.encode(5, edges, 2))
    assert not sat


def test_k4_needs_4_colors():
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    assert not solve(coloring.encode(4, edges, 3))[0]
    sat, model = solve(coloring.encode(4, edges, 4))
    assert sat
    assert coloring.verify(4, edges, coloring.decode(4, 4, model))


def test_bipartite_is_2_colorable():
    edges = [(0, 2), (0, 3), (1, 2), (1, 3)]
    sat, model = solve(coloring.encode(4, edges, 2))
    assert sat
    colors = coloring.decode(4, 2, model)
    assert colors[0] == colors[1]
    assert colors[2] == colors[3]
    assert colors[0] != colors[2]


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_pigeonhole_is_unsat(n):
    assert not solve(pigeonhole.encode(n))[0]


def test_coloring_parse_edges():
    text = "# comment\n0 1\n1 2\n\n2 0\n"
    n, edges = coloring.parse_edges(text)
    assert n == 3
    assert edges == [(0, 1), (1, 2), (2, 0)]
