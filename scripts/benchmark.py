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
    "pmir_split_join_lite",
]


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


def run_algorithm(module_name: str, log: List[List[str]]) -> Dict[str, Any]:
    module = importlib.import_module(module_name)
    result = module.discover(log)
    if "petri_net" in result:
        from petri_eval import replay_log

        result["replay_summary"] = replay_log(result["petri_net"], log)
    return result


def benchmark(log_dir: Path) -> Dict[str, Any]:
    results: Dict[str, Any] = {"logs": {}, "algorithms": ALGORITHMS}
    for log_path in sorted(log_dir.glob("*.json")):
        log = load_log(log_path)
        log_result: Dict[str, Any] = {"trace_count": len(log), "event_count": sum(len(t) for t in log), "results": {}}
        for algorithm in ALGORITHMS:
            try:
                log_result["results"][algorithm] = run_algorithm(algorithm, log)
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
                print(
                    f"  {alg}: ops={ops}, places={summary['places']}, "
                    f"transitions={summary['transitions']}, arcs={summary['arcs']}{replay_text}"
                )


if __name__ == "__main__":
    main()
