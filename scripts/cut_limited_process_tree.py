"""ALG-0003: Cut-Limited Process Tree Miner.

This is a deliberately small inductive-miner-style baseline. It recognizes a
bounded menu of block patterns and compiles those patterns directly to a Petri
net while recording the process-tree evidence used for the decision.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Sequence, Set, Tuple

from alpha_lite import classify_relations, summarize_log
from limited_ops import OpCounter, comparison, construct, relation_classification, scan_event, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name


TraceLog = List[List[str]]
IndexEdge = Tuple[int, int]


def _safe_name(*parts: str) -> str:
    return "_".join(parts).replace(" ", "_").replace("/", "_")


def _tau_name(prefix: str, *parts: str) -> str:
    return f"tau_pt_{prefix}_{_safe_name(*parts)}"


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


def _add_edge_place(net: PetriNet, prefix: str, a: str, b: str, counter: OpCounter) -> str:
    place = place_name(prefix, [a], [b])
    net.add_place(place)
    net.add_arc(transition_name(a), place)
    net.add_arc(place, transition_name(b))
    construct(counter, 3)
    return place


def _wire_chain(net: PetriNet, sequence: Sequence[str], counter: OpCounter) -> None:
    if not sequence:
        return
    net.add_arc("p_start", transition_name(sequence[0]))
    net.add_arc(transition_name(sequence[-1]), "p_end")
    construct(counter, 2)
    for a, b in zip(sequence, sequence[1:]):
        _add_edge_place(net, "pt_seq", a, b, counter)


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


def _all_traces_equal(log: TraceLog, counter: OpCounter) -> bool:
    if not log:
        return False
    reference = log[0]
    for trace in log[1:]:
        comparison(counter)
        if trace != reference:
            return False
    return True


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


def _detect_sequence(log: TraceLog, counter: OpCounter) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    if not _all_traces_equal(log, counter):
        return None
    sequence = list(log[0])
    if not sequence or _has_duplicate_labels(sequence, counter):
        return None
    return {"type": "sequence", "children": [{"type": "activity", "label": a} for a in sequence], "sequence": sequence}


def _detect_xor(log: TraceLog, counter: OpCounter) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    prefix = _common_prefix(log, counter)
    suffix = _common_suffix(log, len(prefix), counter)
    segments = _middle_segments(log, len(prefix), len(suffix))
    alternatives: Set[str] = set()
    for segment in segments:
        comparison(counter)
        if len(segment) != 1:
            return None
        alternatives.add(segment[0])
        set_insert(counter)
    comparison(counter)
    if len(alternatives) < 2:
        return None
    full_labels = list(prefix) + sorted(alternatives) + list(suffix)
    if _has_duplicate_labels(full_labels, counter):
        return None
    return {
        "type": "sequence",
        "children": [
            *[{"type": "activity", "label": a} for a in prefix],
            {"type": "xor", "children": [{"type": "activity", "label": a} for a in sorted(alternatives)]},
            *[{"type": "activity", "label": a} for a in suffix],
        ],
        "cut": "xor",
        "prefix": prefix,
        "alternatives": sorted(alternatives),
        "suffix": suffix,
    }


def _detect_parallel(log: TraceLog, counter: OpCounter) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    prefix = _common_prefix(log, counter)
    suffix = _common_suffix(log, len(prefix), counter)
    segments = _middle_segments(log, len(prefix), len(suffix))
    if not segments:
        return None
    first_set = set(segments[0])
    set_insert(counter, len(first_set))
    if len(first_set) < 2:
        return None
    observed_order_variation = False
    for segment in segments:
        segment_set = set(segment)
        set_insert(counter, len(segment_set))
        comparison(counter, 3)
        if len(segment) != len(segment_set) or segment_set != first_set:
            return None
        if segment != segments[0]:
            observed_order_variation = True
    if not observed_order_variation:
        return None
    full_labels = list(prefix) + sorted(first_set) + list(suffix)
    if _has_duplicate_labels(full_labels, counter):
        return None
    return {
        "type": "sequence",
        "children": [
            *[{"type": "activity", "label": a} for a in prefix],
            {"type": "parallel", "children": [{"type": "activity", "label": a} for a in sorted(first_set)]},
            *[{"type": "activity", "label": a} for a in suffix],
        ],
        "cut": "parallel",
        "prefix": prefix,
        "branches": sorted(first_set),
        "suffix": suffix,
    }


def _detect_parallel_optional_sequence(log: TraceLog, counter: OpCounter) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    prefix = _common_prefix(log, counter)
    suffix = _common_suffix(log, len(prefix), counter)
    segments = _middle_segments(log, len(prefix), len(suffix))
    if not segments:
        return None

    middle_labels: Set[str] = set()
    for segment in segments:
        segment_set = set(segment)
        set_insert(counter, len(segment_set))
        comparison(counter)
        if len(segment) != len(segment_set):
            return None
        middle_labels.update(segment_set)
        set_insert(counter, len(segment_set))
    comparison(counter)
    if len(middle_labels) != 3:
        return None
    full_labels = list(prefix) + sorted(middle_labels) + list(suffix)
    if _has_duplicate_labels(full_labels, counter):
        return None

    for head in sorted(middle_labels):
        for optional_tail in sorted(middle_labels - {head}):
            singleton_candidates = sorted(middle_labels - {head, optional_tail})
            if len(singleton_candidates) != 1:
                continue
            singleton = singleton_candidates[0]
            tail_present = False
            tail_absent = False
            head_before_singleton = False
            singleton_before_head = False
            accepted = True
            for segment in segments:
                segment_set = set(segment)
                set_lookup(counter, 3)
                comparison(counter, 3)
                if head not in segment_set or singleton not in segment_set:
                    accepted = False
                    break
                if optional_tail in segment_set:
                    tail_present = True
                    comparison(counter)
                    if segment.index(optional_tail) < segment.index(head):
                        accepted = False
                        break
                else:
                    tail_absent = True
                comparison(counter)
                if segment.index(head) < segment.index(singleton):
                    head_before_singleton = True
                else:
                    singleton_before_head = True
            comparison(counter, 4)
            if accepted and tail_present and tail_absent and head_before_singleton and singleton_before_head:
                return {
                    "type": "sequence",
                    "children": [
                        *[{"type": "activity", "label": a} for a in prefix],
                        {
                            "type": "parallel",
                            "children": [
                                {
                                    "type": "optional_sequence",
                                    "canonical": [head, optional_tail],
                                    "optional": optional_tail,
                                },
                                {"type": "activity", "label": singleton},
                            ],
                        },
                        *[{"type": "activity", "label": a} for a in suffix],
                    ],
                    "cut": "parallel_optional_sequence",
                    "prefix": prefix,
                    "optional_branch": [head, optional_tail],
                    "singleton_branch": singleton,
                    "suffix": suffix,
                }
    return None


def _subsequence_indices(trace: Sequence[str], canonical: Sequence[str], counter: OpCounter) -> Optional[List[int]]:
    indices: List[int] = []
    position = 0
    for event in trace:
        scan_event(counter)
        found_index: Optional[int] = None
        while position < len(canonical):
            comparison(counter)
            if canonical[position] == event:
                found_index = position
                position += 1
                break
            position += 1
        if found_index is None:
            return None
        indices.append(found_index)
        construct(counter)
    return indices


def _detect_optional_sequence(log: TraceLog, counter: OpCounter) -> Optional[Dict[str, object]]:
    relation_classification(counter)
    if not log:
        return None
    canonical = max((list(trace) for trace in log), key=lambda trace: (len(trace), tuple(trace)))
    comparison(counter, len(log))
    if len(canonical) < 2 or _has_duplicate_labels(canonical, counter):
        return None
    skip_edges: Set[IndexEdge] = set()
    has_short_trace = False
    for trace in log:
        indices = _subsequence_indices(trace, canonical, counter)
        if indices is None:
            return None
        comparison(counter, 3)
        if not indices or indices[0] != 0 or indices[-1] != len(canonical) - 1:
            return None
        if len(indices) < len(canonical):
            has_short_trace = True
        for left, right in zip(indices, indices[1:]):
            comparison(counter)
            if right > left + 1:
                skip_edges.add((left, right))
                set_insert(counter)
    if not has_short_trace or not skip_edges:
        return None
    return {
        "type": "optional_sequence",
        "canonical": canonical,
        "skip_edges": [
            {"from": canonical[left], "to": canonical[right], "skipped": canonical[left + 1 : right]}
            for left, right in sorted(skip_edges)
        ],
        "skip_index_edges": sorted(skip_edges),
    }


def _compile_xor(net: PetriNet, prefix: Sequence[str], alternatives: Sequence[str], suffix: Sequence[str], counter: OpCounter) -> None:
    if prefix:
        net.add_arc("p_start", transition_name(prefix[0]))
        construct(counter)
        for a, b in zip(prefix, prefix[1:]):
            _add_edge_place(net, "pt_seq", a, b, counter)
        split_place = place_name("pt_xor_split", [prefix[-1]], alternatives)
        net.add_place(split_place)
        net.add_arc(transition_name(prefix[-1]), split_place)
        construct(counter, 2)
    else:
        split_place = "p_start"

    for branch in alternatives:
        net.add_arc(split_place, transition_name(branch))
        construct(counter)

    if suffix:
        join_place = place_name("pt_xor_join", alternatives, [suffix[0]])
        net.add_place(join_place)
        construct(counter)
        for branch in alternatives:
            net.add_arc(transition_name(branch), join_place)
            construct(counter)
        net.add_arc(join_place, transition_name(suffix[0]))
        construct(counter)
        for a, b in zip(suffix, suffix[1:]):
            _add_edge_place(net, "pt_seq", a, b, counter)
        net.add_arc(transition_name(suffix[-1]), "p_end")
        construct(counter)
    else:
        for branch in alternatives:
            net.add_arc(transition_name(branch), "p_end")
            construct(counter)


def _compile_parallel(net: PetriNet, prefix: Sequence[str], branches: Sequence[str], suffix: Sequence[str], counter: OpCounter) -> None:
    if prefix:
        net.add_arc("p_start", transition_name(prefix[0]))
        construct(counter)
        for a, b in zip(prefix, prefix[1:]):
            _add_edge_place(net, "pt_seq", a, b, counter)
        split_source = transition_name(prefix[-1])
    else:
        split_source = _tau_name("and_start", *branches)
        net.add_transition(split_source)
        net.add_arc("p_start", split_source)
        construct(counter, 2)

    for branch in branches:
        split_place = place_name("pt_and_split", [split_source], [branch])
        net.add_place(split_place)
        net.add_arc(split_source, split_place)
        net.add_arc(split_place, transition_name(branch))
        construct(counter, 3)

    if suffix:
        join_target = transition_name(suffix[0])
        for branch in branches:
            join_place = place_name("pt_and_join", [branch], [suffix[0]])
            net.add_place(join_place)
            net.add_arc(transition_name(branch), join_place)
            net.add_arc(join_place, join_target)
            construct(counter, 3)
        for a, b in zip(suffix, suffix[1:]):
            _add_edge_place(net, "pt_seq", a, b, counter)
        net.add_arc(transition_name(suffix[-1]), "p_end")
        construct(counter)
    else:
        join_transition = _tau_name("and_end", *branches)
        net.add_transition(join_transition)
        construct(counter)
        for branch in branches:
            join_place = place_name("pt_and_join", [branch], ["end"])
            net.add_place(join_place)
            net.add_arc(transition_name(branch), join_place)
            net.add_arc(join_place, join_transition)
            construct(counter, 3)
        net.add_arc(join_transition, "p_end")
        construct(counter)


def _compile_parallel_optional_sequence(
    net: PetriNet,
    prefix: Sequence[str],
    optional_branch: Sequence[str],
    singleton_branch: str,
    suffix: Sequence[str],
    counter: OpCounter,
) -> None:
    head, optional_tail = optional_branch
    branch_labels = [head, optional_tail, singleton_branch]
    if prefix:
        net.add_arc("p_start", transition_name(prefix[0]))
        construct(counter)
        for a, b in zip(prefix, prefix[1:]):
            _add_edge_place(net, "pt_seq", a, b, counter)
        split_source = transition_name(prefix[-1])
    else:
        split_source = _tau_name("andopt_start", *branch_labels)
        net.add_transition(split_source)
        net.add_arc("p_start", split_source)
        construct(counter, 2)

    if suffix:
        join_target = transition_name(suffix[0])
        join_label = suffix[0]
    else:
        join_target = _tau_name("andopt_end", *branch_labels)
        join_label = "end"
        net.add_transition(join_target)
        construct(counter)

    singleton_split = place_name("pt_andopt_split", [split_source], [singleton_branch])
    singleton_join = place_name("pt_andopt_join", [singleton_branch], [join_label])
    net.add_place(singleton_split)
    net.add_place(singleton_join)
    net.add_arc(split_source, singleton_split)
    net.add_arc(singleton_split, transition_name(singleton_branch))
    net.add_arc(transition_name(singleton_branch), singleton_join)
    net.add_arc(singleton_join, join_target)
    construct(counter, 6)

    optional_split = place_name("pt_andopt_split", [split_source], [head])
    optional_place = place_name("pt_andopt_optional", [head], [optional_tail])
    optional_join = place_name("pt_andopt_join", [head, optional_tail], [join_label])
    skip = _tau_name("andopt_skip", head, optional_tail)
    net.add_place(optional_split)
    net.add_place(optional_place)
    net.add_place(optional_join)
    net.add_transition(skip)
    construct(counter, 4)
    net.add_arc(split_source, optional_split)
    net.add_arc(optional_split, transition_name(head))
    net.add_arc(transition_name(head), optional_place)
    net.add_arc(optional_place, transition_name(optional_tail))
    net.add_arc(optional_place, skip)
    net.add_arc(transition_name(optional_tail), optional_join)
    net.add_arc(skip, optional_join)
    net.add_arc(optional_join, join_target)
    construct(counter, 8)

    if suffix:
        for a, b in zip(suffix, suffix[1:]):
            _add_edge_place(net, "pt_seq", a, b, counter)
        net.add_arc(transition_name(suffix[-1]), "p_end")
        construct(counter)
    else:
        net.add_arc(join_target, "p_end")
        construct(counter)


def _compile_optional_sequence(
    net: PetriNet,
    canonical: Sequence[str],
    skip_index_edges: Sequence[IndexEdge],
    counter: OpCounter,
) -> None:
    _wire_chain(net, canonical, counter)
    boundary_places = {
        index: place_name("pt_seq", [canonical[index]], [canonical[index + 1]])
        for index in range(len(canonical) - 1)
    }
    for left, right in skip_index_edges:
        if right <= left + 1:
            continue
        skipped = canonical[left + 1 : right]
        tau = _tau_name("skip", canonical[left], canonical[right], "over", *skipped)
        net.add_transition(tau)
        net.add_arc(boundary_places[left], tau)
        net.add_arc(tau, boundary_places[right - 1])
        construct(counter, 3)


def _compile_fallback(
    net: PetriNet,
    starts: Counter,
    ends: Counter,
    dfg: Counter,
    counter: OpCounter,
) -> Dict[str, object]:
    for activity in sorted(starts):
        net.add_arc("p_start", transition_name(activity))
        construct(counter)
    for activity in sorted(ends):
        net.add_arc(transition_name(activity), "p_end")
        construct(counter)
    emitted_edges = []
    for a, b in sorted(dfg):
        _add_edge_place(net, "pt_fallback_edge", a, b, counter)
        emitted_edges.append([a, b])
    return {"type": "fallback_dfg", "edge_places": emitted_edges}


def _select_cut(
    log: TraceLog,
    counter: OpCounter,
    enable_parallel_optional: bool = True,
) -> Tuple[str, Dict[str, object], List[Dict[str, str]]]:
    attempts: List[Dict[str, str]] = []
    detectors = [
        ("sequence", _detect_sequence),
        ("xor", _detect_xor),
        ("parallel", _detect_parallel),
    ]
    if enable_parallel_optional:
        detectors.append(("parallel_optional_sequence", _detect_parallel_optional_sequence))
    detectors.append(("optional_sequence", _detect_optional_sequence))

    for cut_name, detector in detectors:
        result = detector(log, counter)
        if result is not None:
            attempts.append({"cut": cut_name, "result": "accepted"})
            return cut_name, result, attempts
        attempts.append({"cut": cut_name, "result": "rejected"})
    fallback = {"type": "fallback_dfg"}
    return "fallback_dfg", fallback, attempts


def discover(log: TraceLog, enable_parallel_optional: bool = True) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    cut_name, process_tree, cut_attempts = _select_cut(log, counter, enable_parallel_optional)

    net = _add_base_net(activities, counter)
    if cut_name == "sequence":
        _wire_chain(net, process_tree["sequence"], counter)  # type: ignore[arg-type]
    elif cut_name == "xor":
        _compile_xor(
            net,
            process_tree["prefix"],  # type: ignore[arg-type]
            process_tree["alternatives"],  # type: ignore[arg-type]
            process_tree["suffix"],  # type: ignore[arg-type]
            counter,
        )
    elif cut_name == "parallel":
        _compile_parallel(
            net,
            process_tree["prefix"],  # type: ignore[arg-type]
            process_tree["branches"],  # type: ignore[arg-type]
            process_tree["suffix"],  # type: ignore[arg-type]
            counter,
        )
    elif cut_name == "parallel_optional_sequence":
        _compile_parallel_optional_sequence(
            net,
            process_tree["prefix"],  # type: ignore[arg-type]
            process_tree["optional_branch"],  # type: ignore[arg-type]
            process_tree["singleton_branch"],  # type: ignore[arg-type]
            process_tree["suffix"],  # type: ignore[arg-type]
            counter,
        )
    elif cut_name == "optional_sequence":
        _compile_optional_sequence(
            net,
            process_tree["canonical"],  # type: ignore[arg-type]
            process_tree["skip_index_edges"],  # type: ignore[arg-type]
            counter,
        )
    else:
        process_tree = _compile_fallback(net, starts, ends, dfg, counter)

    evidence = {
        "configuration": {"enable_parallel_optional": enable_parallel_optional},
        "selected_cut": cut_name,
        "cut_attempts": cut_attempts,
        "process_tree": process_tree,
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
        "candidate_id": "ALG-0003",
        "name": "Cut-Limited Process Tree Miner",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
