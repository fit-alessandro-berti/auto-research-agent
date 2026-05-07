"""ALG-0024 wrapper for cut-limited process-tree mining with multi-body loop choice."""

from __future__ import annotations

from typing import Dict, List

import cut_limited_process_tree


TraceLog = List[List[str]]


def discover(log: TraceLog) -> Dict[str, object]:
    return cut_limited_process_tree.discover(
        log,
        enable_parallel_optional=True,
        enable_short_loop=True,
        enable_multi_body_loop=True,
        candidate_id_override="ALG-0024",
        name_override="Cut-Limited Multi-Body Rework Loop Miner",
    )
