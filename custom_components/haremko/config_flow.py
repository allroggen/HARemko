"""Config flow for HARemko."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_DEVICE_NAME,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
)


class HARemkoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HARemko."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Collect SmartWeb credentials."""
        if user_input is not None:
            email = (user_input.get(CONF_EMAIL) or "").strip()
            password = (user_input.get(CONF_PASSWORD) or "").strip()
            if email and password:
                self._email = email
                self._password = password
                return await self.async_step_device()
            return self.async_show_form(
                step_id="user",
                data_schema=self._build_user_schema(user_input),
                errors={"base": "invalid_auth"},
            )

        return self.async_show_form(step_id="user", data_schema=self._build_user_schema())

    async def async_step_device(self, user_input: dict[str, Any] | None = None):
        """Collect device-specific settings."""
        if user_input is not None:
            device_name = (user_input.get(CONF_DEVICE_NAME) or "").strip()
            if not device_name:
                return self.async_show_form(
                    step_id="device",
                    data_schema=self._build_device_schema(user_input),
                    errors={"base": "invalid_device_name"},
                )

            scan_interval = max(
                5,
                int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS)),
            )
            await self.async_set_unique_id(self._build_unique_id(self._email, device_name))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=device_name,
                data={
                    CONF_EMAIL: self._email,
                    CONF_PASSWORD: self._password,
                    CONF_DEVICE_NAME: device_name,
                    CONF_SCAN_INTERVAL: scan_interval,
                },
            )

        return self.async_show_form(step_id="device", data_schema=self._build_device_schema())

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return HARemkoOptionsFlow(config_entry)

    def _build_user_schema(self, user_input: dict[str, Any] | None = None) -> vol.Schema:
        """Build the credentials step schema."""
        user_input = user_input or {}
        return vol.Schema(
            {
                vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL, "")): str,
                vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
            }
        )

    def _build_device_schema(self, user_input: dict[str, Any] | None = None) -> vol.Schema:
        """Build the device configuration step schema."""
        user_input = user_input or {}
        return vol.Schema(
            {
                vol.Required(CONF_DEVICE_NAME, default=user_input.get(CONF_DEVICE_NAME, "")): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS),
                ): vol.All(vol.Coerce(int), vol.Range(min=5)),
            }
        )

    @staticmethod
    def _build_unique_id(email: str, device_name: str) -> str:
        """Build a stable unique id for one configured device."""
        return f"{email.strip().casefold()}::{device_name.strip().casefold()}"


class HARemkoOptionsFlow(config_entries.OptionsFlow):
    """Handle HARemko options."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage polling options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: max(
                        5,
                        int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS)),
                    )
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self._config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self._config_entry.data.get(
                                CONF_SCAN_INTERVAL,
                                DEFAULT_SCAN_INTERVAL_SECONDS,
                            ),
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5)),
                }
            ),
        )
