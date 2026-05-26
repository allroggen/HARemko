"""HARemko integration foundation."""

from __future__ import annotations

from .coordinator import ChangeAwareStateStore
from .const import DOMAIN
from .diagnostics import build_diagnostics_payload
from .profiles import ModelProfileRegistry, UnitProfile
from .write_queue import WriteCoordinator, WriteRequest


async def async_setup(hass, config) -> bool:
    """Set up the HARemko integration from YAML."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry) -> bool:
    """Set up HARemko from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}
    return True


async def async_unload_entry(hass, entry) -> bool:
    """Unload a HARemko config entry."""
    domain_data = hass.data.get(DOMAIN, {})
    domain_data.pop(entry.entry_id, None)
    return True


__all__ = [
    "ChangeAwareStateStore",
    "ModelProfileRegistry",
    "UnitProfile",
    "WriteCoordinator",
    "WriteRequest",
    "build_diagnostics_payload",
]
