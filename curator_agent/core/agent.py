from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import List
import signal

from curator_agent.core.events import (
    AnalysisCompleted,
    AnalysisStarted,
    DashboardUpdateRequested,
    EventBus,
    NewDataDetected,
)
from curator_agent.db.monitor import DatabaseMonitor
from curator_agent.processes.analysis_runner import AnalysisRunner
from curator_agent.processes.bot_runner import BotProcessManager
from curator_agent.processes.dashboard_runner import DashboardRunner
from curator_agent.state.state import CuratorState


logger = logging.getLogger(__name__)


class CuratorAgent:
    """Main long-running curator process.

    Responsibilities:
    - start and supervise the bot
    - monitor the database for new feedback
    - trigger analysis when new data appears
    - trigger dashboard updates after analysis
    """

    def __init__(
        self,
        poll_interval_seconds: int = 10,
    ) -> None:
        self._poll_interval_seconds = poll_interval_seconds

        self.state = CuratorState()
        self.events = EventBus()
        self.db_monitor = DatabaseMonitor()

        self._bot_manager = BotProcessManager()
        self._analysis_runner = AnalysisRunner()
        self._dashboard_runner = DashboardRunner()

        self._stop_event = asyncio.Event()
        self._tasks: list[asyncio.Task] = []
        self._stop_lock = asyncio.Lock()
        self._analysis_requested = asyncio.Event()

        self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        self.events.subscribe(NewDataDetected, self._on_new_data)
        self.events.subscribe(AnalysisCompleted, self._on_analysis_completed)

    async def start(self) -> None:
        logger.info("CuratorAgent starting")
        self._install_signal_handlers()

        # Start subprocess components first (and supervise them).
        self._tasks = [
            asyncio.create_task(self._bot_manager.supervise(self._stop_event), name="bot-supervisor"),
            asyncio.create_task(
                self._dashboard_runner.supervise(self._stop_event), name="dashboard-supervisor"
            ),
            asyncio.create_task(self._watch_database_loop(), name="db-watch"),
            asyncio.create_task(self._analysis_loop(), name="analysis-loop"),
        ]

        try:
            await self._stop_event.wait()
        finally:
            await self.stop()

        logger.info("CuratorAgent stopped")

    async def stop(self) -> None:
        async with self._stop_lock:
            if self._stop_event.is_set():
                # Stop can be called multiple times safely.
                pass
            else:
                logger.info("CuratorAgent stop requested")
                self._stop_event.set()
                self._analysis_requested.set()

            # Cancel internal tasks (they should also observe stop_event)
            for task in list(self._tasks):
                if not task.done():
                    task.cancel()

            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()

            # Gracefully stop subprocesses (idempotent)
            await asyncio.gather(
                self._analysis_runner.stop(),
                self._bot_manager.stop(),
                self._dashboard_runner.stop(),
                self.db_monitor.close(),
                return_exceptions=True,
            )

    async def _watch_database_loop(self) -> None:
        """Poll the database for unprocessed feedback and trigger analysis."""
        logger.info("Database monitor loop started")
        try:
            while not self._stop_event.is_set():
                try:
                    new_entries = await self.db_monitor.poll_for_new_feedback()
                    count = len(new_entries)

                    if count:
                        # Only trigger when "new" work appears compared to last seen,
                        # to avoid re-triggering analysis every poll while unprocessed
                        # rows exist but analysis hasn't finished updating them yet.
                        if (
                            self.state.last_seen_unprocessed_count == 0
                            or count > self.state.last_seen_unprocessed_count
                        ):
                            logger.info("Detected %s new feedback entries", count)
                            self.events.publish(NewDataDetected(count=count))
                            self._latest_entries = new_entries
                            self._analysis_requested.set()
                        else:
                            # Still unprocessed rows, but no increase since last check.
                            self.state.last_seen_unprocessed_count = count
                    else:
                        self.state.last_seen_unprocessed_count = 0

                except Exception:
                    logger.exception("Error while polling database for new feedback")

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=self._poll_interval_seconds
                    )
                except TimeoutError:
                    continue
        finally:
            logger.info("Database monitor loop stopping")

    async def _analysis_loop(self) -> None:
        """Wait for analysis requests and run them one at a time."""
        logger.info("Analysis loop started")
        try:
            while not self._stop_event.is_set():
                await self._analysis_requested.wait()
                self._analysis_requested.clear()

                if self._stop_event.is_set():
                    break

                if self.state.analysis_in_progress:
                    # If somehow signaled while running, just continue.
                    continue

                entries = getattr(self, "_latest_entries", [])
                if not entries:
                    continue

                await self._run_analysis_job(entries)
        finally:
            logger.info("Analysis loop stopping")

    async def _run_analysis_job(self, entries: List[dict]) -> None:
        if self.state.analysis_in_progress:
            return

        self.state.analysis_in_progress = True
        count = len(entries)
        self.events.publish(AnalysisStarted(count=count))
        logger.info("Analysis job starting for %s entries", count)

        try:
            await self._analysis_runner.run_analysis_once(entries)
            self.state.last_analysis_at = datetime.utcnow()
            self.events.publish(AnalysisCompleted(count=count, stats=None))
        except asyncio.CancelledError:
            logger.info("Analysis job cancelled")
            raise
        except Exception:
            logger.exception("Analysis job failed")
        finally:
            self.state.analysis_in_progress = False

    def _on_new_data(self, event: NewDataDetected) -> None:
        self.state.last_seen_unprocessed_count = event.count

    def _on_analysis_completed(self, event: AnalysisCompleted) -> None:
        logger.info("Analysis completed for %s entries; requesting dashboard update", event.count)
        self.events.publish(DashboardUpdateRequested())
        self._dashboard_runner.trigger_refresh()
        # Reset so we can detect future new arrivals cleanly.
        self.state.last_seen_unprocessed_count = 0

    def _install_signal_handlers(self) -> None:
        """Install SIGINT/SIGTERM handlers to trigger async stop().

        On Windows, asyncio's add_signal_handler is not implemented for SIGTERM,
        so we fall back to signal.signal where needed.
        """
        loop = asyncio.get_running_loop()

        def _request_stop() -> None:
            if not self._stop_event.is_set():
                logger.info("Signal received; requesting shutdown")
                self._stop_event.set()
                self._analysis_requested.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _request_stop)
            except (NotImplementedError, RuntimeError):
                try:
                    signal.signal(sig, lambda *_: loop.call_soon_threadsafe(_request_stop))
                except Exception:
                    # Best-effort only
                    pass

