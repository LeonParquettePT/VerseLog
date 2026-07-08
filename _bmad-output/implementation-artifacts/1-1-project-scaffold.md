---
baseline_commit: 194e95f8a0f4993976efb462219d2a84f119a535
---

# Story 1.1: Project Scaffold

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a contributor,
I want the project scaffolded per the Ports & Adapters architecture,
so that features can be built on a consistent structure instead of everyone inventing their own.

## Acceptance Criteria

1. **Given** an empty repository, **when** the scaffold is created, **then** `core/`, `adapters/{capture,datasource,trigger,ui}/`, `data/`, `tests/` exist with the port interfaces defined. [Source: epics.md#Story-1.1]
2. **And** a passing "hello world" test runs against the scaffold. [Source: epics.md#Story-1.1]

## Tasks / Subtasks

- [ ] Task 1: Initialize Python packaging (AC: #1)
  - [ ] Create `pyproject.toml` at repo root: project metadata, `requires-python = ">=3.12"`, `pytest` as a dev dependency, `[tool.pytest.ini_options]` with `testpaths = ["tests"]`
  - [ ] Use the **src layout**: package code lives under `src/verselog/`, tests under a sibling `tests/` — do not put package code at repo root or tests inside the package
- [ ] Task 2: Create the domain core and port interfaces (AC: #1)
  - [ ] `src/verselog/core/__init__.py`
  - [ ] `src/verselog/core/contract.py` — the `Contract` dataclass: `departure: str`, `arrival: str`, `scu: int`, `reward: float`, `remaining_time: str | None`. This is the **only** shape allowed to cross a port boundary — do not create parallel/competing data shapes in adapters.
  - [ ] `src/verselog/core/ports/__init__.py`
  - [ ] `src/verselog/core/ports/capture_port.py` — abstract `CapturePort` (one method stub, e.g. `capture(self) -> Contract`)
  - [ ] `src/verselog/core/ports/datasource_port.py` — abstract `DataSourcePort` (stub only — concrete needs arrive in Epic 2 Story 2.1)
  - [ ] `src/verselog/core/ports/trigger_port.py` — abstract `TriggerPort` (stub only — concrete needs arrive in Stories 1.2/1.4)
  - [ ] `src/verselog/core/ports/ui_port.py` — abstract `UIPort` (stub only — concrete needs arrive in later stories, see Dev Notes gap below)
  - [ ] Use Python's `abc.ABC` + `@abstractmethod` (stdlib, no new dependency) for every port
- [ ] Task 3: Create empty adapter packages (AC: #1)
  - [ ] `src/verselog/adapters/__init__.py`
  - [ ] `src/verselog/adapters/capture/__init__.py`
  - [ ] `src/verselog/adapters/datasource/__init__.py`
  - [ ] `src/verselog/adapters/trigger/__init__.py`
  - [ ] `src/verselog/adapters/ui/__init__.py`
  - [ ] No concrete adapter classes yet — empty packages only, ready for the stories that populate them
- [ ] Task 4: Create the local data directory (AC: #1)
  - [ ] `data/.gitkeep` at repo root (sibling of `src/`, not inside the package — it holds the runtime SQLite file created later by Epic 2 Story 2.1, not source code)
- [ ] Task 5: Write and pass the scaffold test (AC: #2)
  - [ ] `tests/__init__.py`
  - [ ] `tests/test_scaffold.py` — imports `verselog.core.contract.Contract`, constructs one with dummy values, asserts its fields round-trip; this proves the src-layout package installs/imports correctly, which is the actual value of a "hello world" test at this layer, not a trivial `assert True`
  - [ ] Run `pytest` and confirm it passes

## Dev Notes

- **Paradigm:** Ports & Adapters (Hexagonal). The domain core (`core/`) must never import a concrete adapter module; adapters depend on core-defined port interfaces, never the reverse. [Source: ARCHITECTURE-SPINE.md#AD-1]
- **Runtime:** Python 3.12+ floor (current stable is 3.14.6; 3.12 is the safe compatibility floor since OCR/vision-model library ecosystems lag the newest Python release). [Source: ARCHITECTURE-SPINE.md#AD-2] — verified current via web search during this story's creation (2026).
- **Naming convention:** ports are named `<Noun>Port`; concrete adapters (added in later stories) are named `<Tech><Noun>Adapter`, e.g. `OllamaVisionAdapter`, `TesseractOCRAdapter`. [Source: ARCHITECTURE-SPINE.md#Consistency-Conventions]
- **Contract model:** one shape only, crossing every port boundary — do not let any adapter define its own competing contract-like shape. [Source: ARCHITECTURE-SPINE.md#Consistency-Conventions]
- **Packaging/testing choice made in this story** (Architecture Spine deliberately deferred exact packaging/test-framework choice — this story fills that seed): src layout + `pyproject.toml` + pytest is 2026's standard Python project structure (verified via web search) — package under `src/verselog/`, tests in a sibling `tests/` directory, pytest config centralized in `pyproject.toml`'s `[tool.pytest.ini_options]` rather than a separate `pytest.ini`/`setup.cfg`.
- **`data/` is not package code:** it lives at repo root as a sibling of `src/` and `tests/`, matching the Architecture Spine's structural seed exactly — it's a runtime-data location (the local SQLite file arrives in Epic 2 Story 2.1), not something importable.
- **No concrete adapters in this story.** Every adapter subfolder is intentionally empty (just `__init__.py`). Populating `capture/` starts at Story 1.2, `trigger/` at Story 1.2/1.4, `datasource/` at Epic 2 Story 2.1. Do not pre-build functionality for future stories — that violates the "create only what's needed" principle validated at the readiness-check stage.
- **Coding style:** plain, direct code; comment only non-obvious "why," never restate what the code already says; no defensive handling for cases that cannot occur. [Source: CONTRIBUTING.md#Ground-rules] This applies to the scaffold too — e.g. don't add error handling around the dataclass construction in the test; a `Contract(...)` call either works or the test fails, no need to wrap it.
- **License/attribution header:** none required — MIT license is declared once at repo root (`LICENSE`); do not add per-file license headers, that's not this project's convention.

### Project Structure Notes

- No conflicts detected between the Architecture Spine's named tree and current Python packaging convention — the spine's `core/`, `adapters/*/`, `data/`, `tests/` names are preserved exactly; the only addition this story makes is nesting the importable package under `src/verselog/` (spine left exact packaging as Seed/Deferred, so this is filling a gap, not overriding a decision).
- Final tree after this story:

```text
verselog/                      (repo root — already has README, LICENSE, CONTRIBUTING, RISKS, .gitignore)
  pyproject.toml
  src/
    verselog/
      __init__.py
      core/
        __init__.py
        contract.py
        ports/
          __init__.py
          capture_port.py
          datasource_port.py
          trigger_port.py
          ui_port.py
      adapters/
        __init__.py
        capture/__init__.py
        datasource/__init__.py
        trigger/__init__.py
        ui/__init__.py
  data/
    .gitkeep
  tests/
    __init__.py
    test_scaffold.py
```

### References

- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Design-Paradigm] — Ports & Adapters, core never imports a concrete adapter
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#AD-2] — Python 3.12+ floor
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Consistency-Conventions] — naming convention, single Contract model
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Structural-Seed] — the named directory tree this story creates
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.1] — this story's acceptance criteria, verbatim
- [Source: CONTRIBUTING.md#Ground-rules] — plain/direct code convention
- Web search (2026): src-layout + `pyproject.toml` + pytest confirmed as current Python project-structure best practice (Real Python, pyopensci.org, pytest docs)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
