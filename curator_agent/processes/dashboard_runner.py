from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class DashboardRunner:
    """Runs Streamlit dashboard as a long-lived subprocess."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None

    def start(self) -> None:
        if self._proc and self._proc.poll() is None:
            return

        root = _project_root()
        self._proc = subprocess.Popen(
            ["streamlit", "run", "dashboard/app.py"],
            cwd=str(root),
        )
        logger.info("Dashboard started (pid=%s)", self._proc.pid)

    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def restart_if_needed(self, restart_delay_seconds: int = 2) -> None:
        if self._proc is None:
            self.start()
            return

        exit_code = self._proc.poll()
        if exit_code is None:
            return

        logger.warning(
            "Dashboard process exited (exit_code=%s). Restarting soon.", exit_code
        )
        time.sleep(restart_delay_seconds)
        self.start()

    def trigger_refresh(self) -> None:
        # Streamlit app reads from DB on rerun; no explicit action required here.
        logger.debug("Dashboard refresh hook (no-op)")

