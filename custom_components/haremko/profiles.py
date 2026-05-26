"""Model-first profile mapping for indoor units."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnitProfile:
    """Capabilities for one indoor-unit model family."""

    model: str
    supports_target_temperature: bool = True
    supports_hvac_mode: bool = True
    supports_fan_mode: bool = False
    supports_swing_mode: bool = False
    supports_preset_mode: bool = False


class ModelProfileRegistry:
    """Resolve concrete profiles from model identifiers."""

    def __init__(self) -> None:
        self._profiles: dict[str, UnitProfile] = {
            "mxw": UnitProfile(
                model="mxw",
                supports_target_temperature=True,
                supports_hvac_mode=True,
                supports_fan_mode=True,
                supports_swing_mode=True,
                supports_preset_mode=True,
            ),
            "rkl": UnitProfile(
                model="rkl",
                supports_target_temperature=True,
                supports_hvac_mode=True,
                supports_fan_mode=True,
                supports_swing_mode=False,
                supports_preset_mode=False,
            ),
            "bl": UnitProfile(
                model="bl",
                supports_target_temperature=True,
                supports_hvac_mode=True,
                supports_fan_mode=True,
            ),
            "rbw": UnitProfile(
                model="rbw",
                supports_target_temperature=True,
                supports_hvac_mode=False,
                supports_fan_mode=False,
            ),
            "kwt": UnitProfile(
                model="kwt",
                supports_target_temperature=True,
                supports_hvac_mode=True,
                supports_fan_mode=True,
                supports_swing_mode=True,
            ),
            "lte": UnitProfile(
                model="lte",
                supports_target_temperature=False,
                supports_hvac_mode=False,
                supports_fan_mode=False,
            ),
            "wpm": UnitProfile(
                model="wpm",
                supports_target_temperature=True,
                supports_hvac_mode=True,
                supports_fan_mode=False,
            ),
            "generic": UnitProfile(model="generic"),
        }

    def resolve(self, model_name: str) -> UnitProfile:
        normalized = (model_name or "").strip().casefold()
        for key, profile in self._profiles.items():
            if key != "generic" and key in normalized:
                return profile
        return self._profiles["generic"]
