import asyncio
import importlib
import sys
import types


def _install_homeassistant_stub() -> None:
    if "homeassistant" in sys.modules:
        return

    homeassistant = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")

    class ConfigFlow:
        def __init_subclass__(cls, *, domain=None, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.DOMAIN = domain

        def __init__(self) -> None:
            self._configured_ids = set()
            self._current_unique_id = None

        async def async_set_unique_id(self, unique_id):
            self._current_unique_id = unique_id

        def _abort_if_unique_id_configured(self):
            if self._current_unique_id in self._configured_ids:
                raise RuntimeError("already_configured")
            self._configured_ids.add(self._current_unique_id)

        def async_show_form(self, *, step_id, data_schema=None, errors=None):
            return {
                "type": "form",
                "step_id": step_id,
                "data_schema": data_schema,
                "errors": errors or {},
            }

        def async_create_entry(self, *, title, data):
            return {"type": "create_entry", "title": title, "data": data}

    class OptionsFlow:
        def async_show_form(self, *, step_id, data_schema=None, errors=None):
            return {
                "type": "form",
                "step_id": step_id,
                "data_schema": data_schema,
                "errors": errors or {},
            }

        def async_create_entry(self, *, title, data):
            return {"type": "create_entry", "title": title, "data": data}

    class ConfigEntry:
        def __init__(self, *, data=None, options=None, title="HARemko") -> None:
            self.data = data or {}
            self.options = options or {}
            self.title = title

    config_entries.ConfigFlow = ConfigFlow
    config_entries.OptionsFlow = OptionsFlow
    config_entries.ConfigEntry = ConfigEntry
    homeassistant.config_entries = config_entries

    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.config_entries"] = config_entries


_install_homeassistant_stub()
config_flow = importlib.import_module("custom_components.haremko.config_flow")


def _schema_fields(schema):
    return {key.schema for key in schema.schema}


def test_user_step_exposes_login_fields():
    flow = config_flow.HARemkoConfigFlow()

    result = asyncio.run(flow.async_step_user())

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert _schema_fields(result["data_schema"]) == {"email", "password"}


def test_user_step_requires_credentials():
    flow = config_flow.HARemkoConfigFlow()

    result = asyncio.run(flow.async_step_user({"email": " ", "password": ""}))

    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}


def test_device_step_creates_entry_with_normalized_values():
    flow = config_flow.HARemkoConfigFlow()

    first = asyncio.run(flow.async_step_user({"email": " User@Example.com ", "password": " secret "}))
    result = asyncio.run(
        flow.async_step_device({"device_name": " Wohnzimmer ", "scan_interval": 3})
    )

    assert first["step_id"] == "device"
    assert result["type"] == "create_entry"
    assert result["title"] == "Wohnzimmer"
    assert result["data"] == {
        "email": "User@Example.com",
        "password": "secret",
        "device_name": "Wohnzimmer",
        "scan_interval": 5,
    }


def test_options_flow_uses_existing_scan_interval():
    entry = sys.modules["homeassistant.config_entries"].ConfigEntry(
        data={"scan_interval": 30},
        options={"scan_interval": 45},
    )
    flow = config_flow.HARemkoOptionsFlow(entry)

    result = asyncio.run(flow.async_step_init())

    schema_key = next(iter(result["data_schema"].schema))
    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert schema_key.default() == 45
