from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass
class CuratorConfig:
    """Configuration for the curator agent."""

    poll_interval_seconds: int = int(os.getenv("CURATOR_POLL_INTERVAL", "10"))


def load_config() -> CuratorConfig:
    return CuratorConfig()

