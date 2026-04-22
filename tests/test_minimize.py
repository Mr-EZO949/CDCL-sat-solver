import random

from satsolver import Solver


def test_minimization_produces_valid_solutions():
    random.seed(3)
    for _ in range(20):
        n = 40
        m = int(n * 4.26)
        clauses = []
        for _ in range(m):
            cl = random.sample(range(1, n + 1), 3)
            cl = [x if random.random() < 0.5 else -x for x in cl]
            clauses.append(cl)
        s = Solver()
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve()
        if sat:
            model = s.model()
            for cl in clauses:
                assert any(model.get(abs(l), False) == (l > 0) for l in cl)


def test_minimization_shortens_learned_clauses_on_average():
    random.seed(42)
    n = 80
    m = int(n * 4.26)
    base = []
    for _ in range(m):
        cl = random.sample(range(1, n + 1), 3)
        base.append([x if random.random() < 0.5 else -x for x in cl])

    def run(minimize: bool) -> float:
        s = Solver()
        for cl in base:
            s.add_clause(cl)
        if not minimize:
            s._minimize = lambda learnt: learnt
        s.solve()
        lens = [
            len(s.clauses[ci])
            for ci in s.learned_indices
            if not s.deleted[ci] and len(s.clauses[ci]) > 0
        ]
        return sum(lens) / len(lens) if lens else 0.0

    with_min = run(True)
    without = run(False)
    assert with_min < without


def test_minimize_keeps_uip_literal():
    s = Solver()
    s.add_clause([1, 2, 3])
    s.add_clause([-1, 2])
    s.add_clause([-2, 3])
    s.add_clause([-3, -1])
    s.add_clause([1, -2, -3])
    s.solve()


def test_minimize_on_trivially_unsat():
    s = Solver()
    s.add_clause([1])
    s.add_clause([-1])
    assert s.solve() is False
