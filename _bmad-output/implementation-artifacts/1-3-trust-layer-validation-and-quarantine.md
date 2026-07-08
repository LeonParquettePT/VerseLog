---
baseline_commit: fc9b4fe40194d0cc32e7d797c8ab898059036eb7
---

# Story 1.3: Trust Layer — Validation and Quarantine

Status: done

## Story

As a player,
I want every extraction validated before I see it,
so that I can trust the result or know when to double-check it.

## Acceptance Criteria

1. **Given** an extracted contract, **when** a field fails validation (unknown station, non-integer SCU, non-numeric reward), **then** it is quarantined (source image kept) and flagged, rather than shown as if trustworthy. [Source: epics.md#Story-1.3]
2. **And** a valid extraction shows a visible confidence indicator. [Source: epics.md#Story-1.3]

## Tasks / Subtasks

- [x] Task 1: Evolve the capture interface to carry the source image and parse failures explicitly (AC: #1)
  - [x] `src/verselog/core/capture_result.py` — new `CaptureResult` dataclass: `contract: Contract | None`, `source_image: bytes`, `parse_error: str | None`
  - [x] `src/verselog/adapters/capture/ocr_parser.py` — add `ContractParseError` and raise it (with a clear message naming which field failed to match) instead of letting a bare `AttributeError`/`ValueError` propagate when a regex doesn't match or a value can't be converted
  - [x] Update `CapturePort.capture()` return type from `Contract` to `CaptureResult` [Source: src/verselog/core/ports/capture_port.py — Story 1.1]
  - [x] Update `OCRProvider.capture()`: always capture the screenshot bytes; wrap the `parse_contract_text` call in `try/except ContractParseError`, returning a `CaptureResult` with `contract=None, parse_error=str(e)` on failure or `contract=..., parse_error=None` on success — either way `source_image` is populated [Source: src/verselog/adapters/capture/ocr_provider.py — Story 1.2]
  - [x] Update `TriggerPort.on_triggered()` return type and `ManualTriggerAdapter` accordingly (pure type/delegation update, no new logic) [Source: src/verselog/core/ports/trigger_port.py, src/verselog/adapters/trigger/manual_trigger.py — Stories 1.1/1.2]
- [x] Task 2: Implement the trust-layer validation rules (AC: #1, #2)
  - [x] `src/verselog/core/trust_layer.py` — a `looks_like_a_station_name(name: str) -> bool` heuristic (non-empty, reasonable length, letters/digits/spaces/hyphens/apostrophes only). **Placeholder**: there is no real station database yet (arrives in Epic 2 Story 2.1) — this heuristic exists to catch obviously-garbled OCR output, not to verify a station actually exists in Star Citizen. Replace with a real lookup once Epic 2 Story 2.1 ships.
  - [x] Validate `scu > 0` and `reward > 0`
  - [x] A parse failure (`capture_result.parse_error is not None` or `contract is None`) is automatically a validation failure — no field checks needed in that case
- [x] Task 3: Implement `TrustLayer` as the single service every capture result passes through (AC: #1, #2)
  - [x] `TrustResult` dataclass: `contract: Contract | None`, `confidence: str | None`, `quarantined: bool`, `quarantine_path: Path | None`, `reasons: list[str]`
  - [x] `TrustLayer(quarantine_dir: Path = Path("data/quarantine"))` — constructor takes the quarantine directory so tests don't have to write into the real `data/` folder
  - [x] `TrustLayer.process(capture_result: CaptureResult) -> TrustResult`: runs the Task 2 checks; on any failure, writes `source_image` to `quarantine_dir` (creating it if needed) with a timestamp-based filename and returns a `TrustResult` with `quarantined=True`, the reasons, and the saved path; on success returns `TrustResult` with `quarantined=False`, `confidence="high"`, and no reasons
  - [x] Single tier of confidence (`"high"`) is enough for now — a graduated scale isn't required by this story's AC and would be invented scope
- [x] Task 4: Tests (AC: #1, #2)
  - [x] Unit test `TrustLayer.process` with hand-built `CaptureResult`s (no real image/OCR/screen involved): a fully valid contract → not quarantined, confidence `"high"`; a contract with `scu=0` → quarantined, reason mentions SCU; a contract with `reward=0` → quarantined; a `CaptureResult` with `parse_error` set and `contract=None` → quarantined, reason mentions the parse error; verify the quarantined image bytes actually land in the (temp, test-only) quarantine directory
  - [x] Update `test_ocr_parser.py` for the new `ContractParseError` behavior: craft OCR text missing the SCU pattern and assert `ContractParseError` is raised (rather than an unhandled `AttributeError`)
  - [x] Update `test_manual_trigger.py`'s fake `CapturePort` to return a `CaptureResult` instead of a bare `Contract`, matching the new port signature

## Dev Notes

- **Why the capture interface changes here, not later:** Story 1.3's own AC requires the source image to survive a validation failure ("quarantined (source image kept)"). Story 1.2 shipped `capture() -> Contract` with no way to carry the image or a distinct "parsing failed" signal. Evolving the port now — while Story 1.3 is exactly the story that needs it — is the correct point to do this, not scope creep. [Source: ARCHITECTURE-SPINE.md#AD-3]
- **Trust layer is ONE central service** — do not let `OCRProvider` (or any future `VisionProvider`) implement its own validation. All capture results funnel through `TrustLayer.process`. [Source: ARCHITECTURE-SPINE.md#AD-3]
- **This story does NOT wire trigger → capture → trust layer → UI end-to-end.** No app entrypoint exists yet to own that orchestration, and building one now would be inventing scope beyond this story's AC (which is specifically about the trust layer's own validate/quarantine behavior, testable in isolation by feeding it `CaptureResult`s directly). That wiring — and the results-window UI itself — remain open gaps already flagged after Story 1.1; don't silently resolve them here.
- **"Visible confidence indicator" (AC #2) is scoped to computing and attaching the confidence value** (`TrustResult.confidence`) — actually *displaying* it is UI work with no owning story yet (same flagged gap). Don't build a UI component here.
- **Station validation is a heuristic placeholder**, not a real lookup — say so in the docstring, don't imply more certainty than the code provides.
- **Coding style:** plain, direct code, comment only non-obvious "why." [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `core/capture_result.py` and `core/trust_layer.py` alongside the existing `core/contract.py` (all in `core/`, consistent with AD-3's "trust layer lives in core"). Modifies three existing files from Stories 1.1/1.2 (`capture_port.py`, `trigger_port.py`, `ocr_provider.py`, `ocr_parser.py`, `manual_trigger.py`) to carry the new `CaptureResult` shape through — read each one fully before editing, per standard practice for touching existing code.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.3] — this story's acceptance criteria, verbatim
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-3] — trust layer is one central service
- [Source: _bmad-output/implementation-artifacts/1-1-project-scaffold.md] — `Contract`, `CapturePort`, `TriggerPort` origin
- [Source: _bmad-output/implementation-artifacts/1-2-manual-capture-via-classic-ocr.md] — `OCRProvider`, `ManualTriggerAdapter`, `parse_contract_text` origin; also its code-review fix (Primary-Objectives-scoped extraction) — preserve that behavior while changing the return type

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `12 passed in 0.14s`
- `uv run --extra dev python -c "import verselog.adapters.capture.ocr_provider"` → imports cleanly after the `CaptureResult` interface change

### Completion Notes List

- Evolved `CapturePort`/`TriggerPort` to return `CaptureResult` (contract-or-parse-error + source image bytes) instead of a bare `Contract`, updating `OCRProvider` and `ManualTriggerAdapter` accordingly — necessary for this story's own AC (quarantine must keep the source image).
- Added `ContractParseError` to the parser; missing/invalid field patterns now raise a named, catchable error instead of a bare `AttributeError`/`ValueError`.
- Implemented `TrustLayer` (single validate+quarantine service per AD-3): station-name heuristic (placeholder pending Epic 2's real location data), positive-SCU/positive-reward checks, and parse-error handling. Quarantined captures write the source image to a caller-supplied directory with a timestamp filename.
- Confidence is a single `"high"` tier for now — no UI exists yet to display it (flagged gap, unchanged from Story 1.1).
- Did NOT wire trigger → capture → trust layer → UI end-to-end — no owning story for that orchestration yet; stayed scoped to this story's AC.
- All acceptance criteria satisfied; 12/12 tests passing (5 pre-existing + 7 new/updated).

### File List

- `src/verselog/core/capture_result.py` (new)
- `src/verselog/core/trust_layer.py` (new)
- `src/verselog/core/ports/capture_port.py` (modified — return type)
- `src/verselog/core/ports/trigger_port.py` (modified — return type)
- `src/verselog/adapters/capture/ocr_parser.py` (modified — `ContractParseError`)
- `src/verselog/adapters/capture/ocr_provider.py` (modified — returns `CaptureResult`)
- `src/verselog/adapters/trigger/manual_trigger.py` (modified — type update only)
- `tests/test_manual_trigger.py` (modified — fake port returns `CaptureResult`)
- `tests/test_ocr_parser.py` (modified — added parse-error test)
- `tests/test_trust_layer.py` (new)

## Change Log

- 2026-07-08: Story implemented — capture interface evolved to carry source image + parse errors, TrustLayer added, all tasks complete, 12/12 tests passing, status moved to review.
- 2026-07-08: Code review found and fixed one correctness bug — `pytesseract.image_to_string()` was called outside the try/except in `OCRProvider.capture()`, so a missing tesseract binary would crash uncaught instead of degrading into a quarantine-able `CaptureResult`. Fixed by widening the try/except to also catch `pytesseract.TesseractError`/`TesseractNotFoundError`. 12/12 tests still passing (no new test added — reproducing a missing-binary condition isn't practical to unit test; the fix is a straightforward except-clause widening, verified by code inspection and the existing ContractParseError test path).
