"""Write queue with dedupe, retry, and readback confirmation."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
import time

from .const import MAX_BACKOFF_SECONDS, MAX_WRITE_RETRIES


class WriteError(RuntimeError):
    """Base error for write execution failures."""


class ReadbackMismatchError(WriteError):
    """Raised when write could not be confirmed by readback."""


@dataclass(frozen=True)
class WriteRequest:
    """A normalized write operation for one indoor-unit key."""

    unit_id: str
    field: str
    value: object

    @property
    def dedupe_key(self) -> str:
        return f"{self.unit_id}:{self.field}"


class WriteCoordinator:
    """Sequential write processor with dedupe and exponential backoff."""

    def __init__(
        self,
        send_write: Callable[[WriteRequest], None],
        readback: Callable[[WriteRequest], object | None],
        max_retries: int = MAX_WRITE_RETRIES,
    ) -> None:
        self._send_write = send_write
        self._readback = readback
        self._max_retries = max(1, max_retries)
        self._queue: deque[WriteRequest] = deque()
        self._pending_by_key: dict[str, WriteRequest] = {}

    def enqueue(self, request: WriteRequest) -> None:
        key = request.dedupe_key
        self._pending_by_key[key] = request
        self._rebuild_queue()

    def _rebuild_queue(self) -> None:
        self._queue = deque(self._pending_by_key.values())

    def run_all(self) -> None:
        while self._queue:
            request = self._queue.popleft()
            self._pending_by_key.pop(request.dedupe_key, None)
            self._execute_with_retry(request)

    def _execute_with_retry(self, request: WriteRequest) -> None:
        for attempt in range(1, self._max_retries + 1):
            self._send_write(request)
            observed = self._readback(request)
            if observed == request.value:
                return
            if attempt >= self._max_retries:
                raise ReadbackMismatchError(
                    f"Write not confirmed for {request.dedupe_key}: expected={request.value!r} observed={observed!r}"
                )
            backoff = min(2 ** (attempt - 1), MAX_BACKOFF_SECONDS)
            time.sleep(backoff)
