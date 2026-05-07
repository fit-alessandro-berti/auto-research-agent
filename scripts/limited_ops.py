"""Operation counting helpers for limited-operation discovery prototypes.

The counter is intentionally simple. It is not a CPU profiler; it records the
primitive operations declared by the research protocol so algorithms can be
compared under the same cost model.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class OpCounter:
    counts: Counter = field(default_factory=Counter)

    def inc(self, name: str, n: int = 1) -> None:
        if n < 0:
            raise ValueError("operation increment must be non-negative")
        self.counts[name] += n

    def total(self) -> int:
        return int(sum(self.counts.values()))

    def to_dict(self) -> Dict[str, int]:
        d = dict(self.counts)
        d["total"] = self.total()
        return d


def scan_event(counter: OpCounter, n: int = 1) -> None:
    counter.inc("scan_event", n)


def dict_increment(counter: OpCounter, n: int = 1) -> None:
    counter.inc("dict_increment", n)


def comparison(counter: OpCounter, n: int = 1) -> None:
    counter.inc("comparison", n)


def set_insert(counter: OpCounter, n: int = 1) -> None:
    counter.inc("set_insert", n)


def set_lookup(counter: OpCounter, n: int = 1) -> None:
    counter.inc("set_lookup", n)


def relation_classification(counter: OpCounter, n: int = 1) -> None:
    counter.inc("relation_classification", n)


def construct(counter: OpCounter, n: int = 1) -> None:
    counter.inc("construct", n)
