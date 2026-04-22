from __future__ import annotations


def encode(n: int) -> list[list[int]]:
    def var(p: int, h: int) -> int:
        return p * n + h + 1

    clauses: list[list[int]] = []
    for p in range(n + 1):
        clauses.append([var(p, h) for h in range(n)])
    for h in range(n):
        for p1 in range(n + 1):
            for p2 in range(p1 + 1, n + 1):
                clauses.append([-var(p1, h), -var(p2, h)])
    return clauses
