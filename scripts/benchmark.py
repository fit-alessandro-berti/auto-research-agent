"""Smoke-test benchmark harness for candidate discovery algorithms."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Dict, List

ALGORITHMS = [
    "alpha_lite",
    "dependency_threshold",
    "cut_limited_process_tree",
    "bounded_place_region_miner",
    "region_optional_tau_miner",
    "region_optional_chain_miner",
    "prefix_automaton_compression",
    "prefix_block_abstraction",
    "pmir_split_join_lite",
    "pmir_guarded_split_join",
    "pmir_conflict_aware_optional",
]

NEGATIVE_TRACES = {
    "noise.json": [["A", "B", "D"], ["A", "C", "D"], ["A", "D"]],
    "parallel_ab_cd.json": [["A", "B", "D"], ["A", "C", "D"], ["A", "D"]],
    "sequence.json": [["A", "C", "B", "D"], ["A", "B", "D"], ["A", "D"]],
    "short_loop.json": [["A", "A", "C"], ["B", "A", "C"], ["A", "B", "C"]],
    "skip.json": [["A", "B", "B", "C"], ["A", "C", "B"], ["B", "C"]],
    "xor.json": [["A", "B", "C", "D"], ["A", "D"], ["A", "B", "B", "D"]],
}


def load_log(path: Path) -> List[List[str]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "traces" in data:
        traces = data["traces"]
    elif isinstance(data, list):
        traces = data
    else:
        raise ValueError(f"Unsupported log format in {path}")
    if not all(isinstance(t, list) and all(isinstance(e, str) for e in t) for t in traces):
        raise ValueError(f"Log {path} must contain list[list[str]] traces")
    return traces


def run_algorithm(module_name: str, log: List[List[str]], negative_traces: List[List[str]]) -> Dict[str, Any]:
    module = importlib.import_module(module_name)
    result = module.discover(log)
    if "petri_net" in result:
        from petri_eval import precision_probe, replay_log

        result["replay_summary"] = replay_log(result["petri_net"], log)
        result["precision_probe"] = precision_probe(result["petri_net"], negative_traces)
    return result


def benchmark(log_dir: Path) -> Dict[str, Any]:
    results: Dict[str, Any] = {"logs": {}, "algorithms": ALGORITHMS}
    for log_path in sorted(log_dir.glob("*.json")):
        log = load_log(log_path)
        negative_traces = NEGATIVE_TRACES.get(log_path.name, [])
        log_result: Dict[str, Any] = {
            "trace_count": len(log),
            "event_count": sum(len(t) for t in log),
            "negative_trace_count": len(negative_traces),
            "results": {},
        }
        for algorithm in ALGORITHMS:
            try:
                log_result["results"][algorithm] = run_algorithm(algorithm, log, negative_traces)
            except Exception as exc:  # Keep failures visible and reproducible.
                log_result["results"][algorithm] = {"error": repr(exc)}
        results["logs"][log_path.name] = log_result
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=Path, default=Path("examples/logs"), help="Directory containing JSON logs")
    parser.add_argument("--out", type=Path, default=Path("experiments/smoke-results.json"), help="Output JSON path")
    args = parser.parse_args()

    results = benchmark(args.logs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for log_name, log_result in results["logs"].items():
        print(f"{log_name}: {log_result['trace_count']} traces, {log_result['event_count']} events")
        for alg, alg_result in log_result["results"].items():
            if "error" in alg_result:
                print(f"  {alg}: ERROR {alg_result['error']}")
            else:
                ops = alg_result["operation_counts"]["total"]
                summary = alg_result["structural_summary"]
                replay = alg_result.get("replay_summary", {})
                replay_text = ""
                if replay:
                    replay_text = f", replay={replay['replayed_traces']}/{replay['trace_count']}"
                probe = alg_result.get("precision_probe", {})
                precision_text = ""
                if probe:
                    precision_text = (
                        f", neg_reject={probe['rejected_negative_traces']}/"
                        f"{probe['negative_trace_count']}"
                    )
                print(
                    f"  {alg}: ops={ops}, places={summary['places']}, "
                    f"transitions={summary['transitions']}, arcs={summary['arcs']}"
                    f"{replay_text}{precision_text}"
                )


if __name__ == "__main__":
    main()
