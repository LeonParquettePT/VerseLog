---
baseline_commit: d9a1b00e118b8622cb022c700f27a7685fc3905c
---

# Story 4.1: Application Entrypoint (Wiring)

Status: review

## Story

As a player,
I want to launch VerseLog as one application,
so that triggering a scan runs the whole pipeline instead of me wiring the pieces together myself.

## Acceptance Criteria

1. **Given** the application is launched, **when** a manual trigger fires, **then** capture runs through the model tier Story 1.6's benchmark selected, the result passes through the trust layer, and a validated contract's route/loading plan is computed and handed to the UI, **and** none of these steps requires the player to invoke it manually or run any code themselves. [Source: epics.md#Story-4.1]

## Tasks / Subtasks

- [x] Task 1: Define a `ScanResult` shape that carries everything the UI needs from one scan (AC: #1)
  - [x] `src/verselog/core/scan_result.py` — `ScanResult` dataclass: `contract: Contract | None`, `route_cost: RouteCost | None`, `loading_plan: LoadingPlan | None`, `quarantine_reasons: list[str] = field(default_factory=list)`. `contract is None` + non-empty `quarantine_reasons` means "nothing trustworthy this scan"; a populated `contract` means the happy path. This is a new shape — `UIPort.show_results` has never had a real caller or implementation, so redefining what it accepts is free (see Dev Notes).
- [x] Task 2: Update `UIPort.show_results` to the new shape (AC: #1)
  - [x] `src/verselog/core/ports/ui_port.py` — change `show_results(self, contracts: list[Contract]) -> None` to `show_results(self, results: list[ScanResult]) -> None`. No concrete `UIPort` implementation exists yet (Story 4.2 is the first), so this has zero callers/implementers to break.
- [x] Task 3: Implement `ConsoleUIProvider` — a real, working `UIPort` for this story (AC: #1)
  - [x] `src/verselog/adapters/ui/console_ui_provider.py` — `ConsoleUIProvider(UIPort)`. `show_results(results)` prints each `ScanResult` plainly (contract fields, route cost, loading steps, or the quarantine reasons if `contract is None`). `confirm_risky_contract(contract, risk)` prints the risk's `reason` and prompts via `input("Proceed anyway? [y/N]: ")`, returning `True` only for an explicit `y`/`yes` (case-insensitive) answer — never defaults to proceeding.
  - [x] This is not a placeholder to be deleted later — it's a legitimate, minimal `UIPort` adapter (console output), which Story 4.2 supplements with a Tkinter one. Ports & Adapters means both can coexist; the entrypoint just needs to construct one.
- [x] Task 4: Implement the wiring function (AC: #1)
  - [x] `src/verselog/app.py` — `run(ship_name: str) -> None`:
    1. Construct `SettingsStore()`, `ShipReferenceStore()`, `LocationReferenceStore()` (all default paths under `data/`).
    2. Construct `RouteCostCalculator(location_store, ship_store)` and `LoadingPlanCalculator(route_cost_calculator)`.
    3. Construct benchmark candidates `[("vision", VisionProvider()), ("ocr", OCRProvider())]` (vision first — it's the more precise tier per the established `Vision → OCR` fallback ordering).
    4. `benchmark = Benchmark()`. If `benchmark.should_rerun(settings_store)`: run `benchmark.run(candidates, time_budget=30.0)` and `benchmark.persist(result, settings_store)`. Otherwise read the persisted `benchmark_tier_name` directly from `settings_store`.
    5. Pick the `CapturePort` whose candidate name matches the tier name; if it doesn't match either candidate (corrupted/unexpected settings value), fall back to `"ocr"` — the always-available floor tier.
    6. Construct `ManualTriggerAdapter(selected_capture_port)` and `TrustLayer()`.
    7. `capture_result = trigger.on_triggered()`; `trust_result = trust_layer.process(capture_result)`.
    8. If `trust_result.contract is None`: build `ScanResult(contract=None, route_cost=None, loading_plan=None, quarantine_reasons=trust_result.reasons)`.
    9. Otherwise, try `route_cost_calculator.calculate(...)` and `loading_plan_calculator.derive(...)` for the validated contract and `ship_name`; on a `ValueError` (unknown location/ship/capacity — see Story 2.2/2.3), still build a `ScanResult` with `contract` set and `route_cost`/`loading_plan` left `None`, so the player at least sees what was extracted instead of the whole scan silently vanishing.
    10. Call `ConsoleUIProvider().show_results([scan_result])`.
  - [x] `src/verselog/__main__.py` — a thin CLI: `argparse` with a required `--ship` argument (the ship name to compute route/loading cost for) and an `--import-reference-data` flag that, when passed, runs `CommunityAPIProvider(ship_store).refresh()` and `LocationDataProvider(location_store).refresh()` then exits — the one-time bootstrap Story 2.1's AC assumed but nothing before this story actually triggers. Without reference data imported first, `RouteCostCalculator` will raise a clear "unknown ship/location" `ValueError`, which is an acceptable, actionable failure mode for a fresh install — do not silently auto-import inside `run()` (that would make every scan attempt a network call).
- [x] Task 5: Tests (AC: #1)
  - [x] Unit test `ConsoleUIProvider.show_results` with a fake `ScanResult` (happy path) and a quarantined one (`contract=None`) — capture stdout, assert the right information appears in each case
  - [x] Unit test `ConsoleUIProvider.confirm_risky_contract` with monkeypatched `input()` returning `"y"`, `"n"`, `""`, and `"YES"` — assert only `y`/`yes` (any case) returns `True`
  - [x] Unit test `app.run()` end-to-end with every collaborator faked/injected (a fake `CapturePort` returning a known-good `CaptureResult`, pre-seeded `ShipReferenceStore`/`LocationReferenceStore` via `tmp_path`, a spy `UIPort` capturing what it was called with) — assert the spy received a `ScanResult` with the correct `contract`, `route_cost`, and `loading_plan`
  - [x] Unit test `app.run()`'s quarantine path: a fake `CapturePort` returning a `CaptureResult` with an invalid contract (e.g. non-positive SCU) — assert the spy `UIPort` received a `ScanResult(contract=None, ...)` with the trust layer's quarantine reasons
  - [x] Unit test the benchmark tier selection: monkeypatch `Benchmark.should_rerun` to `False` and pre-seed `settings_store` with `benchmark_tier_name="ocr"` — assert `run()` uses the OCR candidate, not vision (proves the persisted-tier path works, not just the first-run benchmark path)
  - [x] Do NOT attempt to unit test `__main__.py`'s argparse wiring against a real terminal invocation — same documented limitation pattern as `OCRProvider`/`VisionProvider`'s live-capture paths (Stories 1.2/1.5): exercise `app.run()` directly with fakes, treat the CLI shim as a thin, manually-verified pass-through

## Dev Notes

- **Why changing `UIPort.show_results`'s signature is safe:** `grep -rn "UIPort" src/` (done during story creation) confirms `core/ports/ui_port.py` is the *only* file referencing it — no concrete adapter, no test, no other caller exists anywhere in the codebase. Redefining its parameter shape here has zero regression surface. [Source: src/verselog/core/ports/ui_port.py]
- **Why batch/parallel scanning and voice triggering are explicitly out of this story**, even though `BatchScanner` (Story 1.7) and `VoiceTriggerAdapter` (Story 1.4) already exist: `BatchScanner.scan_all()` needs a *list* of `CapturePort`s, one per contract to scan — and Story 1.7's own Dev Notes state plainly that "how ~30 distinct contract screenshots actually get produced (e.g. scrolling through the in-game list)" was left unsolved and flagged as a future/UI concern, explicitly to avoid inventing unverified scrolling/UI automation that could brush against SPEC.md's no-input-injection non-goal. Nothing has been built since to source that list, so wiring `BatchScanner` into the entrypoint now would mean inventing that missing piece — out of scope for this story. Voice triggering needs a real VoiceAttack-side integration this story isn't building; manual triggering alone already satisfies NFR4 ("manual triggering always available"). [Source: _bmad-output/implementation-artifacts/1-7-batch-scanning-parallel-workers.md#Dev-Notes]
- **Benchmark tier caching, not re-running every launch:** Story 1.6's own intent is "runs ONCE at first launch/installation... NOT on every subsequent app or game launch." `Benchmark.should_rerun(settings_store)` already encodes exactly this check (compares stored vs. current CPU count) — use it, don't call `benchmark.run()` unconditionally on every `app.run()` call. [Source: _bmad-output/implementation-artifacts/1-6-hardware-benchmark-model-tier-and-worker-count.md]
- **Reference-data bootstrap is an explicit, separate action, not an implicit side effect of scanning.** `CommunityAPIProvider.refresh()`/`LocationDataProvider.refresh()` both make real network calls (confirmed Story 2.1/2.2) — triggering them silently inside `run()` would turn every single scan attempt into an unwanted network round-trip. Exposing `--import-reference-data` as its own explicit CLI action keeps `run()`'s hot path free of that cost, consistent with NFR1/NFR2 (avoid unnecessary overhead, stay within the time budget). [Source: _bmad-output/implementation-artifacts/2-1-reference-data-import-local-sqlite.md, 2-2-point-to-point-route-cost-calculation.md]
- **`RouteCostCalculator`/`LoadingPlanCalculator` already raise clear `ValueError`s** for an unknown ship/location/capacity mismatch (Stories 2.2/2.3) — `run()` must catch exactly that and still show the extracted `Contract` (better than the whole scan vanishing), not swallow it silently or let it crash the app. [Source: _bmad-output/implementation-artifacts/2-2-point-to-point-route-cost-calculation.md, 2-3-loading-plan-derived-from-single-missions-route.md]
- **`FuelOverrideStore`/`ReputationStore`/`LegalityChecker` are intentionally NOT wired here** — `RouteCostCalculator`'s optional `fuel_override_store` param can stay `None` (falls back to the default formula, Story 2.5's whole point), and legality-risk confirmation is Story 4.3's job once `UIPort.confirm_risky_contract` has something real to call it from. Don't pull those in now; keep this story's surface to exactly what AC #1 asks for.
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `core/scan_result.py`, `app.py` (project root of the package, alongside `core/`/`adapters/` — the natural home for the wiring entrypoint per the Structural Seed), `__main__.py` (enables `python -m verselog`), and `adapters/ui/console_ui_provider.py` (first file in the previously-empty `adapters/ui/` package). Modifies `core/ports/ui_port.py`'s `show_results` signature additively (no other change to the file).

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.1] — this story's acceptance criterion, verbatim, including the 2026-07-09 scope note
- [Source: _bmad-output/implementation-artifacts/1-7-batch-scanning-parallel-workers.md] — the already-documented "sourcing distinct contract screenshots" gap this story does not attempt to close
- [Source: _bmad-output/implementation-artifacts/1-6-hardware-benchmark-model-tier-and-worker-count.md] — `Benchmark.run`/`should_rerun`/`persist`, reused as-is; the "once, not every launch" intent
- [Source: _bmad-output/implementation-artifacts/2-2-point-to-point-route-cost-calculation.md] — `RouteCostCalculator`, its `ValueError` cases this story must handle gracefully
- [Source: _bmad-output/implementation-artifacts/2-3-loading-plan-derived-from-single-missions-route.md] — `LoadingPlanCalculator`, composed the same way
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-1] — Ports & Adapters; `ConsoleUIProvider` and a future Tkinter adapter coexisting behind `UIPort` is exactly what this enables

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `99 passed in 3.05s`
- `uv run python -m verselog --help` → clean argparse usage output (real CLI smoke test, not just unit tests)
- `uv run python -m verselog` (no args) → `error: --ship is required unless --import-reference-data is passed`, exit code 2 (verified the actual error path, not just its test)

### Completion Notes List

- Implemented `ScanResult` (`core/scan_result.py`) and updated `UIPort.show_results` to the new shape — confirmed via `grep -rn "UIPort" src/` that no concrete adapter or caller existed anywhere, so the signature change was free.
- Implemented `ConsoleUIProvider` (`adapters/ui/console_ui_provider.py`) as a real, working `UIPort` — not a placeholder. `confirm_risky_contract` only returns `True` on an explicit `y`/`yes` answer.
- Implemented `app.run()` (`src/verselog/app.py`) wiring manual trigger → capture (tier selected via `Benchmark`, cached in `SettingsStore`) → trust layer → route/loading calculation → `UIPort`. Deviated from the story's literal `run(ship_name: str) -> None` signature by adding optional keyword-only dependencies (`capture_port`, `settings_store`, `ship_store`, `location_store`, `trust_layer`, `ui`, all defaulting to real construction when omitted) — necessary for the tests to inject fakes/tmp_path-backed stores without touching the real `data/` paths, and consistent with the dependency-injection pattern used everywhere else in this codebase (e.g. `http_get` on the datasource providers).
- Found and fixed my own bug during implementation before it ever hit a test: `LoadingPlanCalculator.derive()` returns a `LoadingPlan` directly, not a wrapper with a `.loading_plan` attribute (that shape belongs to `CombinedRoutePlanner.plan()`'s `CombinedPlan` instead) — corrected before writing the test that would have caught it anyway.
- Implemented `__main__.py`: `--ship` (required unless `--import-reference-data` is passed) and `--import-reference-data` (runs both bulk-import providers' `.refresh()`, then exits) — the one-time bootstrap Story 2.1 assumed but nothing before this story actually triggered.
- Real smoke-tested the CLI directly (not just unit tests): `python -m verselog --help` and the missing-`--ship` error path both produce clean, correct output.
- All acceptance criteria satisfied; 100/100 tests passing (92 pre-existing + 8 new, including the partial-success regression test added during code review).

### File List

- `src/verselog/core/scan_result.py` (new)
- `src/verselog/core/ports/ui_port.py` (modified — `show_results` now takes `list[ScanResult]`)
- `src/verselog/adapters/ui/console_ui_provider.py` (new)
- `src/verselog/app.py` (new)
- `src/verselog/__main__.py` (new)
- `tests/test_console_ui_provider.py` (new)
- `tests/test_app.py` (new)

## Change Log

- 2026-07-09: Story implemented — `ScanResult`, updated `UIPort`, `ConsoleUIProvider`, and the `app.run()`/`__main__.py` entrypoint added, wiring manual trigger → capture → trust layer → route/loading calculation → UI for the first time. All tasks complete, 99/99 tests passing, status moved to review.
- 2026-07-09: Code review (self-caught while reading the diff, confirmed by an independent verification agent) found a real bug: if `route_cost_calculator.calculate()` succeeded but the subsequent `loading_plan_calculator.derive()` failed (e.g. cargo capacity exceeded — a check `derive()` does in addition to re-validating the route), the shared `except ValueError` block reset the already-computed `route_cost` back to `None`, discarding a legitimately available result. Fixed by pre-initializing both to `None` before the `try` instead of resetting them in the `except`. Added a regression test. 100/100 tests passing.
