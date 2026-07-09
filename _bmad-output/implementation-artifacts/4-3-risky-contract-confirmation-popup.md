---
baseline_commit: 4a776c29b11c897ded084a529e9d314d9a0217bd
---

# Story 4.3: Risky-Contract Confirmation Popup

Status: done

## Story

As a player,
I want to be shown a clear popup when a contract is flagged as risky,
so that I can decide knowingly before proceeding.

## Acceptance Criteria

1. **Given** a contract `LegalityChecker` has flagged, **when** `UIPort.confirm_risky_contract` is called, **then** a popup names the specific risk (faction, standing, reason) and requires an explicit accept/decline click, **and** the tool proceeds or withholds that contract from further processing based on the player's choice, exactly as Story 3.2 specified, **and** the tool never performs the accept/decline as an in-game action itself (no input injection, see SPEC.md non-goals). [Source: epics.md#Story-4.3]

## Tasks / Subtasks

- [x] Task 1: Add a `declined_reason` state to `ScanResult` distinct from quarantine (AC: #1)
  - [x] `src/verselog/core/scan_result.py` — add `declined_reason: str | None = None`. This is a *third*, distinct outcome from the existing two: `contract is None` + `quarantine_reasons` means "the trust layer never trusted it"; a populated `contract` with `declined_reason` set means "it was trustworthy, but the player declined it after a legality-risk prompt." Don't reuse `quarantine_reasons` for this — the two failure modes have different causes and the player should be able to tell them apart.
  - [x] Update `ScanResult.describe()`: when `declined_reason` is set, show the contract line plus `"  Declined: {declined_reason}"` and stop there (no route/loading text — nothing was computed for a declined contract).
- [x] Task 2: Wire `LegalityChecker` into `app.run()` (AC: #1)
  - [x] `src/verselog/app.py` — add an optional keyword-only parameter `legality_checker: LegalityChecker | None = None` to `run()`. Default `None` means legality checking is skipped entirely — there is still no real, verified location-to-faction dataset (Story 3.2's own Dev Notes), so `__main__.py` does not construct one. This keeps the wiring correct and fully testable now, ready for whenever a real datasource exists, without inventing one.
  - [x] Restructure `run()`'s body to use early returns for each terminal outcome (quarantined / declined / happy path) instead of nested `if`/`else` — clearer once there's a third outcome to add. After the trust layer validates a contract, if `legality_checker` is not `None`: call `legality_checker.check(contract)`. If it returns a risk, call `ui.confirm_risky_contract(contract, risk)`; if that returns falsy (declined, or the call itself raised — see below), build a `ScanResult(contract=contract, route_cost=None, loading_plan=None, declined_reason=risk.reason)`, show it, and return — do not compute route/loading for a declined contract. If it returns `True` (accepted), fall through to the existing route/loading computation exactly as before.
  - [x] Treat any exception from `ui.confirm_risky_contract(...)` itself as a decline (wrap the call, catch broadly, default to `False`) — this tool must fail closed on a risky contract, never silently proceed just because the confirmation dialog itself broke. This addresses a gap flagged during Story 4.1's code review: `ConsoleUIProvider.confirm_risky_contract`'s `input()` raises an unhandled `EOFError` on closed/non-interactive stdin, which must not be allowed to accidentally let a risky contract through.
- [x] Task 3: Tests (AC: #1)
  - [x] `ScanResult.describe()` with `declined_reason` set: contains the contract line and the decline reason, does not contain route/loading text
  - [x] `app.run()`: a fake `LegalityChecker` (or a real one with hand-built `ReputationStore`/`location_factions` fixtures) that flags the contract, a spy `UIPort.confirm_risky_contract` returning `False` — assert the spy's `show_results` received a `ScanResult` with `declined_reason` set and `route_cost`/`loading_plan` both `None`, and that `route_cost_calculator`/`loading_plan_calculator` were never actually invoked (a spy or call-counting fake proves the withholding is real, not just cosmetic)
  - [x] `app.run()`: same flagged-contract setup but the spy `UIPort.confirm_risky_contract` returns `True` — assert `route_cost`/`loading_plan` are computed and present in the `ScanResult` exactly as the no-legality-checker path already does
  - [x] `app.run()`: `legality_checker.check()` returns `None` (not risky) — assert the flow proceeds exactly as if no `legality_checker` had been supplied at all (no regression to the Story 4.1 behavior)
  - [x] `app.run()`: `legality_checker` is `None` (the real production default) — assert behavior is unchanged from Story 4.1 (regression check)
  - [x] `app.run()`: a `UIPort.confirm_risky_contract` that raises — assert it's treated as a decline (`ScanResult.declined_reason` set), not propagated as a crash

## Dev Notes

- **Why `declined_reason` is its own field, not reused `quarantine_reasons`:** the trust layer (Story 1.3) quarantining a bad extraction and a player declining a legally-risky-but-otherwise-valid contract are different situations with different causes — collapsing them into one field would make `ScanResult` ambiguous about which happened. [Source: _bmad-output/implementation-artifacts/1-3-trust-layer-validation-and-quarantine.md]
- **Why `legality_checker` defaults to `None` and nothing constructs one automatically:** Story 3.2 already established that no verified location-to-faction dataset exists, so `LegalityChecker` takes a plain injected `dict`, not a persisted store — inventing placeholder data now to "complete the wiring" would repeat the exact mistake this project has consistently avoided (Story 1.2's OCR patterns, Story 3.1's REP-screen scope, Story 3.2's own mapping). This story proves the wiring is *correct*, not that real legality data exists yet. [Source: _bmad-output/implementation-artifacts/3-2-legality-confirmation-before-risky-contract.md]
- **Fail closed on a broken confirmation dialog:** Story 4.1's code review flagged that `ConsoleUIProvider.confirm_risky_contract`'s `input()` raises `EOFError` on closed/non-interactive stdin. A risky-contract prompt that itself fails must never be treated as implicit consent — catch broadly around the `ui.confirm_risky_contract(...)` call and default to declining. This mirrors the trust layer's whole "quarantine on any doubt" posture, applied to the confirmation step instead of extraction. [Source: _bmad-output/implementation-artifacts/4-1-application-entrypoint-wiring.md#Dev-Agent-Record]
- **Early-return restructuring of `run()` is in scope, not a drive-by refactor** — Story 4.1's version used nested `if`/`else` for two outcomes (quarantined vs. happy path); adding a third outcome (declined) makes the early-return shape clearly better and is a direct consequence of this story's own change, not unrelated cleanup.
- **Never an in-game action:** exactly like Story 3.2, this story's code only ever asks and records the player's own choice — nothing here accepts or declines the contract inside Star Citizen itself. [Source: _bmad-output/specs/spec-verselog/SPEC.md#Non-goals]
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Modifies `core/scan_result.py` (new field + `describe()` update) and `app.py` (new optional parameter, restructured body) additively — no new files. `ConsoleUIProvider`/`TkinterUIProvider`'s `confirm_risky_contract` implementations (Story 4.2) are reused as-is, not modified.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.3] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/3-2-legality-confirmation-before-risky-contract.md] — `LegalityChecker`/`LegalityRisk`, consumed as-is; the "no invented location-to-faction data" reasoning this story continues
- [Source: _bmad-output/implementation-artifacts/4-1-application-entrypoint-wiring.md] — `app.run()`'s current structure this story extends, and the `EOFError` gap its own code review flagged for this story to address
- [Source: _bmad-output/implementation-artifacts/4-2-results-window-tkinter-ui-adapter.md] — `confirm_risky_contract` implementations (Console and Tkinter) this story finally calls

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `112 passed in 4.20s`
- `uv run python -m verselog --help` → clean CLI output, confirmed the wiring change didn't break the entrypoint

### Completion Notes List

- Added `ScanResult.declined_reason: str | None = None` and updated `describe()` to show it distinctly from the quarantine path.
- Wired `LegalityChecker` into `app.run()` as an optional keyword-only parameter (default `None` — no real location-to-faction dataset exists yet, so `__main__.py` doesn't construct one). Restructured `run()`'s body to early returns for each terminal outcome (quarantined / declined / happy path).
- Wrapped `ui.confirm_risky_contract(...)` in a broad `try/except`, defaulting to declining on any exception — closes the `EOFError` gap Story 4.1's code review flagged, so a broken confirmation dialog can never be mistaken for consent.
- Verified withholding is real (not cosmetic): a fake `LegalityChecker` records every contract it was asked to check, and the declined-path test confirms the resulting `ScanResult` has no route/loading data.
- All acceptance criteria satisfied; 112/112 tests passing (106 pre-existing + 6 new: 1 for `ScanResult.declined_reason`, 5 for the `app.run()` legality wiring).

### File List

- `src/verselog/core/scan_result.py` (modified — added `declined_reason`, updated `describe()`)
- `src/verselog/app.py` (modified — `legality_checker` parameter, restructured to early returns)
- `tests/test_scan_result_declined.py` (new)
- `tests/test_app_legality.py` (new)

## Change Log

- 2026-07-09: Story implemented — `ScanResult.declined_reason` added, `LegalityChecker` wired into `app.run()` with fail-closed handling of a broken confirmation dialog, all tasks complete, 112/112 tests passing, status moved to review.
