---
baseline_commit: 6083bf2cf443cc0cee7d391a849c253ddd4a5a1c
---

# Story 1.2: Manual Capture via Classic OCR

Status: done

## Story

As a player,
I want to manually trigger a scan that captures one contract and extracts its data via OCR,
so that I get structured data instead of reading it myself.

## Acceptance Criteria

1. **Given** a contract is visible on screen, **when** the player triggers a manual scan, **then** departure, arrival, SCU, and reward are extracted into the internal Contract shape via `OCRProvider`. [Source: epics.md#Story-1.2]

## Tasks / Subtasks

- [x] Task 1: Add capture dependencies (AC: #1)
  - [x] Add `mss` (screenshot) and `pytesseract` (OCR wrapper) to `pyproject.toml` `[project] dependencies`
  - [x] Note in Dev Notes that the `tesseract` binary itself is an external system dependency (not pip-installable) — not yet documented in `CONTRIBUTING.md`'s empty "Setup instructions", flagged as a gap for a later docs pass, not blocking this story
- [x] Task 2: Implement the OCR text parser as a pure, testable function (AC: #1)
  - [x] `src/verselog/adapters/capture/ocr_parser.py` — `parse_contract_text(raw_text: str) -> Contract`
  - [x] Extract reward from a `¤<number>` pattern
  - [x] Extract SCU as the second (total) number in an `X/Y SCU` pattern
  - [x] Extract arrival from a `Deliver ... to <LOCATION>.` pattern
  - [x] Extract departure from a `Collect ... from <LOCATION>.` pattern
  - [x] Extract remaining_time from a `Contract Availability <value>` pattern; map literal `N/A` to `None`
- [x] Task 3: Implement `OCRProvider` (`CapturePort`) (AC: #1)
  - [x] `src/verselog/adapters/capture/ocr_provider.py` — `OCRProvider` implements `CapturePort.capture()`: takes a screenshot via `mss`, runs `pytesseract.image_to_string`, passes the raw text to `parse_contract_text`
- [x] Task 4: Implement the manual trigger (AC: #1)
  - [x] `src/verselog/adapters/trigger/manual_trigger.py` — `ManualTriggerAdapter` implements `TriggerPort`; constructed with a `CapturePort` dependency, `on_triggered()` delegates to it
- [x] Task 5: Tests (AC: #1)
  - [x] Unit test `parse_contract_text` against realistic OCR-like text modeled on the real contract screenshot already on file (`contract-ui-reference.md`) — assert departure/arrival/scu/reward parse correctly, and that a `Contract Availability N/A` line maps to `remaining_time=None`
  - [x] Unit test `ManualTriggerAdapter` with a fake in-test `CapturePort` (no real screen/OCR involved) — assert `on_triggered()` delegates to the injected capture port and returns its `Contract`
  - [x] Do NOT attempt to unit test `OCRProvider.capture()` end-to-end against a real screen/tesseract binary — that requires a live display and installed `tesseract`, neither guaranteed in a dev/CI environment; its correctness rests on the already-tested parser plus manual verification, noted as a limitation, not silently skipped

## Dev Notes

- **Port composition pattern:** `TriggerPort` is "when to trigger," `CapturePort` is "how to extract" — a trigger adapter is constructed with a capture-port dependency and delegates to it. This is the pattern Story 1.4's voice trigger will reuse; don't collapse trigger and capture into one class. [Source: ARCHITECTURE-SPINE.md#Design-Paradigm]
- **Contract model already exists** at `src/verselog/core/contract.py` (Story 1.1) — reuse it as-is, do not create a second/competing shape. [Source: ARCHITECTURE-SPINE.md#Consistency-Conventions]
- **Real UI field layout to parse against** (from a real screenshot, not invented): Reward as `¤50,250`; `Contract Availability` sometimes literally `N/A`; Primary Objectives like `Collect Quartz from Port Tressler.` and `Deliver 0/6 SCU to Greycat Stanton IV Production Complex-A.` (the SCU total, `6`, is the second number in the `X/Y SCU` pair). [Source: contract-ui-reference.md#Extraction-implication]
- **Known limitation, stated not hidden:** only one real contract example (a Hauling mission) has been captured so far. The parsing patterns in this story are grounded in that one example; Mercenary/Bounty Hunter contract text likely phrases objectives differently and will need broader patterns in a later story once more real examples exist. Do not invent unverified phrasing patterns now.
- **Trust layer not wired yet:** validating/quarantining what this story extracts is Story 1.3. This story's job stops at "extraction produces a Contract" — do not add quarantine/confidence logic here, that would duplicate Story 1.3's work ahead of time.
- **External dependency:** the `tesseract` OCR engine binary must be installed on the system separately from the Python package (`pytesseract` only wraps it, doesn't bundle it). This is a real setup requirement not yet captured in `CONTRIBUTING.md`'s "Setup instructions" section (currently a placeholder) — worth a docs follow-up, not a blocker for this story's code.
- **Coding style:** plain, direct code, comment only non-obvious "why." [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds two new modules under the already-empty `adapters/capture/` (created in Story 1.1) and one under `adapters/trigger/` — no structural surprises, exactly what Story 1.1's scaffold anticipated.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.2] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/specs/spec-verselog/contract-ui-reference.md#Extraction-implication] — real field layout/example text
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Design-Paradigm] — port composition pattern
- [Source: _bmad-output/implementation-artifacts/1-1-project-scaffold.md] — previous story; `Contract`, `CapturePort`, `TriggerPort` already exist, reused as-is
- Web search (2026): `mss` confirmed current, cross-platform (Windows/Linux/macOS), no dependency, actively released — chosen over `Pillow.ImageGrab` because Linux support there depends on external screenshot tools being present, which `mss` avoids

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `5 passed in 0.06s`
- `uv run --extra dev python -c "import verselog.adapters.capture.ocr_provider"` → imports cleanly (sanity check only; `capture()` itself needs a live display + installed `tesseract` binary, not exercised in this environment)

### Completion Notes List

- Added `mss`, `pytesseract`, `Pillow` as direct dependencies.
- Implemented `parse_contract_text` as a pure function, tested against text modeled on the one real captured contract screenshot (Hauling category) — flagged the known limitation that other contract types may need broader patterns later.
- Implemented `OCRProvider` (screenshot via `mss` → OCR via `pytesseract` → parse). Not unit-tested end-to-end (needs a live display/tesseract binary); import-sanity-checked instead, limitation stated explicitly rather than silently skipped.
- Implemented `ManualTriggerAdapter` using the trigger/capture composition pattern, unit-tested with a fake `CapturePort`.
- Trust-layer validation/quarantine intentionally NOT implemented here — that's Story 1.3.
- All acceptance criteria satisfied; 5/5 tests passing (1 from Story 1.1 + 4 new).

### File List

- `pyproject.toml` (modified — added mss/pytesseract/Pillow dependencies)
- `src/verselog/adapters/capture/ocr_parser.py` (new)
- `src/verselog/adapters/capture/ocr_provider.py` (new)
- `src/verselog/adapters/trigger/manual_trigger.py` (new)
- `tests/test_ocr_parser.py` (new)
- `tests/test_manual_trigger.py` (new)
- `uv.lock` (modified)

## Change Log

- 2026-07-08: Story implemented — OCR parser, OCRProvider, and manual trigger added, all tasks complete, 5/5 tests passing, status moved to review.
- 2026-07-08: Code review found and fixed one correctness bug — departure/arrival regexes searched the whole OCR text unscoped, risking a false match against Details/flavor text containing similar phrasing (e.g. "deliver ... to ..." in narrative prose). Fixed by scoping extraction to the text after the "Primary Objectives" heading when present; added a regression test with decoy flavor text. 6/6 tests passing.
