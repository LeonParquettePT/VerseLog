---
baseline_commit: 05f69484e5589c85c3f9cd9ac86c67c504ab6ce8
---

# Story 2.5: Fuel Value Override and Reset

Status: done

## Story

As a player who modified their ship's engine,
I want to override the default fuel value and reset it later,
so that calculations stay accurate for my actual setup.

## Acceptance Criteria

1. **Given** a ship with a modified engine, **when** the player sets an override, **then** route calculations use it instead of the default, **and** a reset action restores the default. [Source: epics.md#Story-2.5]

## Tasks / Subtasks

- [x] Task 1: Implement `FuelOverrideStore` (AC: #1)
  - [x] `src/verselog/core/fuel_override_store.py` — `FuelOverrideStore(settings_store: SettingsStore)`. Wraps the existing `SettingsStore` (AD-7's single settings store) under one JSON key (e.g. `"fuel_overrides"`, a `{ship_name: fuel_per_meter}` dict) — do not introduce a second settings mechanism or a new SQLite table for this.
  - [x] `set_override(ship_name: str, fuel_per_meter: float) -> None` — raise `ValueError` if `fuel_per_meter <= 0` (a fuel rate can't be zero or negative)
  - [x] `get_override(ship_name: str) -> float | None` — `None` means "no override for this ship, use the default formula"
  - [x] `reset(ship_name: str) -> None` — removes any override for that ship; must be safe/a no-op if none was set (don't raise `KeyError`)
- [x] Task 2: Wire the override into `RouteCostCalculator` (AC: #1)
  - [x] Add an **optional** constructor parameter `fuel_override_store: FuelOverrideStore | None = None` to `RouteCostCalculator.__init__`. Default `None` is required — Stories 2.2/2.3/2.4 already construct `RouteCostCalculator(location_store, ship_store)` in three files plus their tests; none of those call sites may need to change.
  - [x] In `calculate()`, when a `fuel_override_store` was provided, look up `fuel_override_store.get_override(ship_name)`. If it returns a value, use it directly as the fuel-per-meter rate. If it returns `None` (or no store was provided at all), fall back to the existing default: `ship.quantum_fuel_capacity / ship.quantum_range`. This is the **only** thing that changes about `fuel_cost`'s computation.
  - [x] Do **not** touch the existing `if ship.quantum_speed <= 0 or ship.quantum_range <= 0: raise ValueError(...)` guard. That guard is about whether the ship can quantum-travel at all (a time/distance concern), not about fuel — it must still apply even when a fuel override is set, since a ship with an overridden fuel rate but no quantum drive still can't make the trip.
- [x] Task 3: Tests (AC: #1)
  - [x] `FuelOverrideStore` round-trip: `set_override` then `get_override` returns the exact value set; a ship with no override returns `None`; `reset` clears a previously-set override back to `None` and is a no-op when nothing was set
  - [x] `FuelOverrideStore.set_override` rejects a non-positive `fuel_per_meter` (`ValueError`)
  - [x] `RouteCostCalculator.calculate()` uses the override's exact fuel rate (not the default `quantum_fuel_capacity/quantum_range` ratio) when one is set for that ship — assert `fuel_cost == distance_meters * override_rate`
  - [x] `RouteCostCalculator.calculate()` falls back to the default formula when a `fuel_override_store` was provided but has no entry for that ship (same result as Story 2.2's existing behavior)
  - [x] `RouteCostCalculator.calculate()` after `reset()` on a previously-overridden ship falls back to the default formula again
  - [x] Confirm `tests/test_route_cost_calculator.py` needs **zero** changes to its existing tests and still passes — the 2-argument construction (no `fuel_override_store` at all) behaves identically to before this story

## Dev Notes

- **Why `RouteCostCalculator` is the integration point, not `ShipReferenceStore`:** AD-4 scopes the SQLite reference-data store to bulk-*imported* community-API data (cargo capacities, fuel defaults, location data). A player's session override is user-set config, not imported data — per AD-7 it belongs in the settings store, kept separate from `ShipReferenceStore` so the two concerns (imported reference data vs. session overrides) don't get conflated in one table. [Source: ARCHITECTURE-SPINE.md#AD-4, #AD-7]
- **Why the override is one derived rate (fuel-per-meter), not the two raw stats it comes from:** `RouteCostCalculator`'s existing formula is `fuel_cost = distance_meters * (ship.quantum_fuel_capacity / ship.quantum_range)` — that ratio is the *only* fuel-related number the codebase's fuel calculation actually consumes. Overriding `quantum_fuel_capacity` and `quantum_range` separately (two numbers) instead of the one rate they're only ever combined into would be needless indirection with no current benefit. [Source: src/verselog/core/route_cost_calculator.py]
- **`ShipReference.fuel_usage_main`** (imported since Story 2.1) is **not** touched by this story — grep confirms it isn't read by any calculation in the codebase yet (only `quantum_fuel_capacity`/`quantum_range` feed `RouteCostCalculator`'s fuel formula). Wiring it in would be scope creep addressing a separate, pre-existing gap this story's AC doesn't ask about.
- **Unit/UI presentation is explicitly out of scope.** No UI adapter exists yet for *any* story so far (the Tkinter seed UI is still listed under ARCHITECTURE-SPINE.md's Deferred section) — what units a player types in, form validation, or converting an "engine tier" choice into a raw fuel-per-meter number are all future UI-adapter concerns. This story only builds the `core/` mechanism a future UI would call into, consistent with every prior Epic 2 story.
- **Backward compatibility is load-bearing, not optional polish:** the new constructor parameter must default to `None` so Stories 2.2/2.3/2.4's existing `RouteCostCalculator(location_store, ship_store)` construction — used directly in `LoadingPlanCalculator`'s and `CombinedRoutePlanner`'s own tests too — keeps working unmodified. [Source: _bmad-output/implementation-artifacts/2-2-point-to-point-route-cost-calculation.md, 2-3-loading-plan-derived-from-single-missions-route.md, 2-4-combined-route-and-loading-plan-for-multiple-missions.md]
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds one new file to `core/`: `fuel_override_store.py`, alongside the existing `settings_store.py` it wraps. Modifies `route_cost_calculator.py` (Story 2.2) additively — no removed behavior, no signature-breaking change (new param is optional with a default).

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.5] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-7] — single settings store, adapters never write it directly (this story's `FuelOverrideStore` is exactly that kind of core-owned wrapper)
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-4] — bulk-imported reference data vs. session config separation, the reason this isn't added to `ShipReferenceStore`
- [Source: src/verselog/core/settings_store.py] — the existing generic JSON-backed key/value store this story wraps, already used by `benchmark.py`'s `persist()`
- [Source: src/verselog/core/route_cost_calculator.py] — the exact fuel formula this story makes overridable, and the quantum-drive guard that must stay untouched
- [Source: _bmad-output/implementation-artifacts/2-2-point-to-point-route-cost-calculation.md] — `RouteCostCalculator`'s existing 2-argument construction that must keep working unmodified

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `80 passed in 2.79s`

### Completion Notes List

- Implemented `FuelOverrideStore` (`core/fuel_override_store.py`) as a thin wrapper over the existing `SettingsStore`, keyed by ship name under one `"fuel_overrides"` JSON key — no new SQLite table, no second settings mechanism.
- Wired it into `RouteCostCalculator` as an optional third constructor parameter (`fuel_override_store: FuelOverrideStore | None = None`); `calculate()` uses the override's rate when present for that ship, otherwise falls back to the existing `quantum_fuel_capacity / quantum_range` default. Left the quantum-drive capability guard untouched.
- `tests/test_route_cost_calculator.py`'s existing tests required zero changes — the 2-argument construction from Stories 2.2/2.3/2.4 still passes unmodified, confirming the new parameter is purely additive.
- All acceptance criteria satisfied; 80/80 tests passing (69 pre-existing + 7 new in `test_fuel_override_store.py` + 4 new in `test_route_cost_calculator.py`).

### File List

- `src/verselog/core/fuel_override_store.py` (new)
- `tests/test_fuel_override_store.py` (new)
- `src/verselog/core/route_cost_calculator.py` (modified — optional `fuel_override_store` param, override lookup in `calculate()`)
- `tests/test_route_cost_calculator.py` (modified — added override/fallback/reset/no-store tests; existing tests untouched)

## Change Log

- 2026-07-09: Story implemented — `FuelOverrideStore` added and wired into `RouteCostCalculator` as an optional, additive dependency, all tasks complete, 80/80 tests passing, status moved to review.
