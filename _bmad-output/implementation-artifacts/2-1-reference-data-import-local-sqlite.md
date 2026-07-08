---
baseline_commit: b28b2b24ce4db986a6a11dd0647f4a950e754a08
---

# Story 2.1: Reference Data Import (Local SQLite)

Status: ready-for-dev

## Story

As a player,
I want accurate ship and fuel reference data available locally,
so that route calculations aren't guesswork.

## Acceptance Criteria

1. **Given** the app's first setup, **when** the bulk import from `CommunityAPIProvider` runs, **then** ship cargo capacities and fuel/quantum-drive stats are stored in the local SQLite database, refreshable later. [Source: epics.md#Story-2.1]

## Tasks / Subtasks

- [ ] Task 1: Add the `requests` dependency (AC: #1)
  - [ ] Add `requests` to `pyproject.toml` `[project] dependencies` — the simplest, most standard synchronous HTTP client for a one-off/periodic bulk-import call, no async needed here
- [ ] Task 2: Define the ship reference schema (AC: #1)
  - [ ] `src/verselog/core/ship_reference.py` — `ShipReference` dataclass: `name: str`, `cargo_capacity_scu: int`, `quantum_fuel_capacity: float`, `quantum_range: float`, `fuel_usage_main: float`. Deliberately lean — the architecture explicitly left the SQLite schema as Deferred/code-owned; this story is where it gets defined, scoped to exactly what the AC asks for (cargo capacity, fuel/quantum stats), not the full field set the API exposes.
  - [ ] `src/verselog/core/ship_reference_store.py` — `ShipReferenceStore(db_path: Path = Path("data/verselog.db"))`: creates a single `ships` table if missing (`name TEXT PRIMARY KEY, cargo_capacity_scu INTEGER, quantum_fuel_capacity REAL, quantum_range REAL, fuel_usage_main REAL`), `save_ships(ships: list[ShipReference])` (upsert, so re-running the import refreshes existing rows), `get_ship(name: str) -> ShipReference | None`
- [ ] Task 3: Implement `CommunityAPIProvider` (`DataSourcePort`) (AC: #1)
  - [ ] `src/verselog/adapters/datasource/community_api_provider.py` — `refresh()` fetches `https://api.star-citizen.wiki/api/vehicles`, follows `links.next` pagination if present, maps each item's `cargo_capacity`, `quantum.quantum_fuel_capacity`, `quantum.quantum_range`, `fuel.usage.main` into a `ShipReference`, and calls `ShipReferenceStore.save_ships(...)`
  - [ ] Inject the HTTP call (`http_get` constructor parameter, defaulting to `requests.get`) so tests supply canned responses instead of hitting the real network
  - [ ] Send an identifying `User-Agent` header (e.g. `"VerseLog (github.com/LeonParquettePT/VerseLog)"`) and a small delay between paginated page requests — the conservative, self-throttled posture already established in `SPEC.md`'s assumptions for this third-party dependency, applied here rather than invented fresh
  - [ ] On an HTTP error, raise a clear, specific exception rather than silently swallowing it — this is a distinct concern from the capture pipeline's graceful-degradation pattern (Stories 1.2/1.3/1.5): a bulk import is an explicit action, not a per-scan extraction the trust layer must never crash on, so a clear failure here is the right behavior, not a defect to paper over
- [ ] Task 4: Tests (AC: #1)
  - [ ] Unit test `CommunityAPIProvider.refresh()` with an injected fake `http_get` returning canned JSON shaped like the real, already-confirmed API response (cargo_capacity, cargo_grids, quantum fields, fuel.usage) — assert the resulting `ShipReference`s land in the store correctly
  - [ ] Unit test pagination: a fake `http_get` returning a `links.next` on page 1 and no `next` on page 2 — assert both pages' ships are imported
  - [ ] Unit test `ShipReferenceStore` directly against a temp-file SQLite DB (`tmp_path`): save then get round-trips; saving the same ship name twice (re-running the import) updates rather than duplicates
  - [ ] Unit test that an HTTP error from the injected `http_get` raises clearly, rather than being silently swallowed

## Dev Notes

- **This is the first story to actually define the SQLite schema** — the architecture spine intentionally left it as Deferred/"owned by the code once it exists." Keep it lean: only the fields this story's AC needs (cargo capacity, fuel/quantum stats), not the full breadth of fields the community API happens to expose. [Source: ARCHITECTURE-SPINE.md#Deferred, ARCHITECTURE-SPINE.md#AD-4]
- **Route cost calculation itself is Story 2.2's job**, not this one — this story only gets accurate reference data into local storage. Don't compute route costs here.
- **Real API shape already confirmed** (from research during the SPEC/architecture phase, not re-derived here): `/api/vehicles` returns `cargo_capacity`, `cargo_grids[].scu`, and a `quantum` object (`quantum_fuel_capacity`, `quantum_range`, etc.) plus a `fuel.usage` breakdown by thruster type (`main`/`retro`/`vtol`/`maneuvering`). Its per-vehicle example route fields (`port_olisar_to_arccorp_*`) are NOT a real route matrix — irrelevant to this story, relevant to Story 2.2. [Source: vision-pipeline.md]
- **Safe-default posture toward the third-party API is already decided, not new here**: conservative self-throttling and clear attribution, no formal permission required to proceed. Apply it (identifying User-Agent, a small inter-page delay) rather than re-litigating whether to. [Source: SPEC.md#Assumptions]
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `core/ship_reference.py` and `core/ship_reference_store.py` (domain model + storage, core-owned per AD-4) and `adapters/datasource/community_api_provider.py` (the first file in the previously-empty `adapters/datasource/` package from the Story 1.1 scaffold).

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.1] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-4] — local reference-data store ownership
- [Source: _bmad-output/specs/spec-verselog/vision-pipeline.md] — confirmed real API shape, non-goal of using its fake route-pair fields
- [Source: _bmad-output/specs/spec-verselog/SPEC.md#Assumptions] — the safe-default usage posture this story applies

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
