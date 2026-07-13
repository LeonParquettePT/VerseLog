---
baseline_commit: aedab3f
---

# Story 5.2: Linux Packaging (via GitHub Actions)

Status: ready-for-dev

## Story

As a Linux player,
I want an installable VerseLog build for my platform too,
so that I'm not a second-class target despite NFR7 naming Linux explicitly.

## Acceptance Criteria

1. **Given** no Linux build environment was available locally when Epic 5 started (WSL install proved impractically slow on this machine; Docker Desktop on Windows has the same underlying dependency), **when** a GitHub Actions Linux runner (a disposable, no-local-footprint build environment) is set up and manually triggered, **then** it produces a single Linux executable that launches the app (Tkinter results window and console entrypoint both reachable) without a separately-installed Python, **and** the executable is published as a GitHub Release asset with a stable download link, not committed into the repository itself, **and** Tesseract and Ollama remain separate, user-installed prerequisites — documented, not bundled (same posture as Story 5.1). [Source: epics.md#Story-5.2]

## Tasks / Subtasks

- [ ] Task 1: Add a GitHub Actions workflow that builds the Linux executable (AC: #1)
  - [ ] Create `.github/workflows/build-linux.yml`, triggered manually via `workflow_dispatch` (not on every push — matches this project's existing manual, deliberate release cadence from Story 5.1; nobody wants a build/release firing on every commit).
  - [ ] Runner: `ubuntu-latest`. Steps: checkout, install `uv` (`astral-sh/setup-uv` action, or the official install script — verify current recommended method), install Tcl/Tk **system** dev headers BEFORE installing/syncing the Python toolchain (`sudo apt-get update && sudo apt-get install -y tk-dev`) — see Dev Notes on why this order matters, `uv sync --extra dev`, then `uv run pyinstaller --onefile --name verselog --console --paths src src/verselog/__main__.py` (same invocation as Story 5.1's Windows build, just on a Linux runner).
  - [ ] Verify inside the workflow that the built binary actually runs: `./dist/verselog --help` and `./dist/verselog` (no args) should print the same usage/error text as the Windows build's equivalent checks (Story 5.1, Task 2) — fail the workflow step if either check fails or errors unexpectedly.
  - [ ] Upload the built `dist/verselog` binary as a workflow artifact (`actions/upload-artifact`) so it can be downloaded and inspected/attached to a Release without re-running the build.
- [ ] Task 2: Publish via GitHub Release, not committed to the repo (AC: #1)
  - [ ] Create a **new** GitHub Release (e.g. tag `v0.1.0-linux`) — do not reuse or rename the existing `v0.1.0-windows` release/tag, since its name is Windows-specific and renaming an already-published release is an unnecessary, avoidable disruption. Attach the Linux binary (renamed `verselog-linux` for clarity, no extension) as a release asset.
  - [ ] Release notes mirror Story 5.1's Windows release notes structure: Tesseract/Ollama are separate required installs (with the same links), this is a Linux-only build (companion to the Windows one), and any Linux-specific first-run caveats discovered during Task 3's manual verification (e.g. missing system Tk/Tcl on the *user's* machine, executable-bit not set after download, etc. — do not invent caveats, only document what Task 3 actually finds).
  - [ ] Update `docs/index.html` and both `README.md`/`README.fr.md` to add a Linux download row/line alongside the existing Windows one, replacing any remaining "Linux not published yet" wording.
- [ ] Task 3: Manual verification on a real Linux desktop (AC: #1)
  - [ ] Download the built artifact and run it on a real Linux desktop environment (the story author has a VMware Workstation VM with Ubuntu available for exactly this) — confirm the Tkinter results window actually renders on a real display, not just that the binary launches headlessly in CI. CI (Task 1) only proves the binary runs and prints the expected CLI text; it cannot prove the GUI renders, since GitHub Actions runners have no display server.
  - [ ] Document the verification steps taken and the outcome in Completion Notes, same rigor as Story 5.1's direct-verification approach (no claiming success without having actually run it).
- [ ] Task 4: Tests (AC: #1)
  - [ ] No new unit tests for the packaging/CI workflow itself — same reasoning as Story 5.1: this is build tooling, not application logic, and the meaningful verification is actually running the produced binary (Tasks 1 and 3), not something `pytest` can usefully assert.
  - [ ] Run the full existing test suite (`uv run --extra dev pytest -q`) locally on Windows before considering this story done, to confirm nothing in Epic 5's backlog additions (Stories 5.4/5.5/5.6, currently just epics.md entries with no code) has silently broken anything — expect the same 114 passed as Story 5.1 left off, since no application code changes here.

## Dev Notes

- **Why GitHub Actions, not a local Linux environment:** confirmed this session that a local WSL install is impractical on this machine (a ~300MB download stalled far below the connection's real throughput — abandoned by the user after ~40+ minutes), and Docker Desktop on Windows shares the same WSL2 dependency in most current setups. The user explicitly chose a disposable, no-local-footprint CI environment instead, for speed, simplicity, and to avoid any repeat risk to their own machine. [Source: _bmad-output/implementation-artifacts/5-1-windows-packaging-pyinstaller.md#Dev-Notes]
- **Why a plain single-file binary, not an AppImage:** epics.md's AC phrases "an AppImage" as an example ("e.g."), not a hard requirement. PyInstaller's `--onefile` does not natively produce an AppImage — wrapping the output would require an additional tool (e.g. `appimagetool`) and more CI complexity for a convenience most players don't strictly need (desktop-icon integration). Story 5.1 already established the precedent of "plain single executable, not a fancier installer format" for Windows; matching that here keeps the two platforms consistent and avoids scope creep. AppImage wrapping can be revisited later if real Linux players ask for it — same "don't build for unconfirmed demand" posture already used for the tablet/compute-offload architecture decision. [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Deferred]
- **Real gotcha confirmed via web research, must be handled in the workflow:** `uv`'s managed Python (via `python-build-standalone`) does not reliably include working `tkinter`/`_tkinter` bindings on Linux unless the system's Tcl/Tk **development** headers (`tk-dev` on Ubuntu/Debian) are present *before* `uv` installs/links its Python interpreter. Installing `tk-dev` after the fact and re-syncing may not fix it — the safest order is: install `tk-dev` first, then let `uv sync` provision Python, so tkinter linking happens against a system that already has it. If tkinter still isn't importable after that, the documented fallback is `uv python install --reinstall` for the project's Python version. Verify this actually works during Task 1 — don't assume the web research is complete; confirm `uv run python -c "import tkinter"` succeeds in the workflow before running PyInstaller, and fail fast with a clear error if it doesn't (cheaper to debug than a PyInstaller build that silently omits tkinter and fails at runtime on the user's machine instead).
- **CI cannot verify the GUI renders — only that the binary runs and its CLI text is correct.** GitHub Actions `ubuntu-latest` runners have no display server (no X11/Wayland), so `TkinterUIProvider`'s actual window can't be shown or screenshotted there. This is exactly why Task 3's manual verification on a real desktop (the user's own VMware/Ubuntu VM) is a required part of this story, not optional polish — mirrors Story 5.1's own principle of "verified directly against the real built executable, not just source-run."
- **`--console` (not `--windowed`), same reasoning as Story 5.1:** `--ship` is still a required CLI argument (Story 5.5, ship-selection-via-GUI, remains backlog) — a windowed-only build would show no error message if the argument is missing.
- **Tesseract/Ollama are NOT bundled**, exact same reasoning as Story 5.1 — separate real programs, not something PyInstaller can vendor, must be documented plainly.
- **New Release, don't touch `v0.1.0-windows`:** that release/tag name is Windows-specific; renaming it to something platform-neutral now would be a disruptive, unnecessary change to something already published and linked from docs/README. A separate `v0.1.0-linux` tag/release keeps things clean without touching existing links.
- **No code-signing equivalent concern on Linux** (unlike Story 5.4's Windows Smart App Control problem) — Linux doesn't have an equivalent OS-level unsigned-binary block by default, though the user may still need to `chmod +x` the downloaded file and/or approve running an unknown script depending on their desktop environment's file manager. Document whatever Task 3's actual verification finds — don't invent Linux-specific caveats that weren't actually observed.
- **Coding style:** the workflow YAML and any build-tooling changes are build/tooling, not application code — same "not CONTRIBUTING.md code-style territory" reasoning Story 5.1 used for its PyInstaller invocation. [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds `.github/workflows/build-linux.yml` (new). No changes to `src/verselog/` — `__main__.py`'s existing `--console-ui`/default-Tkinter wiring (Story 5.1) already works identically on Linux, since it's pure Python with no OS-specific branches. Modifies `docs/index.html`, `README.md`, `README.fr.md` (new Linux download row, alongside Story 5.1's existing Windows one — don't remove or restructure the Windows content, only add to it).

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.2] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/5-1-windows-packaging-pyinstaller.md] — the Windows build this story mirrors: PyInstaller invocation, `--console` rationale, GitHub Release approach, Tesseract/Ollama-not-bundled posture, and the WSL-abandonment context explaining why CI is used instead of a local Linux environment
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Deferred] — "CI pipeline and testing framework choice — revisit once the source tree has real code to test" (now true) and "Packaging/distribution format... revisit once there's a first working build to ship" (Story 5.1 already satisfied this for Windows; this story extends it to Linux)
- Web research (2026): `uv`-managed Python on Linux needs system `tk-dev` present before Python provisioning for `tkinter` to import correctly — a known, documented gotcha (uv issue tracker), not this story's invention
- Web research (2026): PyInstaller's `--onefile` does not natively produce an AppImage; wrapping requires a separate tool — informs the "plain binary, not AppImage" decision above

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

### Completion Notes List

### File List
