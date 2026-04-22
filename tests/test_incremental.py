from satsolver import Solver


def test_add_clause_between_solve_calls_sat():
    s = Solver()
    s.add_clause([1, 2])
    assert s.solve() is True

    s.add_clause([-1])
    assert s.solve() is True
    assert s.assigns[1] is False
    assert s.assigns[2] is True


def test_add_clause_between_solve_calls_becomes_unsat():
    s = Solver()
    s.add_clause([1, 2])
    s.add_clause([-1, 2])
    assert s.solve() is True

    s.add_clause([-2])
    assert s.solve() is False


def test_add_clause_after_sat_preserves_learned_clauses():
    s = Solver()
    s.add_clause([1, 2, 3])
    s.add_clause([-1, -2])
    s.add_clause([-1, -3])
    s.add_clause([-2, -3])
    assert s.solve() is True

    clauses_before = len(s.clauses)
    s.add_clause([4, 5])
    assert s.solve() is True
    assert len(s.clauses) >= clauses_before


def test_add_clause_and_assumptions_interleaved():
    s = Solver()
    s.add_clause([1, 2])
    s.add_clause([-1, 2])
    assert s.solve(assumptions=[-2]) is False
    assert s.solve() is True

    s.add_clause([3, 4])
    assert s.solve(assumptions=[-3]) is True
    assert s.assigns[4] is True


def test_empty_clause_added_incrementally_is_permanent_unsat():
    s = Solver()
    s.add_clause([1, 2])
    assert s.solve() is True
    s.add_clause([])
    assert s.solve() is False
    assert s.solve() is False
