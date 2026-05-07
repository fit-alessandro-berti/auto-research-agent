"""Small JSON-serializable representations for PMIR and Petri nets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple, Any


Arc = Tuple[str, str]


@dataclass
class PetriNet:
    places: List[str] = field(default_factory=list)
    transitions: List[str] = field(default_factory=list)
    arcs: List[Arc] = field(default_factory=list)
    initial_marking: Dict[str, int] = field(default_factory=dict)
    final_marking: Dict[str, int] = field(default_factory=dict)

    def add_place(self, place: str) -> None:
        if place not in self.places:
            self.places.append(place)

    def add_transition(self, transition: str) -> None:
        if transition not in self.transitions:
            self.transitions.append(transition)

    def add_arc(self, source: str, target: str) -> None:
        arc = (source, target)
        if arc not in self.arcs:
            self.arcs.append(arc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "places": sorted(self.places),
            "transitions": sorted(self.transitions),
            "arcs": sorted([{"source": s, "target": t} for s, t in self.arcs], key=lambda x: (x["source"], x["target"])),
            "initial_marking": dict(sorted(self.initial_marking.items())),
            "final_marking": dict(sorted(self.final_marking.items())),
        }

    def structural_summary(self) -> Dict[str, int]:
        silent = [t for t in self.transitions if t.startswith("tau_")]
        return {
            "places": len(self.places),
            "transitions": len(self.transitions),
            "silent_transitions": len(silent),
            "arcs": len(self.arcs),
        }


@dataclass
class PMIR:
    activities: List[str]
    start_counts: Dict[str, int]
    end_counts: Dict[str, int]
    dfg_counts: Dict[str, int]
    relations: Dict[str, str]
    evidence: Dict[str, Any] = field(default_factory=dict)
    operation_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activities": sorted(self.activities),
            "start_counts": dict(sorted(self.start_counts.items())),
            "end_counts": dict(sorted(self.end_counts.items())),
            "dfg_counts": dict(sorted(self.dfg_counts.items())),
            "relations": dict(sorted(self.relations.items())),
            "evidence": self.evidence,
            "operation_counts": self.operation_counts,
        }


def pair_key(a: str, b: str) -> str:
    return f"{a}->{b}"


def transition_name(activity: str) -> str:
    return f"t_{activity}"


def place_name(prefix: str, presets: Iterable[str], postsets: Iterable[str]) -> str:
    pre = "_".join(sorted(presets)) or "src"
    post = "_".join(sorted(postsets)) or "sink"
    raw = f"p_{prefix}_{pre}__{post}"
    return raw.replace(" ", "_").replace("/", "_")
