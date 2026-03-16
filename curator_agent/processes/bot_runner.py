from __future__ import annotations

import asyncio
import logging
import sys
from asyncio.subprocess import Process
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    # curator_agent/processes/bot_runner.py -> curator_agent -> project root
    return Path(__file__).resolve().parents[2]


class BotProcessManager:
    """Runs `run_bot.py` as a managed subprocess."""

    def __init__(self, restart_delay_seconds: int = 5) -> None:
        self._restart_delay_seconds = restart_delay_seconds
        self._proc: Optional[Process] = None

    async def start(self) -> None:
        if self._proc and self._proc.returncode is None:
            return

        root = _project_root()
        logger.info("Starting bot process")
        self._proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "run_bot.py",
            cwd=str(root),
        )
        logger.info("Bot started (pid=%s)", self._proc.pid)

    def is_running(self) -> bool:
        return self._proc is not None and self._proc.returncode is None

    async def restart_if_needed(self, stop_event: asyncio.Event) -> None:
        if self._proc is None:
            await self.start()
            return

        if self._proc.returncode is None:
            return

        logger.warning(
            "Bot crashed/exited (exit_code=%s). Restarting soon.",
            self._proc.returncode,
        )
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=self._restart_delay_seconds)
            return
        except TimeoutError:
            pass

        await self.start()

    async def supervise(
        self,
        stop_event: asyncio.Event,
        health_check_interval_seconds: float = 2.0,
    ) -> None:
        """Continuously supervise bot, restarting on crash, stopping on request."""
        await self.start()
        logger.info("Bot supervision loop started")
        try:
            while not stop_event.is_set():
                await self.restart_if_needed(stop_event)
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=health_check_interval_seconds)
                except TimeoutError:
                    continue
        finally:
            logger.info("Bot supervision loop stopping")
            await self.stop()

    async def stop(self, timeout_seconds: float = 10.0) -> None:
        if self._proc is None:
            return
        if self._proc.returncode is not None:
            logger.info("Bot already stopped (exit_code=%s)", self._proc.returncode)
            return

        logger.info("Stopping bot (pid=%s)", self._proc.pid)
        self._proc.terminate()
        try:
            await asyncio.wait_for(self._proc.wait(), timeout=timeout_seconds)
            logger.info("Bot stopped (exit_code=%s)", self._proc.returncode)
        except TimeoutError:
            logger.warning("Bot did not stop in time; killing (pid=%s)", self._proc.pid)
            self._proc.kill()
            await self._proc.wait()
            logger.info("Bot killed (exit_code=%s)", self._proc.returncode)

