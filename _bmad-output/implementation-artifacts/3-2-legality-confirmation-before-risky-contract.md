---
baseline_commit: a017b5f837eb1582e86811bb57317bd525ff121b
---

# Story 3.2: Legality Confirmation Before a Risky Contract

Status: done

## Story

As a player,
I want to be warned before accepting a contract that might be illegal,
so that I can decide knowingly instead of stumbling into trouble.

## Acceptance Criteria

1. **Given** a scanned contract flagged as potentially illegal (e.g. a trespassing zone) based on the synced reputation, **when** the player reviews it, **then** a popup names the specific risk and requires an explicit accept/decline, **and** the tool honors whichever choice is made rather than silently filtering the contract, **and** the tool never accepts or declines the contract itself — the player always takes the in-game action manually (no input injection, see SPEC.md non-goals). [Source: epics.md#Story-3.2]

## Tasks / Subtasks

- [x] Task 1: Extend `UIPort` with the confirmation interaction (AC: #1)
  - [x] `src/verselog/core/ports/ui_port.py` — add abstract method `confirm_risky_contract(self, contract: Contract, risk: LegalityRisk) -> bool`. This is the first concrete method added since Story 1.1's scaffold comment "Concrete needs arrive in later stories" — a future UI adapter (still Deferred, no adapter exists yet) implements this as an actual popup. Docstring must state plainly: the return value is *only* the player's reported choice (`True` = proceed, `False` = decline) for the tool's own internal handling — implementations must never perform the accept/decline as an in-game action themselves (SPEC.md non-goals: no input injection).
- [x] Task 2: Implement `LegalityRisk` and `LegalityChecker` (AC: #1)
  - [x] `src/verselog/core/legality_checker.py` — `LegalityRisk` dataclass: `faction: str`, `standing: float`, `reason: str` (a ready-to-display message — the "popup names the specific risk" clause needs actual text, not just raw numbers for a future UI to guess how to phrase)
  - [x] `LegalityChecker(reputation_store: ReputationStore, location_factions: dict[str, str], risk_threshold: float)`. `risk_threshold` has **no default** — force the caller to make an explicit choice (see Dev Notes on why a hardcoded default would be an unverified guess).
  - [x] `check(contract: Contract) -> LegalityRisk | None`: check `contract.departure` then `contract.arrival`, in that order. For each, look up `location_factions.get(location)` — if the location isn't in the mapping, skip it (no data ⇒ not flagged, never invent a risk). If a faction is found, look up `reputation_store.get_level(faction)` — if `None` (no synced standing yet), skip it too (missing data must never manufacture a false positive). If a standing is found and `standing <= risk_threshold`, return a `LegalityRisk` for that faction/location immediately. If neither location trips a risk, return `None`.
- [x] Task 3: Tests (AC: #1)
  - [x] A contract whose departure's faction has a standing at or below the threshold returns a `LegalityRisk` naming that faction, with a `reason` string mentioning the faction and the location
  - [x] A contract whose faction has a standing above the threshold returns `None`
  - [x] A contract whose departure/arrival aren't in `location_factions` at all returns `None`
  - [x] A contract whose faction is known but has no synced reputation yet (`get_level` returns `None`) returns `None` — missing data is never treated as risky
  - [x] A contract where departure's faction is safe but arrival's faction is risky returns the arrival's risk — confirms both locations are checked, not just departure
  - [x] The exact boundary `standing == risk_threshold` is flagged (uses `<=`, not `<`)

## Dev Notes

- **The real "which location belongs to which faction" data does not exist in this codebase, and this story does not invent it.** `LocationReference` (Story 2.2) has no faction/territory field, and no verified community-API source for one has been found (unlike ships/coordinates, which were confirmed against real `api.star-citizen.wiki`/`scunpacked-data` responses). Rather than hardcode a guessed mapping — the exact mistake this project has explicitly avoided elsewhere (Story 1.2's OCR patterns, Story 3.1's REP-screen scope) — `LegalityChecker` takes `location_factions: dict[str, str]` as a **plain injected mapping**, not a persisted/bulk-imported store. Building `AD-4`-style SQLite persistence for data with no real source yet would be premature. Once a real mapping is found, a future story wires a real datasource adapter that populates it; the checking *logic* built here is already correct and fully tested against hand-built fixtures in the meantime. [Source: _bmad-output/implementation-artifacts/3-1-reputation-sync.md#Dev-Notes — the same reasoning applied to the REP-screen detection gap]
- **No default `risk_threshold`:** Story 3.1 already flagged that the real scale Star Citizen uses for reputation standing is unverified. Picking a hardcoded default (e.g. `25.0`) now would be an unverified guess baked into the API, silently wrong once real data arrives. Require the caller to pass one explicitly.
- **Scope is one `Contract`'s departure/arrival, not a whole `CombinedPlan`'s route.** Epic 2's `CombinedRoutePlanner` (Story 2.4) can produce routes touching many more locations than one contract's two endpoints, but this story's AC is specifically about a single scanned contract being flagged — checking every stop along a combined multi-mission route is a natural future extension, not something this story's AC asks for. Don't expand scope to consume `CombinedPlan`.
- **`UIPort.confirm_risky_contract` is a port method, not an implementation.** No UI adapter exists yet anywhere in this codebase (the Tkinter seed UI is still Deferred) — this story only extends the *interface* a future adapter will implement, exactly like `show_results` before it. Do not attempt to build a concrete popup here.
- **Never auto-decide:** the non-goal is explicit and absolute — this code must never call any accept/decline action on the contract itself, only report the player's own choice back up. `LegalityChecker`/`UIPort` together only ever *ask and record an answer*; nothing in this story touches the game. [Source: SPEC.md#Non-goals]
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds one new file to `core/`: `legality_checker.py`. Modifies `core/ports/ui_port.py` additively (new abstract method; existing `show_results` untouched).

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.2] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/specs/spec-verselog/SPEC.md#Non-goals] — no input injection, ever; the tool only asks and reports
- [Source: _bmad-output/implementation-artifacts/3-1-reputation-sync.md] — `ReputationStore.get_level()`, consumed directly here; the same "don't invent unverified data" reasoning this story continues
- [Source: src/verselog/core/ports/ui_port.py] — existing `UIPort` scaffold from Story 1.1, extended here for the first time since creation
- [Source: _bmad-output/implementation-artifacts/2-4-combined-route-and-loading-plan-for-multiple-missions.md] — `CombinedRoutePlanner`, explicitly named as out of this story's scope

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `92 passed in 2.92s`

### Completion Notes List

- Implemented `LegalityRisk`/`LegalityChecker` (`core/legality_checker.py`): checks a contract's departure then arrival against an injected `location_factions` mapping and `ReputationStore.get_level()`, flagging the first faction whose standing is at or below an explicit, no-default `risk_threshold`. Missing data (unmapped location, or a faction with no synced standing) is never treated as risky.
- Extended `UIPort` (Story 1.1's scaffold) with `confirm_risky_contract(contract, risk) -> bool` — the first concrete method added since the port was created empty. No concrete `UIPort` adapter exists anywhere yet, so this was a purely additive change with zero regression risk (confirmed: no other file references `UIPort`).
- Deliberately did not build a real location-to-faction data source — no verified mapping has been found (mirrors Story 3.1's REP-screen scoping decision); `location_factions` is a plain injected dict for now.
- All acceptance criteria satisfied for the buildable, testable scope; 92/92 tests passing (86 pre-existing + 6 new).

### File List

- `src/verselog/core/legality_checker.py` (new)
- `src/verselog/core/ports/ui_port.py` (modified — added `confirm_risky_contract` abstract method)
- `tests/test_legality_checker.py` (new)

## Change Log

- 2026-07-09: Story implemented — `LegalityRisk`/`LegalityChecker` added and `UIPort` extended with the confirmation interaction, scoped to the checking logic (location-to-faction data source deferred, no verified mapping available), all tasks complete, 92/92 tests passing, status moved to review.
