---
baseline_commit: aedab3f
---

# Story 5.2: Linux Packaging (via GitHub Actions)

Status: done

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
- [x] Task 2: Publish via GitHub Release, not committed to the repo (AC: #1) — done AFTER this PR merged to main (`workflow_dispatch` from `main`, run 29248135117, success), not on the feature branch, same reasoning as Story 5.1's Task 3.
  - [x] Created GitHub Release `v0.1.0-linux` (tagging merged `main` commit `71f9784`) with the `verselog-linux` binary attached as a release asset (built from the post-merge run, not the earlier feature-branch builds — those were discarded).
  - [x] Release notes mirror Story 5.1's Windows release notes structure: Tesseract/Ollama separate installs, `chmod +x` reminder, links to the companion Windows release, and an honest note that CI-only verification is done and Task 3's real-desktop verification is still pending (no caveat invented beyond what's actually true at this point).
  - [x] Updated `docs/index.html` and both `README.md`/`README.fr.md` with a Linux download row/line alongside the existing Windows one. Also fixed a real latent bug found while doing this: the Windows download link used `/releases/latest`, which — now that a newer `v0.1.0-linux` release exists — would silently point Windows users at the Linux binary. Changed both links to explicit `/releases/tag/v0.1.0-windows` and `/releases/tag/v0.1.0-linux` URLs.
- [x] Task 3: Manual verification on a real Linux desktop (AC: #1) — **done by the project author on a real Ubuntu VM (VMware Workstation)**, not something the dev agent could complete itself.
  - [x] Downloaded `verselog-linux` from the `v0.1.0-linux` release and ran it on a fresh Ubuntu 24.04 Desktop VM: `chmod +x verselog-linux && ./verselog-linux --ship "..."` — the Tkinter results window rendered correctly on the real display, confirming the GUI works end-to-end on Linux, not just headlessly in CI.
  - [x] First run surfaced a real, expected finding rather than a bug: Ollama was installed but its vision model (`qwen2.5vl:3b`) hadn't been pulled yet, producing "status code 404" inside the quarantine message. Not a packaging defect — a fresh Ollama install has zero models by default. This exact scenario is now separately detected and explained upfront by Story 5.3's prerequisite check (built immediately after, directly informed by this finding).
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
- Code review flagged `runs-on: ubuntu-latest` as an unpinned dependency on whatever Python version the runner image ships, risking a future silent break with no local repro. Fixed by pinning to `ubuntu-24.04`; re-verified with workflow run 29247574525 (temporary push-trigger again, commit 099c6ab) — full success, same as before.
- PR #26 merged to `main` (commit 71f9784). Dispatched the real post-merge build via `gh workflow run build-linux.yml --ref main` — run 29248135117, full success, first time `workflow_dispatch` actually worked (the workflow now exists on the default branch).
- Downloaded the post-merge artifact (30,532,944 bytes), created git tag `v0.1.0-linux` on `main`, published GitHub Release `v0.1.0-linux` with the binary attached (`gh release create`).
- While updating `docs/index.html`'s download links, found a real latent bug: the Windows row used `/releases/latest`, which — the instant `v0.1.0-linux` was published as a newer release — would have silently redirected Windows users to the Linux binary. Fixed both platform links to explicit `/releases/tag/...` URLs before this could confuse anyone.
- Project author ran the real binary on a fresh Ubuntu 24.04 Desktop VM (VMware Workstation): `chmod +x verselog-linux && ./verselog-linux --ship "..."` — the Tkinter results window rendered correctly on a real display. First attempt surfaced Ollama's vision model not being pulled yet on the fresh VM ("status code 404"), which directly informed Story 5.3's later extension (detecting this exact case as its own distinct, clearly-worded prerequisite).

### Completion Notes List

- Implemented all 4 tasks: Task 1 (GitHub Actions Linux build workflow), Task 2 (post-merge Release publishing + docs/README updates), Task 3 (manual verification, done by the project author on a real Ubuntu VM — confirmed the Tkinter window renders correctly on Linux), and Task 4 (test suite regression check).
- Real, corrected finding (build-time): the story's own Dev Notes originally proposed installing `tk-dev` before `uv sync` to fix `tkinter` on the Linux runner, based on a GitHub issue describing a *different* symptom (`TclError`, not `ModuleNotFoundError`). Actually running it in CI proved that plan wrong on the first attempt — the real fix is using the system Python (`python3-tk` + `uv sync --python-preference only-system`) instead of uv's own managed Python build, which doesn't ship a working tkinter regardless of system `tk-dev`. Both the failing and the fixed workflow runs are logged above; the Dev Notes section has been corrected in place rather than left wrong.
- Real, corrected finding (docs-time): `docs/index.html`'s Windows download link used `/releases/latest`, which broke the instant a newer Linux release was published. Fixed to explicit tagged URLs for both platforms.
- 114/114 tests passing, no application code changed by this story.

### File List

- `.github/workflows/build-linux.yml` (new)
- `_bmad-output/implementation-artifacts/5-2-linux-packaging-deferred.md` (this file)
- `docs/index.html` (modified, post-merge — Linux download row added, both platform links fixed to explicit tags)
- `README.md` / `README.fr.md` (modified, post-merge — Linux download link added)

## Change Log

- 2026-07-13: Story implemented — `.github/workflows/build-linux.yml` added and verified working via real CI runs (one failing, two fixed/passing) on the feature branch using a temporary push trigger, since `workflow_dispatch` requires the workflow to exist on `main` first. Real gotcha found and corrected: `uv`'s managed Python lacks working tkinter on Linux regardless of `tk-dev`; fixed by using the system Python instead. Code review fix: pinned `ubuntu-latest` to `ubuntu-24.04`. 114/114 tests passing, status moved to review, PR #26 merged.
- 2026-07-13: Post-merge — dispatched the real build from `main`, published GitHub Release `v0.1.0-linux` with the binary attached, updated docs/READMEs (also fixing a real latent bug: the Windows download link used `/releases/latest`, which a newer Linux release would have hijacked).
- 2026-07-13: Task 3 completed — project author verified the real binary on a fresh Ubuntu 24.04 Desktop VM, confirming the Tkinter results window renders correctly. Story fully verified end-to-end on both platforms; marked done.
