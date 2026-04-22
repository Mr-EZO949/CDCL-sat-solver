from __future__ import annotations

from satsolver.cardinality import exactly_one


def var(r: int, c: int, d: int) -> int:
    return (r - 1) * 81 + (c - 1) * 9 + d


def encode(grid: list[list[int]]) -> list[list[int]]:
    clauses: list[list[int]] = []
    next_aux = [9 * 9 * 9 + 1]

    def fresh() -> int:
        v = next_aux[0]
        next_aux[0] += 1
        return v

    for r in range(1, 10):
        for c in range(1, 10):
            clauses.extend(exactly_one([var(r, c, d) for d in range(1, 10)], fresh))

    for r in range(1, 10):
        for d in range(1, 10):
            clauses.extend(exactly_one([var(r, c, d) for c in range(1, 10)], fresh))

    for c in range(1, 10):
        for d in range(1, 10):
            clauses.extend(exactly_one([var(r, c, d) for r in range(1, 10)], fresh))

    for br in range(3):
        for bc in range(3):
            for d in range(1, 10):
                cells = [
                    var(br * 3 + dr + 1, bc * 3 + dc + 1, d)
                    for dr in range(3)
                    for dc in range(3)
                ]
                clauses.extend(exactly_one(cells, fresh))

    for r in range(1, 10):
        for c in range(1, 10):
            v = grid[r - 1][c - 1]
            if v != 0:
                clauses.append([var(r, c, v)])

    return clauses


def decode(model: dict[int, bool]) -> list[list[int]]:
    out = [[0] * 9 for _ in range(9)]
    for r in range(1, 10):
        for c in range(1, 10):
            for d in range(1, 10):
                if model.get(var(r, c, d), False):
                    out[r - 1][c - 1] = d
                    break
    return out


def parse(text: str) -> list[list[int]]:
    digits: list[int] = []
    for ch in text:
        if ch.isdigit():
            digits.append(int(ch))
        elif ch in "._*-":
            digits.append(0)
    if len(digits) != 81:
        raise ValueError(f"expected 81 cells, got {len(digits)}")
    return [digits[i * 9 : (i + 1) * 9] for i in range(9)]


def pretty(grid: list[list[int]]) -> str:
    out = []
    sep = "+-------+-------+-------+"
    for r in range(9):
        if r % 3 == 0:
            out.append(sep)
        row = []
        for c in range(9):
            if c % 3 == 0:
                row.append("|")
            v = grid[r][c]
            row.append(str(v) if v else ".")
        row.append("|")
        out.append(" ".join(row))
    out.append(sep)
    return "\n".join(out)


def verify(grid: list[list[int]]) -> bool:
    for r in range(9):
        if sorted(grid[r]) != list(range(1, 10)):
            return False
    for c in range(9):
        if sorted(grid[r][c] for r in range(9)) != list(range(1, 10)):
            return False
    for br in range(3):
        for bc in range(3):
            block = [grid[br * 3 + dr][bc * 3 + dc] for dr in range(3) for dc in range(3)]
            if sorted(block) != list(range(1, 10)):
                return False
    return True
