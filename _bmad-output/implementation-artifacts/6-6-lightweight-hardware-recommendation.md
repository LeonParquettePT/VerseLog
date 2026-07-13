---
baseline_commit: f3fcf16
---

# Story 6.6: Lightweight, Prerequisite-Independent Hardware Recommendation for the Installer

Status: review

## Story

As a player running the guided installer on a genuinely fresh machine,
I want the installer's hardware check to recommend a tier without depending on prerequisites that aren't installed yet,
so that the recommendation isn't accidentally corrupted by measuring how fast a missing program fails, and so the installer itself doesn't need to bundle the app's full capture stack just to make a rough suggestion.

## Acceptance Criteria

1. **Given** the installer's benchmark step (Story 6.1) currently reuses the real, timing-based `Benchmark` class with real `OCRProvider`/`VisionProvider` candidates, but runs *before* the component-selection step (6.2) that actually installs Tesseract/Ollama, **when** the wizard reaches its hardware-check step on a machine where neither prerequisite is installed yet, **then** the recommendation is based on the machine's hardware (CPU core count, total RAM) via a simple, injectable heuristic, not by running the real (currently-uninstalled) OCR/vision pipeline and timing how fast each one fails, **and** this step no longer persists a `benchmark_*` result into `SettingsStore` — `verselog.exe`'s own real, timing-based `Benchmark` (Story 1.6, already re-run on first launch whenever nothing was ever stored) remains the sole source of truth for the actual runtime tier, **and** the installer's PyInstaller build (Story 6.5) no longer needs to bundle `pytesseract`/`Pillow`/`ollama`/`mss`. [Source: epics.md#Story-6.6]

## Tasks / Subtasks

- [x] Task 1: Add a lightweight, dependency-free hardware estimate (AC: #1)
  - [x] `src/verselog_installer/hardware_estimate.py`: `total_ram_bytes()` (Windows `GlobalMemoryStatusEx` via `ctypes` — no new pip dependency, matching Story 6.3's own precedent of avoiding `pywin32` for a single OS call) and `recommend_tier(total_ram_bytes: int, cpu_count: int) -> str`, a pure, injectable-by-argument function so it's trivially unit-testable without touching the real OS.
  - [x] Threshold: `>= 8 GiB` RAM recommends `"vision"` (matches this project's own confirmed finding that the vision tier needs real headroom — a 4 GB VM works until the model is actually loaded, then doesn't; see Story 5.7's Dev Notes), otherwise `"ocr"`. `cpu_count` is accepted for the interface's sake and to leave room for a future refinement, but is not yet part of the threshold logic — stated plainly, not silently ignored.
- [x] Task 2: Replace the installer's `BenchmarkStep` internals (AC: #1)
  - [x] `src/verselog_installer/steps/benchmark_step.py`: removed the `Benchmark`/`OCRProvider`/`VisionProvider`/`CapturePort` imports entirely. `on_shown()` now calls `hardware_estimate.total_ram_bytes()` and `os.cpu_count()`, feeds them to `recommend_tier()`, and stores the tier name on `self.result` (a small local `HardwareEstimateResult` dataclass exposing just `.tier_name`, matching the only attribute `ComponentSelectionStep` actually reads).
  - [x] No `SettingsStore` interaction at all in this step anymore — `verselog.exe`'s own `Benchmark.should_rerun()` already returns `True` whenever nothing was ever stored (the `_NEVER_STORED` sentinel path), so removing this step's persistence simply means the real app always performs its own real, timed benchmark on first launch, exactly as if no installer had run at all.
- [x] Task 3: Tests (AC: #1)
  - [x] `tests/test_hardware_estimate.py` (new): `recommend_tier()` covers the `>= 8 GiB` boundary both ways (4 cases: comfortably above, comfortably below, exactly at the threshold, one byte below).
  - [x] `tests/test_benchmark_step.py`: rewritten for the new behavior — injects a fake RAM/cpu-count reader, asserts the label shows the recommended tier, asserts no `_settings_store` attribute exists on the step at all, asserts re-entering the step (Back then Next) doesn't recompute (same caching behavior as before, just backed by the new estimate).
  - [x] Confirmed `tests/test_component_selection_step.py` needed no changes — it already fakes `benchmark_step` with a bare `.result.tier_name`, decoupled from `BenchmarkStep`'s internals.
- [x] Task 4: Rebuild and confirm the size drop (AC: #1)
  - [x] First rebuild (Task 1-2 alone): 27.8 MB → 27.83 MB, essentially unchanged. Traced why: `ComponentSelectionStep`'s `PrerequisiteChecker` (Story 5.3, unmodified so far) independently imports `pytesseract`/`ollama` to detect installed prerequisites — a real, separate, and until-now-unnoticed source of the same weight, not fixed by this task alone. See Task 5.
  - [x] After Task 5's `PrerequisiteChecker` rewrite: rebuilt again, `dist/verselog-installer.exe` dropped from 27.8 MB to **11.76 MB** (57% smaller). Confirmed via string search in the built binary: `pytesseract`/`ollama`/`pydantic`/`httpx`/`PIL` all now show 0 occurrences (previously non-zero); `mss` shows 2 residual, incidental string matches with no corresponding import anywhere in `verselog_installer`'s own source.
- [x] Task 5: Remove `PrerequisiteChecker`'s unnecessary heavy dependencies (AC: #1, discovered mid-story)
  - [x] `src/verselog/core/vision_model.py` (new): `DEFAULT_VISION_MODEL` moved here from `vision_provider.py` (which now imports it from this new shared, dependency-free location) so `PrerequisiteChecker` doesn't need to import the whole `vision_provider` module (and its `ollama`/screenshot/`mss` chain) just for one string constant.
  - [x] `src/verselog/adapters/system/prerequisite_checker.py`: rewritten to check Tesseract via a direct `subprocess.run(["tesseract", "--version"], ...)` call instead of importing `pytesseract`, and Ollama via a raw `urllib.request` GET against `/api/tags` instead of importing the `ollama` client — both confirmed to answer the exact same question the original code asked (verified the real Ollama API's JSON shape directly against this machine's own running Ollama instance: `{"models": [{"name": ..., "model": ..., ...}]}`). Deliberately plain HTTP, not HTTPS: Ollama's local API has no TLS listener (`http://localhost:11434`), and the request never leaves the machine.
  - [x] `tests/test_prerequisite_checker.py`: rewritten to monkeypatch `subprocess.run`/`urllib.request.urlopen` instead of the (now-removed) `pytesseract`/`ollama` module attributes; same test coverage (both available, Tesseract missing two ways, Ollama unreachable, both missing, vision model not yet pulled).
- [ ] Task 6: Re-publish the updated installer (AC: #1)
  - [ ] Re-publish the updated `verselog-installer.exe` to the existing `v0.1.0-windows` GitHub Release (replacing Story 6.5's asset), done after this PR merges to main (same "tag the merged state" precedent as Stories 5.1/6.5).

## Dev Notes

- **How this was found:** the project's own author asked why `verselog-installer.exe` (~27.8 MB) was nearly as heavy as `verselog.exe` (~29.3 MB) despite the installer being a small Tkinter wizard. Tracing it: `BenchmarkStep` (Story 6.1) imports `OCRProvider`/`VisionProvider` to reuse the real `Benchmark` class, and those adapters import `pytesseract`, `Pillow`, `ollama`, `mss` — PyInstaller's static analysis bundles whatever a program's imports reach, so nearly the app's entire capture stack ends up inside the installer too.
- **The deeper bug this surfaced, not just a size problem:** the installer's wizard order is Welcome → Benchmark → Component Selection → Finish — i.e., the benchmark step runs *before* Tesseract/Ollama are installed. `OCRProvider`/`VisionProvider` both catch their respective "not installed"/"unreachable" errors gracefully (no crash), but that means on a genuinely fresh machine, timing them measures *how fast they fail*, not real performance — a fast failure looks like a fast, capable tier and could get recommended, which is backwards. This was a real, previously-unnoticed correctness bug in Story 6.1, not something invented for this story.
- **Why not persist this installer-time guess into `SettingsStore` at all:** doing so would risk `verselog.exe`'s own `Benchmark.should_rerun()` (Story 1.6) seeing a `benchmark_cpu_count` already stored and matching the real machine, and skipping its own real, timed benchmark on first launch — locking in the installer's rough guess indefinitely (until the CPU core count itself changes). Leaving `SettingsStore` untouched means the real app *always* performs its own proper benchmark the first time it actually runs, which is both simpler and strictly more correct — confirmed with the project's own author, who specifically wanted the real app to retain the ability to "upgrade or downgrade" the recommendation for real, not have it pre-decided by a rough installer-time guess.
- **Why `ctypes` + `GlobalMemoryStatusEx`, not a new dependency (e.g. `psutil`):** matches Story 6.3's own precedent (PowerShell COM automation instead of `pywin32`) of reaching for a Windows-native mechanism over a new pip dependency for a single, narrow OS query — especially valuable here since avoiding a new dependency is the entire point of this story.
- **`cpu_count` accepted but not yet used in the threshold:** stated honestly in Task 1 rather than silently dropped — RAM is the dominant, already-confirmed constraint for the vision tier (Story 5.7's own finding), and adding a CPU-based refinement without a concrete confirmed threshold would be inventing a number rather than reusing a known one.
- **Coding style:** plain, direct code, matching the existing step-based patterns from Stories 6.1/6.2/6.3. [Source: CONTRIBUTING.md#Ground-rules]
- **Task 5 discovered mid-story, not planned upfront:** the first rebuild after Tasks 1-2 barely moved the needle (27.8 → 27.83 MB), which surfaced that `ComponentSelectionStep`'s `PrerequisiteChecker` (Story 5.3) independently imports `pytesseract`/`ollama` for its own legitimate reason (detecting whether Tesseract/Ollama are already installed) — a real, separate source of the exact same weight, unrelated to the benchmark step this story originally targeted. Fixing it required touching `src/verselog/` (shared app code), which the AC as originally written didn't anticipate — confirmed with the project's own author (who raised the size question in the first place) before proceeding.
- **`verselog.exe`'s own size is unaffected by Task 5:** it already imports `pytesseract`/`Pillow`/`ollama`/`mss` directly for its real `OCRProvider`/`VisionProvider` capture adapters, regardless of what `PrerequisiteChecker` does — this story only removes a *redundant* second import path that existed solely for the installer's lighter-weight "is it installed" question.
- **Why plain HTTP for the Ollama check, not HTTPS:** Ollama's local API listens on `http://localhost:11434` with no TLS certificate — it's a local-only service that never leaves the machine. HTTPS here would simply fail to connect (no TLS listener to negotiate with), not add any real protection. Raised and clarified directly with the project's own author, who initially suggested HTTPS as a general good practice before confirming this specific case doesn't apply.

### Project Structure Notes

- Adds `src/verselog_installer/hardware_estimate.py` (new), `src/verselog/core/vision_model.py` (new), and `tests/test_hardware_estimate.py` (new). Modifies `src/verselog_installer/steps/benchmark_step.py` (internals replaced), `tests/test_benchmark_step.py` (rewritten), `src/verselog/adapters/system/prerequisite_checker.py` (rewritten to avoid heavy imports), `src/verselog/adapters/capture/vision_provider.py` (now imports `DEFAULT_VISION_MODEL` instead of defining it), and `tests/test_prerequisite_checker.py` (rewritten). No changes to `ComponentSelectionStep`, `FinishStep`, or `verselog/app.py`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-6.6] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/6-1-installer-wizard-shell-benchmark-step.md] — the original `BenchmarkStep` this story replaces the internals of
- [Source: _bmad-output/implementation-artifacts/6-5-package-guided-installer-pyinstaller.md] — the ~27.8 MB build size this story sets out to reduce
- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.7] — the confirmed RAM-hungry-vision-tier finding this story's threshold reuses rather than inventing a new number

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `183 passed` (176 baseline − 1 old benchmark_step test + 3 new benchmark_step tests + 4 hardware_estimate tests + 1 net prerequisite_checker test = 183). Known pre-existing Tk() flake observed twice during this story (`test_component_selection_step.py` once, `test_installer_wizard.py` once), each cleared on immediate retry — same documented environment issue, not caused by this story's changes.
- First `pyinstaller --onefile --windowed` rebuild (Tasks 1-2 only): `dist/verselog-installer.exe` 27,836,776 → 27,830,597 bytes — essentially no change, which is what led to discovering Task 5's real cause.
- Second rebuild (after Task 5): `dist/verselog-installer.exe` → 11,761,993 bytes (11.76 MB), down from 27.8 MB, a 57% reduction. Confirmed via `grep -ac` string search in the built binary: `pytesseract`/`ollama`/`pydantic`/`httpx`/`PIL` all 0 occurrences (previously non-zero, `PIL` had been 89); `mss` shows 2 residual string matches with no corresponding import anywhere in `verselog_installer`'s source (confirmed via `grep -rn "mss" src/verselog_installer/` returning nothing) — almost certainly an incidental string fragment elsewhere in the bundled runtime, not a real bundled `mss` package.
- Verified the real Ollama REST API's JSON response shape directly: queried `http://localhost:11434/api/tags` on this dev machine's own running Ollama instance, confirmed each model entry has both `"name"` and `"model"` keys with identical values — the rewritten `_ollama_models()` reads `"model"`, matching exactly what the original `ollama.list()`-based code read via `model.model`.
- Verified `pytesseract.get_tesseract_version()`'s own real source (via `inspect.getsource`) to confirm the rewritten subprocess-based check replicates the same underlying mechanism (`subprocess` call to `tesseract --version`, `OSError` on a missing binary) rather than guessing at the behavior.

### Completion Notes List

- Fixed the real correctness bug found while investigating the file-size question: the installer's benchmark step no longer times an uninstalled OCR/vision pipeline (which would measure failure speed, not performance) — it now uses a simple, injectable RAM-based heuristic (`>= 8 GiB` → vision, matching Story 5.7's own confirmed RAM finding) and no longer persists anything to `SettingsStore`, leaving `verselog.exe`'s own real, timed benchmark as the sole source of truth on first real launch.
- Fixed the actual file-size cause, discovered mid-story: `PrerequisiteChecker` (Story 5.3, used by `ComponentSelectionStep`) independently imported `pytesseract`/`ollama` for its own legitimate "is it installed" check, pulling in the same heavy dependency chain (`Pillow`, `pydantic`, `httpx`, `anyio`) regardless of the benchmark step's own fix. Rewrote it to use a direct `subprocess` call and a raw `urllib.request` HTTP call instead — same behavior, verified against this machine's real, running Tesseract/Ollama installs, zero new dependencies.
- `verselog-installer.exe`: 27.8 MB → 11.76 MB (57% smaller). `verselog.exe` itself is unaffected — it still needs the full capture stack for its own real OCR/vision work.
- 183/183 tests passing.

### File List

- `src/verselog_installer/hardware_estimate.py` (new)
- `src/verselog_installer/steps/benchmark_step.py` (modified — internals replaced, no more real Benchmark/OCRProvider/VisionProvider/SettingsStore)
- `src/verselog/core/vision_model.py` (new — `DEFAULT_VISION_MODEL`, moved out of `vision_provider.py`)
- `src/verselog/adapters/capture/vision_provider.py` (modified — imports the constant instead of defining it)
- `src/verselog/adapters/system/prerequisite_checker.py` (modified — subprocess/urllib instead of pytesseract/ollama client libraries)
- `tests/test_hardware_estimate.py` (new)
- `tests/test_benchmark_step.py` (rewritten)
- `tests/test_prerequisite_checker.py` (rewritten)

## Change Log

- 2026-07-13: Story created — directly from the project's own author noticing `verselog-installer.exe`'s file size was suspiciously close to `verselog.exe`'s, tracing that to both a real size problem and a previously-unnoticed correctness bug (benchmarking uninstalled prerequisites measures failure speed, not performance).
- 2026-07-13: Tasks 1-4 done — lightweight hardware-based recommendation replaces the real timing-based benchmark in the installer. First rebuild showed almost no size change, tracing that to `PrerequisiteChecker`'s own separate heavy imports (Task 5, added mid-story after confirming with the user). After Task 5: `verselog-installer.exe` 27.8 MB → 11.76 MB. 183/183 tests passing, status moved to review.
