from __future__ import annotations

from typing import Callable


def at_least_one(lits: list[int]) -> list[list[int]]:
    return [list(lits)]


def at_most_one_pairwise(lits: list[int]) -> list[list[int]]:
    out: list[list[int]] = []
    for i in range(len(lits)):
        for j in range(i + 1, len(lits)):
            out.append([-lits[i], -lits[j]])
    return out


def at_most_one_sequential(
    lits: list[int], fresh: Callable[[], int]
) -> list[list[int]]:
    n = len(lits)
    if n <= 1:
        return []
    if n == 2:
        return [[-lits[0], -lits[1]]]
    s = [fresh() for _ in range(n - 1)]
    out: list[list[int]] = []
    out.append([-lits[0], s[0]])
    out.append([-lits[n - 1], -s[n - 2]])
    for i in range(1, n - 1):
        out.append([-lits[i], s[i]])
        out.append([-s[i - 1], s[i]])
        out.append([-lits[i], -s[i - 1]])
    return out


def at_most_one(
    lits: list[int], fresh: Callable[[], int] | None = None, threshold: int = 5
) -> list[list[int]]:
    if fresh is None or len(lits) <= threshold:
        return at_most_one_pairwise(lits)
    return at_most_one_sequential(lits, fresh)


def exactly_one(
    lits: list[int], fresh: Callable[[], int] | None = None, threshold: int = 5
) -> list[list[int]]:
    return at_least_one(lits) + at_most_one(lits, fresh, threshold)


def _totalizer(
    lits: list[int], k: int, fresh: Callable[[], int]
) -> tuple[list[int], list[list[int]]]:
    n = len(lits)
    if n == 0:
        return [], []
    if n == 1:
        return [lits[0]], []
    mid = n // 2
    left_out, left_cls = _totalizer(lits[:mid], k, fresh)
    right_out, right_cls = _totalizer(lits[mid:], k, fresh)

    m = min(len(left_out) + len(right_out), k + 1)
    out = [fresh() for _ in range(m)]

    clauses = list(left_cls) + list(right_cls)
    for a in range(len(left_out) + 1):
        for b in range(len(right_out) + 1):
            r = a + b
            if r == 0 or r > m:
                continue
            cl: list[int] = []
            if a > 0:
                cl.append(-left_out[a - 1])
            if b > 0:
                cl.append(-right_out[b - 1])
            cl.append(out[r - 1])
            clauses.append(cl)
    return out, clauses


def at_most_k(
    lits: list[int], k: int, fresh: Callable[[], int]
) -> list[list[int]]:
    n = len(lits)
    if k >= n:
        return []
    if k < 0:
        return [[]]
    if k == 0:
        return [[-l] for l in lits]
    if k == 1:
        return at_most_one_sequential(lits, fresh)

    out, clauses = _totalizer(lits, k, fresh)
    if k < len(out):
        clauses.append([-out[k]])
    return clauses


def at_least_k(
    lits: list[int], k: int, fresh: Callable[[], int]
) -> list[list[int]]:
    if k <= 0:
        return []
    if k == 1:
        return at_least_one(lits)
    neg = [-l for l in lits]
    return at_most_k(neg, len(lits) - k, fresh)


def exactly_k(
    lits: list[int], k: int, fresh: Callable[[], int]
) -> list[list[int]]:
    return at_least_k(lits, k, fresh) + at_most_k(lits, k, fresh)
