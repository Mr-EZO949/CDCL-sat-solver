from __future__ import annotations

from collections import deque
from typing import IO, Iterable


class Solver:
    def __init__(self, proof: IO[str] | None = None) -> None:
        self.clauses: list[list[int]] = []
        self.watches: dict[int, list[int]] = {}
        self.assigns: dict[int, bool] = {}
        self.level: dict[int, int] = {}
        self.reason: dict[int, int | None] = {}
        self.trail: list[int] = []
        self.trail_lim: list[int] = []
        self.qhead = 0
        self.vars: set[int] = set()
        self.activity: dict[int, float] = {}
        self.var_inc = 1.0
        self.var_decay = 0.95
        self.phase: dict[int, bool] = {}
        self.unsat_at_init = False
        self.conflicts = 0
        self.decisions = 0
        self.propagations = 0
        self.restarts = 0
        self.learned_units = 0
        self.deletions = 0
        self.proof = proof
        self.assumptions: list[int] = []
        self.conflict_clause: list[int] = []
        self._max_var = 0

        self.is_learned: list[bool] = []
        self.lbd: list[int] = []
        self.deleted: list[bool] = []
        self.learned_indices: list[int] = []

        self.lbd_window: deque[int] = deque(maxlen=50)
        self.lbd_sum_global = 0.0
        self.lbd_count_global = 0

        self.reduce_limit = 2000
        self.reduce_inc = 300

    def value(self, lit: int) -> bool | None:
        v = abs(lit)
        if v not in self.assigns:
            return None
        a = self.assigns[v]
        return a if lit > 0 else not a

    def current_level(self) -> int:
        return len(self.trail_lim)

    def new_var(self) -> int:
        self._max_var += 1
        v = self._max_var
        self.vars.add(v)
        self.activity.setdefault(v, 0.0)
        self.phase.setdefault(v, False)
        return v

    def _emit(self, clause: Iterable[int], deletion: bool = False) -> None:
        if self.proof is None:
            return
        parts = ["d"] if deletion else []
        parts.extend(str(l) for l in clause)
        parts.append("0")
        self.proof.write(" ".join(parts) + "\n")

    def _register_clause(self, clause: list[int], learned: bool, lbd: int = 0) -> int:
        ci = len(self.clauses)
        self.clauses.append(clause)
        self.is_learned.append(learned)
        self.lbd.append(lbd)
        self.deleted.append(False)
        self.watches.setdefault(clause[0], []).append(ci)
        self.watches.setdefault(clause[1], []).append(ci)
        if learned:
            self.learned_indices.append(ci)
        return ci

    def add_clause(self, lits: Iterable[int]) -> None:
        if self.current_level() > 0:
            self.backtrack(0)

        seen: dict[int, bool] = {}
        for l in lits:
            if l == 0:
                raise ValueError("0 is not a valid literal")
            if -l in seen:
                return
            seen[l] = True
        clause = list(seen.keys())

        for l in clause:
            v = abs(l)
            self.vars.add(v)
            if v > self._max_var:
                self._max_var = v
            self.activity.setdefault(v, 0.0)
            self.phase.setdefault(v, False)

        if len(clause) == 0:
            self.unsat_at_init = True
            return

        if len(clause) == 1:
            l = clause[0]
            v = abs(l)
            want = l > 0
            if v in self.assigns:
                if self.assigns[v] != want:
                    self.unsat_at_init = True
                return
            self.assigns[v] = want
            self.level[v] = 0
            self.reason[v] = None
            self.trail.append(l)
            return

        self._register_clause(clause, learned=False)

    def add_clauses(self, clauses: Iterable[Iterable[int]]) -> None:
        for cl in clauses:
            self.add_clause(cl)

    def enqueue(self, lit: int, reason_ci: int | None) -> bool:
        v = abs(lit)
        want = lit > 0
        if v in self.assigns:
            return self.assigns[v] == want
        self.assigns[v] = want
        self.level[v] = self.current_level()
        self.reason[v] = reason_ci
        self.trail.append(lit)
        return True

    def propagate(self) -> int | None:
        while self.qhead < len(self.trail):
            lit = self.trail[self.qhead]
            self.qhead += 1
            self.propagations += 1
            neg = -lit

            ws = self.watches.get(neg, [])
            self.watches[neg] = []
            conflict: int | None = None
            i = 0
            while i < len(ws):
                ci = ws[i]
                if conflict is not None:
                    self.watches[neg].append(ci)
                    i += 1
                    continue
                if self.deleted[ci]:
                    i += 1
                    continue

                clause = self.clauses[ci]
                if clause[0] == neg:
                    clause[0], clause[1] = clause[1], clause[0]

                if self.value(clause[0]) is True:
                    self.watches[neg].append(ci)
                    i += 1
                    continue

                found = False
                for k in range(2, len(clause)):
                    if self.value(clause[k]) is not False:
                        clause[1], clause[k] = clause[k], clause[1]
                        self.watches.setdefault(clause[1], []).append(ci)
                        found = True
                        break
                if found:
                    i += 1
                    continue

                self.watches[neg].append(ci)
                if self.value(clause[0]) is False:
                    conflict = ci
                else:
                    self.enqueue(clause[0], ci)
                i += 1

            if conflict is not None:
                return conflict
        return None

    def _compute_lbd(self, clause: list[int]) -> int:
        levels: set[int] = set()
        for l in clause:
            lv = self.level.get(abs(l), 0)
            if lv > 0:
                levels.add(lv)
        return len(levels)

    def analyze(self, confl_ci: int) -> tuple[list[int], int]:
        seen: set[int] = set()
        learnt: list[int] = [0]
        path_c = 0
        p: int | None = None
        index = len(self.trail) - 1
        current_level = self.current_level()
        confl = confl_ci

        while True:
            for q in self.clauses[confl]:
                if p is not None and q == p:
                    continue
                v = abs(q)
                lv = self.level.get(v, 0)
                if v in seen or lv == 0:
                    continue
                seen.add(v)
                self.bump_var(v)
                if lv >= current_level:
                    path_c += 1
                else:
                    learnt.append(q)
            while abs(self.trail[index]) not in seen:
                index -= 1
            p = self.trail[index]
            index -= 1
            seen.remove(abs(p))
            path_c -= 1
            if path_c <= 0:
                break
            confl = self.reason[abs(p)]  # type: ignore[assignment]

        assert p is not None
        learnt[0] = -p

        learnt = self._minimize(learnt)

        if len(learnt) == 1:
            bj_level = 0
        else:
            max_i = 1
            for i in range(2, len(learnt)):
                if self.level[abs(learnt[i])] > self.level[abs(learnt[max_i])]:
                    max_i = i
            learnt[1], learnt[max_i] = learnt[max_i], learnt[1]
            bj_level = self.level[abs(learnt[1])]

        return learnt, bj_level

    def _minimize(self, learnt: list[int]) -> list[int]:
        if len(learnt) <= 1:
            return learnt
        marked = {abs(l) for l in learnt}
        cache: dict[int, bool] = {}

        def redundant(v: int) -> bool:
            if v in cache:
                return cache[v]
            r = self.reason.get(v)
            if r is None:
                cache[v] = False
                return False
            for q in self.clauses[r]:
                vq = abs(q)
                if vq == v:
                    continue
                if self.level.get(vq, 0) == 0:
                    continue
                if vq in marked:
                    continue
                if not redundant(vq):
                    cache[v] = False
                    return False
            cache[v] = True
            return True

        kept = [learnt[0]]
        for l in learnt[1:]:
            v = abs(l)
            if self.reason.get(v) is not None and redundant(v):
                continue
            kept.append(l)
        return kept

    def analyze_final(self, confl_ci: int | None, confl_lit: int | None) -> list[int]:
        out_conflict: list[int] = []
        if self.current_level() == 0:
            return out_conflict

        seen: set[int] = set()
        if confl_lit is not None:
            seen.add(abs(confl_lit))
            out_conflict.append(confl_lit)
        if confl_ci is not None:
            for q in self.clauses[confl_ci]:
                v = abs(q)
                if self.level.get(v, 0) > 0:
                    seen.add(v)

        i = len(self.trail) - 1
        start = self.trail_lim[0]
        while i >= start:
            lit = self.trail[i]
            v = abs(lit)
            if v in seen:
                r = self.reason.get(v)
                if r is None:
                    out_conflict.append(lit)
                else:
                    for q in self.clauses[r]:
                        if abs(q) != v and self.level.get(abs(q), 0) > 0:
                            seen.add(abs(q))
            i -= 1
        return out_conflict

    def backtrack(self, level: int) -> None:
        if self.current_level() <= level:
            return
        target = self.trail_lim[level] if level < len(self.trail_lim) else 0
        while len(self.trail) > target:
            lit = self.trail.pop()
            v = abs(lit)
            self.phase[v] = self.assigns[v]
            del self.assigns[v]
            del self.level[v]
            del self.reason[v]
        del self.trail_lim[level:]
        self.qhead = len(self.trail)

    def bump_var(self, v: int) -> None:
        a = self.activity.get(v, 0.0) + self.var_inc
        self.activity[v] = a
        if a > 1e100:
            for u in self.activity:
                self.activity[u] *= 1e-100
            self.var_inc *= 1e-100

    def decay_activities(self) -> None:
        self.var_inc /= self.var_decay

    def pick_branching_var(self) -> int | None:
        best = None
        best_act = -1.0
        for v in self.vars:
            if v not in self.assigns:
                a = self.activity.get(v, 0.0)
                if a > best_act:
                    best_act = a
                    best = v
        return best

    @staticmethod
    def luby(i: int) -> int:
        n = i + 1
        k = 1
        while (1 << k) - 1 < n:
            k += 1
        if (1 << k) - 1 == n:
            return 1 << (k - 1)
        return Solver.luby(i - (1 << (k - 1)) + 1)

    def _locked(self, ci: int) -> bool:
        if self.deleted[ci]:
            return False
        clause = self.clauses[ci]
        if not clause:
            return False
        l0 = clause[0]
        v = abs(l0)
        return v in self.assigns and self.reason.get(v) == ci

    def reduce_db(self) -> None:
        candidates = [
            ci for ci in self.learned_indices
            if not self.deleted[ci] and not self._locked(ci) and self.lbd[ci] > 2
        ]
        if not candidates:
            return
        candidates.sort(key=lambda ci: (self.lbd[ci], -len(self.clauses[ci])))
        keep = len(candidates) // 2
        to_delete = candidates[keep:]

        for ci in to_delete:
            clause = self.clauses[ci]
            self._emit(clause, deletion=True)
            if len(clause) >= 2:
                w0 = self.watches.get(clause[0])
                if w0 is not None and ci in w0:
                    w0.remove(ci)
                w1 = self.watches.get(clause[1])
                if w1 is not None and ci in w1:
                    w1.remove(ci)
            self.deleted[ci] = True
            self.deletions += 1

        self.learned_indices = [
            ci for ci in self.learned_indices if not self.deleted[ci]
        ]

    def _glucose_trigger(self, recent_required: int = 50) -> bool:
        if len(self.lbd_window) < recent_required:
            return False
        if self.lbd_count_global == 0:
            return False
        recent_avg = sum(self.lbd_window) / len(self.lbd_window)
        global_avg = self.lbd_sum_global / self.lbd_count_global
        return recent_avg * 0.8 > global_avg

    def _decide_assumption(self) -> int:
        while self.current_level() < len(self.assumptions):
            a = self.assumptions[self.current_level()]
            v = self.value(a)
            if v is True:
                self.trail_lim.append(len(self.trail))
            elif v is False:
                self.conflict_clause = self.analyze_final(None, -a)
                return -1
            else:
                self.trail_lim.append(len(self.trail))
                self.enqueue(a, None)
                return 1
        return 0

    def solve(self, assumptions: Iterable[int] | None = None) -> bool:
        self.conflict_clause = []
        assumptions_list = list(assumptions) if assumptions is not None else []
        if self.unsat_at_init:
            if not assumptions_list:
                self._emit([])
            return False

        self.backtrack(0)
        self.assumptions = assumptions_list

        for a in self.assumptions:
            v = abs(a)
            if v not in self.vars:
                self.vars.add(v)
                if v > self._max_var:
                    self._max_var = v
                self.activity.setdefault(v, 0.0)
                self.phase.setdefault(v, False)

        restart_base = 100
        restart_idx = 0
        conflicts_this_restart = 0

        while True:
            conflict = self.propagate()
            if conflict is not None:
                self.conflicts += 1
                conflicts_this_restart += 1
                if self.current_level() == 0:
                    if not self.assumptions:
                        self._emit([])
                    return False
                if self.current_level() <= len(self.assumptions):
                    self.conflict_clause = self.analyze_final(conflict, None)
                    return False

                learnt, bj_level = self.analyze(conflict)
                if bj_level < len(self.assumptions):
                    bj_level = len(self.assumptions)

                lbd = self._compute_lbd(learnt)
                self.lbd_window.append(lbd)
                self.lbd_sum_global += lbd
                self.lbd_count_global += 1

                self._emit(learnt)
                self.backtrack(bj_level)

                if len(learnt) == 1:
                    self.learned_units += 1
                    self.enqueue(learnt[0], None)
                else:
                    ci = self._register_clause(learnt, learned=True, lbd=lbd)
                    self.enqueue(learnt[0], ci)

                self.decay_activities()

                if len(self.learned_indices) > self.reduce_limit:
                    self.backtrack(len(self.assumptions))
                    self.reduce_db()
                    self.reduce_limit += self.reduce_inc
                    continue
            else:
                luby_limit = self.luby(restart_idx) * restart_base
                if (
                    conflicts_this_restart >= luby_limit
                    or self._glucose_trigger()
                ):
                    self.restarts += 1
                    self.backtrack(len(self.assumptions))
                    restart_idx += 1
                    conflicts_this_restart = 0
                    self.lbd_window.clear()
                    continue

                status = self._decide_assumption()
                if status == -1:
                    return False
                if status == 1:
                    continue

                if len(self.assigns) == len(self.vars):
                    return True

                v = self.pick_branching_var()
                if v is None:
                    return True
                self.decisions += 1
                self.trail_lim.append(len(self.trail))
                lit = v if self.phase.get(v, False) else -v
                self.enqueue(lit, None)

    def unsat_core(self) -> list[int]:
        return list(self.conflict_clause)

    def model(self) -> dict[int, bool]:
        return dict(self.assigns)

    def stats(self) -> dict[str, int]:
        return {
            "vars": len(self.vars),
            "clauses": len(self.clauses) - self.deletions,
            "decisions": self.decisions,
            "conflicts": self.conflicts,
            "propagations": self.propagations,
            "restarts": self.restarts,
            "learned_units": self.learned_units,
            "deletions": self.deletions,
        }

    def stats_line(self) -> str:
        return " ".join(f"{k}={v}" for k, v in self.stats().items())
