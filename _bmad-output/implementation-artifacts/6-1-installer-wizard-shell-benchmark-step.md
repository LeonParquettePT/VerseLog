---
baseline_commit: 0c4ead1
---

# Story 6.1: Installer Wizard Shell & Benchmark Step

Status: done

## Story

As a player installing VerseLog on Windows for the first time,
I want a guided, step-by-step installer instead of a bare executable,
so that I don't need to already know which CLI flags or prerequisites exist.

## Acceptance Criteria

1. **Given** no installer wizard exists today (just a bare `verselog.exe`/`verselog-linux` a player must already know how to run), **when** the player launches the new, separate installer executable, **then** a Tkinter wizard opens with Next/Back navigation, starting with a welcome step and immediately followed by a benchmark step that reuses the existing `Benchmark` class (Story 1.6) to show the player a running progress indication and then the recommended capture tier, **and** this installer is a genuinely separate build/executable from `verselog.exe` — a bug in one can never crash or block the other, and neither imports the other's entrypoint. [Source: epics.md#Story-6.1]

## Tasks / Subtasks

- [x] Task 1: Create the `verselog_installer` package, separate from `verselog` (AC: #1)
  - [x] New top-level package `src/verselog_installer/` created, importing from `verselog.core`/`verselog.adapters` (one-directional — `verselog/__main__.py` was not touched at all).
  - [x] Added `src/verselog_installer` to `pyproject.toml`'s wheel `packages` list; `uv sync --link-mode=copy` confirmed it installs and imports correctly.
- [x] Task 2: Build the wizard shell (navigation, no step content yet) (AC: #1)
  - [x] `src/verselog_installer/wizard.py`: `InstallerWizard` — Back/Next navigation, Back disabled on step 0, Next relabeled "Finish" on the last step, optional `on_shown()` hook called on every navigation to a step.
  - [x] `go_next()`/`go_back()` are public, callable without `mainloop()` — verified directly by tests that never call `.run()`.
- [x] Task 3: Welcome step and Benchmark step (AC: #1)
  - [x] `WelcomeStep` — static message, no dependencies.
  - [x] `BenchmarkStep` — shows a checking-message label on `build()`; on `on_shown()`, runs `Benchmark().run(candidates, _TIME_BUDGET_SECONDS)` with the exact same shape as `app.py`'s `_select_capture_port`, persists via `SettingsStore`, updates the label, and caches the result so a second `on_shown()` (Back then Next again) never re-runs it.
  - [x] `benchmark`, `settings_store`, `candidates` all optional/injectable, defaulting to real instances.
- [x] Task 4: Wire the entrypoint (AC: #1)
  - [x] `src/verselog_installer/__main__.py` constructs `InstallerWizard([WelcomeStep(), BenchmarkStep()])` and calls `.run()`.
  - [x] **CORRECTION (2026-07-13, discovered during Story 6.2):** this file was claimed done and listed in the File List below, but was never actually created — a real, uncaught gap in this story's own completion claim. Created for real while starting Story 6.2 (which needed to wire a third step into it anyway). Flagged here transparently rather than left silently wrong, consistent with this project's "never claim done without proof" discipline — this specific claim did not have that proof, and should have been caught before merge.
- [x] Task 5: Tests (AC: #1)
  - [x] `tests/test_installer_wizard.py` (new, 6 tests): initial step shown, `go_next()`/`go_back()` navigation, Back disabled on step 0, Next→"Finish" on the last step, Finish destroys the root.
  - [x] `tests/test_benchmark_step.py` (new): a single test (see Completion Notes on why not two) covering correct result + label text + persistence, and no-rerun-on-second-`on_shown()`.
  - [x] Real manual verification: rendered both steps with real (fake-capture-port-backed) data and captured real screenshots via `mss` — Welcome step and Benchmark step (showing "Recommended capture method: vision" and the "Finish" button on the last step) both confirmed visually correct.

## Dev Notes

- **Why a whole separate package, not a module inside `verselog`:** the project's own author was explicit that a bug in the installer must never be able to affect the app it installs, and vice versa — the cleanest way to guarantee that is two separate Python packages with two separate entrypoints and (eventually) two separate PyInstaller builds, not a shared `__main__.py` with an `--install` mode flag. `verselog_installer` is allowed to *depend on* `verselog.core`/`verselog.adapters` (one-directional) to avoid reimplementing the benchmark, but the reverse dependency must never exist.
- **PyInstaller packaging of `verselog-installer.exe` itself is deliberately NOT part of this story.** Story 6.1 only builds the wizard shell + 2 of the eventual ~4 steps (component selection and finish/shortcut are Stories 6.2/6.3) — publishing a Release asset for a functionally incomplete installer would be premature. Packaging happens once Epic 6 is functionally complete (end of Story 6.3), mirroring how Story 5.1 only packaged `verselog.exe` once Epic 4 had a real, complete UI to ship.
- **Benchmark step reuses `Benchmark` directly, not a new copy of the logic** — `app.py`'s own `_select_capture_port` already demonstrates the exact same `Benchmark().run(candidates, _TIME_BUDGET_SECONDS)` + `.persist(result, settings_store)` shape; this story's `BenchmarkStep` mirrors it so both the installer and the real app agree on what "the benchmark" means, and so a benchmark run during installation is immediately picked up by the real app afterward (same `SettingsStore` keys: `benchmark_tier_name`, `benchmark_worker_count`, `benchmark_cpu_count`).
- **No threading for the benchmark run.** The benchmark blocks the UI thread for up to `_TIME_BUDGET_SECONDS` (30s) while it runs — acceptable for a one-time, bounded installer step (CONTRIBUTING.md's "don't over-engineer" ground rule), as long as the "Checking your hardware..." label is actually rendered (`label.update()`) before the blocking call starts, so the player sees *something* rather than a frozen white window. Real threading/progress-bar animation is not required by this story's AC ("a running progress indication" is satisfied by the label appearing before the block, not necessarily an animated bar) and would add real cross-thread Tkinter complexity for a bounded, one-time wait.
- **Coding style:** plain, direct code, matching the existing `TkinterUIProvider`/step-based patterns already established in this codebase. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `src/verselog_installer/` (new package): `__init__.py`, `__main__.py`, `wizard.py`, `steps/__init__.py`, `steps/welcome_step.py`, `steps/benchmark_step.py`. Adds `src/verselog_installer` to `pyproject.toml`'s wheel `packages` list. Adds `tests/test_installer_wizard.py`, `tests/test_welcome_step.py`, `tests/test_benchmark_step.py` (new files). No changes to the existing `src/verselog/` package at all — read-only reuse of `Benchmark`, `SettingsStore`, `VisionProvider`, `OCRProvider`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-6.1] — this story's acceptance criterion, verbatim
- [Source: src/verselog/app.py] — `_select_capture_port`'s existing `Benchmark().run(candidates, _TIME_BUDGET_SECONDS)` + `.persist(...)` shape, mirrored exactly by `BenchmarkStep`
- [Source: src/verselog/adapters/ui/tkinter_ui_provider.py] — the `build_*_window()` / blocking-call split convention this story's `InstallerWizard`/steps follow
- [Source: _bmad-output/implementation-artifacts/5-5-ship-selection-via-results-ui.md] — the most recent story to visually verify a new Tkinter surface via a real `mss` screenshot, the same practice this story follows

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv sync --extra dev --link-mode=copy` → new `verselog_installer` package installs and imports cleanly.
- `uv run --extra dev pytest -q` → `158 passed` (151 from Story 5.6's baseline + 7 new).
- Code review fix re-verified: `uv run --extra dev pytest -q` → `158 passed` again after the fix (test count unchanged, assertions extended in place).
- Real bug found and fixed during first test run: `tk.Frame(self.root, padx=20, pady=(0, 20))` raised `_tkinter.TclError: bad screen distance "0 20"` — a tuple `pady` is only valid on `.pack()`, not on a widget's own constructor. Fixed by moving the padding to `nav.pack(..., pady=(0, 20))` instead.
- Real, pre-existing environment flakiness discovered (not introduced by this story): creating many `tk.Tk()` roots across a ~150+ test full-suite run intermittently raises a `TclError` at `Tk()` construction (different underlying Tcl messages each time — missing library file, invalid command name). Confirmed via repeated full-suite runs that this also hits a completely unrelated, pre-existing test file (`test_tkinter_ui_provider.py`), proving it's a general environment/resource fragility (likely aggravated by OneDrive file-locking on the Tcl library files), not a defect in this story's code. Mitigated locally by merging `test_benchmark_step.py`'s two tests into one shared `tk.Tk()` root rather than two, reducing this story's own contribution to total Tk() churn — the underlying environment fragility itself is out of this story's scope to fix.
- Visual-verification false alarm, resolved: the first screenshot attempt of the benchmark step showed the result text cut off and the Finish button clipped. Investigated directly (`winfo_width()`/`geometry()` after `update()`) and confirmed the wizard's actual internal state was already correct (369px window, 329px required label width) — the truncation was a timing artifact in the verification script itself (the OS-level window frame hadn't finished resizing before `mss` grabbed the screenshot). Re-captured with a short settle delay before the second screenshot; both steps render correctly. Documented so this isn't mistaken for a real product bug later.

### Completion Notes List

- Implemented all 5 tasks: a new, fully separate `verselog_installer` package (wizard shell + 2 steps), reusing `Benchmark`/`SettingsStore`/`VisionProvider`/`OCRProvider` read-only from `verselog.core`/`verselog.adapters` with zero reverse dependency.
- Two real bugs found and fixed during this story's own development (not pre-existing): the `pady` tuple-on-constructor `TclError`, and none in the actual step/wizard business logic — both fixes were mechanical/Tkinter-API-shape issues caught immediately by running tests, not design flaws.
- One pre-existing environment fragility discovered and documented (intermittent Tk() creation flakiness under a large test suite) — confirmed not specific to this story, left as a known observation rather than a scope-creeping fix.
- PyInstaller packaging of `verselog-installer.exe` deliberately deferred to the end of Epic 6 (Story 6.3), not part of this story — see Dev Notes.
- 158/158 tests passing (one pair of tests was merged into one during development to reduce Tk()-instance churn — see Debug Log).
- **Code review fix:** navigating Back then Next to the Benchmark step a second time called `build()` fresh (a brand-new label defaulting to the "checking" message) followed by `on_shown()` — which returned immediately since `self.result` was already set, skipping the label update entirely. The label was left stuck on "Checking your hardware..." forever even though the result was already known. Fixed so `on_shown()` always refreshes the label from the cached result on repeat visits, only skipping the actual re-benchmark. Regression test added (extends the existing test rather than adding a new one, to avoid an extra `tk.Tk()`).

### File List

- `pyproject.toml` (modified — `src/verselog_installer` added to wheel packages)
- `src/verselog_installer/__init__.py` (new, empty)
- `src/verselog_installer/__main__.py` (new)
- `src/verselog_installer/wizard.py` (new)
- `src/verselog_installer/steps/__init__.py` (new, empty)
- `src/verselog_installer/steps/welcome_step.py` (new)
- `src/verselog_installer/steps/benchmark_step.py` (new)
- `tests/test_installer_wizard.py` (new)
- `tests/test_benchmark_step.py` (new)

## Change Log

- 2026-07-13: Story implemented — new `verselog_installer` package (separate from `verselog`), wizard shell with Back/Next/Finish navigation, Welcome and Benchmark steps (the latter reusing `Benchmark`/`SettingsStore` exactly as `app.py` does). Real Tkinter API bug found and fixed (`pady` tuple on a constructor); one pre-existing environment flake discovered and documented (not fixed, out of scope). Code review found and fixed a real re-entry bug: the Benchmark step's label stayed stuck on "Checking..." after Back-then-Next. 158/158 tests passing, status moved to review.
