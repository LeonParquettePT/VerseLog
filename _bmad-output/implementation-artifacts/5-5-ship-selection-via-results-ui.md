---
baseline_commit: df71f37
---

# Story 5.5: Ship Selection via the Results UI

Status: review

## Story

As a player who doesn't use VoiceAttack or the command line,
I want to pick my ship from the graphical interface,
so that I don't have to launch VerseLog with a `--ship` command-line argument every time.

## Acceptance Criteria

1. **Given** `--ship` is required on the command line today (confirmed working via manual testing in Stories 5.1/5.4), **when** a player launches VerseLog without a `--ship` argument, **then** the Tkinter UI presents a ship-selection screen (populated from `ShipReferenceStore`'s already-imported data) before the scan begins, instead of `argparse` erroring out, **and** `--ship` remains available as a command-line shortcut for players who prefer it (VoiceAttack users, scripted/console workflows) — this doesn't replace the CLI path, it adds a GUI path for everyone else. [Source: epics.md#Story-5.5]

## Tasks / Subtasks

- [x] Task 1: Let `ShipReferenceStore` list all known ship names (AC: #1)
  - [x] Added `list_ship_names(self) -> list[str]` to `src/verselog/core/ship_reference_store.py`, returning names sorted alphabetically (`SELECT name FROM ships ORDER BY name`) — deterministic order for both the dropdown and its tests, not insertion order.
- [x] Task 2: Add a `select_ship` method to `UIPort` and implement it in both adapters (AC: #1)
  - [x] Added `select_ship(self, ship_names: list[str]) -> str | None` as a new abstract method on `src/verselog/core/ports/ui_port.py`.
  - [x] `ConsoleUIProvider.select_ship`: prints a numbered list, prompts with `input()`, parses the number back to a name; returns `None` for empty/invalid/out-of-range input rather than raising.
  - [x] `TkinterUIProvider.select_ship`: builds a `ttk.Combobox` pre-filled with `ship_names` plus a "Start scan" button, via a new testable `build_ship_selection_window(ship_names) -> tk.Tk`; `select_ship` runs `mainloop()` and returns whatever `self._selected_ship` ended up as (set by the button's callback, or left `None` if the window closes first).
  - [x] Empty-list case handled explicitly in both adapters: a plain message pointing at `--import-reference-data`, no dropdown at all.
- [x] Task 3: Wire `app.run()` and `__main__.py` to use ship selection when `--ship` is omitted (AC: #1)
  - [x] `src/verselog/app.py`: `run()`'s `ship_name` parameter is now `str | None = None`. When `ship_name is None`, calls `ui.select_ship(ship_store.list_ship_names())` before triggering a capture; returns immediately (no capture, no results window) if that comes back `None`.
  - [x] `src/verselog/__main__.py`: `parser.error(...)` now only fires for `not args.ship and args.console_ui`. Default (Tkinter) path proceeds with `ship_name=None` when `--ship` is omitted.
- [x] Task 4: Tests (AC: #1)
  - [x] `tests/test_ship_reference_store.py`: empty-store and alphabetical-sort cases added.
  - [x] `tests/test_console_ui_provider.py`: chosen-name, out-of-range/invalid-answer, and empty-list cases added.
  - [x] `tests/test_tkinter_ui_provider.py`: combobox pre-fill, empty-list message, and cancel-returns-None cases added. Also visually verified directly: rendered `build_ship_selection_window` and captured a real screenshot (via `mss`) confirming the combobox and "Start scan" button actually render correctly — not just asserted via widget introspection.
  - [x] `tests/test_app.py`: added `select_ship`-returns-a-name (route uses it), `select_ship`-returns-`None` (no capture, nothing shown), and the explicit VoiceAttack/CLI regression test (`select_ship` never called when `ship_name` is given).
  - [x] `tests/test_main.py`: `--console-ui` without `--ship` still errors (`SystemExit`, message updated to name `--console-ui` specifically); default path without `--ship` now succeeds and passes `ship_name=None` through to `run()`.

## Dev Notes

- **Why only the Tkinter path gets a selection screen, not console/scripted workflows:** the epics.md AC is explicit that `--ship` "remains available as a command-line shortcut for players who prefer it (VoiceAttack users, scripted/console workflows)". VoiceAttack (Story 1.4) and any scripted use of `--console-ui` already pass `--ship` programmatically — there is no human sitting at a console prompt in those workflows to interactively pick from a list, so building an interactive console picker would be solving a problem nobody described. Keeping `--console-ui` + no `--ship` as a `parser.error(...)` (unchanged from today) is deliberate, not an oversight. [Source: _bmad-output/planning-artifacts/epics.md#Story-5.5]
- **`select_ship` is called before capture, not after:** `app.run()` today only *uses* `ship_name` near the end (`route_cost_calculator.calculate(...)`, `loading_plan_calculator.derive(...)`) — nothing technically stops selection from happening after a scan. But the AC says "before the scan begins", and the natural UX is pick-then-scan, not scan-then-ask. Implement it that way: call `ui.select_ship(...)` immediately after `ship_store` is constructed, before `trigger.on_triggered()`.
- **Fail-closed, matching `confirm_risky_contract`'s established pattern:** if the player closes the ship-selection window without choosing (or the console prompt gets a bad answer), `select_ship` returns `None` and `run()` returns immediately — no capture, no results window, nothing partially done. This mirrors the existing `confirm_risky_contract` → fail-closed pattern from Story 4.3 (a broken/cancelled UI interaction must never be treated as implicit permission to keep going).
- **The empty-ship-list case is real, not hypothetical:** a fresh install (per Story 5.1/5.2's own packaging notes) has no reference data imported until the player runs `--import-reference-data` once. Presenting an empty combobox with no explanation would be confusing — show a plain message instead ("No ships found — run VerseLog with --import-reference-data first").
- **`ShipReferenceStore.get_ship(name)` already exists and is unaffected by this story** — `list_ship_names()` is purely additive, a new read method alongside it. No changes to `save_ships`, the `ships` table schema, or `get_ship`'s behavior.
- **UIPort is a plain ABC (`abc.ABC`), not enforced via `Protocol`** — adding a new `@abstractmethod` to it will NOT break existing test doubles that don't formally subclass `UIPort` (e.g. `test_app.py`'s `_SpyUI`, `test_app_legality.py`'s `_SpyUI` — both are duck-typed, not `UIPort` subclasses), since Python only enforces abstract methods at instantiation time for actual subclasses. Real, registered subclasses (`ConsoleUIProvider`, `TkinterUIProvider`) MUST implement the new method or they'll fail to instantiate — both are updated by this story so that's covered. [Source: src/verselog/core/ports/ui_port.py, tests/test_app.py#_SpyUI, tests/test_app_legality.py#_SpyUI — read directly during story creation, confirmed no formal `UIPort` inheritance in either test double]
- **Coding style:** plain, direct code, no new abstractions beyond the one new port method and the one new store method this story actually needs. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Modifies `src/verselog/core/ship_reference_store.py` (new method), `src/verselog/core/ports/ui_port.py` (new abstract method), `src/verselog/adapters/ui/console_ui_provider.py` and `src/verselog/adapters/ui/tkinter_ui_provider.py` (new method each), `src/verselog/app.py` (`ship_name` becomes optional, new selection call), `src/verselog/__main__.py` (conditional `--ship` requirement). No new files except tests extending the existing test files for each of the above (one new test file is not needed — every touched module already has a test file).

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.5] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/4-2-results-window-tkinter-ui-adapter.md] — the `build_results_window` testable-builder pattern this story's `build_ship_selection_window` follows
- [Source: _bmad-output/implementation-artifacts/4-3-risky-contract-confirmation-popup.md] — the fail-closed `confirm_risky_contract` pattern `select_ship` mirrors
- [Source: _bmad-output/implementation-artifacts/5-1-windows-packaging-pyinstaller.md#Dev-Notes] — "`--ship` remains a required CLI argument — no ship-selection UI is built here", the gap this story closes
- Raised directly by the project's own author during real manual testing of the packaged Windows exe (2026-07-13): requiring a CLI argument for ship selection is a real UX gap for non-VoiceAttack, non-CLI players

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `127 passed in 4.78s` (114 pre-existing + 13 new)
- Rendered `TkinterUIProvider().build_ship_selection_window([...])` directly and captured a real screenshot via `mss` — confirmed the combobox is pre-filled and the "Start scan" button renders as designed, not just inferred from widget introspection in tests.

### Completion Notes List

- Implemented all 4 tasks fully: `ShipReferenceStore.list_ship_names()`, a new `UIPort.select_ship` abstract method implemented in both `ConsoleUIProvider` and `TkinterUIProvider`, `app.run()`'s `ship_name` made optional with selection wired in before capture, and `__main__.py`'s `--ship` requirement narrowed to `--console-ui` only.
- Explicit regression test added per the project author's own concern raised mid-story: confirmed `ui.select_ship` is never called when `ship_name` is passed explicitly, so VoiceAttack (Story 1.4) and any other `--ship`-passing caller see zero behavior change.
- Empty-ship-list edge case (no reference data imported yet) handled in both adapters, not just the Tkinter one — a real first-run scenario, not hypothetical.
- 127/127 tests passing (114 pre-existing + 13 new); no regressions.
- **Code review fix:** `app.run()` originally checked `if ship_name is None`, so an explicitly empty `--ship ""` (e.g. from a VoiceAttack profile whose variable substitution produced blank text) silently bypassed selection and proceeded with an invalid empty ship name instead of either prompting or erroring clearly — a real regression versus the pre-story behavior (which treated any falsy `--ship` as missing). Fixed to `if not ship_name` in both the initial check and the post-selection check, with a new regression test (`test_run_treats_an_empty_ship_name_the_same_as_none`). 128/128 tests passing after the fix.

### File List

- `src/verselog/core/ship_reference_store.py` (modified — `list_ship_names()`)
- `src/verselog/core/ports/ui_port.py` (modified — new `select_ship` abstract method)
- `src/verselog/adapters/ui/console_ui_provider.py` (modified — `select_ship` implementation)
- `src/verselog/adapters/ui/tkinter_ui_provider.py` (modified — `select_ship` + `build_ship_selection_window`, new `__init__`)
- `src/verselog/app.py` (modified — `ship_name` optional, selection wired in)
- `src/verselog/__main__.py` (modified — `--ship` only required with `--console-ui`)
- `tests/test_ship_reference_store.py` (modified — new tests)
- `tests/test_console_ui_provider.py` (modified — new tests)
- `tests/test_tkinter_ui_provider.py` (modified — new tests)
- `tests/test_app.py` (modified — new tests, `_SpyUI`/`_FakeCapturePort` extended)
- `tests/test_main.py` (modified — new tests)

## Change Log

- 2026-07-13: Story implemented — ship selection via the Tkinter UI when `--ship` is omitted, `--ship` still required only for `--console-ui`, with an explicit regression test confirming VoiceAttack/CLI callers are unaffected. Visually verified the selection window renders correctly via a real screenshot. 127/127 tests passing, status moved to review.
