from __future__ import annotations


def _dedup(clauses: list[list[int]]) -> list[list[int]]:
    out: list[list[int]] = []
    for cl in clauses:
        seen: dict[int, bool] = {}
        tautology = False
        for l in cl:
            if -l in seen:
                tautology = True
                break
            seen[l] = True
        if tautology:
            continue
        out.append(list(seen.keys()))
    return out


def _occur_index(clauses: list[list[int]]) -> dict[int, list[int]]:
    idx: dict[int, list[int]] = {}
    for i, cl in enumerate(clauses):
        for l in cl:
            idx.setdefault(l, []).append(i)
    return idx


def subsume(clauses: list[list[int]]) -> list[list[int]]:
    clauses = _dedup(clauses)
    sets = [frozenset(c) for c in clauses]
    order = sorted(range(len(clauses)), key=lambda i: len(clauses[i]))
    alive = [True] * len(clauses)
    occ = _occur_index(clauses)

    for i in order:
        if not alive[i]:
            continue
        ci = sets[i]
        pivot = min(ci, key=lambda l: len(occ.get(l, [])))
        for j in occ.get(pivot, []):
            if j == i or not alive[j]:
                continue
            if len(clauses[j]) < len(clauses[i]):
                continue
            if ci <= sets[j]:
                alive[j] = False

    return [clauses[i] for i in range(len(clauses)) if alive[i]]


def self_subsume(clauses: list[list[int]]) -> list[list[int]]:
    clauses = [list(c) for c in _dedup(clauses)]
    sets = [set(c) for c in clauses]
    changed = True
    while changed:
        changed = False
        for i in range(len(clauses)):
            if not clauses[i]:
                continue
            ci = sets[i]
            for l in list(ci):
                for j in range(len(clauses)):
                    if i == j or not clauses[j]:
                        continue
                    cj = sets[j]
                    if -l not in cj:
                        continue
                    if len(ci) > len(cj):
                        continue
                    rest_i = ci - {l}
                    rest_j = cj - {-l}
                    if rest_i <= rest_j:
                        cj.discard(-l)
                        clauses[j] = list(cj)
                        changed = True
                        if not clauses[j]:
                            return [[]]
    return [c for c in clauses if c]


def unit_propagate_fixpoint(clauses: list[list[int]]) -> list[list[int]] | None:
    clauses = [list(c) for c in clauses]
    assigned: dict[int, bool] = {}

    while True:
        units: list[int] = []
        new_clauses: list[list[int]] = []
        satisfied = False
        for cl in clauses:
            reduced: list[int] = []
            sat = False
            for l in cl:
                v = abs(l)
                want = l > 0
                if v in assigned:
                    if assigned[v] == want:
                        sat = True
                        break
                else:
                    reduced.append(l)
            if sat:
                continue
            if not reduced:
                return None
            if len(reduced) == 1:
                units.append(reduced[0])
            new_clauses.append(reduced)
        clauses = new_clauses
        if not units:
            break
        for u in units:
            v = abs(u)
            want = u > 0
            if v in assigned:
                if assigned[v] != want:
                    return None
                continue
            assigned[v] = want

    return clauses


def preprocess(clauses: list[list[int]]) -> list[list[int]] | None:
    cs = unit_propagate_fixpoint(clauses)
    if cs is None:
        return None
    cs = self_subsume(cs)
    if cs == [[]]:
        return None
    cs = subsume(cs)
    return cs
