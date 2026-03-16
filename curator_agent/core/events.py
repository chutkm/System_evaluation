from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Protocol, Type, TypeVar


@dataclass
class Event:
    """Base class for all curator events."""


@dataclass
class NewDataDetected(Event):
    """Emitted when new, unprocessed feedback appears in the database."""

    count: int


@dataclass
class AnalysisStarted(Event):
    count: int


@dataclass
class AnalysisCompleted(Event):
    count: int
    stats: Dict[str, Any] | None = None


@dataclass
class DashboardUpdateRequested(Event):
    pass


@dataclass
class DashboardUpdated(Event):
    pass


@dataclass
class ProcessCrashed(Event):
    name: str
    exit_code: int | None
    error: str | None = None


HandlerT = TypeVar("HandlerT", bound=Callable[[Event], Any])


class SupportsHandle(Protocol):
    def __call__(self, event: Event) -> Any: ...


class EventBus:
    """Very small in-process pub/sub event bus."""

    def __init__(self) -> None:
        self._subscribers: Dict[Type[Event], List[SupportsHandle]] = {}

    def subscribe(self, event_type: Type[Event], handler: SupportsHandle) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: Event) -> None:
        for event_type, handlers in self._subscribers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    handler(event)
