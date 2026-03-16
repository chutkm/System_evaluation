from __future__ import annotations

import asyncio
import logging

from curator_agent.config import load_config
from curator_agent.core.agent import CuratorAgent


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


async def _async_main() -> None:
    configure_logging()
    config = load_config()
    agent = CuratorAgent(poll_interval_seconds=config.poll_interval_seconds)
    try:
        await agent.start()
    finally:
        await agent.stop()


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()

