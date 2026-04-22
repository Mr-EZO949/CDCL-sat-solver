from satsolver import Solver
from satsolver.preprocess import (
    preprocess,
    self_subsume,
    subsume,
    unit_propagate_fixpoint,
)


def test_subsume_drops_superset_clauses():
    cs = [[1, 2], [1, 2, 3], [1, 2, -3, 4], [5, 6]]
    out = subsume(cs)
    sets = [frozenset(c) for c in out]
    assert frozenset([1, 2]) in sets
    assert frozenset([5, 6]) in sets
    assert frozenset([1, 2, 3]) not in sets


def test_subsume_keeps_unrelated_clauses():
    cs = [[1, 2], [3, 4], [5, 6]]
    assert len(subsume(cs)) == 3


def test_self_subsume_strengthens():
    cs = [[1, 2], [-1, 2, 3]]
    out = [frozenset(c) for c in self_subsume(cs)]
    assert frozenset([2, 3]) in out
    assert frozenset([-1, 2, 3]) not in out


def test_self_subsume_drops_tautologies():
    cs = [[1, 2], [1, -1, 2]]
    out = self_subsume(cs)
    sets = [frozenset(c) for c in out]
    assert frozenset([1, -1, 2]) not in sets


def test_unit_prop_eliminates_satisfied_clauses():
    cs = [[1], [-1, 2], [-2, 3], [3, 4, 5]]
    out = unit_propagate_fixpoint(cs)
    assert out == []


def test_unit_prop_detects_conflict():
    assert unit_propagate_fixpoint([[1], [-1]]) is None


def test_preprocess_preserves_satisfiability():
    import random
    random.seed(11)
    n = 30
    m = int(n * 4.0)
    clauses = []
    for _ in range(m):
        cl = random.sample(range(1, n + 1), 3)
        clauses.append([x if random.random() < 0.5 else -x for x in cl])

    s1 = Solver()
    for cl in clauses:
        s1.add_clause(cl)
    orig = s1.solve()

    pre = preprocess(clauses)
    if pre is None:
        assert orig is False
        return
    s2 = Solver()
    for cl in pre:
        s2.add_clause(cl)
    assert s2.solve() is orig


def test_preprocess_shrinks_typical_instance():
    cs = [[1, 2], [1, 2, 3], [1, 2, 3, 4], [-1, 2], [-1, 2, 5], [5]]
    out = preprocess(cs)
    assert out is not None
    assert len(out) < len(cs)
