"""ALG-0014: Prefix Block Abstraction Miner.

This candidate refines ALG-0005 by trying a small grammar abstraction before
falling back to exact prefix-automaton replay. The first abstraction pass looks
for common-prefix/common-suffix middle segments that can be compiled as either
a parallel block or an optional singleton branch in parallel with a mandatory
singleton branch.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Sequence, Set, Tuple

from alpha_lite import classify_relations, summarize_log
from limited_ops import OpCounter, comparison, construct, relation_classification, scan_event, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name
from prefix_automaton_compression import (
    _compile_automaton,
    _compressed_edges,
    _compress_states,
    _insert_traces,
)


TraceLog = List[List[str]]


def _safe_name(*parts: str) -> str:
    return "_".join(parts).replace(" ", "_").replace("/", "_")


def _tau_name(prefix: str, *parts: str) -> str:
    return f"tau_pba_{prefix}_{_safe_name(*parts)}"


def _has_duplicate_labels(sequence: Sequence[str], counter: OpCounter) -> bool:
    seen: Set[str] = set()
    for activity in sequence:
        scan_event(counter)
        set_lookup(counter)
        if activity in seen:
            return True
        seen.add(activity)
        set_insert(counter)
    return False


def _common_prefix(log: TraceLog, counter: OpCounter) -> List[str]:
    if not log:
        return []
    prefix: List[str] = []
    for index, activity in enumerate(log[0]):
        matched = True
        for trace in log[1:]:
            comparison(counter, 2)
            if index >= len(trace) or trace[index] != activity:
                matched = False
                break
        if not matched:
            break
        prefix.append(activity)
        construct(counter)
    return prefix


def _common_suffix(log: TraceLog, prefix_len: int, counter: OpCounter) -> List[str]:
    if not log:
        return []
    max_suffix_len = min(max(0, len(trace) - prefix_len) for trace in log)
    suffix: List[str] = []
    for offset in range(1, max_suffix_len + 1):
        activity = log[0][-offset]
        matched = True
        for trace in log[1:]:
            comparison(counter, 2)
            if trace[-offset] != activity:
                matched = False
                break
        if not matched:
            break
        suffix.insert(0, activity)
        construct(counter)
    return suffix


def _middle_segments(log: TraceLog, prefix_len: int, suffix_len: int) -> List[List[str]]:
    end = None if suffix_len == 0 else -suffix_len
    return [trace[prefix_len:end] for trace in log]


def _segment_set(segment: Sequence[str], counter: OpCounter) -> Optional[Set[str]]:
    labels = set(segment)
    set_insert(counter, len(labels))
    comparison(counter)
    if len(labels) != len(segment):
        return None
    return labels


def _detect_parallel_block(log: TraceLog, counter: OpCounter) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    prefix = _common_prefix(log, counter)
    suffix = _common_suffix(log, len(prefix), counter)
    segments = _middle_segments(log, len(prefix), len(suffix))
    if not segments:
        return None
    first_set = _segment_set(segments[0], counter)
    if first_set is None or len(first_set) < 2:
        return None

    observed_order_variation = False
    for segment in segments:
        segment_set = _segment_set(segment, counter)
        comparison(counter, 3)
        if segment_set is None or segment_set != first_set:
            return None
        if segment != segments[0]:
            observed_order_variation = True
    full_labels = list(prefix) + sorted(first_set) + list(suffix)
    comparison(counter)
    if not observed_order_variation or _has_duplicate_labels(full_labels, counter):
        return None
    return {
        "type": "parallel_block",
        "prefix": prefix,
        "branches": sorted(first_set),
        "suffix": suffix,
    }


def _detect_optional_singleton_parallel(log: TraceLog, counter: OpCounter) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    prefix = _common_prefix(log, counter)
    suffix = _common_suffix(log, len(prefix), counter)
    segments = _middle_segments(log, len(prefix), len(suffix))
    if not segments:
        return None

    segment_sets: List[Set[str]] = []
    union_labels: Set[str] = set()
    intersection_labels: Optional[Set[str]] = None
    for segment in segments:
        segment_set = _segment_set(segment, counter)
        if segment_set is None or not segment_set:
            return None
        segment_sets.append(segment_set)
        union_labels.update(segment_set)
        set_insert(counter, len(segment_set))
        if intersection_labels is None:
            intersection_labels = set(segment_set)
        else:
            intersection_labels.intersection_update(segment_set)
        comparison(counter)

    if intersection_labels is None:
        return None
    comparison(counter, 3)
    if len(union_labels) != 2 or len(intersection_labels) != 1:
        return None
    mandatory = next(iter(intersection_labels))
    optional_candidates = sorted(union_labels - intersection_labels)
    if len(optional_candidates) != 1:
        return None
    optional = optional_candidates[0]
    full_labels = list(prefix) + sorted(union_labels) + list(suffix)
    if _has_duplicate_labels(full_labels, counter):
        return None

    optional_present = False
    optional_absent = False
    mandatory_before_optional = False
    optional_before_mandatory = False
    for segment, segment_set in zip(segments, segment_sets):
        set_lookup(counter, 2)
        if mandatory not in segment_set:
            return None
        if optional in segment_set:
            optional_present = True
            comparison(counter)
            if segment.index(mandatory) < segment.index(optional):
                mandatory_before_optional = True
            else:
                optional_before_mandatory = True
        else:
            optional_absent = True
    comparison(counter, 4)
    if not (optional_present and optional_absent and mandatory_before_optional and optional_before_mandatory):
        return None
    return {
        "type": "optional_singleton_parallel",
        "prefix": prefix,
        "mandatory_branch": mandatory,
        "optional_branch": optional,
        "suffix": suffix,
    }


def _select_grammar(log: TraceLog, counter: OpCounter) -> Tuple[str, Dict[str, object], List[Dict[str, str]]]:
    attempts: List[Dict[str, str]] = []
    for name, detector in [
        ("parallel_block", _detect_parallel_block),
        ("optional_singleton_parallel", _detect_optional_singleton_parallel),
    ]:
        grammar = detector(log, counter)
        if grammar is not None:
            attempts.append({"grammar": name, "result": "accepted"})
            return name, grammar, attempts
        attempts.append({"grammar": name, "result": "rejected"})
    return "exact_prefix_automaton", {"type": "exact_prefix_automaton"}, attempts


def _add_base_net(activities: Sequence[str], counter: OpCounter) -> PetriNet:
    net = PetriNet()
    net.add_place("p_start")
    net.add_place("p_end")
    net.initial_marking = {"p_start": 1}
    net.final_marking = {"p_end": 1}
    construct(counter, 2)
    for activity in sorted(activities):
        net.add_transition(transition_name(activity))
        construct(counter)
    return net


def _add_edge_place(net: PetriNet, prefix: str, a: str, b: str, counter: OpCounter) -> None:
    place = place_name(prefix, [a], [b])
    net.add_place(place)
    net.add_arc(transition_name(a), place)
    net.add_arc(place, transition_name(b))
    construct(counter, 3)


def _wire_prefix(net: PetriNet, prefix: Sequence[str], block_labels: Sequence[str], counter: OpCounter) -> str:
    if prefix:
        net.add_arc("p_start", transition_name(prefix[0]))
        construct(counter)
        for a, b in zip(prefix, prefix[1:]):
            _add_edge_place(net, "pba_seq", a, b, counter)
        return transition_name(prefix[-1])
    split_source = _tau_name("block_start", *block_labels)
    net.add_transition(split_source)
    net.add_arc("p_start", split_source)
    construct(counter, 2)
    return split_source


def _join_target(net: PetriNet, suffix: Sequence[str], block_labels: Sequence[str], counter: OpCounter) -> str:
    if suffix:
        return transition_name(suffix[0])
    join = _tau_name("block_end", *block_labels)
    net.add_transition(join)
    construct(counter)
    return join


def _wire_suffix(net: PetriNet, suffix: Sequence[str], join_target: str, counter: OpCounter) -> None:
    if suffix:
        for a, b in zip(suffix, suffix[1:]):
            _add_edge_place(net, "pba_seq", a, b, counter)
        net.add_arc(transition_name(suffix[-1]), "p_end")
        construct(counter)
    else:
        net.add_arc(join_target, "p_end")
        construct(counter)


def _compile_parallel_block(
    net: PetriNet,
    prefix: Sequence[str],
    branches: Sequence[str],
    suffix: Sequence[str],
    counter: OpCounter,
) -> None:
    split_source = _wire_prefix(net, prefix, branches, counter)
    join = _join_target(net, suffix, branches, counter)
    for branch in branches:
        split_place = place_name("pba_and_split", [split_source], [branch])
        join_place = place_name("pba_and_join", [branch], [join])
        net.add_place(split_place)
        net.add_place(join_place)
        net.add_arc(split_source, split_place)
        net.add_arc(split_place, transition_name(branch))
        net.add_arc(transition_name(branch), join_place)
        net.add_arc(join_place, join)
        construct(counter, 6)
    _wire_suffix(net, suffix, join, counter)


def _compile_optional_singleton_parallel(
    net: PetriNet,
    prefix: Sequence[str],
    mandatory: str,
    optional: str,
    suffix: Sequence[str],
    counter: OpCounter,
) -> None:
    block_labels = sorted([mandatory, optional])
    split_source = _wire_prefix(net, prefix, block_labels, counter)
    join = _join_target(net, suffix, block_labels, counter)

    mandatory_split = place_name("pba_andopt_split", [split_source], [mandatory])
    mandatory_join = place_name("pba_andopt_join", [mandatory], [join])
    net.add_place(mandatory_split)
    net.add_place(mandatory_join)
    net.add_arc(split_source, mandatory_split)
    net.add_arc(mandatory_split, transition_name(mandatory))
    net.add_arc(transition_name(mandatory), mandatory_join)
    net.add_arc(mandatory_join, join)
    construct(counter, 6)

    optional_split = place_name("pba_andopt_split", [split_source], [optional])
    optional_join = place_name("pba_andopt_join", [optional], [join])
    skip = _tau_name("andopt_skip", optional)
    net.add_place(optional_split)
    net.add_place(optional_join)
    net.add_transition(skip)
    construct(counter, 3)
    net.add_arc(split_source, optional_split)
    net.add_arc(optional_split, transition_name(optional))
    net.add_arc(optional_split, skip)
    net.add_arc(transition_name(optional), optional_join)
    net.add_arc(skip, optional_join)
    net.add_arc(optional_join, join)
    construct(counter, 6)
    _wire_suffix(net, suffix, join, counter)


def _compile_block_net(activities: Sequence[str], grammar: Dict[str, object], counter: OpCounter) -> PetriNet:
    net = _add_base_net(activities, counter)
    if grammar["type"] == "parallel_block":
        _compile_parallel_block(
            net,
            grammar["prefix"],  # type: ignore[arg-type]
            grammar["branches"],  # type: ignore[arg-type]
            grammar["suffix"],  # type: ignore[arg-type]
            counter,
        )
    elif grammar["type"] == "optional_singleton_parallel":
        _compile_optional_singleton_parallel(
            net,
            grammar["prefix"],  # type: ignore[arg-type]
            grammar["mandatory_branch"],  # type: ignore[arg-type]
            grammar["optional_branch"],  # type: ignore[arg-type]
            grammar["suffix"],  # type: ignore[arg-type]
            counter,
        )
    else:
        raise ValueError(f"unsupported grammar type: {grammar['type']}")
    return net


def _compile_exact_automaton(log: TraceLog, counter: OpCounter) -> Tuple[PetriNet, Dict[str, object]]:
    children, terminal_nodes, variants = _insert_traces(log, counter)
    node_to_state, _signatures, merge_evidence = _compress_states(children, terminal_nodes, counter)
    edges, terminal_states = _compressed_edges(children, node_to_state, terminal_nodes, counter)
    states = set(node_to_state.values())
    net = _compile_automaton(states, edges, node_to_state[0], terminal_states, counter)
    raw_edge_count = sum(len(outgoing) for outgoing in children)
    evidence = {
        "raw_trie_nodes": len(children),
        "raw_trie_edges": raw_edge_count,
        "compressed_states": len(states),
        "compressed_edges": len(edges),
        "terminal_states": sorted(terminal_states),
        "start_state": node_to_state[0],
        "variant_count": len(variants),
        "state_merges": {
            state: data
            for state, data in sorted(merge_evidence.items())
            if len(data["raw_nodes"]) > 1  # type: ignore[index]
        },
    }
    return net, evidence


def discover(log: TraceLog) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    grammar_name, grammar, attempts = _select_grammar(log, counter)

    if grammar_name == "exact_prefix_automaton":
        net, fallback_evidence = _compile_exact_automaton(log, counter)
    else:
        net = _compile_block_net(activities, grammar, counter)
        fallback_evidence = {}

    evidence = {
        "selected_grammar": grammar_name,
        "grammar_attempts": attempts,
        "grammar": grammar,
        "fallback": fallback_evidence,
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
        "candidate_id": "ALG-0014",
        "name": "Prefix Block Abstraction Miner",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
