from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Any, Callable, Optional


JobFunc = Callable[[], Any]


@dataclass
class Job:
    name: str
    func: JobFunc


class Scheduler:
    """Very small single-worker job scheduler.

    Used to serialize analysis jobs so that only one analysis runs at a time,
    even if the database monitor detects multiple batches of new data.
    """

    def __init__(self) -> None:
        self._queue: "queue.Queue[Job]" = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._shutdown = threading.Event()

    def start(self) -> None:
        if self._worker_thread and self._worker_thread.is_alive():
            return

        self._worker_thread = threading.Thread(
            target=self._run, name="curator-scheduler", daemon=True
        )
        self._worker_thread.start()

    def _run(self) -> None:
        while not self._shutdown.is_set():
            try:
                job = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                job.func()
            finally:
                self._queue.task_done()

    def enqueue(self, name: str, func: JobFunc) -> None:
        self._queue.put(Job(name=name, func=func))

    def stop(self) -> None:
        self._shutdown.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5)
