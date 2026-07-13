---
baseline_commit: 0f00818
---

# Story 6.2: Component Selection & Guided Installation

Status: done

## Story

As a player who just saw the installer's benchmark recommendation,
I want to choose exactly which prerequisites get installed, with a sensible default already checked,
so that I stay in control of what happens to my machine while not having to research each prerequisite myself.

## Acceptance Criteria

1. **Given** the benchmark step (6.1) has produced a recommended capture tier, and `PrerequisiteChecker` (Story 5.3) can already detect what's missing, **when** the wizard reaches the component-selection step, **then** each missing prerequisite (Tesseract, Ollama, the vision model) is shown as its own checkbox, pre-checked only when the benchmark's recommended tier actually needs it (e.g. the vision model checkbox isn't pre-checked if the benchmark recommends the lighter OCR tier), **and** nothing is installed until the player explicitly clicks an "Install" button after reviewing their checkbox selections — consistent with this project's "never act without explicit confirmation" posture, now expressed as an installer UX instead of a plain warning message, **and** the actual install step, for each checked item, launches that prerequisite's own official installer/download (not a silent, fully-scripted install this project's own WSL experience already showed the risk of) — the player still completes each official installer themselves. [Source: epics.md#Story-6.2]

## Tasks / Subtasks

- [x] Task 1: Build the component-selection step (AC: #1)
  - [x] `src/verselog_installer/steps/component_selection_step.py`: `ComponentSelectionStep`. `build()` calls `PrerequisiteChecker().check_missing()` and renders one `tk.Checkbutton` per missing item; shows a plain "everything's already installed" message when nothing is missing.
  - [x] Pre-check logic implemented exactly as specified: `"ocr"` tier pre-checks only `"Tesseract OCR"`; `"vision"` tier pre-checks `"Ollama"` and the `"Ollama vision model (...)"` entry; `result is None` pre-checks nothing.
- [x] Task 2: Wire the "Install Selected" action (AC: #1)
  - [x] "Install Selected" button inside the step's own frame, separate from wizard nav.
  - [x] URL items → injectable `opener` (defaults to `webbrowser.open`); command items → injectable `message_shower` (defaults to `messagebox.showinfo`). Both DI-friendly, defaulting to real implementations.
- [x] Task 3: Wire the step into the installer's step list (AC: #1)
  - [x] **Real gap found and fixed while doing this task:** `src/verselog_installer/__main__.py` did not actually exist — Story 6.1 had claimed it was created but never actually ran the Write tool for it (corrected retroactively in that story's file, see its Change Log). Created it now with all 3 steps: `WelcomeStep`, `BenchmarkStep`, `ComponentSelectionStep(benchmark_step)`, sharing the same `BenchmarkStep` instance.
- [x] Task 4: Tests (AC: #1)
  - [x] `tests/test_component_selection_step.py` (new, 6 tests): pre-check behavior for `"ocr"`/`"vision"`/`None` tiers, empty-missing-list message, unchecked items never trigger `opener`/`message_shower`, checked URL/command items call the correct injected callable with the exact right argument.
  - [x] `tests/test_installer_main.py` (new, 2 tests): since `__main__.py` didn't exist before this story, added tests confirming it builds the wizard with all 3 steps in the right order and that `ComponentSelectionStep` shares the exact same `BenchmarkStep` instance (not a second, separate one).
  - [x] Real manual verification: rendered the step with 3 missing prerequisites and a `"vision"`-tier fake benchmark result, captured a real screenshot — Tesseract unchecked, Ollama and vision model checked, "Install Selected" button visible, confirmed correct.

## Dev Notes

- **Why "Install Selected" opens official installers/downloads rather than running commands directly:** explicitly decided during Story 5.3's own discussion and reconfirmed here — this project's own WSL install attempt (documented in Story 5.2's Dev Notes) demonstrated firsthand the elevation/reliability risk of scripted, silent installs. A checkbox + explicit "Install Selected" click *is* the player's explicit confirmation (satisfying SPEC.md's "never act without explicit confirmation" posture), but what happens after that click still stops short of silently running installers — it opens the *official* installer/download for the player to complete themselves, same posture as Story 5.3's plain warning message, just expressed as a guided UI action instead of static text.
- **Pre-check logic is intentionally narrow and tier-specific, not "pre-check everything missing".** The AC's own example (vision model unchecked when OCR is recommended) establishes the rule: only pre-check what the *actual recommended tier* needs, so a player who'll only ever use the lighter OCR tier isn't nudged into installing a multi-GB vision model they don't need for their hardware. This mirrors Story 5.7's own RAM-awareness reasoning (heavier tiers have real costs, not free to install "just in case").
- **`ComponentSelectionStep` depends on `BenchmarkStep` only by duck-typed attribute shape (`.result.tier_name`), not by import** — avoids a real coupling between the two step modules; either could change internally as long as that one attribute shape holds. Consistent with this codebase's existing Ports & Adapters discipline of depending on shapes/interfaces, not concrete types, wherever reasonably possible.
- **No changes to `PrerequisiteChecker` itself** — this story is pure UI wiring around the already-complete Story 5.3 detection logic.
- **Coding style:** plain, direct code, matching the existing step-based patterns from Story 6.1. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `src/verselog_installer/steps/component_selection_step.py` (new). Modifies `src/verselog_installer/__main__.py` (adds the new step to the wizard's step list). Adds `tests/test_component_selection_step.py` (new). No changes to `src/verselog/` (the main app package) at all.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-6.2] — this story's acceptance criterion, verbatim
- [Source: src/verselog/adapters/system/prerequisite_checker.py] — `PrerequisiteChecker.check_missing()`, reused directly, not reimplemented
- [Source: _bmad-output/implementation-artifacts/5-3-prerequisite-check-tesseract-ollama.md] — the "never install automatically" posture this story's "Install Selected" button still respects (opens official installers, doesn't script them)
- [Source: _bmad-output/implementation-artifacts/6-1-installer-wizard-shell-benchmark-step.md] — `BenchmarkStep`'s `.result` shape this story reads from, and the wizard step/DI conventions this story follows

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `166 passed` (158 from Story 6.1's baseline + 8 new).
- Real gap discovered mid-story: `src/verselog_installer/__main__.py` didn't exist despite Story 6.1 claiming it did. Confirmed via a plain `find`/`ls` check before touching anything else. Created it as part of this story's Task 3.
- Code review fix required a regression test that calls `build()` twice on the same step — this reliably triggered the known Tk()-creation flake (7 separate `tk.Tk()` roots in one file). Fixed *for this file* by refactoring to a shared, module-scoped `root` pytest fixture instead of one `tk.Tk()` per test — confirmed clean across 3 consecutive runs afterward. The same flake still occurs at the full-suite level (other, unrelated Tkinter test files each create their own roots too) — tracked as new Story 6.4 rather than fixed project-wide as a drive-by change in this story.

### Completion Notes List

- Implemented all 4 tasks: a checkbox-driven component-selection step, tier-aware pre-checking, an "Install Selected" action that opens official installers/downloads (never scripts a silent install), and wiring into a `__main__.py` that — as a real, transparently-corrected finding — had to be created from scratch rather than modified, since it never actually existed from Story 6.1.
- Retroactively corrected Story 6.1's own file to flag this gap honestly rather than leave it silently wrong.
- **Code review fix:** navigating Back then Next to this step silently discarded the player's own manual checkbox choices, reverting to the tier-based defaults every time `build()` ran. Fixed by preserving `_check_vars` across rebuilds — only a genuinely new missing item gets a fresh default. Regression test added.
- New Story 6.4 added to the backlog: a proper, project-wide fix for the recurring Tk()-creation test flake (observed independently in Stories 6.1 and 6.2, on different test files each time) — this story only fixed its own new test file locally.
- 166/166 tests passing.

### File List

- `src/verselog_installer/steps/component_selection_step.py` (new)
- `src/verselog_installer/__main__.py` (new — retroactive fix for a Story 6.1 gap, plus wiring the new step)
- `tests/test_component_selection_step.py` (new)
- `tests/test_installer_main.py` (new)
- `_bmad-output/implementation-artifacts/6-1-installer-wizard-shell-benchmark-step.md` (modified — correction note about the missing `__main__.py`)

## Change Log

- 2026-07-13: Story implemented — `ComponentSelectionStep` (tier-aware pre-checking, "Install Selected" opening official installers/downloads), and `src/verselog_installer/__main__.py` created for real (discovered it never existed from Story 6.1, corrected that story's record). 166/166 tests passing, status moved to review.
