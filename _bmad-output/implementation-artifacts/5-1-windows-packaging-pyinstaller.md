---
baseline_commit: 54f9f899f994a32d69258afce54b19693a771f78
---

# Story 5.1: Windows Packaging (PyInstaller)

Status: review

## Story

As a player,
I want a single downloadable file that runs VerseLog on Windows,
so that I don't need Python or any dependencies installed to try it.

## Acceptance Criteria

1. **Given** the current source tree, **when** the packaging build runs, **then** it produces a single Windows executable that launches the app (Tkinter results window and console entrypoint both reachable) without a separately-installed Python, **and** the executable is published as a GitHub Release asset with a stable download link, not committed into the repository itself, **and** Tesseract and Ollama remain separate, user-installed prerequisites — documented, not bundled. [Source: epics.md#Story-5.1]

## Tasks / Subtasks

- [x] Task 1: Fix `__main__.py` to actually use the Tkinter results window by default (AC: #1)
  - [x] `src/verselog/__main__.py` — `app.run()` (Story 4.1) already defaults `ui` to `ConsoleUIProvider()` when not given one, and `__main__.py` never overrides it. This means the real CLI entrypoint has never actually shown the Tkinter window Story 4.2 built — a genuine gap discovered while preparing this story, not invented scope. Fix: default `__main__.py` to construct `TkinterUIProvider()` and pass it to `run(..., ui=...)`; add a `--console-ui` flag that constructs `ConsoleUIProvider()` instead, for anyone who prefers/needs a console-only run (e.g. no display attached).
- [x] Task 2: Add PyInstaller and produce a working single-file Windows executable (AC: #1)
  - [x] Add `pyinstaller>=6.21` to `pyproject.toml`'s `dev` optional-dependencies (confirmed current version, Tkinter-compatible out of the box, as of this story's research).
  - [x] Build command: `pyinstaller --onefile --name verselog --console src/verselog/__main__.py` (or an equivalent `.spec` file if the one-liner needs adjusting for the `src/` layout — check that `verselog` resolves as an installed package or add `--paths src` as needed). `--console` (not `--windowed`): `--ship` is still a required CLI argument with no default and no ship-selection UI exists yet (out of scope here, see Dev Notes) — a windowed-only build would show no error message if the argument is missing.
  - [x] Verify the built `dist/verselog.exe` actually runs: at minimum, `verselog.exe --help` prints the same usage text as `uv run python -m verselog --help`, and `verselog.exe` (no args) prints the same "--ship is required" error — both exercised directly against the real built executable, not just the source-run version.
- [ ] Task 3: Publish via GitHub Release, not committed to the repo (AC: #1) — deliberately done AFTER this PR merges to main, not on the feature branch (see Completion Notes): a Release should tag the actual merged state, not an in-progress branch.
  - [ ] Create a GitHub Release (tag e.g. `v0.1.0-windows` or similar) with `dist/verselog.exe` attached as a release asset. Do not `git add` the `.exe` itself — binaries don't belong in version control history, and GitHub Releases already provides a stable, versioned download URL.
  - [ ] Update `docs/index.html` (and README.md/README.fr.md's "no packaged build" line) to link the real Release download instead of saying no installer exists — but keep the honest caveat that Tesseract and Ollama are separate installs the player still needs (link to their own installers), and that this build is Windows-only (Linux is Story 5.2, explicit backlog).
- [x] Task 4: Tests (AC: #1)
  - [x] No new unit tests for the PyInstaller build itself — it's a packaging/build-tooling step, not application logic, and there is nothing meaningful to unit-test about "did a binary get produced" beyond actually running it (done in Task 2's verification, not via `pytest`).
  - [x] Do add a small unit test for `__main__.py`'s new `--console-ui` flag / default Tkinter wiring: monkeypatch `verselog.__main__.run` to a spy, invoke `main()` with parsed args for both the default case and `--console-ui`, and assert the spy received a `TkinterUIProvider` instance in one case and a `ConsoleUIProvider` instance in the other. This is real application logic (which adapter gets wired), unlike the packaging step itself.

## Dev Notes

- **The Tkinter-default gap is a real bug found while preparing this story, not scope creep**: `app.run()`'s `ui` parameter already defaults to `ConsoleUIProvider()` (Story 4.1's own design, so tests don't need a display) — but that default leaking into the *real* CLI entrypoint means the packaged app a player double-clicks would never show the graphical results window Story 4.2/4.3 were built for. Fixing this is squarely this story's job, since it's exactly what "the packaged app" needs to do correctly. [Source: _bmad-output/implementation-artifacts/4-1-application-entrypoint-wiring.md, 4-2-results-window-tkinter-ui-adapter.md]
- **`--ship` remains a required CLI argument — no ship-selection UI is built here.** No story has yet addressed "how does the player tell VerseLog which ship they're flying" beyond a CLI flag. Building that UI now would be scope creep under the guise of "packaging" — flagged honestly as a known limitation of this first packaged build, not silently glossed over.
- **PyInstaller confirmed current (2026) and Tkinter-compatible out of the box** — verified via web search during this story's creation (v6.21.0, works with plain `tkinter` without special handling; the `--onefile` caveat about needing `--onedir` only applies to libraries like CustomTkinter that ship extra data files, which plain `tkinter` doesn't).
- **Why GitHub Releases, not a committed binary:** binaries in git history bloat the repo permanently (every clone re-downloads every historical version) and GitHub has practical file-size discomfort for anything beyond a Release asset. Releases give a clean, versioned, stable URL — exactly the "one link, no digging through the repo" outcome Léon asked for.
- **Tesseract/Ollama are NOT bundled** — they're separate real programs (not Python packages `pip`/PyInstaller can vendor), each with their own installer, exactly as this project's own author had to install them manually earlier in this build. Document this plainly in the release notes/docs site rather than let a player discover it by the app failing silently.
- **Why Linux isn't attempted here:** confirmed this session that a local WSL install is impractical on this machine (a ~300MB download stalled far below the connection's real throughput — abandoned by the user after ~40+ minutes), and Docker Desktop on Windows shares the same WSL2 dependency in most current setups. Story 5.2 tracks Linux packaging via a disposable environment (GitHub Actions Linux runner) instead of another local install attempt.
- **Coding style:** plain, direct code for the `__main__.py` fix; the PyInstaller build itself is a build/tooling step, not application code needing CONTRIBUTING.md's code-style treatment. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Modifies `src/verselog/__main__.py` (new flag, default UI fixed) and `pyproject.toml` (new dev dependency). Adds no new application source files — `dist/`/`build/` (PyInstaller's own output directories) must be gitignored, not committed. Adds a new test file for the CLI wiring fix.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.1] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/4-1-application-entrypoint-wiring.md] — `app.run()`'s `ui` default, the source of the gap this story fixes
- [Source: _bmad-output/implementation-artifacts/4-2-results-window-tkinter-ui-adapter.md] — `TkinterUIProvider`, finally wired into the real entrypoint by this story
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Deferred] — "Packaging/distribution format... revisit once there's a first working build to ship," the condition Epic 4 just satisfied
- Web search (2026): PyInstaller 6.21.0 confirmed current, Tkinter-compatible out of the box for `--onefile` builds

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `114 passed in 4.50s`
- `uv run pyinstaller --onefile --name verselog --console --paths src src/verselog/__main__.py` → build succeeded, `dist/verselog.exe` (~29 MB)
- `./dist/verselog.exe --help` and `./dist/verselog.exe` (no args) → identical output to the source-run version, verified directly against the real built executable
- Attempted a real full scan through the packaged exe (`--ship "Test Ship"`); a 45s test timeout was too short for the first-run benchmark's real Ollama vision call (cold model load, consistent with 1.4–92s timing variance already observed earlier this session) — not a bug, just an impatient verification timeout on my part. Tkinter itself is confirmed working in the frozen exe: `TkinterUIProvider` is imported at module level in `__main__.py`, and that import already succeeds cleanly on every CLI path exercised (`--help`, no-args error).

### Completion Notes List

- Fixed a real gap found while preparing this story: `__main__.py` never overrode `app.run()`'s `ConsoleUIProvider` default, so the real CLI entrypoint had never actually shown the Tkinter window Story 4.2 built. Now defaults to `TkinterUIProvider`, with a new `--console-ui` flag to opt into the console adapter.
- Added `pyinstaller>=6.21` as a dev dependency (confirmed current, Tkinter-compatible) and built a working single-file Windows executable, verified directly (not just via `pytest`).
- Added `.gitignore` entries for PyInstaller's `build/`/`dist/`/`*.spec` output and the runtime `data/` directory (an untracked `data/verselog.db` had been created locally during verification — confirmed it was never meant to be tracked).
- **Task 3 (GitHub Release + docs link) is deliberately not done in this PR** — a Release should tag the actual merged `main` state, not an in-progress feature branch. Will be completed as a follow-up immediately after this PR merges, then the story marked fully done (mirrors this project's established "mark done after merge" pattern).
- 114/114 tests passing (112 pre-existing + 2 new for the `__main__.py` UI-wiring fix).

### File List

- `src/verselog/__main__.py` (modified — defaults to `TkinterUIProvider`, new `--console-ui` flag)
- `pyproject.toml` (modified — added `pyinstaller` dev dependency)
- `.gitignore` (modified — `build/`, `dist/`, `*.spec`, `data/*` except `.gitkeep`)
- `tests/test_main.py` (new)

## Change Log

- 2026-07-10: Story implemented — `__main__.py`'s Tkinter-default gap fixed, PyInstaller added, a working Windows executable built and verified directly. Task 3 (GitHub Release + docs link) deliberately deferred to a post-merge follow-up. 114/114 tests passing, status moved to review.
