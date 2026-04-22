from satsolver import Solver


def _solve(clauses):
    s = Solver()
    for cl in clauses:
        s.add_clause(cl)
    return s, s.solve()


def _model_satisfies(clauses, model):
    for cl in clauses:
        if not any(model.get(abs(l), False) == (l > 0) for l in cl):
            return False
    return True


def test_empty_formula_is_sat():
    s = Solver()
    assert s.solve() is True


def test_empty_clause_is_unsat():
    s, sat = _solve([[]])
    assert sat is False


def test_single_unit_clause():
    s, sat = _solve([[1]])
    assert sat is True
    assert s.assigns[1] is True


def test_conflicting_units_is_unsat():
    _, sat = _solve([[1], [-1]])
    assert sat is False


def test_tautology_is_dropped():
    s, sat = _solve([[1, -1]])
    assert sat is True


def test_duplicate_literals_are_normalised():
    s, sat = _solve([[1, 1, 1], [-1, -1]])
    assert sat is False


def test_simple_sat_formula():
    clauses = [[1, 2], [-1, 2], [1, -2]]
    s, sat = _solve(clauses)
    assert sat is True
    assert _model_satisfies(clauses, s.model())


def test_simple_unsat_formula():
    _, sat = _solve([[1, 2], [-1, 2], [1, -2], [-1, -2]])
    assert sat is False


def test_chain_of_implications():
    clauses = [[1], [-1, 2], [-2, 3], [-3, 4], [-4, 5]]
    s, sat = _solve(clauses)
    assert sat is True
    for v in range(1, 6):
        assert s.assigns[v] is True


def test_model_is_complete_for_all_vars():
    clauses = [[1, 2, 3], [-1, -2, -3], [1, -2], [-1, 2, 3]]
    s, sat = _solve(clauses)
    assert sat is True
    for v in (1, 2, 3):
        assert v in s.model()
    assert _model_satisfies(clauses, s.model())


def test_large_horn_chain_resolves_by_unit_propagation():
    clauses = [[1]]
    for v in range(1, 200):
        clauses.append([-v, v + 1])
    s, sat = _solve(clauses)
    assert sat is True
    assert s.assigns[200] is True
    assert s.conflicts == 0


def test_stats_reports_decisions_and_conflicts():
    clauses = [[1, 2], [-1, 2], [1, -2], [-1, -2]]
    s, _ = _solve(clauses)
    stats = s.stats()
    assert stats["conflicts"] >= 1
    assert stats["vars"] == 2


def test_luby_sequence():
    expected = [1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8]
    for i, v in enumerate(expected):
        assert Solver.luby(i) == v, (i, Solver.luby(i), v)
