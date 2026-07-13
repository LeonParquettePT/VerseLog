---
baseline_commit: 09d471a
---

# Story 6.3: Finish Screen & Shortcut

Status: review

## Story

As a player who just finished installing VerseLog's prerequisites,
I want a clear finish screen with the option to create a shortcut,
so that launching VerseLog afterward doesn't require remembering a file path.

## Acceptance Criteria

1. **Given** the player has completed (or skipped) the component-selection step, **when** the wizard reaches its final step, **then** it confirms completion plainly and offers a checkbox to create a desktop and/or Start Menu shortcut to `verselog.exe`, **and** declining the shortcut is just as valid an ending as accepting it — the wizard never assumes. [Source: epics.md#Story-6.3]

## Tasks / Subtasks

- [x] Task 1: Give `InstallerWizard` a completion hook (AC: #1)
  - [x] `go_next()` now calls the last step's optional `on_finish()` (via `getattr(..., None)`, mirroring `on_shown()`'s existing shape) immediately before `root.destroy()`. Verified with 2 new tests: a step defining `on_finish()` gets it called exactly once on Finish, and a step without one (the existing test fakes) doesn't break anything.
- [x] Task 2: Build the finish step (AC: #1)
  - [x] `src/verselog_installer/steps/finish_step.py`: `FinishStep`. `build()` shows the completion message plus two checkboxes, both checked by default; `BooleanVar`s are created once and reused across rebuilds (Story 6.2's lesson applied proactively, not rediscovered).
  - [x] `on_finish()` creates a shortcut per still-checked box via an injectable `shortcut_creator` (defaults to a real PowerShell `WScript.Shell` implementation). Declining both → zero calls, confirmed by test.
- [x] Task 3: Wire the step into the installer's step list (AC: #1)
  - [x] `FinishStep()` added as the new last step. `test_installer_main.py` updated (4 steps now, in order) and re-verified.
- [x] Task 4: Tests (AC: #1)
  - [x] `tests/test_installer_wizard.py`: 2 new tests (see Task 1).
  - [x] `tests/test_finish_step.py` (new, 5 tests): defaults, both-checked, one-unchecked, both-unchecked, and Back-then-Next preservation.
  - [x] Real manual verification of the *real* `_create_shortcut` implementation: invoked it against a scratch path (`.../scratchpad/VerseLog-test.lnk`, never the real desktop/Start Menu), confirmed a genuine 1664-byte `.lnk` file was created, then deleted it immediately.
  - [x] Real manual verification of the rendered step: screenshot confirms the completion message and both pre-checked checkboxes render correctly.

## Dev Notes

- **Why a new `on_finish()` hook on the wizard, not just handling it inside `FinishStep.build()`:** shortcut creation must happen in response to the player's final "Finish" click, not merely when the step is shown (that would create the shortcut immediately on arrival, before the player has even seen or adjusted the checkboxes — the opposite of "declining is just as valid", since by the time they could decline, it would already be done). `InstallerWizard.go_next()` is the only place that currently knows "this is the terminal action, the window is about to close" — extending it with an optional hook, mirroring `on_shown()`'s existing shape, is the natural and minimal way to give a step a say at that exact moment.
- **Real Windows shortcut creation without a new dependency:** a `.lnk` file is a binary format; the standard way to create one from Python without adding `pywin32` as a new dependency is to shell out to PowerShell's `WScript.Shell` COM automation (`New-Object -ComObject WScript.Shell` → `.CreateShortcut(...)` → `.Save()`). This avoids a new package-manager dependency for a single, infrequent, one-shot action.
- **Where `verselog.exe` is assumed to live:** this installer does not itself copy/place `verselog.exe` anywhere (out of scope for this epic, which only covers benchmarking and prerequisite-install guidance — see Story 6.1/6.2's own Dev Notes). The shortcut's target path defaults to `verselog.exe` alongside the installer's own executable (`Path(sys.executable).parent / "verselog.exe"` when frozen via PyInstaller, else a plain relative path for running from source) — the assumption is the two are distributed side by side, consistent with how Story 5.1/5.2's Release assets already work (a single downloadable file per platform). This default is injectable, so it isn't hard-baked if that assumption changes later.
- **Learning directly applied from Story 6.2's own code review finding** (checkbox state must survive Back-then-Next re-entry) — implemented correctly the first time here instead of waiting to be caught again in review.
- **Coding style:** plain, direct code, matching the existing step-based patterns from Stories 6.1/6.2. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Modifies `src/verselog_installer/wizard.py` (new `on_finish()` hook in `go_next()`), `src/verselog_installer/__main__.py` (adds `FinishStep()` to the step list). Adds `src/verselog_installer/steps/finish_step.py` (new). Adds `tests/test_finish_step.py` (new); extends `tests/test_installer_wizard.py`. No changes to `src/verselog/` (the main app package) at all.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-6.3] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/6-1-installer-wizard-shell-benchmark-step.md] — `on_shown()`'s existing optional-hook shape, mirrored here as `on_finish()`
- [Source: _bmad-output/implementation-artifacts/6-2-component-selection-guided-installation.md] — the checkbox-state-preserved-across-re-entry code review finding, applied proactively here instead of waiting to rediscover it

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `174 passed` (166 from Story 6.2's baseline + 8 new).
- Known pre-existing Tk()-creation environment flake observed twice more during this story, on different files each time (`test_finish_step.py`'s shared fixture once, `test_installer_wizard.py` once) — confirmed by immediate re-runs, not a defect from this story's changes. Still tracked as Story 6.4, not fixed here.
- Real verification of `_create_shortcut()` (the actual, non-injected implementation): ran it against `.../scratchpad/VerseLog-test.lnk` pointing at an arbitrary real file — confirmed a genuine 1664-byte `.lnk` was created via the PowerShell `WScript.Shell` COM approach, then deleted the scratch artifact immediately. Never touched the real desktop or Start Menu.

### Completion Notes List

- Implemented all 4 tasks: `InstallerWizard.go_next()` gained an `on_finish()` hook (mirroring `on_shown()`'s existing shape), `FinishStep` shows a completion message + two shortcut checkboxes (checked by default), `on_finish()` creates a shortcut per checked box via an injectable, real-by-default `shortcut_creator` (PowerShell COM automation, no new dependency), and it's wired in as the wizard's new last step.
- Applied Story 6.2's own code-review lesson (checkbox state must survive Back-then-Next re-entry) proactively from the start, rather than needing it caught again in review — confirmed by a dedicated regression test.
- Epic 6 is now functionally complete (all 3 stories done) — PyInstaller packaging of `verselog-installer.exe` itself, deliberately deferred since Story 6.1, is the natural next piece of work, not part of this story.
- 174/174 tests passing.

### File List

- `src/verselog_installer/wizard.py` (modified — new `on_finish()` hook)
- `src/verselog_installer/steps/finish_step.py` (new)
- `src/verselog_installer/__main__.py` (modified — adds `FinishStep()`)
- `tests/test_installer_wizard.py` (modified — new tests)
- `tests/test_finish_step.py` (new)
- `tests/test_installer_main.py` (modified — updated for 4 steps)

## Change Log

- 2026-07-13: Story implemented — `on_finish()` wizard hook, `FinishStep` (completion message, shortcut checkboxes, real PowerShell-based shortcut creation), wired as the installer's final step. Epic 6 is now functionally complete. 174/174 tests passing, status moved to review.
