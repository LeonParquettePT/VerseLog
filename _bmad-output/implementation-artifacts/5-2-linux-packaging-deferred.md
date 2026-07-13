---
baseline_commit: aedab3f
---

# Story 5.2: Linux Packaging (via GitHub Actions)

Status: review

## Story

As a Linux player,
I want an installable VerseLog build for my platform too,
so that I'm not a second-class target despite NFR7 naming Linux explicitly.

## Acceptance Criteria

1. **Given** no Linux build environment was available locally when Epic 5 started (WSL install proved impractically slow on this machine; Docker Desktop on Windows has the same underlying dependency), **when** a GitHub Actions Linux runner (a disposable, no-local-footprint build environment) is set up and manually triggered, **then** it produces a single Linux executable that launches the app (Tkinter results window and console entrypoint both reachable) without a separately-installed Python, **and** the executable is published as a GitHub Release asset with a stable download link, not committed into the repository itself, **and** Tesseract and Ollama remain separate, user-installed prerequisites — documented, not bundled (same posture as Story 5.1). [Source: epics.md#Story-5.2]

## Tasks / Subtasks

- [x] Task 1: Add a GitHub Actions workflow that builds the Linux executable (AC: #1)
  - [x] Created `.github/workflows/build-linux.yml`, triggered manually via `workflow_dispatch` (not on every push — matches this project's existing manual, deliberate release cadence from Story 5.1; nobody wants a build/release firing on every commit).
  - [x] Runner: `ubuntu-latest`. Steps: checkout, install `uv` (`astral-sh/setup-uv@v8.3.2`), `uv sync --extra dev --python-preference only-system`, then `uv run pyinstaller --onefile --name verselog --console --paths src src/verselog/__main__.py` (same invocation as Story 5.1's Windows build, just on a Linux runner). **The Dev Notes' original `tk-dev`-before-`uv-sync` plan did not work in practice** — see Debug Log/Completion Notes for the real fix (system Python via `python3-tk` + `--python-preference only-system`, not `tk-dev` + uv's own managed Python).
  - [x] Verified inside the workflow that the built binary actually runs: `./dist/verselog --help` and `./dist/verselog` (no args) print identical usage/error text to the Windows build's equivalent checks (Story 5.1, Task 2) — the workflow step fails if either check fails or errors unexpectedly.
  - [x] Uploads the built `dist/verselog` binary as a workflow artifact (`actions/upload-artifact@v4`) so it can be downloaded and attached to a Release without re-running the build.
- [ ] Task 2: Publish via GitHub Release, not committed to the repo (AC: #1) — **deliberately done AFTER this PR merges to main**, not on the feature branch, same reasoning as Story 5.1's Task 3: a Release should tag the actual merged state, not an in-progress branch. (Practically also required here: `workflow_dispatch` only works once the workflow file exists on the default branch — confirmed by a real `HTTP 404` when attempting it from the feature branch — so the real, final build can only be triggered post-merge anyway.)
  - [ ] Create a **new** GitHub Release (e.g. tag `v0.1.0-linux`) — do not reuse or rename the existing `v0.1.0-windows` release/tag, since its name is Windows-specific and renaming an already-published release is an unnecessary, avoidable disruption. Attach the Linux binary (renamed `verselog-linux` for clarity, no extension) as a release asset.
  - [ ] Release notes mirror Story 5.1's Windows release notes structure: Tesseract/Ollama are separate required installs (with the same links), this is a Linux-only build (companion to the Windows one), and any Linux-specific first-run caveats discovered during Task 3's manual verification (e.g. missing system Tk/Tcl on the *user's* machine, executable-bit not set after download, etc. — do not invent caveats, only document what Task 3 actually finds).
  - [ ] Update `docs/index.html` and both `README.md`/`README.fr.md` to add a Linux download row/line alongside the existing Windows one, replacing any remaining "Linux not published yet" wording.
- [ ] Task 3: Manual verification on a real Linux desktop (AC: #1) — also post-merge, using the artifact from the post-merge build in Task 2
  - [ ] Download the built artifact and run it on a real Linux desktop environment (the story author has a VMware Workstation VM with Ubuntu available for exactly this) — confirm the Tkinter results window actually renders on a real display, not just that the binary launches headlessly in CI. CI (Task 1) only proves the binary runs and prints the expected CLI text; it cannot prove the GUI renders, since GitHub Actions runners have no display server.
  - [ ] Document the verification steps taken and the outcome in Completion Notes, same rigor as Story 5.1's direct-verification approach (no claiming success without having actually run it).
- [x] Task 4: Tests (AC: #1)
  - [x] No new unit tests for the packaging/CI workflow itself — same reasoning as Story 5.1: this is build tooling, not application logic, and the meaningful verification is actually running the produced binary (Tasks 1 and 3), not something `pytest` can usefully assert.
  - [x] Ran the full existing test suite (`uv run --extra dev pytest -q`) locally on Windows: `114 passed in 4.54s` — confirms nothing in Epic 5's backlog additions (Stories 5.4/5.5/5.6, epics.md entries only, no code) broke anything, since this story makes no application code changes.

## Dev Notes

- **Why GitHub Actions, not a local Linux environment:** confirmed this session that a local WSL install is impractical on this machine (a ~300MB download stalled far below the connection's real throughput — abandoned by the user after ~40+ minutes), and Docker Desktop on Windows shares the same WSL2 dependency in most current setups. The user explicitly chose a disposable, no-local-footprint CI environment instead, for speed, simplicity, and to avoid any repeat risk to their own machine. [Source: _bmad-output/implementation-artifacts/5-1-windows-packaging-pyinstaller.md#Dev-Notes]
- **Why a plain single-file binary, not an AppImage:** epics.md's AC phrases "an AppImage" as an example ("e.g."), not a hard requirement. PyInstaller's `--onefile` does not natively produce an AppImage — wrapping the output would require an additional tool (e.g. `appimagetool`) and more CI complexity for a convenience most players don't strictly need (desktop-icon integration). Story 5.1 already established the precedent of "plain single executable, not a fancier installer format" for Windows; matching that here keeps the two platforms consistent and avoids scope creep. AppImage wrapping can be revisited later if real Linux players ask for it — same "don't build for unconfirmed demand" posture already used for the tablet/compute-offload architecture decision. [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Deferred]
- **Real gotcha, confirmed by an actual failed CI run (not just web research):** installing `tk-dev` before `uv sync` (the original plan below, based on a GitHub issue about a different symptom) did **not** fix it — the workflow failed with `ModuleNotFoundError: No module named 'tkinter'`, not the `TclError`/missing-library symptom that `tk-dev` targets. Root cause: `uv`'s own managed Python (`python-build-standalone`) is a portable prebuilt binary; installing system `tk-dev` has no effect on it at all, because it doesn't get compiled locally. **The actual fix:** install `python3-tk` (which wires up a fully working tkinter for Ubuntu's system Python) and tell `uv` to use that system interpreter instead of downloading its own via `uv sync --extra dev --python-preference only-system`. Confirmed working end-to-end in CI: `uv run python -c "import tkinter"` succeeds and the built binary's `--help`/no-args output matches Windows exactly. (Original plan, kept here for the record: "install `tk-dev` before `uv sync` provisions Python" — this was wrong and is superseded by the above.)
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
- Confirmed via a real failed then fixed CI run (2026-07-13, run IDs 29246500167 → 29246686908): `uv`'s own managed Python on Linux lacks a working `tkinter` regardless of system `tk-dev`; using the system Python (`python3-tk` + `uv sync --python-preference only-system`) is the fix that actually worked
- Web research (2026): PyInstaller's `--onefile` does not natively produce an AppImage; wrapping requires a separate tool — informs the "plain binary, not AppImage" decision above

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest -q` → `114 passed in 4.54s`
- Workflow run 29246500167 (temporary push-trigger, commit d5ff720): `Verify tkinter is importable` failed — `ModuleNotFoundError: No module named 'tkinter'` — the `tk-dev`-before-`uv-sync` plan from the original Dev Notes did not work.
- Workflow run 29246686908 (temporary push-trigger, commit 6c3e9ac, after switching to `python3-tk` + `uv sync --python-preference only-system`): full success — tkinter import check passed, PyInstaller build succeeded, `./dist/verselog --help` and `./dist/verselog` (no args) printed output identical to the Windows build's equivalent checks, `verselog-linux` artifact uploaded.
- Downloaded and inspected the `verselog-linux` artifact from run 29246686908 locally (30,532,232 bytes) to confirm the upload step actually produced a real file — then discarded it, since it was built from a pre-merge commit and Task 2/3 will use a fresh post-merge build instead (same principle as Story 5.1's Task 3 deferral).
- Attempted `gh workflow run build-linux.yml --ref story-5.2-linux-packaging` before the workflow existed on `main`: `HTTP 404: workflow build-linux.yml not found on the default branch` — confirmed `workflow_dispatch` cannot be used at all until the workflow file is merged to the default branch, even when targeting a different ref. Used a temporary branch-scoped `push:` trigger to verify on the feature branch instead, then removed it before requesting review.

### Completion Notes List

- Implemented Task 1 (GitHub Actions Linux build workflow) and Task 4 (test suite regression check); Tasks 2 and 3 (Release publishing + manual desktop verification) are deliberately deferred to a post-merge follow-up, mirroring Story 5.1's own "Release should tag merged main" precedent — and practically required here too, since `workflow_dispatch` only works once the workflow exists on `main`.
- Real, corrected finding: the story's own Dev Notes originally proposed installing `tk-dev` before `uv sync` to fix `tkinter` on the Linux runner, based on a GitHub issue describing a *different* symptom (`TclError`, not `ModuleNotFoundError`). Actually running it in CI proved that plan wrong on the first attempt — the real fix is using the system Python (`python3-tk` + `uv sync --python-preference only-system`) instead of uv's own managed Python build, which doesn't ship a working tkinter regardless of system `tk-dev`. Both the failing and the fixed workflow runs are logged above; the Dev Notes section has been corrected in place rather than left wrong.
- 114/114 tests passing, no application code changed by this story.

### File List

- `.github/workflows/build-linux.yml` (new)
- `_bmad-output/implementation-artifacts/5-2-linux-packaging-deferred.md` (this file)

## Change Log

- 2026-07-13: Story implemented — `.github/workflows/build-linux.yml` added and verified working via two real CI runs (one failing, one fixed) on the feature branch using a temporary push trigger, since `workflow_dispatch` requires the workflow to exist on `main` first. Real gotcha found and corrected: `uv`'s managed Python lacks working tkinter on Linux regardless of `tk-dev`; fixed by using the system Python instead. Task 2 (GitHub Release) and Task 3 (manual desktop verification) deliberately deferred to a post-merge follow-up. 114/114 tests passing, status moved to review.
