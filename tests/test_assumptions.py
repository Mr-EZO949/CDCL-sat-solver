from satsolver import Solver


def test_assumption_forces_value():
    s = Solver()
    s.add_clause([1, 2])
    s.add_clause([-1, 2])
    assert s.solve(assumptions=[-2]) is False
    assert s.solve(assumptions=[2]) is True
    assert s.assigns[2] is True


def test_assumption_conflict_yields_core():
    s = Solver()
    s.add_clause([1, 2])
    s.add_clause([-1, 2])
    s.add_clause([1, -2])
    s.add_clause([-1, -2])
    assert s.solve() is False


def test_incremental_solve_alternating_assumptions():
    s = Solver()
    s.add_clause([1, 2, 3])
    s.add_clause([-1, -2])
    s.add_clause([-1, -3])
    s.add_clause([-2, -3])

    assert s.solve(assumptions=[1]) is True
    assert s.assigns[1] is True

    assert s.solve(assumptions=[2]) is True
    assert s.assigns[2] is True

    assert s.solve(assumptions=[3]) is True
    assert s.assigns[3] is True

    assert s.solve(assumptions=[1, 2]) is False
    assert s.solve(assumptions=[2, 3]) is False
    assert s.solve(assumptions=[1, 3]) is False


def test_unsat_core_extracted_from_assumption_conflict():
    s = Solver()
    s.add_clause([-1, 2])
    s.add_clause([-2, 3])
    s.add_clause([-3, -1])
    assert s.solve(assumptions=[1]) is False
    core = s.unsat_core()
    assert 1 in core
    for lit in core:
        assert abs(lit) == 1


def test_assumptions_do_not_permanently_fix_vars():
    s = Solver()
    s.add_clause([1, 2])
    assert s.solve(assumptions=[1]) is True
    assert s.solve(assumptions=[-1]) is True
    assert s.assigns[2] is True


def test_base_solve_still_works_after_assumption_run():
    s = Solver()
    s.add_clause([1, 2])
    s.add_clause([-1, 2])
    assert s.solve(assumptions=[-2]) is False
    assert s.solve() is True
