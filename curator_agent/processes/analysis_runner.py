from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class AnalysisRunner:
    """Runs `run_analysis.py` as a one-shot subprocess."""

    def run_analysis_once(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("Running analysis script for %s new entries", len(entries))
        root = _project_root()

        completed = subprocess.run(
            [sys.executable, "run_analysis.py"],
            cwd=str(root),
            capture_output=False,
            text=False,
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(f"run_analysis.py exited with code {completed.returncode}")

        return {"processed": len(entries), "returncode": completed.returncode}

