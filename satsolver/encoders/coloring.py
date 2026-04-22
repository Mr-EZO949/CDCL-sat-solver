from __future__ import annotations

from satsolver.cardinality import exactly_one


def var(k: int, node: int, color: int) -> int:
    return node * k + color + 1


def encode(num_nodes: int, edges: list[tuple[int, int]], k: int) -> list[list[int]]:
    clauses: list[list[int]] = []
    for n in range(num_nodes):
        clauses.extend(exactly_one([var(k, n, c) for c in range(k)]))
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(k, u, c), -var(k, v, c)])
    return clauses


def decode(num_nodes: int, k: int, model: dict[int, bool]) -> list[int]:
    out = [-1] * num_nodes
    for n in range(num_nodes):
        for c in range(k):
            if model.get(var(k, n, c), False):
                out[n] = c
                break
    return out


def verify(num_nodes: int, edges: list[tuple[int, int]], colors: list[int]) -> bool:
    if any(c < 0 for c in colors):
        return False
    return all(colors[u] != colors[v] for (u, v) in edges)


def parse_edges(text: str) -> tuple[int, list[tuple[int, int]]]:
    edges: list[tuple[int, int]] = []
    max_node = -1
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        u, v = int(parts[0]), int(parts[1])
        edges.append((u, v))
        if u > max_node:
            max_node = u
        if v > max_node:
            max_node = v
    return max_node + 1, edges
