---
baseline_commit: aca3fe463be3360027f6f3594e62396bd2f1822f
---

# Story 3.1: Reputation Sync

Status: done

## Story

As a player,
I want my reputation level synced automatically,
so that legality checks are always based on my current standing.

## Acceptance Criteria

1. **Given** the app launches or performs a scan, **when** reputation sync runs, **then** the current reputation level is detected/updated automatically, **and** the player can manually reconfigure it if it changes mid-session. [Source: epics.md#Story-3.1]

## Tasks / Subtasks

- [x] Task 1: Define `ReputationLevel` and `ReputationStore` (AC: #1)
  - [x] `src/verselog/core/reputation_store.py` — `ReputationLevel` dataclass: `faction: str`, `standing: float` (per-faction, not one overall number — Story 3.2's "trespassing zone" example is inherently faction/territory-specific)
  - [x] `ReputationStore(settings_store: SettingsStore)` — layered on the existing `SettingsStore` under one JSON key (e.g. `"reputation_levels"`, a `{faction: standing}` dict), exactly mirroring `FuelOverrideStore`'s pattern from Story 2.5. AD-7 explicitly names "reputation level" as settings-store content — do not create a new SQLite table or reference-data store for this (AD-4 scopes SQLite to bulk-*imported* community data, which this isn't).
  - [x] `set_level(faction: str, standing: float) -> None` — the manual-reconfigure entry point (AC's second clause)
  - [x] `get_level(faction: str) -> float | None` — `None` means "no known standing for this faction yet"
  - [x] `sync(detected_levels: list[ReputationLevel]) -> None` — bulk-updates every faction in the list in one call, mirroring `ShipReferenceStore.save_ships()`'s bulk-upsert shape (Story 2.1). An empty list is a no-op: it must never clear or reset factions not present in it — this is a partial update of whatever was actually detected, not a full resync.
- [x] Task 2: Tests (AC: #1)
  - [x] `set_level` then `get_level` returns the exact value set
  - [x] `get_level` for a faction with no stored standing returns `None`
  - [x] `sync()` with multiple `ReputationLevel` entries updates each faction independently
  - [x] `sync()` with an empty list is a no-op — a previously-set faction's standing is unchanged, not cleared
  - [x] `set_level` called after `sync()` correctly overrides just that one faction, leaving others untouched (independence check, mirroring `test_fuel_override_store.py`'s per-ship independence test)
  - [x] Values persist across separate `ReputationStore` instances constructed from the same underlying settings file (mirrors `FuelOverrideStore`'s persistence test)

## Dev Notes

- **What this story deliberately does NOT build, and why:** the actual mechanism that *detects* a reputation reading from the game (screen capture + OCR/vision parsing of the in-game REP screen) is **not** implemented here. SPEC.md's non-goals rule out game-state/memory reading — any detection has to be screen-based, like `CapturePort`/`OCRProvider`/`VisionProvider` (Epic 1) — but unlike contracts, there is no real captured reference screenshot of the REP screen on file yet (`contract-ui-reference.md` only covers the contract board). Inventing an unverified OCR text pattern for a screen nobody has looked at would repeat the exact mistake this project has explicitly avoided elsewhere (see Story 1.2's Dev Notes: "do not invent unverified phrasing patterns now"; and this session's real discovery that assumed Ollama model names/prompts didn't survive contact with real screenshots). `ReputationStore.sync()` is the integration point a future capture adapter calls into once a real reference screenshot exists to design against — this story builds and tests that integration point in isolation, which is fully verifiable without it. [Source: SPEC.md#Non-goals; _bmad-output/implementation-artifacts/1-2-manual-capture-via-classic-ocr.md#Dev-Notes]
- **Why "the app launches or performs a scan" isn't wired to anything yet:** there is no application entrypoint anywhere in this codebase yet that wires trigger → capture → trust layer → UI together (a gap flagged as early as Story 1.1 and still open) — every story so far has been `core/`/`adapters/` logic only. Wiring *when* `ReputationStore.sync()` actually gets called (on launch, after every scan, etc.) is an entrypoint-integration concern for whenever that entrypoint gets built, not something a `core/`-only story can meaningfully do. Don't add launch/scan-lifecycle hooks here.
- **Per-faction, not one global number:** Story 3.2's own example ("a trespassing zone") is about standing with whichever faction controls a specific territory, not one overall reputation score — `ReputationLevel`/`ReputationStore` must be keyed by faction from the start, not retrofitted later.
- **No range validation on `standing`:** without a real reference screenshot, the actual scale Star Citizen uses (0–100? a signed range? something else) isn't verified — inventing a bound now risks being wrong later, the same reasoning as not inventing OCR patterns above. Leave it an unconstrained `float`.
- **Composition pattern:** identical shape to Story 2.5's `FuelOverrideStore` (wraps `SettingsStore`, one JSON key, per-key independence) — reuse that pattern directly rather than inventing a new one. [Source: _bmad-output/implementation-artifacts/2-5-fuel-value-override-and-reset.md]
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds one new file to `core/`: `reputation_store.py`, alongside `fuel_override_store.py` and `settings_store.py`. No structural surprises.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.1] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.2] — confirms reputation is consumed per-faction/per-territory by the legality check, not as one global number
- [Source: _bmad-output/specs/spec-verselog/SPEC.md#Non-goals] — no game-state/memory reading; any real detection must be screen-based like CAP-1
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-7] — explicitly names "reputation level" as settings-store content
- [Source: _bmad-output/implementation-artifacts/2-5-fuel-value-override-and-reset.md] — `FuelOverrideStore`'s pattern, reused directly for `ReputationStore`
- [Source: _bmad-output/implementation-artifacts/2-1-reference-data-import-local-sqlite.md] — `ShipReferenceStore.save_ships()`'s bulk-upsert shape, the pattern `sync()` mirrors

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `86 passed in 2.95s`

### Completion Notes List

- Implemented `ReputationLevel`/`ReputationStore` (`core/reputation_store.py`), layered on the existing `SettingsStore` under one `"reputation_levels"` key, exactly mirroring `FuelOverrideStore`'s pattern from Story 2.5.
- `set_level()` is the manual-reconfigure entry point; `sync()` bulk-updates from a list of detected readings (mirrors `ShipReferenceStore.save_ships()`'s bulk-upsert shape) and is a documented no-op on an empty list, so a "nothing detected this pass" result never wipes previously-known standings.
- Deliberately did not build any screen-capture/OCR-parsing mechanism for the REP screen — no real reference screenshot exists yet to design an unverified text pattern against (same discipline as Story 1.2's contract-type scoping). `sync()` is the integration point a future capture adapter will call into.
- All acceptance criteria satisfied for the buildable, testable scope; 86/86 tests passing (80 pre-existing + 6 new).

### File List

- `src/verselog/core/reputation_store.py` (new)
- `tests/test_reputation_store.py` (new)

## Change Log

- 2026-07-09: Story implemented — `ReputationLevel`/`ReputationStore` added, scoped to the storage/sync-integration layer (screen-detection deferred, no real reference screenshot available), all tasks complete, 86/86 tests passing, status moved to review.
