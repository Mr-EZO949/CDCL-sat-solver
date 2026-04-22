import itertools
import random

from satsolver import Solver


def brute_force(clauses, n):
    for bits in itertools.product([False, True], repeat=n):
        ok = True
        for cl in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in cl):
                ok = False
                break
        if ok:
            return True, bits
    return False, None


def model_satisfies(clauses, model):
    for cl in clauses:
        if not any(model.get(abs(l), False) == (l > 0) for l in cl):
            return False
    return True


def test_agrees_with_brute_force_on_500_random_formulas():
    random.seed(42)
    for trial in range(500):
        n = random.randint(3, 8)
        m = random.randint(n, 4 * n)
        clauses = []
        for _ in range(m):
            k = random.randint(1, 3)
            vs = random.sample(range(1, n + 1), k)
            clauses.append([v if random.random() < 0.5 else -v for v in vs])

        bf_sat, _ = brute_force(clauses, n)

        s = Solver()
        for cl in clauses:
            s.add_clause(cl)
        solver_sat = s.solve()

        assert bf_sat == solver_sat, f"trial {trial}: clauses={clauses}"
        if solver_sat:
            assert model_satisfies(clauses, s.model()), f"trial {trial}"


def test_agrees_with_brute_force_on_unsat_heavy_sample():
    random.seed(7)
    n = 6
    for trial in range(200):
        m = random.randint(20, 40)
        clauses = []
        for _ in range(m):
            vs = random.sample(range(1, n + 1), 3)
            clauses.append([v if random.random() < 0.5 else -v for v in vs])

        bf_sat, _ = brute_force(clauses, n)
        s = Solver()
        for cl in clauses:
            s.add_clause(cl)
        assert bf_sat == s.solve(), f"trial {trial}: clauses={clauses}"
