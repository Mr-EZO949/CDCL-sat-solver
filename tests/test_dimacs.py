from satsolver import Solver, dimacs


def test_parse_basic():
    text = """
c a comment
p cnf 3 2
1 -3 0
2 3 -1 0
"""
    assert dimacs.parse(text) == [[1, -3], [2, 3, -1]]


def test_parse_ignores_blank_and_percent_lines():
    text = "p cnf 1 1\n\n%\n1 0\n"
    assert dimacs.parse(text) == [[1]]


def test_parse_handles_clauses_spanning_lines():
    text = "1 2 3\n-1 -2\n0\n4 0\n"
    assert dimacs.parse(text) == [[1, 2, 3, -1, -2], [4]]


def test_dump_roundtrip():
    clauses = [[1, -2, 3], [-1, 2], [3]]
    text = dimacs.dump(clauses)
    parsed = dimacs.parse(text)
    assert parsed == clauses


def test_end_to_end_solve_from_dimacs():
    text = "p cnf 3 3\n1 2 3 0\n-1 -2 0\n-1 -3 0\n"
    clauses = dimacs.parse(text)
    s = Solver()
    for cl in clauses:
        s.add_clause(cl)
    assert s.solve() is True
