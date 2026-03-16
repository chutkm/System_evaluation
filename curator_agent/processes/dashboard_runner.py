from __future__ import annotations

import asyncio
import logging
from asyncio.subprocess import Process
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class DashboardRunner:
    """Runs Streamlit dashboard as a long-lived subprocess."""

    def __init__(self) -> None:
        self._proc: Optional[Process] = None

    async def start(self) -> None:
        if self._proc and self._proc.returncode is None:
            return

        root = _project_root()
        logger.info("Starting dashboard process (Streamlit)")
        self._proc = await asyncio.create_subprocess_exec(
            "streamlit",
            "run",
            "dashboard/app.py",
            cwd=str(root),
        )
        logger.info("Dashboard started (pid=%s)", self._proc.pid)

    def is_running(self) -> bool:
        return self._proc is not None and self._proc.returncode is None

    async def restart_if_needed(
        self,
        stop_event: asyncio.Event,
        restart_delay_seconds: int = 2,
    ) -> None:
        if self._proc is None:
            await self.start()
            return

        if self._proc.returncode is None:
            return

        logger.warning(
            "Dashboard process exited (exit_code=%s). Restarting soon.",
            self._proc.returncode,
        )
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=restart_delay_seconds)
            return
        except TimeoutError:
            pass
        await self.start()

    def trigger_refresh(self) -> None:
        # Streamlit app reads from DB on rerun; no explicit action required here.
        logger.debug("Dashboard refresh hook (no-op)")

    async def supervise(
        self, stop_event: asyncio.Event, health_check_interval_seconds: float = 2.0
    ) -> None:
        await self.start()
        logger.info("Dashboard supervision loop started")
        try:
            while not stop_event.is_set():
                await self.restart_if_needed(stop_event)
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=health_check_interval_seconds)
                except TimeoutError:
                    continue
        finally:
            logger.info("Dashboard supervision loop stopping")
            await self.stop()

    async def stop(self, timeout_seconds: float = 10.0) -> None:
        if self._proc is None:
            return
        if self._proc.returncode is not None:
            logger.info("Dashboard already stopped (exit_code=%s)", self._proc.returncode)
            return

        logger.info("Stopping dashboard (pid=%s)", self._proc.pid)
        self._proc.terminate()
        try:
            await asyncio.wait_for(self._proc.wait(), timeout=timeout_seconds)
            logger.info("Dashboard stopped (exit_code=%s)", self._proc.returncode)
        except TimeoutError:
            logger.warning(
                "Dashboard did not stop in time; killing (pid=%s)", self._proc.pid
            )
            self._proc.kill()
            await self._proc.wait()
            logger.info("Dashboard killed (exit_code=%s)", self._proc.returncode)

