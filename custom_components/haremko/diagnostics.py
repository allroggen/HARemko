"""Diagnostics helpers for transparent multi-unit metadata."""

from __future__ import annotations

from dataclasses import dataclass

from .profiles import UnitProfile


@dataclass(frozen=True)
class IndoorUnitInfo:
    """Runtime metadata for a discovered indoor unit."""

    unit_id: str
    name: str
    model: str
    portal_path: str
    portal_type: str | None = None
    portal_dev: str | None = None


def build_diagnostics_payload(unit: IndoorUnitInfo, profile: UnitProfile) -> dict[str, object]:
    return {
        "unit_id": unit.unit_id,
        "name": unit.name,
        "model": unit.model,
        "profile": profile.model,
        "portal_path": unit.portal_path,
        "portal_type": unit.portal_type,
        "portal_dev": unit.portal_dev,
        "capabilities": {
            "target_temperature": profile.supports_target_temperature,
            "hvac_mode": profile.supports_hvac_mode,
            "fan_mode": profile.supports_fan_mode,
            "swing_mode": profile.supports_swing_mode,
            "preset_mode": profile.supports_preset_mode,
        },
    }
