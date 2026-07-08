---
baseline_commit: 65cabd8b47b6410dd326f068812bcbc5127922a7
---

# Story 1.6: Hardware Benchmark (Model Tier + Worker Count)

Status: review

## Story

As a player,
I want the app to pick the right model and parallelism for my machine once,
so that scanning stays fast without me tuning anything.

## Acceptance Criteria

1. **Given** first launch (while the game is running) or a detected hardware change, **when** the benchmark runs, **then** it selects a model tier (Vision → OCR fallback) and a safe worker count N, within the configured time budget. [Source: epics.md#Story-1.6]
2. **And** a "Re-run benchmark" action exists in settings for manual re-trigger. [Source: epics.md#Story-1.6]

## Tasks / Subtasks

- [x] Task 1: Settings persistence (AC: #1, #2)
  - [x] `src/verselog/core/settings_store.py` — `SettingsStore`, a small JSON-file-backed key/value store (`data/settings.json` default path, matching the `data/` runtime-data convention from Story 1.1). `get(key, default=None)` / `set(key, value)`, persists immediately on `set`.
- [x] Task 2: Benchmark routine (AC: #1)
  - [x] `src/verselog/adapters/capture/benchmark.py` — `BenchmarkResult` dataclass (`tier_name: str`, `worker_count: int`, `elapsed_seconds: float`); `Benchmark.run(candidates: list[tuple[str, CapturePort]], time_budget: float) -> BenchmarkResult`
  - [x] Times each candidate's `.capture()` call in the given order (the established fallback chain: Phi-3-Vision → Moondream2 → classic OCR); returns the **first** candidate whose elapsed time fits `time_budget`; if none fit, returns the **last** (lightest) candidate anyway with its actual elapsed time (never leaves the player with no provider at all)
  - [x] Worker count heuristic: `max(1, floor(time_budget / elapsed_seconds))`, capped at `os.cpu_count()` — documented as a starting heuristic, not a precisely-tuned formula (no real-world timing data exists yet to tune it further)
  - [x] Benchmark timing is about **speed only**, not extraction correctness — do not route trial captures through `TrustLayer` (that's a separate concern, already handled by Story 1.3)
- [x] Task 3: Re-run trigger and coarse hardware-change detection (AC: #1, #2)
  - [x] `Benchmark.should_rerun(settings_store: SettingsStore) -> bool`: `True` if no prior benchmark result is stored, or if the stored CPU core count (`os.cpu_count()`) differs from the current one. **Documented limitation**: this only catches a CPU core-count change, not e.g. a GPU swap — a fuller hardware fingerprint is future work, not invented here without real signal to base it on.
  - [x] `Benchmark.run(...)` is itself the "Re-run benchmark" action at the code level — there is no settings UI yet to wire a literal button to (same flagged gap as prior stories); calling `run()` again *is* the manual re-trigger.
  - [x] Persist the result via `SettingsStore`: tier name, worker count, and the CPU core count used for the hardware-change check
- [x] Task 4: Tests (AC: #1, #2)
  - [x] Unit test `Benchmark.run` with fake `CapturePort`s whose `capture()` calls `time.sleep()` for a small, known duration — assert the first candidate within budget is selected, and that a too-slow first candidate correctly falls back to the next
  - [x] Unit test the "never leaves the player with no provider" case: all candidates too slow → last (lightest) candidate still returned
  - [x] Unit test the worker-count heuristic's arithmetic directly
  - [x] Unit test `should_rerun`: no stored result → `True`; same CPU count stored → `False`; different CPU count stored → `True`
  - [x] Unit test `SettingsStore` against a temp-directory JSON file (`tmp_path`), not the real `data/settings.json`

## Dev Notes

- **This story does not detect whether Star Citizen is actually running.** The SPEC/CAP-3 language "while the game is running" describes when a *caller* should invoke the benchmark for a meaningful reading (an idle-PC benchmark reads as artificially more powerful — see `vision-pipeline.md`); detecting the game process itself is a separate, unbuilt capability and out of scope here. This story provides the benchmark mechanism; a future UI/orchestration story is responsible for prompting the player to have the game running before triggering it.
- **AD-8 satisfied together, not separately:** `Benchmark.run` returns tier AND worker count from the same pass, not two independent decisions. [Source: ARCHITECTURE-SPINE.md#AD-8]
- **Settings store is new in this story** — Stories 1.1-1.5 referenced AD-7's "one local settings store" as a binding constraint but none of them needed to build it yet. This is the first story that actually persists something (benchmark results), so it's the right point to add it, not scope creep. [Source: ARCHITECTURE-SPINE.md#AD-7]
- **Worker count heuristic is a documented starting point, not a tuned formula** — no real-world timing data exists yet to calibrate it further; don't present it as more precise than it is.
- **Coarse hardware-change detection, not a full fingerprint** — checking only `os.cpu_count()` is a stdlib-only, honest, limited signal. Don't invent GPU/RAM detection without a concrete need or library choice already established.
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `core/settings_store.py` (new file in `core/`, consistent with AD-7's "settings store owned by domain core") and `adapters/capture/benchmark.py` (new file in `adapters/capture/`, consistent with the Capability → Architecture Map: "CAP-3 ... adapters/capture/ (routine) + core/ (settings)"). [Source: ARCHITECTURE-SPINE.md#Capability-Architecture-Map]

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.6] — this story's acceptance criteria, verbatim
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-7] — settings store ownership
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-8] — benchmark determines tier + worker count together
- [Source: _bmad-output/specs/spec-verselog/vision-pipeline.md] — the established fallback chain (Phi-3-Vision → Moondream2 → classic OCR) and "benchmark while the game is running" rationale
- [Source: _bmad-output/implementation-artifacts/1-5-local-vision-provider-ollama.md] — `VisionProvider`, reused as a benchmark candidate alongside `OCRProvider`

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `30 passed in 0.96s`

### Completion Notes List

- Implemented `SettingsStore` (JSON-file-backed, `data/settings.json` default), the first story to actually persist settings per AD-7.
- Implemented `Benchmark.run`: times ordered candidates, returns the first within budget, falls back to the last (lightest) candidate if none fit — never leaves no provider chosen. Worker-count heuristic documented as a starting point, not tuned.
- Implemented `Benchmark.should_rerun` (coarse CPU-core-count check) and `Benchmark.persist` (writes tier/worker-count/cpu-count to `SettingsStore`).
- Did NOT implement game-process detection or a real settings UI — both explicitly out of scope per Dev Notes; `Benchmark.run()` itself is the manual re-trigger at the code level.
- All acceptance criteria satisfied; 30/30 tests passing (19 pre-existing + 11 new).

### File List

- `src/verselog/core/settings_store.py` (new)
- `src/verselog/adapters/capture/benchmark.py` (new)
- `tests/test_settings_store.py` (new)
- `tests/test_benchmark.py` (new)

## Change Log

- 2026-07-08: Story implemented — SettingsStore and Benchmark added, all tasks complete, 30/30 tests passing, status moved to review.
- 2026-07-08: Code review found and fixed one correctness bug — `should_rerun` used `None` both as the "never stored" sentinel and as a value `os.cpu_count()` can legitimately return, so on a platform where cpu_count is undetermined the benchmark would re-run on every launch instead of once. Fixed with a distinct `_NEVER_STORED` sentinel object; added a regression test with `os.cpu_count` monkeypatched to `None`. 31/31 tests passing.
