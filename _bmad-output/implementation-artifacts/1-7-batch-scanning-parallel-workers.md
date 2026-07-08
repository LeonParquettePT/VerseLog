---
baseline_commit: 94ce7ccb171de9e2286e8e00e3809b680bf43145
---

# Story 1.7: Batch Scanning (Parallel Workers)

Status: ready-for-dev

## Story

As a player facing a full contract board,
I want many contracts scanned at once instead of one by one,
so that I'm not stuck waiting when there are dozens of contracts.

## Acceptance Criteria

1. **Given** N workers from Story 1.6's benchmark, **when** the player scans a batch (e.g. ~30 contracts), **then** extraction runs in parallel across up to N workers. [Source: epics.md#Story-1.7]
2. **And** every result is still handed to the trust layer (Story 1.3) serially, with no race conditions on quarantine/confidence state. [Source: epics.md#Story-1.7]

## Tasks / Subtasks

- [ ] Task 1: Implement `BatchScanner` (AC: #1, #2)
  - [ ] `src/verselog/core/batch_scanner.py` — constructed with a `TrustLayer`; `scan_all(capture_ports: list[CapturePort], worker_count: int) -> list[TrustResult]`
  - [ ] Run `capture()` for each provided `CapturePort` concurrently via `concurrent.futures.ThreadPoolExecutor(max_workers=max(1, worker_count))` — I/O-bound work (screenshot + OCR/Ollama call), threads are the right tool, no new dependency
  - [ ] As each future completes (`as_completed`), immediately call `TrustLayer.process()` on its result **in the calling thread** — never inside a worker thread — so quarantine/confidence writes are never concurrent, satisfying AD-6 by construction rather than by locking
  - [ ] Preserve input order in the returned `list[TrustResult]` (map futures back to their original index), so results.
  - [ ] If a worker's `capture()` raises unexpectedly (all current `CapturePort`s are designed not to, per Stories 1.2/1.3/1.5, but a batch of ~30 real captures is exactly the scenario where one bad one shouldn't sink the rest), catch it and feed the trust layer a `CaptureResult(contract=None, source_image=b"", parse_error=str(exc))` instead of letting the whole batch abort
- [ ] Task 2: Tests (AC: #1, #2)
  - [ ] Prove actual parallelism: N fake `CapturePort`s that each sleep a known duration, `worker_count > 1` → total wall-clock time is well under the sum of individual sleep times
  - [ ] Prove result order is preserved regardless of completion order (mix fast/slow fakes)
  - [ ] Prove serial hand-off to the trust layer: a `TrustLayer` (or a spy wrapping it) records call order/timing; assert no two `process()` calls overlap even though captures ran concurrently
  - [ ] Prove one raising `CapturePort` doesn't abort the rest of the batch — its `TrustResult` is quarantined, others complete normally
  - [ ] Prove a mixed batch (some valid, some invalid contracts) produces the expected mix of trusted/quarantined `TrustResult`s, matching `TrustLayer`'s existing validation rules (Story 1.3) — an integration-style test, not just mocks

## Dev Notes

- **What this story does NOT solve:** how ~30 *distinct* contract screenshots actually get produced (e.g. scrolling through the in-game list and capturing each). No existing doc specifies that mechanism, and inventing scrolling/UI automation here would be unverified scope creep — possibly bumping into the same ToS-sensitive territory already resolved in `SPEC.md`'s non-goals (no input injection). This story takes "a list of `CapturePort`s, one per contract to scan" as its input and focuses purely on running them safely in parallel; sourcing that list is a future/UI concern.
- **Concurrency mechanism:** `ThreadPoolExecutor`, not `multiprocessing` — the work per capture is I/O-bound (screenshot, then an external OCR/Ollama call), so threads avoid the overhead/complexity of process pools without hitting GIL-bound CPU work. [Source: ARCHITECTURE-SPINE.md#AD-6]
- **Serial hand-off is structural, not a lock:** because every `TrustLayer.process()` call happens in the loop iterating `as_completed()` — which runs in the single calling thread — there is nothing to synchronize; two calls literally cannot overlap. Don't add a `threading.Lock` around `TrustLayer` calls, that would be solving a problem that doesn't exist given this design. [Source: ARCHITECTURE-SPINE.md#AD-6]
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `core/batch_scanner.py` — lives in `core/` (not `adapters/`) since it orchestrates the trust layer, which is itself core-owned (AD-3); it depends on `CapturePort` (the abstraction), not any concrete adapter, keeping the dependency direction correct per AD-1.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.7] — this story's acceptance criteria, verbatim
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-6] — parallel capture, serial trust layer
- [Source: _bmad-output/implementation-artifacts/1-6-hardware-benchmark-model-tier-and-worker-count.md] — where the worker-count `N` this story consumes comes from
- [Source: _bmad-output/implementation-artifacts/1-3-trust-layer-validation-and-quarantine.md] — `TrustLayer`/`TrustResult`, reused as-is

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
