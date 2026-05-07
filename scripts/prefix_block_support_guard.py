"""ALG-0015 wrapper for prefix block abstraction with support/noise guards."""

from __future__ import annotations

from typing import Dict, List

import prefix_block_abstraction


TraceLog = List[List[str]]


def discover(log: TraceLog) -> Dict[str, object]:
    return prefix_block_abstraction.discover(
        log,
        max_parallel_support_skew=2,
        enable_prefix_merge=True,
        enable_dominant_sequence=True,
        allow_exact_fallback=True,
    )
