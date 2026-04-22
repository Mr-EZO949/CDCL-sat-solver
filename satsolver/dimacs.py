from __future__ import annotations


def parse(text: str) -> list[list[int]]:
    clauses: list[list[int]] = []
    current: list[int] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("c", "p", "%")):
            continue
        for tok in line.split():
            try:
                n = int(tok)
            except ValueError:
                continue
            if n == 0:
                clauses.append(current)
                current = []
            else:
                current.append(n)
    if current:
        clauses.append(current)
    return clauses


def dump(clauses: list[list[int]]) -> str:
    n_vars = max((abs(l) for cl in clauses for l in cl), default=0)
    lines = [f"p cnf {n_vars} {len(clauses)}"]
    for cl in clauses:
        lines.append(" ".join(str(l) for l in cl) + " 0")
    return "\n".join(lines) + "\n"
