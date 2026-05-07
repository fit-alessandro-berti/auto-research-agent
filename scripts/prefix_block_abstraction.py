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
from limited_ops import (
    OpCounter,
    arithmetic,
    comparison,
    construct,
    dict_increment,
    relation_classification,
    scan_event,
    set_insert,
    set_lookup,
)
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


def _support_counts(segments: Sequence[Sequence[str]], counter: OpCounter) -> List[int]:
    counts: Counter = Counter()
    for segment in segments:
        counts[tuple(segment)] += 1
        dict_increment(counter)
    return sorted(counts.values())


def _support_skew_ok(
    segments: Sequence[Sequence[str]],
    max_parallel_support_skew: Optional[int],
    counter: OpCounter,
) -> Tuple[bool, List[int]]:
    counts = _support_counts(segments, counter)
    comparison(counter)
    if not counts or max_parallel_support_skew is None:
        return True, counts
    arithmetic(counter)
    comparison(counter)
    return max(counts) <= min(counts) * max_parallel_support_skew, counts


def _parallel_block_from_segments(
    prefix: Sequence[str],
    suffix: Sequence[str],
    segments: Sequence[Sequence[str]],
    max_parallel_support_skew: Optional[int],
    counter: OpCounter,
    origin: str,
) -> Optional[Dict[str, object]]:
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
    support_ok, support_counts = _support_skew_ok(segments, max_parallel_support_skew, counter)
    if not support_ok:
        return None
    return {
        "type": "parallel_block",
        "prefix": prefix,
        "branches": sorted(first_set),
        "suffix": suffix,
        "origin": origin,
        "support_counts": support_counts,
    }


def _detect_parallel_block(
    log: TraceLog,
    counter: OpCounter,
    max_parallel_support_skew: Optional[int] = None,
    enable_prefix_merge: bool = False,
    prefix_merge_policy: str = "before_common",
) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    prefix = _common_prefix(log, counter)
    suffix = _common_suffix(log, len(prefix), counter)
    segments = _middle_segments(log, len(prefix), len(suffix))

    if enable_prefix_merge and len(prefix) > 1 and prefix_merge_policy == "before_common":
        moved = prefix[-1]
        merged_segments = [[moved, *segment] for segment in segments]
        construct(counter, len(merged_segments))
        merged = _parallel_block_from_segments(
            prefix[:-1],
            suffix,
            merged_segments,
            max_parallel_support_skew,
            counter,
            "prefix_merge",
        )
        if merged is not None:
            return merged

    common_boundary = _parallel_block_from_segments(
        prefix,
        suffix,
        segments,
        max_parallel_support_skew,
        counter,
        "common_boundary",
    )
    if not enable_prefix_merge or len(prefix) <= 1:
        return common_boundary
    if prefix_merge_policy == "after_common_rejects" and common_boundary is not None:
        return common_boundary
    if prefix_merge_policy == "after_common_rejects":
        moved = prefix[-1]
        merged_segments = [[moved, *segment] for segment in segments]
        construct(counter, len(merged_segments))
        merged = _parallel_block_from_segments(
            prefix[:-1],
            suffix,
            merged_segments,
            max_parallel_support_skew,
            counter,
            "prefix_merge",
        )
        if merged is not None:
            return merged
    return common_boundary


def _prefix_merge_ambiguity(
    log: TraceLog,
    counter: OpCounter,
    max_parallel_support_skew: Optional[int],
) -> Dict[str, object]:
    relation_classification(counter)
    prefix = _common_prefix(log, counter)
    suffix = _common_suffix(log, len(prefix), counter)
    segments = _middle_segments(log, len(prefix), len(suffix))
    common_boundary = _parallel_block_from_segments(
        prefix,
        suffix,
        segments,
        max_parallel_support_skew,
        counter,
        "common_boundary",
    )
    prefix_merge = None
    if len(prefix) > 1:
        moved = prefix[-1]
        merged_segments = [[moved, *segment] for segment in segments]
        construct(counter, len(merged_segments))
        prefix_merge = _parallel_block_from_segments(
            prefix[:-1],
            suffix,
            merged_segments,
            max_parallel_support_skew,
            counter,
            "prefix_merge",
        )

    comparison(counter, 2)
    if common_boundary is None or prefix_merge is None:
        return {
            "detected": False,
            "reason": "requires both common_boundary and prefix_merge parallel alternatives",
        }

    common_signature = (
        tuple(common_boundary["prefix"]),  # type: ignore[index]
        tuple(common_boundary["branches"]),  # type: ignore[index]
        tuple(common_boundary["suffix"]),  # type: ignore[index]
    )
    merge_signature = (
        tuple(prefix_merge["prefix"]),  # type: ignore[index]
        tuple(prefix_merge["branches"]),  # type: ignore[index]
        tuple(prefix_merge["suffix"]),  # type: ignore[index]
    )
    comparison(counter)
    if common_signature == merge_signature:
        return {
            "detected": False,
            "reason": "common_boundary and prefix_merge alternatives are equivalent",
            "alternatives": [common_boundary],
        }
    return {
        "detected": True,
        "type": "prefix_merge_vs_common_boundary",
        "reason": "both grammars replay observed traces but imply different branch scopes",
        "alternatives": [
            {
                "policy": "sequence_prefix_precision",
                "grammar": common_boundary,
            },
            {
                "policy": "full_parallel_generalization",
                "grammar": prefix_merge,
            },
        ],
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


def _detect_dominant_sequence(
    log: TraceLog,
    counter: OpCounter,
    min_dominant_count: int = 2,
    min_dominant_ratio_percent: int = 60,
) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    if not log:
        return None
    first_set = set(log[0])
    set_insert(counter, len(first_set))
    for trace in log:
        trace_set = set(trace)
        set_insert(counter, len(trace_set))
        comparison(counter)
        if trace_set != first_set:
            return None
    counts: Counter = Counter()
    for trace in log:
        counts[tuple(trace)] += 1
        dict_increment(counter)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    sequence, support = ranked[0]
    comparison(counter, 3)
    if support < min_dominant_count or _has_duplicate_labels(sequence, counter):
        return None
    if len(ranked) > 1 and support == ranked[1][1]:
        return None
    arithmetic(counter)
    comparison(counter)
    if support * 100 < len(log) * min_dominant_ratio_percent:
        return None
    return {
        "type": "dominant_sequence",
        "sequence": list(sequence),
        "support": support,
        "trace_count": len(log),
        "variant_count": len(ranked),
    }


def _select_grammar(
    log: TraceLog,
    counter: OpCounter,
    max_parallel_support_skew: Optional[int] = None,
    enable_prefix_merge: bool = False,
    enable_dominant_sequence: bool = False,
    prefix_merge_policy: str = "before_common",
    min_dominant_count: int = 2,
    min_dominant_ratio_percent: int = 60,
) -> Tuple[str, Dict[str, object], List[Dict[str, str]]]:
    attempts: List[Dict[str, str]] = []
    grammar = _detect_parallel_block(
        log,
        counter,
        max_parallel_support_skew,
        enable_prefix_merge,
        prefix_merge_policy,
    )
    if grammar is not None:
        attempts.append({"grammar": "parallel_block", "result": "accepted"})
        return "parallel_block", grammar, attempts
    attempts.append({"grammar": "parallel_block", "result": "rejected"})

    grammar = _detect_optional_singleton_parallel(log, counter)
    if grammar is not None:
        attempts.append({"grammar": "optional_singleton_parallel", "result": "accepted"})
        return "optional_singleton_parallel", grammar, attempts
    attempts.append({"grammar": "optional_singleton_parallel", "result": "rejected"})

    if enable_dominant_sequence:
        grammar = _detect_dominant_sequence(
            log,
            counter,
            min_dominant_count=min_dominant_count,
            min_dominant_ratio_percent=min_dominant_ratio_percent,
        )
        if grammar is not None:
            attempts.append({"grammar": "dominant_sequence", "result": "accepted"})
            return "dominant_sequence", grammar, attempts
        attempts.append({"grammar": "dominant_sequence", "result": "rejected"})
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


def _wire_sequence(net: PetriNet, sequence: Sequence[str], counter: OpCounter) -> None:
    if not sequence:
        return
    net.add_arc("p_start", transition_name(sequence[0]))
    net.add_arc(transition_name(sequence[-1]), "p_end")
    construct(counter, 2)
    for a, b in zip(sequence, sequence[1:]):
        _add_edge_place(net, "pba_seq", a, b, counter)


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
    elif grammar["type"] == "dominant_sequence":
        _wire_sequence(
            net,
            grammar["sequence"],  # type: ignore[arg-type]
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


def _compile_rejecting_net(activities: Sequence[str], counter: OpCounter) -> PetriNet:
    return _add_base_net(activities, counter)


def discover(
    log: TraceLog,
    max_parallel_support_skew: Optional[int] = None,
    enable_prefix_merge: bool = False,
    enable_dominant_sequence: bool = False,
    allow_exact_fallback: bool = True,
    prefix_merge_policy: str = "before_common",
    min_dominant_count: int = 2,
    min_dominant_ratio_percent: int = 60,
    emit_prefix_merge_ambiguity: bool = False,
    candidate_id_override: Optional[str] = None,
    name_override: Optional[str] = None,
) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    grammar_name, grammar, attempts = _select_grammar(
        log,
        counter,
        max_parallel_support_skew=max_parallel_support_skew,
        enable_prefix_merge=enable_prefix_merge,
        enable_dominant_sequence=enable_dominant_sequence,
        prefix_merge_policy=prefix_merge_policy,
        min_dominant_count=min_dominant_count,
        min_dominant_ratio_percent=min_dominant_ratio_percent,
    )

    if grammar_name == "exact_prefix_automaton":
        if allow_exact_fallback:
            net, fallback_evidence = _compile_exact_automaton(log, counter)
        else:
            grammar_name = "no_grammar"
            grammar = {"type": "no_grammar"}
            net = _compile_rejecting_net(activities, counter)
            fallback_evidence = {"disabled": True}
    else:
        net = _compile_block_net(activities, grammar, counter)
        fallback_evidence = {}

    ambiguity_evidence = {"detected": False, "reason": "not requested"}
    if emit_prefix_merge_ambiguity:
        ambiguity_evidence = _prefix_merge_ambiguity(log, counter, max_parallel_support_skew)
        ambiguity_evidence["selected_policy"] = (
            "full_parallel_generalization"
            if isinstance(grammar, dict) and grammar.get("origin") == "prefix_merge"
            else "sequence_prefix_precision"
            if isinstance(grammar, dict) and grammar.get("origin") == "common_boundary"
            else "not_applicable"
        )

    if max_parallel_support_skew is not None and enable_prefix_merge and enable_dominant_sequence:
        candidate_id = "ALG-0015" if allow_exact_fallback else "ALG-0016"
        name = (
            "Prefix Block Support-Guard Miner"
            if allow_exact_fallback
            else "Prefix Block Grammar-Only Ablation"
        )
    else:
        candidate_id = "ALG-0014"
        name = "Prefix Block Abstraction Miner"
    if candidate_id_override is not None:
        candidate_id = candidate_id_override
        name = name_override or name

    evidence = {
        "configuration": {
            "max_parallel_support_skew": max_parallel_support_skew,
            "enable_prefix_merge": enable_prefix_merge,
            "enable_dominant_sequence": enable_dominant_sequence,
            "allow_exact_fallback": allow_exact_fallback,
            "prefix_merge_policy": prefix_merge_policy,
            "min_dominant_count": min_dominant_count,
            "min_dominant_ratio_percent": min_dominant_ratio_percent,
            "emit_prefix_merge_ambiguity": emit_prefix_merge_ambiguity,
        },
        "selected_grammar": grammar_name,
        "grammar_attempts": attempts,
        "grammar": grammar,
        "fallback": fallback_evidence,
        "ambiguity": ambiguity_evidence,
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
        "candidate_id": candidate_id,
        "name": name,
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
