"""ALG-0026: bounded-count policy set for cut-limited loop evidence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Sequence

import cut_limited_length_bounded_loop
from limited_ops import OpCounter, construct
from pn_ir import PetriNet, place_name, transition_name


TraceLog = List[List[str]]


def _safe_name(*parts: str) -> str:
    return "_".join(parts).replace(" ", "_").replace("/", "_")


def _loop_entry_transition(anchor: str) -> str:
    return f"t_loop_entry_{_safe_name(anchor)}"


def _loop_repeat_transition(anchor: str) -> str:
    return f"t_loop_repeat_{_safe_name(anchor)}"


def _add_labeled_transition(net: PetriNet, transition: str, label: str, counter: OpCounter) -> None:
    net.add_transition(transition)
    net.transition_labels[transition] = label
    construct(counter, 2)


def _wire_transition_sequence(
    net: PetriNet,
    start_place: str,
    transitions: Sequence[str],
    end_place: str,
    counter: OpCounter,
    place_prefix: str,
) -> None:
    if not transitions:
        return
    net.add_arc(start_place, transitions[0])
    construct(counter)
    for left, right in zip(transitions, transitions[1:]):
        place = place_name(place_prefix, [left], [right])
        net.add_place(place)
        net.add_arc(left, place)
        net.add_arc(place, right)
        construct(counter, 3)
    net.add_arc(transitions[-1], end_place)
    construct(counter)


def _add_normal_transitions(
    net: PetriNet,
    activities: Sequence[str],
    duplicate_labeled: Sequence[str],
    counter: OpCounter,
) -> None:
    duplicate_set = set(duplicate_labeled)
    for activity in sorted(activities):
        if activity in duplicate_set:
            continue
        net.add_transition(transition_name(activity))
        construct(counter)


def _body_sequences(process_tree: Dict[str, Any]) -> List[List[str]]:
    if process_tree.get("type") == "single_rework_loop":
        body = process_tree.get("body")
        return [list(body)] if isinstance(body, list) else []
    bodies = process_tree.get("bodies")
    if not isinstance(bodies, list):
        return []
    return [list(body) for body in bodies if isinstance(body, list)]


def _compile_at_most_once_loop(
    activities: Sequence[str],
    process_tree: Dict[str, Any],
    counter: OpCounter,
) -> PetriNet:
    prefix = list(process_tree.get("prefix", []))
    anchor = str(process_tree.get("anchor"))
    suffix = list(process_tree.get("suffix", []))
    bodies = _body_sequences(process_tree)

    net = PetriNet()
    net.add_place("p_start")
    net.add_place("p_end")
    net.initial_marking = {"p_start": 1}
    net.final_marking = {"p_end": 1}
    construct(counter, 2)

    _add_normal_transitions(net, activities, [anchor], counter)
    entry = _loop_entry_transition(anchor)
    repeat = _loop_repeat_transition(anchor)
    _add_labeled_transition(net, entry, anchor, counter)
    _add_labeled_transition(net, repeat, anchor, counter)

    after_entry = "p_loop_policy_after_entry"
    before_repeat = "p_loop_policy_before_repeat"
    suffix_entry = "p_loop_policy_suffix_entry"
    net.add_place(after_entry)
    net.add_place(before_repeat)
    net.add_place(suffix_entry)
    construct(counter, 3)

    prefix_transitions = [transition_name(activity) for activity in prefix]
    entry_place = "p_start"
    if prefix_transitions:
        entry_place = "p_loop_policy_before_entry"
        net.add_place(entry_place)
        construct(counter)
        _wire_transition_sequence(net, "p_start", prefix_transitions, entry_place, counter, "pt_loop_policy_prefix")
    net.add_arc(entry_place, entry)
    net.add_arc(entry, after_entry)
    construct(counter, 2)

    for index, body in enumerate(bodies):
        transitions = [transition_name(activity) for activity in body]
        _wire_transition_sequence(
            net,
            after_entry,
            transitions,
            before_repeat,
            counter,
            f"pt_loop_policy_body_{index}",
        )
    net.add_arc(before_repeat, repeat)
    net.add_arc(repeat, suffix_entry)
    construct(counter, 2)

    zero_exit = "tau_loop_policy_zero_exit"
    net.add_transition(zero_exit)
    net.add_arc(after_entry, zero_exit)
    net.add_arc(zero_exit, suffix_entry)
    construct(counter, 3)

    suffix_transitions = [transition_name(activity) for activity in suffix]
    _wire_transition_sequence(net, suffix_entry, suffix_transitions, "p_end", counter, "pt_loop_policy_suffix")
    return net


def _policy_alternatives(base: Dict[str, Any]) -> Dict[str, Any]:
    evidence = base.get("pmir", {}).get("evidence", {})
    process_tree = evidence.get("process_tree", {})
    if not process_tree.get("bounded_count_ambiguous"):
        return {
            "detected": False,
            "type": None,
            "reason": "no_bounded_count_ambiguous_loop_evidence",
            "selected_policy": None,
            "alternatives": [],
        }
    if process_tree.get("type") not in {
        "single_rework_loop",
        "multi_body_rework_loop",
        "body_support_guard_rework_loop",
    }:
        return {
            "detected": False,
            "type": None,
            "reason": "selected_cut_is_not_supported_loop_evidence",
            "selected_policy": None,
            "alternatives": [],
        }

    activities = base.get("pmir", {}).get("activities", [])
    counter = OpCounter()
    at_most_once = _compile_at_most_once_loop(activities, process_tree, counter)
    compile_counts = counter.to_dict()
    discovery_total = base.get("operation_counts", {}).get("total", 0)
    return {
        "detected": True,
        "type": "loop_count_policy",
        "reason": "zero_one_loop_evidence_does_not_identify_unbounded_vs_at_most_once",
        "selected_policy": "unbounded_repeat",
        "alternatives": [
            {
                "policy": "unbounded_repeat",
                "candidate_source": base.get("candidate_id"),
                "petri_net": base.get("petri_net"),
                "compile_operation_counts": {"total": 0},
                "total_with_discovery_ops": discovery_total,
            },
            {
                "policy": "at_most_once",
                "candidate_source": "ALG-0026",
                "petri_net": at_most_once.to_dict(),
                "compile_operation_counts": compile_counts,
                "total_with_discovery_ops": discovery_total + compile_counts["total"],
            },
        ],
    }


def result_from_base(
    base: Dict[str, Any],
    candidate_id_override: str = "ALG-0026",
    name_override: str = "Loop Count Policy-Set Protocol",
) -> Dict[str, object]:
    result = deepcopy(base)
    result["candidate_id"] = candidate_id_override
    result["name"] = name_override
    policy_set = _policy_alternatives(base)
    result["pmir"]["evidence"]["loop_count_policy_set"] = policy_set
    result["pmir"]["evidence"]["selected_policy"] = policy_set.get("selected_policy")
    return result


def discover(log: TraceLog) -> Dict[str, object]:
    base = cut_limited_length_bounded_loop.discover(log)
    return result_from_base(base)
