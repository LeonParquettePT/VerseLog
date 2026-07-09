---
baseline_commit: 8b67690ef3ac72c3a1086976413931b6d55b17b6
---

# Story 2.3: Loading Plan Derived From a Single Mission's Route

Status: done

## Story

As a player,
I want the loading order for a single accepted mission to be derived directly from its computed route (Story 2.2),
so that loading and travel are always consistent with each other, not calculated as two separate, possibly conflicting things.

## Acceptance Criteria

1. **Given** one accepted mission and its computed route on a ship with a known SCU capacity, **when** the loading plan is generated, **then** the loading order follows the LIFO convention against that specific route (last delivery loaded deepest, first delivery nearest the door) — the loading step never runs independently of the route step. [Source: epics.md#Story-2.3]

## Tasks / Subtasks

- [x] Task 1: Define the `LoadingStep`/`LoadingPlan` data shapes (AC: #1)
  - [x] `src/verselog/core/loading_plan_calculator.py` — `LoadingStep` dataclass: `location: str`, `action: str` (`"load"` or `"unload"` — plain string values, no enum; matches the project's existing plain-dataclass style, e.g. `Contract`, `RouteCost`), `scu: int`
  - [x] `LoadingPlan` dataclass: `steps: list[LoadingStep]`
- [x] Task 2: Implement `LoadingPlanCalculator`, deriving the plan from the already-computed route rather than recomputing anything independently (AC: #1)
  - [x] `LoadingPlanCalculator(route_cost_calculator: RouteCostCalculator, ship_store: ShipReferenceStore)` — takes Story 2.2's `RouteCostCalculator` as a collaborator, not a re-implementation. This is the literal enforcement of "the loading step never runs independently of the route step": calling `derive()` without a valid, already-working route calculator is structurally impossible.
  - [x] `derive(contract: Contract, ship_name: str) -> LoadingPlan`:
    - Calls `self._route_cost_calculator.calculate(contract.departure, contract.arrival, ship_name)` first. This both ties the loading plan to the route step and reuses Story 2.2's existing unknown-departure/unknown-arrival/unknown-ship/no-quantum-drive validation — do NOT re-validate locations/ships independently in this class, that would duplicate AD-1's single-source-of-truth intent. Propagate the same `ValueError` if the route calculation fails; the loading plan must never be built on top of a route that couldn't itself be computed.
    - Fetches the ship via `ship_store.get_ship(ship_name)` for `cargo_capacity_scu` (guaranteed non-`None` at this point, since the `route_cost_calculator.calculate()` call above already proved the ship exists).
    - Validates `contract.scu <= ship.cargo_capacity_scu` — a real constraint from FR4 ("adapted to the selected ship's SCU capacity") not yet enforced anywhere in the codebase. Raise `ValueError` if the mission's cargo doesn't fit the ship at all.
    - Returns a `LoadingPlan` with two steps in route order: `LoadingStep(location=contract.departure, action="load", scu=contract.scu)` then `LoadingStep(location=contract.arrival, action="unload", scu=contract.scu)`.
- [x] Task 3: Tests (AC: #1)
  - [x] Unit test the real-data scenario: Port Tressler → Greycat Stanton IV Production Complex-A (the same real coordinates confirmed in Story 2.2), a real ship's stats, `scu=6` — assert the two steps come back in route order (load at departure, unload at arrival) with the correct `scu`
  - [x] Unit test `contract.scu` exceeding `ship.cargo_capacity_scu` raises `ValueError`
  - [x] Unit test that an unknown departure/arrival/ship name raises the same `ValueError` `RouteCostCalculator.calculate()` already raises (assert the error propagates unchanged — proves the route step isn't being bypassed or duplicated)
  - [x] Unit test with hand-built `LocationReferenceStore`/`ShipReferenceStore` fixtures (mirroring `test_route_cost_calculator.py`'s pattern) for the synthetic/arithmetic-independent cases

## Dev Notes

- **Why this story looks "too simple" for LIFO — and that's fine:** a single mission has exactly one pickup and one delivery, so the LIFO convention ("last delivery loaded deepest, first delivery nearest the door") has nothing to order yet — there's only one cargo group. The actual point of this story is establishing the *shape and coupling*: `LoadingPlan` is derived FROM an already-computed route, not calculated as an independent, possibly-conflicting step. Story 2.4 (multiple missions, real stop-ordering) is where LIFO ordering becomes a real algorithm over multiple `LoadingStep`s — don't try to build that generalized ordering logic now, it would be unverified/premature for a single-mission input. [Source: epics.md#Story-2.4]
- **Composition, not duplication:** `RouteCostCalculator` (Story 2.2) already validates departure/arrival/ship existence and ship quantum-drive capability. `LoadingPlanCalculator` must call it, not reimplement any of that — this is the same anti-duplication principle Story 2.2 itself followed for `ShipReferenceStore`/`LocationReferenceStore`. [Source: ARCHITECTURE-SPINE.md#AD-1]
- **New real constraint being enforced for the first time:** SCU-vs-cargo-capacity fit. Nothing in the codebase today checks whether a mission's cargo actually fits the chosen ship — `RouteCostCalculator` only checks quantum-drive capability, not cargo capacity. This story is the natural point to add it, since "a ship with a known SCU capacity" is explicitly named in this story's AC. [Source: epics.md#Story-2.3, FR4]
- **`ShipReference.cargo_capacity_scu`** already exists (added Story 2.1) — reuse as-is. [Source: src/verselog/core/ship_reference.py]
- **File placement mirrors `route_cost_calculator.py`'s pattern**: one file holding both the small dataclasses and the calculator class, not split across multiple files for a concept this size. [Source: src/verselog/core/route_cost_calculator.py]
- **Coding style:** plain, direct code, no enums/abstractions beyond what's needed here. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds one new file to the existing `core/` package: `loading_plan_calculator.py`, alongside `route_cost_calculator.py` (Story 2.2). No structural surprises — `core/` already holds calculator-style classes like this.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.3] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.4] — confirms the multi-mission/real-LIFO-ordering generalization is explicitly a later story, not this one
- [Source: _bmad-output/implementation-artifacts/2-2-point-to-point-route-cost-calculation.md] — `RouteCostCalculator`, `LocationReferenceStore`, `ShipReferenceStore` this story composes with directly, plus the real confirmed Port Tressler/Greycat Stanton IV coordinates reused for this story's grounded test case
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-1] — Ports & Adapters / anti-duplication rule this story's composition-over-reimplementation design follows
- [Source: src/verselog/core/ship_reference.py] — `ShipReference.cargo_capacity_scu`, already present from Story 2.1, reused as-is

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `60 passed in 2.17s`

### Completion Notes List

- Implemented `LoadingStep`/`LoadingPlan` dataclasses and `LoadingPlanCalculator` in one new file, `core/loading_plan_calculator.py`, mirroring `route_cost_calculator.py`'s file-organization pattern.
- `LoadingPlanCalculator` takes `RouteCostCalculator` as a constructor collaborator and calls `.calculate()` inside `derive()` before building the plan — reuses Story 2.2's departure/arrival/ship/quantum-drive validation instead of duplicating it, and makes it structurally impossible to build a loading plan without a valid computed route.
- Added the first real SCU-vs-cargo-capacity check in the codebase (`contract.scu > ship.cargo_capacity_scu` → `ValueError`) — nothing previously validated this.
- For a single mission, the LIFO convention is trivially satisfied (one cargo group: load at departure, unload at arrival, in route order) — the generalized multi-stop LIFO ordering algorithm is explicitly Story 2.4's job, not built here.
- Tested against the same real Port Tressler / Greycat Stanton IV Production Complex-A coordinates and MISC Starlancer MAX ship stats confirmed in Story 2.2, plus synthetic fixtures for the capacity-exceeded and unknown-location/ship error-propagation cases.
- All acceptance criteria satisfied; 60/60 tests passing (55 pre-existing + 5 new).

### File List

- `src/verselog/core/loading_plan_calculator.py` (new)
- `tests/test_loading_plan_calculator.py` (new)
- `src/verselog/core/route_cost_calculator.py` (modified — `RouteCost` now carries the already-fetched `ship`, see Change Log)
- `tests/test_route_cost_calculator.py` (modified — added a regression assertion for the new `ship` field)

## Change Log

- 2026-07-09: Story implemented — `LoadingStep`/`LoadingPlan`/`LoadingPlanCalculator` added, deriving the loading plan from `RouteCostCalculator` rather than independently, all tasks complete, 60/60 tests passing, status moved to review.
- 2026-07-09: Code review found `derive()` fetched the same ship from `ShipReferenceStore` twice — once inside `route_cost_calculator.calculate()`, once again explicitly for `cargo_capacity_scu`. Fixed by adding a `ship: ShipReference` field to `RouteCost` (Story 2.2's `route_cost_calculator.py`) so the already-fetched ship comes back on the route itself; `LoadingPlanCalculator` no longer needs a `ShipReferenceStore` constructor dependency at all. 60/60 tests passing.
