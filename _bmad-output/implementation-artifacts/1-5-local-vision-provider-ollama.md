---
baseline_commit: 0afe12dc669cfd379706414209a37c1bb3911455
---

# Story 1.5: Local Vision Provider (Ollama)

Status: done

## Story

As a player,
I want a more precise extraction option,
so that OCR errors on tricky UI elements are reduced.

## Acceptance Criteria

1. **Given** Ollama is available locally, **when** `VisionProvider` is selected, **then** it returns the same Contract shape as `OCRProvider`, swappable behind the same port with no change elsewhere. [Source: epics.md#Story-1.5]

## Tasks / Subtasks

- [x] Task 1: Add the `ollama` dependency (AC: #1)
  - [x] Add `ollama` to `pyproject.toml` `[project] dependencies`
- [x] Task 2: Implement `VisionProvider` (`CapturePort`) using Ollama structured outputs (AC: #1)
  - [x] `src/verselog/adapters/capture/vision_provider.py` — screenshot via `mss` (reuse the same capture approach as `OCRProvider`), then `ollama.chat(...)` with the screenshot image and a hand-written JSON schema (`format=`) matching `Contract`'s fields (departure, arrival, scu, reward, remaining_time) — no need for a `pydantic` dependency just to generate one schema
  - [x] Default model name `phi3-vision`, constructor parameter so Story 1.6's benchmark can swap tiers later without touching this class (`Phi-3-Vision → Moondream2 → classic OCR` fallback chain already established) [Source: vision-pipeline.md]
  - [x] Parse the JSON response into a `Contract`; on any failure (Ollama unreachable, model not pulled, malformed/incomplete JSON) catch it and return `CaptureResult(contract=None, source_image=..., parse_error=str(exc))` — same graceful-degradation lesson Story 1.3's code review established for `OCRProvider`, applied here from the start rather than reactively
- [x] Task 3: Tests (AC: #1)
  - [x] Unit test the JSON-response-to-Contract parsing logic in isolation (extract it as its own small function, e.g. `_contract_from_json(raw_json: str) -> Contract`) using hand-written JSON strings — no real Ollama call involved
  - [x] Unit test that a malformed/incomplete JSON response is caught and produces a `CaptureResult` with `parse_error` set, not an uncaught exception
  - [x] Do NOT attempt to unit test `VisionProvider.capture()` end-to-end against a real Ollama instance — same documented limitation as `OCRProvider`'s live screen/tesseract path (Story 1.2): needs a live display and a running Ollama with the model pulled, neither guaranteed in a dev/CI environment

## Dev Notes

- **Same port, swappable:** `VisionProvider` implements `CapturePort` exactly like `OCRProvider` — same `CaptureResult` return shape, nothing downstream (trust layer, future callers) needs to know which one ran. [Source: ARCHITECTURE-SPINE.md#AD-1]
- **Structured output over regex:** unlike `OCRProvider`'s regex-based text parsing, a vision model can be prompted to directly return the fields as JSON (Ollama's `format=` parameter accepts a raw JSON-schema dict — confirmed current 2026 API via web search, no need to add `pydantic` just to build one schema by hand).
- **Model tier is a constructor parameter, not hardcoded** — Story 1.6's benchmark will pick between `phi3-vision`/`moondream` by constructing `VisionProvider` with a different `model` argument. Don't hardcode the model name inside the class body.
- **Graceful degradation from the start:** Story 1.3's code review found and fixed a bug where `OCRProvider` let an external-tool failure (missing tesseract) crash uncaught instead of degrading into a `CaptureResult`. Apply that lesson here proactively: wrap the Ollama call and JSON parsing together in one broad `try/except`, don't wait for a review to catch it.
- **Coding style:** plain, direct code. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds one file to the existing `adapters/capture/` package (alongside `ocr_parser.py`, `ocr_provider.py` from Story 1.2). No new top-level structure.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.5] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/specs/spec-verselog/vision-pipeline.md] — established model fallback chain (Phi-3-Vision → Moondream2 → classic OCR)
- [Source: _bmad-output/implementation-artifacts/1-3-trust-layer-validation-and-quarantine.md] — the graceful-degradation lesson (CaptureResult + parse_error) this story applies from the start
- Web search (2026): Ollama's Python client `chat(..., format=<json-schema-dict>, options={"temperature": 0})` confirmed as the current structured-output pattern for vision models, response parsed via `response.message.content`

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `19 passed in 12.41s`

### Completion Notes List

- Added `ollama` dependency; implemented `VisionProvider` (`CapturePort`) using Ollama's structured-output `format=` parameter with a hand-written JSON schema (no `pydantic` dependency needed for one schema).
- Extracted `_contract_from_json` as its own testable function; unit-tested directly with hand-written JSON (well-formed, missing field, malformed JSON).
- Applied Story 1.3's graceful-degradation lesson proactively: the Ollama call + JSON parsing are wrapped in one broad `try/except` from the start, verified with monkeypatched `mss`/`ollama.chat` so `capture()` itself is exercised without a real screen or running Ollama instance.
- Model name (`phi3-vision` default) is a constructor parameter, ready for Story 1.6's benchmark to swap tiers.
- All acceptance criteria satisfied; 19/19 tests passing (13 pre-existing + 6 new).

### File List

- `pyproject.toml` (modified — added `ollama` dependency)
- `src/verselog/adapters/capture/vision_provider.py` (new)
- `tests/test_vision_provider.py` (new)
- `uv.lock` (modified)

## Change Log

- 2026-07-08: Story implemented — VisionProvider added (Ollama structured outputs), all tasks complete, 19/19 tests passing, status moved to review.
- 2026-07-08: Code review found duplicated screenshot-capture logic between `OCRProvider` and `VisionProvider` (identical mss+PIL+PNG-encode block). Extracted a shared `adapters/capture/screenshot.py::take_screenshot()`, updated both providers and the vision-provider tests to use it. 19/19 tests still passing.
- 2026-07-09: Real end-to-end verification against Ollama (installed locally) and the same two real screenshots used for Story 1.2's OCR verification, run through the actual `VisionProvider.capture()` path (screenshot mocked to the real image file, everything else real). Found and fixed four real issues, none catchable by the existing hand-written-JSON unit tests:
  1. **The assumed default model name `phi3-vision` does not exist in the Ollama library.** Confirmed via web search and by attempting to pull it. The real, currently-available model combining LLaVA's vision encoder with a Phi-3 backbone is tagged `llava-phi3`.
  2. **`llava-phi3` and `moondream` both completely hallucinate on real Star Citizen screenshots** — tested with structured JSON output *and* free-form description prompts. `llava-phi3` described a car's dashboard console; `moondream` produced repetitive, unrelated text and near-placeholder JSON (`{"departure": "X", "arrival": "Y", ...}`). Neither model is viable for this use case regardless of the fallback-chain tier assumed in `vision-pipeline.md`.
  3. **`llama3.2-vision` fails outright on the currently-installed Ollama version (0.31.2)**: `error loading model: unknown model architecture: 'mllama'`. This is an Ollama-side limitation, not fixable in this codebase; ruled out for now.
  4. **`qwen2.5vl:3b` is the only one of the four models tested that actually reads the real screenshot content** (correct reward, correct departure/arrival on the Hauling contract) — adopted as the new default model. Two follow-on bugs found and fixed: (a) it initially returned the *current* SCU amount (the X in "X/Y SCU") instead of the *capacity* (the Y) despite the schema description already saying "the total" — fixed by making the prompt and schema description give a concrete worked example instead of an abstract description; (b) a busier contract screen (the Mercenary-type screenshot) pushed the request past Ollama's 4096-token default context window, failing outright — fixed by setting `options={"num_ctx": 8192}`.
  - **New known limitation surfaced, not yet fixed**: for a contract type the prompt doesn't cover (e.g. Mercenary, which has no departure/arrival/SCU concept), `VisionProvider` doesn't fail the way `OCRProvider` does — it returns a *confident-looking but fabricated* `Contract` (empty departure/arrival strings, invented SCU/reward numbers) instead of raising. Verified this is still caught safely: `TrustLayer._validate` already rejects empty departure/arrival names via `looks_like_a_station_name`, so the fabricated result gets quarantined rather than reaching downstream code — but this is worth a dedicated fix (e.g. having the model signal "not a hauling contract" explicitly) in a later story rather than relying solely on the trust layer's side effect.
  - Updated `vision-pipeline.md`'s fallback chain to reflect confirmed real Ollama tags (`llava-phi3 → moondream → classic OCR` was the assumption; real-world testing shows only `qwen2.5vl:3b` is currently viable as a vision tier).
  - 55/55 tests passing (no test changes needed — the fixes were prompt/schema/config only, not shape changes).
