from custom_components.haremko.coordinator import ChangeAwareStateStore, UnitState
from custom_components.haremko.diagnostics import IndoorUnitInfo, build_diagnostics_payload
from custom_components.haremko.profiles import ModelProfileRegistry
from custom_components.haremko.write_queue import WriteCoordinator, WriteRequest


def test_model_profile_registry_resolves_known_and_default():
    registry = ModelProfileRegistry()
    assert registry.resolve("MXW 354").model == "mxw"
    assert registry.resolve("Unknown").model == "generic"


def test_change_aware_store_reports_only_effective_changes():
    store = ChangeAwareStateStore()
    first = store.update_many([UnitState(unit_id="u1", values={"temp": 21})])
    second = store.update_many([UnitState(unit_id="u1", values={"temp": 21})])
    third = store.update_many([UnitState(unit_id="u1", values={"temp": 22})])
    assert first == {"u1": {"temp": 21}}
    assert second == {}
    assert third == {"u1": {"temp": 22}}


def test_write_queue_dedupes_and_confirms():
    writes: list[tuple[str, object]] = []
    state = {"u1:target_temp": 20}

    def send_write(request: WriteRequest) -> None:
        key = f"{request.unit_id}:{request.field}"
        writes.append((key, request.value))
        state[key] = request.value

    def readback(request: WriteRequest):
        return state.get(f"{request.unit_id}:{request.field}")

    queue = WriteCoordinator(send_write=send_write, readback=readback, max_retries=2)
    queue.enqueue(WriteRequest(unit_id="u1", field="target_temp", value=22))
    queue.enqueue(WriteRequest(unit_id="u1", field="target_temp", value=23))
    queue.run_all()
    assert writes == [("u1:target_temp", 23)]


def test_diagnostics_payload_contains_profile_capabilities():
    registry = ModelProfileRegistry()
    profile = registry.resolve("KWT 200")
    payload = build_diagnostics_payload(
        IndoorUnitInfo(
            unit_id="indoor-1",
            name="Wohnzimmer",
            model="KWT 200",
            portal_path="/device/path",
            portal_type="climate",
            portal_dev="abc",
        ),
        profile,
    )
    assert payload["unit_id"] == "indoor-1"
    assert payload["capabilities"]["fan_mode"] is True
