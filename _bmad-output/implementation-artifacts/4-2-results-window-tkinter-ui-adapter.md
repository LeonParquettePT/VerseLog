---
baseline_commit: 3ae97648a3c4e739e179c9ee3d88a940b575911c
---

# Story 4.2: Results Window (Tkinter UI Adapter)

Status: done

## Story

As a player,
I want to see my scan results and recommendations in VerseLog's own window,
so that I don't have to read logs or code to know what the tool found.

## Acceptance Criteria

1. **Given** one or more validated contracts with a computed route and loading plan, **when** the results are shown, **then** a Tkinter window displays each contract's departure, arrival, reward, route cost, and loading steps in large, readable text, **and** the window is VerseLog's own, separate from the game — never a live overlay tracking the in-game list (see SPEC.md non-goals). [Source: epics.md#Story-4.2]

## Tasks / Subtasks

- [x] Task 1: Extract the shared result-formatting logic out of `ConsoleUIProvider` before duplicating it (AC: #1)
  - [x] `src/verselog/core/scan_result.py` — add `ScanResult.describe(self) -> str`, moving the exact formatting logic `ConsoleUIProvider.show_results`/`_format_contract` already has (Story 4.1) onto the dataclass itself. Both the console adapter and this story's new Tkinter adapter need identical text — writing it twice would be exactly the kind of duplication this project's own review process has caught before (e.g. Story 2.3/2.4's duplicate-computation fixes).
  - [x] Update `src/verselog/adapters/ui/console_ui_provider.py` — `show_results` becomes `for result in results: print(result.describe())`; delete the now-redundant `_format_contract` method. `confirm_risky_contract` is untouched.
- [x] Task 2: Implement `TkinterUIProvider` (AC: #1)
  - [x] `src/verselog/adapters/ui/tkinter_ui_provider.py` — `TkinterUIProvider(UIPort)`.
  - [x] Split window construction from the blocking event loop so it's testable: `build_results_window(results: list[ScanResult]) -> tk.Tk` creates the `Tk()` root, sets a title, and adds one `tk.Label` per `ScanResult` (using `result.describe()` as its text) at a large, readable font size (e.g. 14pt+ — NFR9 says "large, readable text" explicitly, don't leave it at Tkinter's tiny default). `show_results(results)` calls `build_results_window(results)` then `.mainloop()` — the public `UIPort` method blocks until the player closes the window, matching this being the tool's own separate window the player checks after a scan, not a background overlay.
  - [x] `confirm_risky_contract(contract, risk) -> bool` — a real, working implementation via `tkinter.messagebox.askyesno`, showing the contract and `risk.reason` in the dialog message. This satisfies `UIPort`'s abstract method (required for `TkinterUIProvider` to be instantiable at all) with genuine, correct behavior now — Story 4.3's job is wiring `LegalityChecker` into `app.py` to actually *call* this, and adjusting the exact popup wording if its own AC needs more than what's built here, not re-implementing the dialog from scratch.
- [x] Task 3: Tests (AC: #1)
  - [x] `ScanResult.describe()`: happy path (contract + route cost + loading plan) contains departure/arrival/reward/route-cost/loading-step text; quarantine path (`contract=None`) contains the quarantine reasons
  - [x] `TkinterUIProvider.build_results_window(results)`: build a real `Tk()` window (this environment has a real display — confirmed via a direct `tkinter.Tk()` smoke check before writing this story) with a fake `ScanResult`, walk `root.winfo_children()` to find the label(s), assert the rendered text matches `result.describe()` and the font size is at least 14pt, then `root.destroy()` — never call `.mainloop()` in a test, it blocks forever waiting for a window close event
  - [x] `TkinterUIProvider.confirm_risky_contract`: monkeypatch `tkinter.messagebox.askyesno` to a fake returning `True`/`False` in turn, assert the return value passes through unchanged and the call received the risk's `reason` text somewhere in its arguments
  - [x] Do NOT attempt to unit test the blocking `show_results`/real `.mainloop()` path or a real interactive `askyesno` click — same documented limitation pattern as every other live-UI/live-hardware path in this project (Stories 1.2, 1.5): exercise `build_results_window` and the monkeypatched dialog directly instead

## Dev Notes

- **Why `describe()` moves onto `ScanResult` instead of being duplicated:** `ConsoleUIProvider` (Story 4.1) already has this exact formatting logic. A second `UIPort` implementation needing the identical text is precisely the signal to extract it once, not copy-paste it — consistent with this project's established anti-duplication discipline. [Source: _bmad-output/implementation-artifacts/4-1-application-entrypoint-wiring.md]
- **"Large, readable text" is a literal NFR9 requirement, not a nice-to-have** — pick an explicit font size (14pt or larger) rather than leaving Tkinter's small default. [Source: epics.md NFR9]
- **Window construction split from `mainloop()` is what makes this testable at all** — `mainloop()` blocks until the window is closed, which a test can never do. Build the window, inspect it, `destroy()` it; never call `mainloop()` from a test. This mirrors the same "can't automate the truly live part" limitation this project has already documented for `OCRProvider.capture()`/`VisionProvider.capture()`. [Source: _bmad-output/implementation-artifacts/1-2-manual-capture-via-classic-ocr.md, 1-5-local-vision-provider-ollama.md]
- **Confirmed Tkinter actually works in this dev environment** before writing this story: `uv run python -c "import tkinter; tkinter.Tk()..."` succeeded — the `uv`-managed Python build does bundle Tcl/Tk here. If a future contributor's environment lacks it, that's a packaging/distribution concern (already Deferred in ARCHITECTURE-SPINE.md), not something this story needs to guard against.
- **`confirm_risky_contract` is implemented for real here, not stubbed** — `UIPort` is an ABC with two abstract methods, so `TkinterUIProvider` can't exist without both. Story 4.3 wires `LegalityChecker` into `app.py` and calls it; this story only needs the dialog itself to work correctly in isolation.
- **Coding style:** plain, direct code, no premature widget-abstraction layer beyond what one results window needs. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `adapters/ui/tkinter_ui_provider.py` alongside `console_ui_provider.py` (Story 4.1) — both are legitimate, coexisting `UIPort` implementations per Ports & Adapters (AD-1), not a "replace the placeholder" situation. Modifies `core/scan_result.py` (adds `describe()`) and `adapters/ui/console_ui_provider.py` (uses it) additively.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.2] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/4-1-application-entrypoint-wiring.md] — `ScanResult`, `UIPort`, `ConsoleUIProvider`, the formatting logic this story extracts and reuses
- [Source: _bmad-output/specs/spec-verselog/SPEC.md#Non-goals] — the results window must never be a live overlay tracking the in-game list
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-1] — Ports & Adapters; multiple `UIPort` adapters coexisting is exactly what this enables

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `106 passed in 3.98s`
- Real visual verification: built the actual window with real data (Port Tressler contract, real route cost, loading plan, plus a quarantined result), rendered it, and screenshotted it — confirmed large readable text and correct content for both the happy path and the quarantine path.

### Completion Notes List

- Extracted `ScanResult.describe()` before duplicating formatting logic into a second `UIPort` adapter; `ConsoleUIProvider` now calls it too, its old `_format_contract` helper deleted. Existing Story 4.1 console tests still pass unmodified — the printed text is byte-identical, just assembled once instead of via multiple `print()` calls.
- Implemented `TkinterUIProvider`: `build_results_window()` (testable, no event loop) separated from `show_results()` (blocks on `.mainloop()`), one `tk.Label` per `ScanResult` at 14pt. `confirm_risky_contract()` uses `tkinter.messagebox.askyesno`, a real working implementation (required since `UIPort` is an ABC with two abstract methods).
- Confirmed Tkinter actually works in this `uv`-managed environment before starting (a real `tkinter.Tk()` smoke check), then verified again at the end with an actual rendered, screenshotted window — not just unit tests.
- All acceptance criteria satisfied; 106/106 tests passing (100 pre-existing + 6 new: 2 for `ScanResult.describe()`, 4 for `TkinterUIProvider`).

### File List

- `src/verselog/core/scan_result.py` (modified — added `describe()`)
- `src/verselog/adapters/ui/console_ui_provider.py` (modified — uses `describe()`, `_format_contract` removed)
- `src/verselog/adapters/ui/tkinter_ui_provider.py` (new)
- `tests/test_scan_result.py` (new)
- `tests/test_tkinter_ui_provider.py` (new)

## Change Log

- 2026-07-09: Story implemented — `ScanResult.describe()` extracted and reused, `TkinterUIProvider` added as the real results window (NFR9), all tasks complete, 106/106 tests passing, status moved to review.
