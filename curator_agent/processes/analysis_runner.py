from __future__ import annotations

import asyncio
import logging
import sys
from asyncio.subprocess import Process
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class AnalysisRunner:
    """Runs `run_analysis.py` as a one-shot subprocess."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._proc: Process | None = None

    async def run_analysis_once(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("Running analysis script for %s new entries", len(entries))
        async with self._lock:
            root = _project_root()
            self._proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "run_analysis.py",
                cwd=str(root),
        )
            logger.info("Analysis started (pid=%s)", self._proc.pid)
            returncode = await self._proc.wait()
            logger.info("Analysis finished (returncode=%s)", returncode)
            self._proc = None

            if returncode != 0:
                raise RuntimeError(f"run_analysis.py exited with code {returncode}")

            return {"processed": len(entries), "returncode": returncode}

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Terminate currently running analysis (if any)."""
        proc = self._proc
        if proc is None or proc.returncode is not None:
            return

        logger.info("Stopping analysis (pid=%s)", proc.pid)
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout_seconds)
            logger.info("Analysis stopped (exit_code=%s)", proc.returncode)
        except TimeoutError:
            logger.warning("Analysis did not stop in time; killing (pid=%s)", proc.pid)
            proc.kill()
            await proc.wait()
            logger.info("Analysis killed (exit_code=%s)", proc.returncode)

