from __future__ import annotations

from typing import List, Dict, Any

from database.repository import get_unprocessed_feedback


class DatabaseMonitor:
    """Thin wrapper around existing repository helpers.

    It encapsulates how we detect "new data" for the curator agent.
    """

    async def poll_for_new_feedback(self) -> List[Dict[str, Any]]:
        """Return a list of unprocessed feedback rows."""
        return await get_unprocessed_feedback()

    async def close(self) -> None:
        """Placeholder for graceful DB shutdown.

        Current repository helpers open/close sessions per call, so there is
        nothing persistent to tear down here. This hook exists to keep the
        curator's shutdown path explicit and future-proof.
        """
        return None

