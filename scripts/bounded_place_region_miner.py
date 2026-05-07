"""ALG-0004: Bounded Place-Candidate Region Miner.

This prototype is solver-free and intentionally small. It enumerates bounded
place candidates, checks each candidate against observed token-balance
constraints, and greedily keeps places that do not block positive replay.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Tuple

from alpha_lite import classify_relations, summarize_log
from limited_ops import OpCounter, arithmetic, comparison, construct, relation_classification, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name


PlaceCandidate = Tuple[Tuple[str, ...], Tuple[str, ...]]
TraceLog = List[List[str]]


def _subsets(items: Sequence[str], max_size: int) -> Iterable[Tuple[str, ...]]:
    for size in range(1, min(max_size, len(items)) + 1):
        yield from combinations(items, size)


def _candidate_has_direct_evidence(candidate: PlaceCandidate, dfg: Counter, counter: OpCounter) -> bool:
    pre, post = candidate
    for a in pre:
        for b in post:
            set_lookup(counter)
            comparison(counter)
            if dfg.get((a, b), 0) <= 0:
                return False
    return True


def _candidate_replays(candidate: PlaceCandidate, log: TraceLog, counter: OpCounter) -> Tuple[bool, str]:
    pre, post = set(candidate[0]), set(candidate[1])
    for trace in log:
        tokens = 0
        for event in trace:
            set_lookup(counter, 2)
            if event in post:
                tokens -= 1
                arithmetic(counter)
                comparison(counter)
                if tokens < 0:
                    return False, "underflow"
            if event in pre:
                tokens += 1
                arithmetic(counter)
        comparison(counter)
        if tokens != 0:
            return False, "final_residue"
    return True, "accepted"


def _places_replay_log(candidates: List[PlaceCandidate], log: TraceLog, counter: OpCounter) -> bool:
    for trace in log:
        tokens = [0 for _candidate in candidates]
        construct(counter, len(candidates))
        for event in trace:
            for index, candidate in enumerate(candidates):
                pre, post = candidate
                set_lookup(counter, 2)
                if event in post:
                    tokens[index] -= 1
                    arithmetic(counter)
                    comparison(counter)
                    if tokens[index] < 0:
                        return False
                if event in pre:
                    tokens[index] += 1
                    arithmetic(counter)
        for token_count in tokens:
            comparison(counter)
            if token_count != 0:
                return False
    return True


def _enumerate_valid_candidates(
    activities: Sequence[str],
    dfg: Counter,
    log: TraceLog,
    max_set_size: int,
    counter: OpCounter,
) -> Tuple[List[PlaceCandidate], Dict[str, int]]:
    valid: List[PlaceCandidate] = []
    stats = {
        "enumerated": 0,
        "rejected_overlap": 0,
        "rejected_no_direct_evidence": 0,
        "rejected_underflow": 0,
        "rejected_final_residue": 0,
    }

    for pre in _subsets(activities, max_set_size):
        for post in _subsets(activities, max_set_size):
            stats["enumerated"] += 1
            relation_classification(counter)
            comparison(counter)
            if set(pre) & set(post):
                stats["rejected_overlap"] += 1
                continue
            if not _candidate_has_direct_evidence((pre, post), dfg, counter):
                stats["rejected_no_direct_evidence"] += 1
                continue
            ok, reason = _candidate_replays((pre, post), log, counter)
            if not ok:
                if reason == "underflow":
                    stats["rejected_underflow"] += 1
                else:
                    stats["rejected_final_residue"] += 1
                continue
            valid.append((pre, post))
            construct(counter)
    return valid, stats


def _select_nonblocking_candidates(valid: List[PlaceCandidate], log: TraceLog, counter: OpCounter) -> Tuple[List[PlaceCandidate], int]:
    selected: List[PlaceCandidate] = []
    rejected_positive_replay = 0
    ordered = sorted(valid, key=lambda candidate: (-(len(candidate[0]) + len(candidate[1])), candidate))
    for candidate in ordered:
        trial = selected + [candidate]
        comparison(counter)
        if _places_replay_log(trial, log, counter):
            selected.append(candidate)
            construct(counter)
        else:
            rejected_positive_replay += 1
    return selected, rejected_positive_replay


def _compile_net(activities: Sequence[str], starts: Counter, ends: Counter, candidates: List[PlaceCandidate], counter: OpCounter) -> PetriNet:
    net = PetriNet()
    net.add_place("p_start")
    net.add_place("p_end")
    net.initial_marking = {"p_start": 1}
    net.final_marking = {"p_end": 1}
    construct(counter, 2)

    for activity in activities:
        net.add_transition(transition_name(activity))
        construct(counter)
    for activity in sorted(starts):
        net.add_arc("p_start", transition_name(activity))
        construct(counter)
    for activity in sorted(ends):
        net.add_arc(transition_name(activity), "p_end")
        construct(counter)
    for pre, post in candidates:
        place = place_name("region", pre, post)
        net.add_place(place)
        construct(counter)
        for activity in pre:
            net.add_arc(transition_name(activity), place)
            construct(counter)
        for activity in post:
            net.add_arc(place, transition_name(activity))
            construct(counter)
    return net


def discover(log: TraceLog, max_set_size: int = 2) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    valid, stats = _enumerate_valid_candidates(activities, dfg, log, max_set_size, counter)
    selected, rejected_positive_replay = _select_nonblocking_candidates(valid, log, counter)
    net = _compile_net(activities, starts, ends, selected, counter)

    evidence = {
        "configuration": {"max_set_size": max_set_size},
        "candidate_stats": {
            **stats,
            "valid_local_candidates": len(valid),
            "selected_candidates": len(selected),
            "rejected_positive_replay": rejected_positive_replay,
        },
        "valid_local_candidates": [[list(pre), list(post)] for pre, post in valid],
        "selected_candidates": [[list(pre), list(post)] for pre, post in selected],
    }
    pmir = PMIR(
        activities=activities,
        start_counts=dict(starts),
        end_counts=dict(ends),
        dfg_counts={pair_key(a, b): c for (a, b), c in dfg.items()},
        relations={pair_key(a, b): r for (a, b), r in rel.items() if r != "unrelated"},
        evidence=evidence,
        operation_counts=counter.to_dict(),
    )
    return {
        "candidate_id": "ALG-0004",
        "name": "Bounded Place-Candidate Region Miner",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
