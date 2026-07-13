---
project_name: 'VerseLog'
user_name: 'Léon'
date: '2026-07-13'
sections_completed: ['technology_stack', 'architecture', 'testing', 'code_quality', 'workflow', 'anti_patterns', 'communication']
existing_patterns_found: 12
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## What VerseLog is

A free, open-source, community-collaborative logistics assistant for Star Citizen. It reads the player's contract board (via screen capture + OCR/vision), validates what it reads, and returns a route/cargo plan maximizing aUEC/minute. Built to run *alongside* the game on modest hardware, not to compete with it for resources. Full contract: `_bmad-output/specs/spec-verselog/SPEC.md`.

## Technology Stack & Versions

- Python >=3.12, managed with `uv` (not pip/poetry/conda directly)
- Build backend: `hatchling`
- Runtime deps: `mss` (screenshot), `pytesseract` + `Pillow` (OCR/Tesseract), `ollama` (local vision LLM client), `requests` (community API)
- Dev deps: `pytest>=8`, `pyinstaller>=6.21`
- Packaging: PyInstaller `--onefile`, built for Windows locally and for Linux via a GitHub Actions `ubuntu-24.04` runner (not `ubuntu-latest` — pinned deliberately, see Anti-Patterns)
- No frontend framework — UI is Tkinter (stdlib), swappable via `UIPort`

## Architecture — Ports & Adapters (AD-1)

`core/` is pure domain logic and **never imports a concrete adapter**. Everything that touches the outside world (screen capture, OCR, Ollama, Tkinter, SQLite, the community API, the filesystem) lives under `adapters/` and implements a `Port` (ABC) defined in `core/ports/`.

- `core/ports/capture_port.py` (`CapturePort`) — implemented by `adapters/capture/{ocr_provider,vision_provider}.py`
- `core/ports/ui_port.py` (`UIPort`) — implemented by `adapters/ui/{console_ui_provider,tkinter_ui_provider}.py`
- Adding a new capability to `UIPort` or `CapturePort` means adding an abstract method AND implementing it in **every** concrete adapter, or the class fails to instantiate (Python enforces this at instantiation time, not at method-call time — this has caught real bugs in this project when a new abstract method was added and an adapter's `__init__` had to change too).
- Duck-typed test doubles (e.g. `_SpyUI` in test files) do **not** subclass `UIPort`, so adding a new abstract method does **not** break them automatically — but any test that then reaches the new code path via a real `run()` call will get an `AttributeError` unless the test double is updated too. Always grep for every test double implementing a Port before adding a method to it.
- `app.py`'s `run()` function is the composition root: it constructs every adapter with a sensible real default when not given one (`ui if ui is not None else ConsoleUIProvider()`, etc.) — this is the pattern to follow for any new optional collaborator, **except** when the collaborator does real I/O in a way that would make every existing test slower/non-deterministic if left un-injected (see Testing Rules below).

## Testing Rules

- **Red-green-refactor, always**: write the failing test first, run it, confirm it fails for the expected reason, then implement.
- **No generic mocking libraries.** This codebase uses small hand-written fakes/spies/stubs per test file (e.g. `_FakeCapturePort`, `_SpyUI`, `_StubPrerequisiteChecker`), not `unittest.mock.Mock()` or similar. Follow this convention for new tests.
- **Any new dependency that performs real I/O (network, subprocess, filesystem beyond the project's own SQLite/JSON stores) must be explicitly faked in every existing test that calls through it**, not left to its real default. When `PrerequisiteChecker` (real Tesseract/Ollama I/O) was added to `app.run()`'s default construction, every pre-existing `run()` call site in the test suite had to be retrofitted with a stub — otherwise tests silently started hitting the real host machine, differing between this dev's machine (has Tesseract/Ollama installed) and CI (doesn't).
- **Real manual verification is required for anything a `pytest` assertion can't observe** — a GUI actually rendering, a packaged executable actually running, a CI workflow actually succeeding. This project has repeatedly caught real bugs this way (a Tkinter window never actually shown from the real CLI entrypoint despite passing unit tests; a GitHub Actions workflow that looked plausible on paper but failed differently twice in practice). Never claim something works based on unit tests alone when a runtime check is possible.
- Monkeypatch at the **module level** where the dependency is imported (e.g. `monkeypatch.setattr(vision_provider_module.ollama, "chat", ...)`), not via `unittest.mock.patch` path strings.

## Code Quality & Style Rules (from `CONTRIBUTING.md`)

- **Functional first, clean second.** A working, correct change beats a beautifully abstracted one. Don't add flexibility/design patterns for problems the project doesn't have yet.
- **Plain, direct code.** Comment only what the code can't say for itself (a non-obvious constraint, a workaround, a "why" — never a "what"). No boilerplate, no defensive handling for cases that can't occur.
- **Respect `SPEC.md`'s constraints**: no paid cloud dependency, must stay usable on modest hardware, no mandatory microphone/voice requirement.

## Development Workflow Rules

- **BMad Method, one branch per story.** Every story: dedicated Git branch → implement (TDD) → tests → `code-review` skill → merge to `main` → mark the story `done` in both its own file and `sprint-status.yaml`. This applies even to docs-only or CI-only changes.
- Story files live in `_bmad-output/implementation-artifacts/*.md`; `sprint-status.yaml` in the same folder is the single source of truth for what's backlog/ready-for-dev/in-progress/review/done — always read it before assuming project state.
- Epics and the full backlog (including deferred ideas raised mid-session, each with its own justification) live in `_bmad-output/planning-artifacts/epics.md`.
- A GitHub Actions `workflow_dispatch` trigger **cannot be invoked at all** until the workflow file exists on the default branch (`main`) — not even by targeting a different `ref`. To test a new workflow on a feature branch, add a temporary branch-scoped `push:` trigger, verify, then remove it before requesting review.
- Release binaries (Windows `.exe`, Linux binary) are published via **GitHub Releases**, never committed to the repo. Link to Releases using explicit `/releases/tag/<tag>` URLs in docs, never `/releases/latest` — a second platform's release becomes "latest" the moment it's published, silently hijacking any `/releases/latest` link pointing at the first one (a real bug hit in this project).

## Critical Anti-Patterns / Don't-Miss Rules

- **Never install third-party prerequisites (Tesseract, Ollama) automatically or silently.** Explicitly rejected by design — detect and inform only (`PrerequisiteChecker` + `UIPort.warn_missing_prerequisites`), never invoke an installer on the player's behalf. Same posture for any future "helper" automation: this project always fails closed toward requiring the player's own explicit action.
- **`UIPort.confirm_risky_contract` and similar player-facing decisions must fail closed.** If the confirmation dialog itself throws (e.g. `EOFError` on closed stdin), treat it as a decline, never as implicit consent. Wrap in `try/except Exception: accepted = False`, not a narrower exception type.
- **No input injection into the game, ever** (see `SPEC.md` non-goals). `UIPort` methods only report the player's choice back to VerseLog's own logic — they never simulate a keypress/click inside Star Citizen itself.
- **A missing/quarantined capture is a normal, expected outcome, not an error** — the trust layer quarantining an unparseable or implausible capture (e.g. testing outside the actual game, where OCR/vision can't find real station names) is the pipeline working correctly, not a bug to "fix" by loosening validation.
- **Local vision-model inference (Ollama) is memory-hungry once actually invoked** — confirmed directly: fine on a 4 GB test VM until the model loads, not enough once it does. Don't assume a "the binary launches fine" check on modest hardware also proves the vision tier is safe to run there.
- **PyInstaller-built executables are unsigned and will be blocked by Windows Smart App Control** (a categorical block, no per-app "Run anyway" override, unlike SmartScreen) until the project pursues code signing (deferred: Story 5.4, SignPath Foundation).
- **`uv`'s own managed Python does not reliably ship a working `tkinter` on Linux**, regardless of system `tk-dev` being installed. Use the system Python instead (`apt install python3-tk` + `uv sync --python-preference only-system`) — confirmed the hard way via two failed-then-fixed CI runs, not from documentation alone.

## Communication Conventions

- Léon (the project owner) communicates in **French**; respond in French. Code, comments, commit messages, and story/doc files are in **English** (`document_output_language`).
- Work continuously through a story's full cycle without pausing for incremental explanations — save the full walkthrough for when the user actually asks for one.
- Léon intentionally keeps this project inside a OneDrive-synced folder for backup redundancy despite the sync noise it causes (git gc, `.venv`, `__pycache__` churn) — don't suggest moving it out.
- For anything Léon frames around real data-loss risk ("in case I lose everything"), don't assume the narrowest interpretation of the request — confirm scope, and afterward name exactly what was done/saved rather than a generic "all done."
