import io
import random

from satsolver import Solver


def _random_3sat(n, m, seed):
    rng = random.Random(seed)
    clauses = []
    for _ in range(m):
        cl = rng.sample(range(1, n + 1), 3)
        clauses.append([x if rng.random() < 0.5 else -x for x in cl])
    return clauses


def test_deletion_fires_on_hard_instance():
    s = Solver()
    s.reduce_limit = 200
    for cl in _random_3sat(120, int(120 * 4.26), seed=17):
        s.add_clause(cl)
    s.solve()
    assert s.deletions > 0


def test_deletion_does_not_break_correctness():
    for seed in [1, 2, 3]:
        clauses = _random_3sat(60, int(60 * 4.26), seed)
        s = Solver()
        s.reduce_limit = 50
        for cl in clauses:
            s.add_clause(cl)
        sat = s.solve()
        if sat:
            model = s.model()
            for cl in clauses:
                assert any(model.get(abs(l), False) == (l > 0) for l in cl)


def test_drat_emits_deletion_lines_when_reducing():
    buf = io.StringIO()
    s = Solver(proof=buf)
    s.reduce_limit = 50
    for cl in _random_3sat(80, int(80 * 4.26), seed=9):
        s.add_clause(cl)
    s.solve()
    deletes = [l for l in buf.getvalue().splitlines() if l.startswith("d ")]
    assert len(deletes) > 0


def test_locked_clauses_not_deleted():
    s = Solver()
    s.reduce_limit = 5
    clauses = [[1, 2], [-1, 2], [1, -2, 3], [-1, 2, 3], [-2, 3, 4], [-3, 4, 5],
               [-4, 5, 6], [-5, 6, 7], [-6, 7, 8]]
    for cl in clauses:
        s.add_clause(cl)
    s.solve()
    for ci in range(len(s.clauses)):
        if s.is_learned[ci] and s._locked(ci):
            assert not s.deleted[ci]
