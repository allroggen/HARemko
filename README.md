# HARemko

Model-first foundation for a better REMKO/Home Assistant integration.

## Implemented architecture

- **Transport layer (Cloud/MQTT ready):**
  - structured around explicit write/read primitives
  - prepared for SmartWeb cloud polling behavior
- **Profile layer (model-first):**
  - `ModelProfileRegistry` resolves capabilities by model family (`mxw`, `rkl`, `bl`, `rbw`, `kwt`, `lte`, `wpm`)
  - enables per-indoor-unit capability mapping
- **Entity/state layer:**
  - `ChangeAwareStateStore` publishes only effective state changes
  - supports cleaner and faster UI updates

## Robustness improvements

- `WriteCoordinator` adds:
  - **queued writes** (sequential execution)
  - **dedupe** by `unit_id + field`
  - **retry with backoff**
  - **readback confirmation**

## Diagnostics and UX

- `build_diagnostics_payload` exposes per-unit metadata:
  - unit id, model, profile, portal metadata
  - explicit capability map for transparency/debugging
- config flow now mirrors the reference split:
  - login step with SmartWeb email/password
  - device step with name and polling interval

## Project layout

- `/home/runner/work/HARemko/HARemko/custom_components/haremko/`
  - `profiles.py`
  - `coordinator.py`
  - `write_queue.py`
  - `diagnostics.py`
  - `const.py`
  - `manifest.json`

## Validation

Tests are provided in:

- `/home/runner/work/HARemko/HARemko/tests/test_haremko_foundation.py`