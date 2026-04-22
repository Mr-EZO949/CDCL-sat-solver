from itertools import combinations

from satsolver import Solver, cardinality


def _make_fresh(start: int):
    counter = [start - 1]

    def fresh() -> int:
        counter[0] += 1
        return counter[0]

    return fresh


def _count_models(clauses, nvars, projection):
    models = set()

    def recurse(i, assign):
        if i > nvars:
            for cl in clauses:
                if not any(assign.get(abs(l), False) == (l > 0) for l in cl):
                    return
            key = tuple(assign.get(v, False) for v in projection)
            models.add(key)
            return
        assign[i] = True
        recurse(i + 1, assign)
        assign[i] = False
        recurse(i + 1, assign)
        del assign[i]

    recurse(1, {})
    return models


def test_sinz_at_most_one_agrees_with_pairwise_semantically():
    lits = [1, 2, 3, 4, 5, 6]
    nvars = len(lits)
    pw = cardinality.at_most_one_pairwise(lits)
    fresh = _make_fresh(nvars + 1)
    seq = cardinality.at_most_one_sequential(lits, fresh)

    pw_models = _count_models(pw, nvars, lits)
    seq_models = _count_models(seq, nvars + (nvars - 1), lits)
    assert pw_models == seq_models
    assert len(pw_models) == nvars + 1


def test_sinz_encoding_is_linear_size():
    lits = list(range(1, 21))
    fresh = _make_fresh(100)
    seq = cardinality.at_most_one_sequential(lits, fresh)
    pw = cardinality.at_most_one_pairwise(lits)
    assert len(seq) <= 3 * len(lits)
    assert len(pw) == len(lits) * (len(lits) - 1) // 2


def test_at_most_k_allows_exactly_k_true():
    lits = [1, 2, 3, 4, 5]
    fresh = _make_fresh(6)
    clauses = cardinality.at_most_k(lits, 2, fresh)
    for subset in combinations(lits, 3):
        s = Solver()
        for cl in clauses:
            s.add_clause(cl)
        for l in subset:
            s.add_clause([l])
        assert s.solve() is False
    for subset in combinations(lits, 2):
        s = Solver()
        for cl in clauses:
            s.add_clause(cl)
        for l in subset:
            s.add_clause([l])
        for l in lits:
            if l not in subset:
                s.add_clause([-l])
        assert s.solve() is True


def test_exactly_k_forces_exact_cardinality():
    lits = [1, 2, 3, 4]
    fresh = _make_fresh(5)
    clauses = cardinality.exactly_k(lits, 2, fresh)

    for chosen in combinations(lits, 2):
        s = Solver()
        for cl in clauses:
            s.add_clause(cl)
        for l in chosen:
            s.add_clause([l])
        for l in lits:
            if l not in chosen:
                s.add_clause([-l])
        assert s.solve() is True

    for chosen in combinations(lits, 1):
        s = Solver()
        for cl in clauses:
            s.add_clause(cl)
        for l in chosen:
            s.add_clause([l])
        for l in lits:
            if l not in chosen:
                s.add_clause([-l])
        assert s.solve() is False


def test_at_most_one_dispatch_switches_on_threshold():
    small = cardinality.at_most_one([1, 2, 3])
    assert small == cardinality.at_most_one_pairwise([1, 2, 3])

    fresh = _make_fresh(100)
    big = cardinality.at_most_one([1, 2, 3, 4, 5, 6, 7], fresh=fresh)
    assert len(big) < 7 * 6 // 2
