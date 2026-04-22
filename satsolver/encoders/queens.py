from __future__ import annotations

from satsolver.cardinality import at_most_one


def var(n: int, r: int, c: int) -> int:
    return r * n + c + 1


def encode(n: int) -> list[list[int]]:
    clauses: list[list[int]] = []

    for r in range(n):
        clauses.append([var(n, r, c) for c in range(n)])

    for r in range(n):
        clauses.extend(at_most_one([var(n, r, c) for c in range(n)]))

    for c in range(n):
        clauses.extend(at_most_one([var(n, r, c) for r in range(n)]))

    for k in range(-(n - 1), n):
        diag = [var(n, r, r - k) for r in range(n) if 0 <= r - k < n]
        if len(diag) > 1:
            clauses.extend(at_most_one(diag))

    for k in range(2 * n - 1):
        anti = [var(n, r, k - r) for r in range(n) if 0 <= k - r < n]
        if len(anti) > 1:
            clauses.extend(at_most_one(anti))

    return clauses


def decode(n: int, model: dict[int, bool]) -> list[int]:
    out = [-1] * n
    for r in range(n):
        for c in range(n):
            if model.get(var(n, r, c), False):
                out[r] = c
                break
    return out


def pretty(placement: list[int]) -> str:
    n = len(placement)
    lines = []
    for r in range(n):
        row = ["Q" if placement[r] == c else "." for c in range(n)]
        lines.append(" ".join(row))
    return "\n".join(lines)


def verify(placement: list[int]) -> bool:
    n = len(placement)
    if any(c < 0 for c in placement):
        return False
    if len(set(placement)) != n:
        return False
    for r1 in range(n):
        for r2 in range(r1 + 1, n):
            if abs(placement[r1] - placement[r2]) == abs(r1 - r2):
                return False
    return True
