"""Change-aware state coordination for indoor units."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class UnitState:
    """Normalized state for one indoor unit."""

    unit_id: str
    values: dict[str, object]


class ChangeAwareStateStore:
    """Stores only effective state changes to reduce noisy updates."""

    def __init__(self) -> None:
        self._state_by_unit: dict[str, dict[str, object]] = {}

    def update_many(self, states: list[UnitState]) -> dict[str, dict[str, object]]:
        changed: dict[str, dict[str, object]] = {}
        for state in states:
            previous = self._state_by_unit.get(state.unit_id)
            if previous == state.values:
                continue
            self._state_by_unit[state.unit_id] = dict(state.values)
            changed[state.unit_id] = dict(state.values)
        return changed

    def snapshot(self) -> Mapping[str, dict[str, object]]:
        return {unit_id: dict(values) for unit_id, values in self._state_by_unit.items()}
