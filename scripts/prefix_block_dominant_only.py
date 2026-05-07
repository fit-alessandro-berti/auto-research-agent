"""ALG-0019 wrapper for prefix block abstraction with dominant-sequence handling only."""

from __future__ import annotations

from typing import Dict, List

import prefix_block_abstraction


TraceLog = List[List[str]]


def discover(log: TraceLog) -> Dict[str, object]:
    return prefix_block_abstraction.discover(
        log,
        max_parallel_support_skew=2,
        enable_prefix_merge=False,
        enable_dominant_sequence=True,
        allow_exact_fallback=True,
        candidate_id_override="ALG-0019",
        name_override="Prefix Block Dominant-Sequence Ablation",
    )
