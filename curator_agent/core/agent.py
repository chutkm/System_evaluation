from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from typing import List

from curator_agent.core.events import (
    AnalysisCompleted,
    AnalysisStarted,
    DashboardUpdateRequested,
    EventBus,
    NewDataDetected,
)
from curator_agent.core.scheduler import Scheduler
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
        self.scheduler = Scheduler()
        self.db_monitor = DatabaseMonitor()

        self._bot_manager = BotProcessManager()
        self._analysis_runner = AnalysisRunner()
        self._dashboard_runner = DashboardRunner()

        self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        self.events.subscribe(NewDataDetected, self._on_new_data)
        self.events.subscribe(AnalysisCompleted, self._on_analysis_completed)

    async def start(self) -> None:
        logger.info("Starting CuratorAgent")
        self.scheduler.start()
        self._dashboard_runner.start()
        self._bot_manager.start()

        await asyncio.gather(
            self._watch_database_loop(),
            asyncio.to_thread(self._bot_manager.run_forever),
            asyncio.to_thread(self._dashboard_health_loop),
        )

    def _dashboard_health_loop(self) -> None:
        while True:
            self._dashboard_runner.restart_if_needed()
            time.sleep(2)

    async def _watch_database_loop(self) -> None:
        """Poll the database for unprocessed feedback and trigger analysis."""
        logger.info("Starting database monitor loop")
        while True:
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
                        self._schedule_analysis(new_entries)
                    else:
                        # Still unprocessed rows, but no increase since last check.
                        self.state.last_seen_unprocessed_count = count
                else:
                    self.state.last_seen_unprocessed_count = 0

            except Exception:
                logger.exception("Error while polling database for new feedback")

            await asyncio.sleep(self._poll_interval_seconds)

    def _schedule_analysis(self, entries: List[dict]) -> None:
        if self.state.analysis_in_progress:
            # Let the next poll trigger another run; keep logic simple for now.
            logger.info("Analysis already in progress; skipping scheduling another job")
            return

        def job() -> None:
            self._run_analysis_job(entries)

        self.state.analysis_in_progress = True
        self.scheduler.enqueue("analysis", job)

    def _run_analysis_job(self, entries: List[dict]) -> None:
        count = len(entries)
        self.events.publish(AnalysisStarted(count=count))
        logger.info("Running analysis for %s entries", count)

        try:
            self._analysis_runner.run_analysis_once(entries)
            self.state.last_analysis_at = datetime.utcnow()
            self.events.publish(AnalysisCompleted(count=count, stats=None))
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

