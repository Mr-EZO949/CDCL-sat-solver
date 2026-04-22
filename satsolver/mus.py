from __future__ import annotations

from satsolver.solver import Solver


def extract(clauses: list[list[int]]) -> list[list[int]] | None:
    if not clauses:
        return None

    max_var = 0
    for cl in clauses:
        for l in cl:
            if abs(l) > max_var:
                max_var = abs(l)

    n = len(clauses)
    selectors = [max_var + 1 + i for i in range(n)]

    s = Solver()
    for i, cl in enumerate(clauses):
        s.add_clause(list(cl) + [selectors[i]])

    all_active = [-sel for sel in selectors]
    if s.solve(all_active) is not False:
        return None

    in_mus = [True] * n

    for i in range(n):
        if not in_mus[i]:
            continue
        assumptions = [selectors[i]]
        for j in range(n):
            if j != i and in_mus[j]:
                assumptions.append(-selectors[j])
        if s.solve(assumptions) is False:
            in_mus[i] = False

    return [clauses[i] for i in range(n) if in_mus[i]]
