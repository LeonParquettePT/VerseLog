---
baseline_commit: 0505b84
---

# Story 5.6: Monitor Selection for Capture

Status: review

## Story

As a player with more than one monitor,
I want to tell VerseLog which screen I actually play on,
so that captures aren't taken across every monitor by default, reducing noise and capture errors.

## Acceptance Criteria

1. **Given** capture today grabs all connected monitors by default (confirmed during real manual testing: a screenshot taken outside the game spanned both of the tester's screens), **when** a player opens VerseLog's settings, **then** they can select a specific monitor to capture instead of all of them, with "all screens" remaining the default so single-monitor players see no change, **and** the selection persists across runs via `SettingsStore`, consistent with how the benchmark tier is already persisted. [Source: epics.md#Story-5.6]

## Tasks / Subtasks

- [x] Task 1: Let `take_screenshot()` and the capture providers target a specific monitor (AC: #1)
  - [x] `src/verselog/adapters/capture/screenshot.py`: `take_screenshot(monitor_index: int = 0) -> bytes`, using `sct.monitors[monitor_index]` instead of the hardcoded `sct.monitors[0]`. Default stays `0` so nothing changes for anyone who doesn't opt in.
  - [x] `OCRProvider.__init__(self, monitor_index: int = 0)` and `VisionProvider.__init__(self, model: str = DEFAULT_VISION_MODEL, monitor_index: int = 0)`: store it, pass it through to `take_screenshot(self._monitor_index)` in `capture()`. Verified via new tests (`tests/test_screenshot.py`, `tests/test_ocr_provider.py` (new file), `tests/test_vision_provider.py` extended) that the index actually reaches `take_screenshot`, not just that the constructor accepts it.
- [x] Task 2: Wire monitor selection into `app.run()`, persisted via `SettingsStore` (AC: #1)
  - [x] Added `monitor_index: int | None = None` to `run()`'s parameters. When given, persisted via `settings_store.set("capture_monitor_index", monitor_index)`; always reads the resolved value back via `settings_store.get("capture_monitor_index", 0)` before constructing the providers, so a run without `monitor_index` picks up whatever was persisted last time.
  - [x] Only constructs `VisionProvider(monitor_index=...)`/`OCRProvider(monitor_index=...)` with the resolved index inside the existing `if capture_port is None:` branch — a test-injected `capture_port` bypasses this entirely, unchanged from today. Verified with 3 new tests covering: explicit index given + persisted, persisted index reused when omitted, and default `0` when nothing was ever persisted.
- [x] Task 3: Expose it on the command line, with validation (AC: #1)
  - [x] `src/verselog/__main__.py`: added `--monitor` (`type=int`, optional, help text explaining `0 = all screens combined (default)`, `1, 2, ... = a specific screen`). No settings-screen UI exists anywhere in this project — a CLI flag mirrors the existing `--ship`/`--console-ui` pattern, satisfying "the selection persists across runs" without inventing an unscoped settings UI (see Dev Notes).
  - [x] When `--monitor` is given, validated against the real connected-monitor count (`len(mss.mss().monitors)`) before calling `run()`, via `parser.error(...)` — same style as the existing `--ship`-required check.
  - [x] `monitor_index=args.monitor` passed through to `run(...)` (`None` when `--monitor` wasn't given, handled by `run()`'s own default).
- [x] Task 4: Tests (AC: #1)
  - [x] `tests/test_screenshot.py` (new): default index `0`, and an explicitly-given index, both verified against `sct.grab`'s actual argument.
  - [x] `tests/test_ocr_provider.py` (new) and `tests/test_vision_provider.py` (extended): constructing either provider with a non-default `monitor_index` results in `take_screenshot` being called with that exact index.
  - [x] `tests/test_app.py`: 3 new tests — explicit `monitor_index` given (persisted + used), `monitor_index` omitted reuses the persisted value, and defaults to `0` when nothing was ever persisted. Verified via fake `VisionProvider`/`OCRProvider` classes monkeypatched into `app` module (avoids any real capture I/O, consistent with how `capture_port` is always faked).
  - [x] `tests/test_main.py`: 3 new tests — `--monitor 1` (in range) passes through correctly, `--monitor 5` (out of range, 2-monitor fake) triggers `SystemExit` via `parser.error`, and omitting `--monitor` passes `None` through.

## Dev Notes

- **Why a CLI flag, not a graphical settings screen:** epics.md's AC says "when a player opens VerseLog's settings", but this project has no settings UI at all today — `SettingsStore` (Story 1.6) is a plain JSON file, written to only programmatically (benchmark tier/worker count), never through any player-facing screen. Building a full settings UI here would be a much bigger, unscoped undertaking triggered incidentally by a monitor-selection story. `--monitor`, mirroring the already-established `--ship`/`--console-ui` CLI flags, satisfies the AC's real requirement (a way to set it, persisted via `SettingsStore`) without that scope creep. A graphical settings screen remains a legitimate future story if a player asks for one specifically.
- **`mss` monitor indexing (verified directly against the installed library):** `sct.monitors[0]` is a synthetic "all monitors combined" bounding box — this is *today's* existing behavior and exactly what spanned both of the tester's screens during Story 4.1/5.1 manual testing. `sct.monitors[1..N]` are the real, individual physical monitors. Keeping `0` as the default preserves current behavior for single-monitor players (where `monitors[0]` and `monitors[1]` describe the same single screen anyway) and for anyone who hasn't opted in yet.
- **Real uncaught-crash risk found while researching this story, not invented:** `OCRProvider.capture()` and `VisionProvider.capture()` both call `take_screenshot()` *before* entering their `try/except` blocks (confirmed by reading both files directly) — an `IndexError` from an invalid monitor index would crash the whole app, not degrade gracefully like every other capture failure in this codebase. Validating `--monitor` up front in `__main__.py` (where the real monitor count can be cheaply queried via `mss.mss().monitors`) avoids ever reaching that code path with a bad value, rather than trying to make `take_screenshot()` itself swallow the error (which would just turn a clear config mistake into a silent, confusing blank capture).
- **Persistence mirrors the benchmark tier/worker-count pattern exactly** (`SettingsStore.get`/`.set` with a plain string key, `"capture_monitor_index"`) — no new storage mechanism, no schema.
- **Coding style:** plain, direct code; no new abstractions beyond the one new constructor parameter each on two existing classes, one new `run()` parameter, one new CLI flag. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Modifies `src/verselog/adapters/capture/screenshot.py`, `src/verselog/adapters/capture/ocr_provider.py`, `src/verselog/adapters/capture/vision_provider.py`, `src/verselog/app.py`, `src/verselog/__main__.py`. Adds `tests/test_screenshot.py` (new); extends `tests/test_vision_provider.py`, `tests/test_app.py`, `tests/test_main.py`. No changes to `SettingsStore` itself (its generic `get`/`set` API already covers this).

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.6] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/5-5-ship-selection-via-results-ui.md] — the most recently completed story, whose "extend an existing default-constructed dependency with a new optional, persisted setting" shape this story mirrors
- Confirmed directly by reading `src/verselog/adapters/capture/ocr_provider.py` and `vision_provider.py` (2026-07-13): `take_screenshot()` is called outside both providers' `try/except` blocks — the uncaught-`IndexError` risk this story's CLI-level validation avoids
- Raised by the project's own author after noticing their own multi-monitor Windows test screenshot captured both screens at once — a real precision/noise concern for anyone with more than one monitor, not a hypothetical

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `150 passed in 4.92s` (139 from Story 5.3's baseline + 11 new)

### Completion Notes List

- Implemented all 4 tasks: `take_screenshot(monitor_index=0)`, both capture providers accepting/forwarding `monitor_index`, `app.run()`'s new `monitor_index` parameter (persisted via `SettingsStore`, resolved-value-first design so omitting it reuses last time's choice), and `__main__.py`'s new `--monitor` flag with real-monitor-count validation.
- Interpreted "opens VerseLog's settings" as a CLI flag (`--monitor`), not a graphical settings screen, since no such screen exists anywhere in this project yet — documented explicitly in Dev Notes rather than silently narrowing scope or building an unscoped settings UI.
- Confirmed via direct code reading (not assumption) that `take_screenshot()` is called outside both providers' `try/except` blocks — an out-of-range monitor index would otherwise crash the app with an uncaught `IndexError`. Validation happens in `__main__.py` instead, where the real monitor count can be cheaply queried.
- 150/150 tests passing.
- **Code review fix:** `settings_store.set("capture_monitor_index", ...)` was nested inside `if capture_port is None:`, so an explicit `monitor_index` was silently never persisted when a caller also injected a `capture_port` (not reachable from the real CLI today, but a real inconsistency for any future/test caller combining both). Moved the persistence line above the `capture_port is None` check so it always happens regardless. New regression test added. 151/151 tests passing after the fix.

### File List

- `src/verselog/adapters/capture/screenshot.py` (modified — `monitor_index` parameter)
- `src/verselog/adapters/capture/ocr_provider.py` (modified — `monitor_index` constructor param)
- `src/verselog/adapters/capture/vision_provider.py` (modified — `monitor_index` constructor param)
- `src/verselog/app.py` (modified — `monitor_index` parameter, persisted + resolved)
- `src/verselog/__main__.py` (modified — new `--monitor` flag, validated against real monitor count)
- `tests/test_screenshot.py` (new)
- `tests/test_ocr_provider.py` (new)
- `tests/test_vision_provider.py` (modified — `_patch_screenshot` updated, new test)
- `tests/test_app.py` (modified — new tests, new fakes)
- `tests/test_main.py` (modified — new tests)

## Change Log

- 2026-07-13: Story implemented — monitor selection wired through `take_screenshot()`, both capture providers, `app.run()` (persisted via `SettingsStore`), and a new `--monitor` CLI flag with validation. 150/150 tests passing, status moved to review.
