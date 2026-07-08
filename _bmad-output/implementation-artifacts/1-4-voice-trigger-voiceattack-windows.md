---
baseline_commit: 09aa2741899c16466433e263ac815c884405c402
---

# Story 1.4: Voice Trigger (VoiceAttack, Windows)

Status: done

## Story

As a Windows player,
I want to trigger a scan by voice command,
so that I don't have to alt-tab or click while playing.

## Acceptance Criteria

1. **Given** VoiceAttack is configured, **when** the player says the scan command, **then** the same scan as the manual trigger runs. [Source: epics.md#Story-1.4]
2. **And** on Linux, only the manual trigger is available, with no error shown for the missing voice path. [Source: epics.md#Story-1.4]

## Tasks / Subtasks

- [x] Task 1: Implement `VoiceTriggerAdapter` (AC: #1)
  - [x] `src/verselog/adapters/trigger/voice_trigger.py` — same composition pattern as `ManualTriggerAdapter` (Story 1.2): constructed with a `CapturePort`, `on_triggered()` delegates to it
  - [x] No VoiceAttack-specific Python import — VoiceAttack integrates by calling OUT to an external command/script when its voice command fires, not by our code calling INTO a VoiceAttack SDK. That "how VoiceAttack's profile invokes this adapter" plumbing is explicitly Deferred in the architecture (VoiceAttack plugin integration mechanics) and out of scope here.
- [x] Task 2: Tests (AC: #1, #2)
  - [x] Unit test `VoiceTriggerAdapter` with a fake `CapturePort`, mirroring `test_manual_trigger.py` — proves delegation works and returns the same `CaptureResult` shape as the manual trigger
  - [x] No platform-conditional test needed for AC #2: since `VoiceTriggerAdapter` has zero VoiceAttack-specific imports or Windows-only code, it is trivially importable/usable on any platform — the module itself never raises on Linux. Document this reasoning in Dev Notes rather than fabricating a Linux-specific test double for something that never diverges by platform.

## Dev Notes

- **Reused pattern, not new design:** identical trigger/capture composition to `ManualTriggerAdapter` (Story 1.2) — `TriggerPort` is "when," `CapturePort` is "how." Don't invent a different shape for voice. [Source: ARCHITECTURE-SPINE.md#Design-Paradigm]
- **What "VoiceAttack integration" means for this story, precisely:** VoiceAttack is an external Windows application; it triggers our code by running a command/script/executable when its voice command fires — our code never imports or depends on a VoiceAttack package. This is why `VoiceTriggerAdapter` has no platform-specific logic at all: it's just another `TriggerPort` implementation. The actual VoiceAttack *profile* (what command/script it runs, how it's configured) is the still-Deferred "VoiceAttack plugin integration mechanics" — a real gap, but a separate concern from this adapter class, and not something buildable/testable without an actual VoiceAttack installation.
- **AC #2 is satisfied by construction, not by a platform branch:** because nothing in `VoiceTriggerAdapter` is Windows-specific, there is nothing to fail or error on Linux — the class works identically everywhere. "Only manual trigger available on Linux" describes reality at the *VoiceAttack-installation* level (VoiceAttack itself doesn't run on Linux), not something this module needs to detect or guard against.
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds one file to the already-existing `adapters/trigger/` package (Story 1.1 scaffold, populated by Story 1.2's `manual_trigger.py`). No new top-level structure.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.4] — this story's acceptance criteria, verbatim
- [Source: _bmad-output/implementation-artifacts/1-2-manual-capture-via-classic-ocr.md] — the trigger/capture composition pattern this story reuses
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Deferred] — "VoiceAttack plugin integration mechanics" explicitly deferred; this story does not resolve it

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `13 passed in 0.14s`

### Completion Notes List

- Implemented `VoiceTriggerAdapter`, identical composition pattern to `ManualTriggerAdapter` — no VoiceAttack-specific code, since VoiceAttack calls out to us rather than us calling into it.
- AC #2 (no error on Linux) is satisfied by construction: the class has zero platform-specific logic, so there's nothing to fail on any platform. Documented this reasoning rather than fabricating a platform-conditional test.
- The actual VoiceAttack profile/script wiring remains explicitly Deferred (architecture spine) — not this story's scope.
- All acceptance criteria satisfied; 13/13 tests passing (12 pre-existing + 1 new).

### File List

- `src/verselog/adapters/trigger/voice_trigger.py` (new)
- `tests/test_voice_trigger.py` (new)

## Change Log

- 2026-07-08: Story implemented — VoiceTriggerAdapter added, all tasks complete, 13/13 tests passing, status moved to review.
