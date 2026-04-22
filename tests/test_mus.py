from satsolver import Solver
from satsolver.mus import extract


def _is_unsat(clauses):
    s = Solver()
    for cl in clauses:
        s.add_clause(cl)
    return s.solve() is False


def test_mus_of_satisfiable_returns_none():
    assert extract([[1, 2], [-1, 2]]) is None


def test_mus_drops_unrelated_clause():
    cs = [[1, 2], [-1, 2], [1, -2], [-1, -2], [3, 4]]
    mus = extract(cs)
    assert mus is not None
    assert [3, 4] not in mus
    assert len(mus) == 4
    assert _is_unsat(mus)


def test_mus_of_pigeonhole_is_entire_formula():
    cs = [[1], [2], [-1, -2]]
    mus = extract(cs)
    assert mus is not None
    assert _is_unsat(mus)
    for i in range(len(mus)):
        remaining = mus[:i] + mus[i + 1:]
        assert not _is_unsat(remaining)


def test_mus_is_minimal_not_just_unsat():
    cs = [[1, 2], [-1, 2], [1, -2], [-1, -2], [1, 2, 3], [-3, 1]]
    mus = extract(cs)
    assert mus is not None
    assert _is_unsat(mus)
    for i in range(len(mus)):
        remaining = mus[:i] + mus[i + 1:]
        assert not _is_unsat(remaining), f"clause {mus[i]} is redundant in returned MUS"


def test_mus_of_empty_formula_returns_none():
    assert extract([]) is None
