---
baseline_commit: ddc9f01e593379b3470744aeb8f27d4e485e9f99
---

# Story 2.2: Point-to-Point Route Cost Calculation

Status: done

## Story

As a player,
I want the real fuel/time cost of a trip calculated for my ship,
so that I know what a route actually costs.

## Acceptance Criteria

1. **Given** two locations and a ship (any system, e.g. Stanton or Pyro), **when** a route cost is requested, **then** it's computed from location coordinates plus that ship's quantum stats — not from a fake precomputed pair. [Source: epics.md#Story-2.2]

## Tasks / Subtasks

- [x] Task 1: Import real location coordinates (AC: #1)
  - [x] **Discovery during this story**: `api.star-citizen.wiki`'s `/api/locations` does NOT expose x/y/z coordinates (confirmed directly, list and detail views). Real coordinates come from a different StarCitizenWiki-maintained source: `scunpacked-data`'s `starmap_positions.json` (raw game-file datamining, 1250 entities across Stanton/Pyro/Nyx, verified to include this project's own captured example locations). [Source: SPEC.md#Assumptions, updated this story]
  - [x] `src/verselog/core/location_reference.py` — `LocationReference` dataclass: `name: str`, `system: str`, `x: float`, `y: float`, `z: float`
  - [x] `src/verselog/core/location_reference_store.py` — `LocationReferenceStore`, mirroring `ShipReferenceStore`'s pattern: a `locations` table (`name TEXT PRIMARY KEY, system TEXT, x REAL, y REAL, z REAL`), `save_locations(...)` (upsert), `get_location(name) -> LocationReference | None`
  - [x] `src/verselog/adapters/datasource/location_data_provider.py` — `LocationDataProvider` (`DataSourcePort`): fetches the single `starmap_positions.json` file (no pagination needed, unlike the ships API), maps each `entities[]` item's `name`/`system`/`x`/`y`/`z` into a `LocationReference`, saves to the store. HTTP call injectable (`http_get` parameter), same testability pattern as `CommunityAPIProvider`.
- [x] Task 2: Extend `ShipReference` with the fields needed for time, not just fuel (AC: #1)
  - [x] Add `quantum_speed: float` and `quantum_spool_time: float` to `ShipReference` and the `ships` table/store (Story 2.1 only captured fuel-related fields; this story is what actually needs speed/spool-time for the *time* half of "fuel/time cost", so extending now is the right point, not scope creep). Update `CommunityAPIProvider`'s `_ship_from_json` to populate them from the already-confirmed `quantum.quantum_speed`/`quantum.quantum_spool_time` fields.
- [x] Task 3: Implement `RouteCostCalculator` (AC: #1)
  - [x] `src/verselog/core/route_cost_calculator.py` — `RouteCost` dataclass (`distance_meters: float`, `travel_time_seconds: float`, `fuel_cost: float`); `RouteCostCalculator(location_store, ship_store).calculate(departure: str, arrival: str, ship_name: str) -> RouteCost`
  - [x] Distance: 3D Euclidean distance between the two `LocationReference` coordinates (stdlib `math`, no new dependency)
  - [x] Travel time: `quantum_spool_time + distance / quantum_speed`
  - [x] Fuel cost: `distance * (quantum_fuel_capacity / quantum_range)` — a per-meter rate derived from the ship's full-tank range, not an invented constant
  - [x] Raise a clear error (e.g. `ValueError`) if the departure, arrival, or ship name isn't found in the stores — an explicit lookup failure, not a silent zero-cost result
- [x] Task 4: Tests (AC: #1)
  - [x] Unit test `RouteCostCalculator` with hand-built `LocationReference`/`ShipReference` fixtures (known coordinates, known ship stats) — assert the distance/time/fuel arithmetic against hand-computed expected values
  - [x] Unit test using the *real* confirmed coordinates for Port Tressler and Greycat Stanton IV Production Complex-A (from `starmap_positions.json`) with a real ship's stats — a grounded, non-synthetic regression case
  - [x] Unit test the missing-departure/arrival/ship error path
  - [x] Unit test `LocationDataProvider` with an injected fake `http_get` returning a small canned `entities` array — no real network, no pagination to test (single-file fetch)
  - [x] Unit test `LocationReferenceStore` round-trip and upsert-not-duplicate, mirroring `test_ship_reference_store.py`
  - [x] Update `test_community_api_provider.py`'s fixtures/assertions for the two new `ShipReference` fields

## Dev Notes

- **Two distinct third-party sources now, not one** — ships/cargo/fuel from `api.star-citizen.wiki`, location coordinates from `scunpacked-data`. Keep them as separate adapters (`CommunityAPIProvider`, `LocationDataProvider`), both implementing `DataSourcePort`, both writing into the same local SQLite file via their own stores. Don't conflate them into one class. [Source: vision-pipeline.md, updated this story]
- **No pagination needed for locations** — `starmap_positions.json` is a single static file (~1250 entities, ~500KB), unlike the paginated ships endpoint. Don't build pagination handling that isn't needed here.
- **`ShipReference` schema extension is a legitimate evolution, not scope creep** — Story 2.1 only needed fuel-related fields for its own AC; this story is precisely where the "time" half of the cost calculation becomes necessary, so it's the right point to add `quantum_speed`/`quantum_spool_time`. [Source: _bmad-output/implementation-artifacts/2-1-reference-data-import-local-sqlite.md]
- **Formula is a straightforward physical model** (distance ÷ speed + spool time; fuel-per-meter derived from the ship's own full-tank range), not an invented heuristic like some earlier placeholders (station-name check, worker-count sizing) — the inputs are real, confirmed data, so state the formula plainly.
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `core/location_reference.py`, `core/location_reference_store.py`, `core/route_cost_calculator.py` (core-owned, per AD-1/AD-4), and `adapters/datasource/location_data_provider.py` (second file in the `adapters/datasource/` package alongside `community_api_provider.py`). Modifies `ShipReference`/`ShipReferenceStore`/`CommunityAPIProvider` from Story 2.1 to add two fields.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.2] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/specs/spec-verselog/vision-pipeline.md] — updated this story with the two-source reality (api.star-citizen.wiki + scunpacked-data)
- [Source: _bmad-output/implementation-artifacts/2-1-reference-data-import-local-sqlite.md] — `ShipReference`/`ShipReferenceStore`/`CommunityAPIProvider`, extended here
- github.com/StarCitizenWiki/scunpacked-data — `starmap_positions.json`, verified directly (1250 entities, Stanton/Pyro/Nyx, includes this project's own captured contract's exact locations)

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `52 passed in 1.97s`
- Verified `starmap_positions.json` directly via curl before implementing (rate-limited on raw.githubusercontent.com, succeeded via the jsdelivr CDN mirror) — 1250 entities, includes Port Tressler and Greycat Stanton IV Production Complex-A

### Completion Notes List

- **Major discovery this story**: `api.star-citizen.wiki`'s `/api/locations` has no coordinates at all (confirmed directly). Found `scunpacked-data`'s `starmap_positions.json` as the real coordinate source instead — same GitHub org, actively maintained, confirmed to include this project's own captured contract's exact locations. Updated `SPEC.md`/`vision-pipeline.md` accordingly.
- Implemented `LocationReference`/`LocationReferenceStore`/`LocationDataProvider` mirroring the ship-reference pattern from Story 2.1, but single-file (no pagination needed).
- Extended `ShipReference`/`ShipReferenceStore`/`CommunityAPIProvider` with `quantum_speed`/`quantum_spool_time` — Story 2.1 only captured fuel-related fields; this story needed speed/spool-time for the time half of the cost formula.
- Implemented `RouteCostCalculator`: 3D Euclidean distance (stdlib `math.dist`), travel time (spool time + distance/speed), fuel cost (distance × fuel-capacity/range ratio) — a plain physical formula from real, confirmed inputs, not an invented heuristic.
- Validated against both synthetic fixtures (exact arithmetic) and the real Port Tressler ↔ Greycat Stanton IV coordinates (~2,084,563 m, computed and cross-checked).
- All acceptance criteria satisfied; 52/52 tests passing.

### File List

- `src/verselog/core/location_reference.py` (new)
- `src/verselog/core/location_reference_store.py` (new)
- `src/verselog/adapters/datasource/location_data_provider.py` (new)
- `src/verselog/core/route_cost_calculator.py` (new)
- `src/verselog/core/ship_reference.py` (modified — added quantum_speed/quantum_spool_time)
- `src/verselog/core/ship_reference_store.py` (modified — schema extended)
- `src/verselog/adapters/datasource/community_api_provider.py` (modified — populates new fields)
- `tests/test_route_cost_calculator.py` (new)
- `tests/test_location_reference_store.py` (new)
- `tests/test_location_data_provider.py` (new)
- `tests/test_ship_reference_store.py` (modified — fixture updated)
- `tests/test_community_api_provider.py` (modified — fixture/assertions updated)

## Change Log

- 2026-07-08: Story implemented — location coordinate source discovered and integrated, ShipReference extended, RouteCostCalculator added, all tasks complete, 52/52 tests passing, status moved to review.
- 2026-07-09: Code review found and fixed one correctness bug — `calculate()` divided by `quantum_speed`/`quantum_range` without checking they're non-zero, crashing with an opaque `ZeroDivisionError` for ships with no quantum drive (confirmed real: ground vehicles like the Nox speeder bike have `null` quantum stats in the live API). Fixed with an explicit `ValueError` matching the method's existing validation-error pattern. 53/53 tests passing.
