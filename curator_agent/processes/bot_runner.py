from __future__ import annotations

import logging
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    # curator_agent/processes/bot_runner.py -> curator_agent -> project root
    return Path(__file__).resolve().parents[2]


class BotProcessManager:
    """Runs `run_bot.py` as a managed subprocess."""

    def __init__(self, restart_delay_seconds: int = 5) -> None:
        self._restart_delay_seconds = restart_delay_seconds
        self._proc: subprocess.Popen | None = None

    def start(self) -> None:
        if self._proc and self._proc.poll() is None:
            return

        root = _project_root()
        self._proc = subprocess.Popen(
            [sys.executable, "run_bot.py"],
            cwd=str(root),
        )
        logger.info("Bot started (pid=%s)", self._proc.pid)

    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def restart_if_needed(self) -> None:
        if self._proc is None:
            self.start()
            return

        exit_code = self._proc.poll()
        if exit_code is None:
            return

        logger.warning("Bot crashed/exited (exit_code=%s). Restarting soon.", exit_code)
        time.sleep(self._restart_delay_seconds)
        self.start()

    def run_forever(self, health_check_interval_seconds: float = 2.0) -> None:
        """Continuously run the bot, restarting on crash."""
        self.start()
        while True:
            self.restart_if_needed()
            time.sleep(health_check_interval_seconds)

