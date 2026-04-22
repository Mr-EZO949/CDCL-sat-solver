import io

from satsolver import Solver


def _parse_proof(text: str) -> list[tuple[bool, list[int]]]:
    out: list[tuple[bool, list[int]]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        deletion = False
        toks = line.split()
        if toks[0] == "d":
            deletion = True
            toks = toks[1:]
        assert toks[-1] == "0"
        out.append((deletion, [int(x) for x in toks[:-1]]))
    return out


def test_drat_emits_learned_clauses_on_unsat():
    buf = io.StringIO()
    s = Solver(proof=buf)
    for cl in [[1, 2], [-1, 2], [1, -2], [-1, -2]]:
        s.add_clause(cl)
    assert s.solve() is False

    steps = _parse_proof(buf.getvalue())
    assert len(steps) >= 1
    assert all(not d for d, _ in steps)


def test_drat_no_emission_on_trivial_sat():
    buf = io.StringIO()
    s = Solver(proof=buf)
    s.add_clause([1, 2])
    assert s.solve() is True
    assert buf.getvalue() == ""


def test_drat_ends_with_empty_clause_on_unsat_via_learning():
    buf = io.StringIO()
    s = Solver(proof=buf)
    for cl in [[1, 2], [-1, 2], [1, -2], [-1, -2]]:
        s.add_clause(cl)
    assert s.solve() is False
    steps = _parse_proof(buf.getvalue())
    final = steps[-1]
    assert final[0] is False
    assert final[1] == []


def test_drat_empty_clause_also_on_trivial_unsat():
    buf = io.StringIO()
    s = Solver(proof=buf)
    s.add_clause([1])
    s.add_clause([-1])
    assert s.solve() is False
    steps = _parse_proof(buf.getvalue())
    assert steps[-1] == (False, [])


def test_drat_is_valid_text_format():
    buf = io.StringIO()
    s = Solver(proof=buf)
    for cl in [[1, 2, 3], [-1, 2], [-2, 3], [-3, 1], [-1, -2, -3]]:
        s.add_clause(cl)
    s.solve()
    for line in buf.getvalue().splitlines():
        line = line.strip()
        if not line:
            continue
        toks = line.split()
        if toks[0] == "d":
            toks = toks[1:]
        assert toks[-1] == "0"
        for t in toks[:-1]:
            int(t)
