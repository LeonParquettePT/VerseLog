---
baseline_commit: 932c912
---

# Story 5.3: Prerequisite Check for Tesseract/Ollama

Status: review

## Story

As a player installing VerseLog for the first time,
I want to know clearly if Tesseract or Ollama are missing,
so that I'm not left guessing why a scan silently fails.

## Acceptance Criteria

1. **Given** VerseLog launches, **when** Tesseract and/or Ollama are not detected on the system, **then** the player is told plainly which prerequisite is missing, with a link to install it, **and** nothing is installed automatically without the player's explicit action — consistent with this project's existing "never act without explicit confirmation" posture (see Story 3.2/4.3's legality-confirmation precedent). [Source: epics.md#Story-5.3]

**Extended mid-story (2026-07-13), same AC's spirit:** real manual testing of the packaged Linux build on a fresh Ubuntu VM hit exactly the scenario this story exists to prevent — Ollama installed and reachable, but its vision model not yet pulled, surfacing as a confusing "status code 404" deep inside `VisionProvider` instead of a plain explanation. The check now also detects "Ollama reachable but vision model missing" as its own distinct, correctly-worded case (not lumped in with "Ollama not installed at all").

## Tasks / Subtasks

- [x] Task 1: Detect whether Tesseract/Ollama are present, without installing anything (AC: #1)
  - [x] Added `src/verselog/core/missing_prerequisite.py`: a plain `MissingPrerequisite` dataclass (`name: str`, `install_url: str`).
  - [x] Added `src/verselog/adapters/system/prerequisite_checker.py` (new `adapters/system/` package, `__init__.py` matching the existing empty-file convention): `PrerequisiteChecker.check_missing(self) -> list[MissingPrerequisite]`. Tesseract via `pytesseract.get_tesseract_version()`, Ollama via `ollama.list()`, both wrapped in broad `except Exception`.
- [x] Task 2: Add a `warn_missing_prerequisites` method to `UIPort` and implement it in both adapters (AC: #1)
  - [x] Added `warn_missing_prerequisites(self, missing: list[MissingPrerequisite]) -> None` as a new abstract method on `UIPort`.
  - [x] `ConsoleUIProvider.warn_missing_prerequisites`: prints each missing prerequisite's name and install URL; prints nothing for an empty list.
  - [x] `TkinterUIProvider.warn_missing_prerequisites`: `messagebox.showwarning` listing each missing prerequisite and its install URL as plain text; returns immediately without opening any dialog when `missing` is empty.
- [x] Task 3: Wire the check into `app.run()` (AC: #1)
  - [x] Added `prerequisite_checker: PrerequisiteChecker | None = None` to `run()`'s parameters, defaulting to a real `PrerequisiteChecker()` when not given.
  - [x] `ui.warn_missing_prerequisites(prerequisite_checker.check_missing())` is called once, right after `ui` and `prerequisite_checker` are resolved, before the ship-selection/capture logic.
  - [x] Confirmed via test (`test_run_warns_about_missing_prerequisites_but_still_completes_the_scan`) that this never blocks — the scan completes and results are still shown even with a missing prerequisite reported.
- [x] Task 4: Tests (AC: #1)
  - [x] `tests/test_prerequisite_checker.py` (new): empty-missing when both succeed; Tesseract/Ollama/both reported missing when their respective calls raise.
  - [x] `tests/test_console_ui_provider.py`: prints each missing item's name/URL; prints nothing for an empty list.
  - [x] `tests/test_tkinter_ui_provider.py`: `messagebox.showwarning` called with each missing item's name/URL; NOT called for an empty list.
  - [x] `tests/test_app.py`: `run()` with a stub reporting one missing prerequisite — `warn_missing_prerequisites` called, scan still completes. A second test confirms `warn_missing_prerequisites` is still called (with `[]`) when nothing is missing.
  - [x] **Retrofit required and done:** every pre-existing `run()` call site in `tests/test_app.py` and `tests/test_app_legality.py` (8 in the former, 1 shared helper in the latter) now explicitly injects a stub `prerequisite_checker` returning `[]` — without this, they would have silently started performing real Tesseract/Ollama I/O against the actual host machine on every test run (the same class of problem `capture_port` is always faked for), which is slow, non-deterministic, and would behave differently in CI (no Tesseract/Ollama) versus this machine (both installed). Not scope creep — leaving pre-existing tests hitting real I/O would have been a real regression in test hygiene introduced by this story's own new default.
- [x] Task 5 (added mid-story, real finding from manual Linux VM testing): distinguish "Ollama not reachable at all" from "Ollama reachable but the vision model isn't pulled" (AC extension above)
  - [x] Extracted `DEFAULT_VISION_MODEL = "qwen2.5vl:3b"` as a module-level constant in `vision_provider.py` (was a bare default-parameter literal) so `PrerequisiteChecker` can reference the exact same model name rather than duplicating the string in two files.
  - [x] `PrerequisiteChecker.check_missing()` now calls `ollama.list()` once, extracts the set of installed model names from the response's `.models[].model` shape (confirmed via direct introspection: `ollama.ListResponse.Model.model_fields` shows a `model: str` field), and reports a distinct `MissingPrerequisite` (`"Ollama vision model (qwen2.5vl:3b)"`, instructions `"ollama pull qwen2.5vl:3b"`) when Ollama is reachable but the model isn't in that set — separate from the "Ollama isn't installed/reachable at all" case, since the fix is completely different (a pull command vs. installing the whole program).
  - [x] Also renamed `MissingPrerequisite.install_url` → `install_instructions` across the dataclass, both adapters, `PrerequisiteChecker`, and all touched tests — a pull command isn't a URL, and the field needs to hold either.
  - [x] New test (`test_check_missing_reports_the_vision_model_when_ollama_is_reachable_but_the_model_isnt_pulled`) reproduces the exact scenario hit during real testing.

## Dev Notes

- **Why detection lives in `adapters/`, not `core/`:** `PrerequisiteChecker` performs real I/O against the host machine (subprocess-launching `tesseract --version` under the hood via `pytesseract`, and an HTTP call to Ollama's local API) — exactly the same class of "real external interaction" that `VisionProvider`/`OCRProvider` already encapsulate as adapters. `core/` stays free of that per AD-1 (Ports & Adapters); only the resulting `MissingPrerequisite` data shape is shared into `core/`.
- **Why this is a warning, not a gate:** the AC doesn't ask VerseLog to refuse to run — it asks for the player to be told plainly instead of being left guessing why a scan silently fails. The existing capture pipeline (`VisionProvider`/`OCRProvider`) already degrades gracefully to quarantine when a provider is unavailable (Story 1.2/1.5's own error handling) — this story only adds an upfront, plain-language explanation of *why* that might happen, it does not change what happens if the player proceeds anyway.
- **Why nothing is installed automatically:** explicitly rejected during Story 5.1's own discussion (see epics.md's "Added 2026-07-10" note on this story) — silently installing third-party prerequisites would carry the same elevation/reliability risk the project's own WSL install attempt demonstrated firsthand this session, just hidden a level deeper inside VerseLog itself. This story only detects and informs; it never invokes an installer.
- **Reusing pytesseract's already-imported exception surface:** `ocr_provider.py` already imports and handles `pytesseract.TesseractNotFoundError` — this story doesn't need to import that specific exception type itself since it catches broadly, but it confirms `pytesseract.get_tesseract_version()` is the right call (same library already a hard dependency, no new package needed).
- **`ollama.list()` confirmed present on the installed `ollama` package** (verified directly: `dir(ollama)` includes `list`, `chat`, `ResponseError`, `RequestError`, etc. — this project already depends on `ollama>=0.4` for `VisionProvider`, no new dependency needed).
- **Coding style:** plain, direct code — one small new adapter class, one new dataclass, one new port method implemented twice. No new abstractions beyond what AC #1 actually needs. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `src/verselog/core/missing_prerequisite.py` (new), `src/verselog/adapters/system/` (new package) with `prerequisite_checker.py` and an `__init__.py` (matching the existing `adapters/capture/`, `adapters/ui/` package structure — check whether existing adapter packages use an `__init__.py` or rely on implicit namespace packages before creating one, to stay consistent). Modifies `src/verselog/core/ports/ui_port.py`, `src/verselog/adapters/ui/console_ui_provider.py`, `src/verselog/adapters/ui/tkinter_ui_provider.py`, `src/verselog/app.py`. Adds one new test file (`tests/test_prerequisite_checker.py`), extends three existing ones.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.3] — this story's acceptance criterion, verbatim, including the "Added 2026-07-10" note explaining why automatic installation was explicitly rejected
- [Source: src/verselog/adapters/capture/vision_provider.py] — the broad `except Exception` pattern for "Ollama unreachable, model missing, malformed JSON, etc." this story's Ollama check mirrors
- [Source: src/verselog/adapters/capture/ocr_provider.py] — confirms `pytesseract.TesseractNotFoundError` is the exception a missing Tesseract binary raises, and that `pytesseract` is already a hard dependency
- [Source: _bmad-output/implementation-artifacts/5-5-ship-selection-via-results-ui.md] — the most recently completed `UIPort` extension (`select_ship`) this story's `warn_missing_prerequisites` follows the same "new abstract method, implement in both adapters" shape as
- Verified directly (2026-07-13): `dir(ollama)` on the installed package confirms `list`, `chat`, `ResponseError`, `RequestError` are present — no version bump needed

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `139 passed in 4.89s` (114 from Story 5.2's baseline + 25 new/retrofitted)
- Live confirmation of the exact scenario this story's Task 5 addresses: the project author ran the packaged Linux build on a fresh Ubuntu VM and got "model qwen2.5vl... not found, status code 404" — Ollama installed and running, model not pulled. Reproduced deterministically as a new unit test rather than left as an anecdote.
- `uv run python -c "import ollama; print(ollama.ListResponse.Model.model_fields)"` → confirmed the `.models[].model` shape used by `_ollama_models()`.

### Completion Notes List

- Implemented all 4 originally-scoped tasks plus a 5th added mid-story after real manual testing surfaced a scenario the original scope hadn't covered (Ollama reachable, vision model missing) — extended rather than deferred, since it's squarely within this story's own stated purpose ("so that I'm not left guessing why a scan silently fails").
- Renamed `MissingPrerequisite.install_url` to `install_instructions` since the new vision-model case needed to carry a shell command (`ollama pull ...`), not a URL — done immediately while the field had only two call sites, before more code could depend on the misleading name.
- Extracted `VisionProvider`'s hardcoded model string into a shared `DEFAULT_VISION_MODEL` constant so the checker and the actual capture code can never drift apart on which model name matters.
- Retrofitted 9 pre-existing `run()` call sites across `test_app.py`/`test_app_legality.py` with a stub `prerequisite_checker` to keep tests fast and deterministic (real I/O against Tesseract/Ollama would otherwise run on every test, differing between this dev machine and CI).
- 139/139 tests passing.

### File List

- `src/verselog/core/missing_prerequisite.py` (new)
- `src/verselog/adapters/system/__init__.py` (new, empty)
- `src/verselog/adapters/system/prerequisite_checker.py` (new)
- `src/verselog/adapters/capture/vision_provider.py` (modified — `DEFAULT_VISION_MODEL` constant extracted)
- `src/verselog/core/ports/ui_port.py` (modified — new `warn_missing_prerequisites` abstract method)
- `src/verselog/adapters/ui/console_ui_provider.py` (modified — `warn_missing_prerequisites` implementation)
- `src/verselog/adapters/ui/tkinter_ui_provider.py` (modified — `warn_missing_prerequisites` implementation)
- `src/verselog/app.py` (modified — `prerequisite_checker` parameter, wired in)
- `tests/test_prerequisite_checker.py` (new)
- `tests/test_console_ui_provider.py` (modified — new tests)
- `tests/test_tkinter_ui_provider.py` (modified — new tests)
- `tests/test_app.py` (modified — new tests, retrofitted existing `run()` calls)
- `tests/test_app_legality.py` (modified — retrofitted `_run()` helper and `_SpyUI`)

## Change Log

- 2026-07-13: Story implemented — Tesseract/Ollama/vision-model detection via a new `PrerequisiteChecker` adapter, surfaced through a new `UIPort.warn_missing_prerequisites` method (both adapters), wired into `app.run()` as an upfront warning that never blocks the scan. Extended mid-story after real manual Linux VM testing surfaced the exact "Ollama reachable but model not pulled" scenario this story exists to prevent guessing about. 139/139 tests passing, status moved to review.
