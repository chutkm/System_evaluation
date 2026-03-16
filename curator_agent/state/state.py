from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CuratorState:
    """In-memory runtime state for the curator agent."""

    last_analysis_at: datetime | None = None
    analysis_in_progress: bool = False
    last_seen_unprocessed_count: int = 0
    # Additional fields can be added later (e.g. last processed ID).

