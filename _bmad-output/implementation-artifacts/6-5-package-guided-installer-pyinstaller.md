---
baseline_commit: 8a2ec9b
---

# Story 6.5: Package the Guided Installer (PyInstaller)

Status: done

## Story

As a player who wants a guided install experience instead of a bare `verselog.exe`,
I want the installer wizard itself distributed as a single downloadable Windows executable,
so that I don't need Python installed to run the installer any more than I need it to run VerseLog itself.

## Acceptance Criteria

1. **Given** Stories 6.1–6.3 have produced a functionally complete Tkinter wizard (`verselog_installer/__main__.py`) that is only runnable from source today, **when** the packaging build runs, **then** it produces a single Windows executable (`verselog-installer.exe`) that launches the full wizard (Welcome → Benchmark → Component Selection → Finish) without a separately-installed Python, **and** the executable is published as a GitHub Release asset (following Story 5.1's precedent — not committed into the repository itself), **and** `verselog.exe` and `verselog-installer.exe` remain two separate downloadable files — the installer's Finish-step shortcut still points at wherever `verselog.exe` is placed alongside it, exactly as Story 6.3 already assumed. [Source: epics.md#Story-6.5]

## Tasks / Subtasks

- [x] Task 1: Produce a working single-file Windows executable for the installer (AC: #1)
  - [x] Build command: `pyinstaller --onefile --windowed --name verselog-installer --paths src src/verselog_installer/__main__.py` (`--windowed`, not `--console`: unlike Story 5.1's `verselog.exe`, `__main__.py` here takes no CLI arguments at all — a pure Tkinter GUI flow, so a dangling console window behind the wizard would be pure noise, not a safety net). Build succeeded cleanly: `dist/verselog-installer.exe`, ~27.8 MB, PyInstaller's own `hook-_tkinter.py` processed with no errors or warnings beyond the pre-existing, harmless `tzdata` hidden-import notice already seen on Story 5.1's build.
  - [x] Verify the built `dist/verselog-installer.exe` actually runs: **blocked by Windows Smart App Control** on this machine — every launch attempt (direct `subprocess.Popen`, `Start-Process`) was refused with "Une stratégie de contrôle d'application a bloqué ce fichier", confirmed via `Get-WinEvent` (Code Integrity Policy ID `{0283ac0f-fff1-49ae-ada1-8a933130cad6}`, "did not meet the Enterprise signing level requirements"). This is the exact same known limitation Story 5.1 already documented for `verselog.exe` (unsigned PyInstaller binaries) — confirmed with the user, who declined to toggle Smart App Control off for this verification. Direct launch+screenshot evidence is not available for this story as a result; see Debug Log for the indirect verification relied on instead.
- [x] Task 2: Publish via GitHub Release, not committed to the repo (AC: #1) — done AFTER this PR merged to main, not on the feature branch (mirrors Story 5.1's Task 3 precedent: a Release should tag the actual merged state).
  - [x] Uploaded `dist/verselog-installer.exe` to the existing `v0.1.0-windows` GitHub Release, alongside `verselog.exe`. Rewrote the release notes to lead with the installer as the recommended download, with `verselog.exe` kept as the direct/no-wizard option; also corrected a stale line claiming Linux packaging was "tracked for later" (Story 5.2 shipped it separately, `v0.1.0-linux` already exists).
  - [x] Updated `docs/index.html` (installer listed first, marked "recommended", direct `verselog.exe` kept as a second row) and both `README.md`/`README.fr.md` (same ordering, plus refreshed stale project stats — 4 epics/25 stories/176 tests — that hadn't been touched since an earlier story).
  - Note: rebuilding `verselog.exe` itself (its current Release asset predates Stories 5.3/5.5/5.6, already flagged in `SESSION-STATUS.md`) is explicitly out of scope here — confirmed with the user this is a separate, later action, not bundled into this story.
- [x] Task 3: Tests (AC: #1)
  - [x] No new unit tests for the PyInstaller build step itself — same reasoning as Story 5.1: it's a packaging/build-tooling step, not application logic, nothing meaningful to unit-test beyond actually running the binary. Full existing suite re-confirmed green (`176 passed`) to make sure the build process touched nothing application-facing.

## Dev Notes

- **Why `--windowed` here but `--console` in Story 5.1:** `verselog.exe`'s `__main__.py` has a required `--ship` CLI argument with no default — Story 5.1 deliberately kept a console so a missing/wrong argument still prints a visible error. `verselog_installer`'s `__main__.py` (see File List/references below) takes zero CLI arguments; it is a pure Tkinter wizard from the first frame to the last. A console window behind it would only be visual noise, working against the "native installer feel" this whole epic is modeled on (Python's own installer, VMware Workstation's — neither shows a console).
- **Two separate executables, deliberately:** this project's Ports & Adapters boundary (`verselog_installer` may import FROM `verselog.core`/`verselog.adapters`, never the reverse) already ensures a bug in one package can't break the other at the source level. Packaging them as two separate PyInstaller builds carries that same isolation through to the shipped binaries — a broken installer build can never brick the already-working `verselog.exe`, and vice versa.
- **`verselog-installer.spec`/`build/`/`dist/` stay gitignored**, matching Story 5.1's existing `.gitignore` entries (`build/`, `dist/`, `*.spec`) — no new `.gitignore` changes needed here, the existing wildcard already covers a second `.spec` file.
- **Where `verselog.exe` is assumed to live, revisited:** Story 6.3's `FinishStep` already defaults its shortcut's target to `Path(sys.executable).parent / "verselog.exe"` when frozen — i.e., it assumes `verselog-installer.exe` and `verselog.exe` are distributed side by side in the same folder. This story doesn't change that assumption or copy `verselog.exe` anywhere; it only makes the installer itself a real downloadable binary. A player who runs the installer and then wants the shortcut to work must place both executables in the same folder — worth stating plainly in the Release notes/docs, not silently assumed.
- **Coding style:** N/A — this story is a packaging/build-tooling step, no application source changes expected (see Story 5.1's own precedent for the same distinction). [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds no new application source files. Produces `dist/verselog-installer.exe` (gitignored, published as a GitHub Release asset only) and a local `verselog-installer.spec` (gitignored, matching the existing `*.spec` wildcard). Modifies `docs/index.html` (post-merge, download links) and possibly `README.md`/`README.fr.md` if they need the new download mentioned.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-6.5] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/5-1-windows-packaging-pyinstaller.md] — the precedent this story follows: PyInstaller `--onefile`, GitHub Release (not committed binary) published as a post-merge follow-up, docs updated with the real download link
- [Source: _bmad-output/implementation-artifacts/6-3-finish-screen-shortcut.md] — the shortcut target-path assumption (`verselog.exe` alongside the installer's own executable) that this story's packaging must remain consistent with

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run pyinstaller --onefile --windowed --name verselog-installer --paths src src/verselog_installer/__main__.py` → build succeeded, `dist/verselog-installer.exe` (~27.8 MB).
- Direct launch attempts (`subprocess.Popen`, PowerShell `Start-Process`) both blocked by Windows Smart App Control — confirmed via `Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational'`: "did not meet the Enterprise signing level requirements" (Code Integrity events 3033/3077/3118). Asked the user whether to temporarily disable Smart App Control for a real launch+screenshot verification; declined. Documented as the same known, already-accepted limitation from Story 5.1 rather than worked around.
- `uv run --extra dev pytest -q` → `176 passed` (unchanged from Story 6.3's baseline — this story adds no application source code).

### Completion Notes List

- Built `dist/verselog-installer.exe` via PyInstaller `--onefile --windowed` (windowed, not console — unlike `verselog.exe`, this entrypoint takes no CLI arguments at all, so a console window would only be visual noise behind the wizard).
- Direct runtime verification (launch + screenshot) is not available for this story: Windows Smart App Control blocks the freshly-built, unsigned exe on this machine, confirmed via Windows event log detail, and the user declined to toggle Smart App Control off just for this check. This is the exact same limitation already documented in Story 5.1 for `verselog.exe` — not a new or story-specific defect. Confidence in a working build instead comes from: the build completing with no errors (PyInstaller's own `_tkinter` hook processed cleanly), and every step class (`WelcomeStep`, `BenchmarkStep`, `ComponentSelectionStep`, `FinishStep`) already having real, source-run screenshot verification during Stories 6.1–6.3.
- Task 2 (GitHub Release publishing + docs update) is deliberately not done in this PR — mirrors Story 5.1's own precedent: a Release should tag the actual merged `main` state, not an in-progress feature branch. Will be completed as a follow-up immediately after this PR merges, then the story marked fully done.
- No application source files changed — this is a packaging/build-tooling story only, same as Story 5.1. 176/176 tests passing (unchanged).

### File List

- No application source files added or modified.
- `dist/verselog-installer.exe` (gitignored build output — not committed, published as a GitHub Release asset)
- `verselog-installer.spec` (gitignored, PyInstaller-generated, matches the existing `*.spec` wildcard)
- `docs/index.html` (modified, post-merge — installer listed first/recommended, direct `verselog.exe` link kept)
- `README.md` / `README.fr.md` (modified, post-merge — same download ordering, refreshed stale project stats)

## Change Log

- 2026-07-13: Story created — packaging the guided installer wizard itself as `verselog-installer.exe`, the piece every prior Epic 6 story deliberately deferred until now.
- 2026-07-13: Task 1 done — built `verselog-installer.exe` via PyInstaller `--onefile --windowed`. Direct launch verification blocked by Windows Smart App Control (same known limitation as Story 5.1); user confirmed not to disable it for this check. 176/176 tests passing (no application code changed). Status moved to review; Task 2 (Release publishing) deliberately deferred to a post-merge follow-up.
- 2026-07-13: Task 2 completed post-merge — `verselog-installer.exe` uploaded to the existing `v0.1.0-windows` Release, notes rewritten to recommend it first; `docs/index.html` and both READMEs updated the same way, per the user's explicit request to make the installer the prioritized download. Rebuilding the stale `verselog.exe` asset itself confirmed out of scope for this story. Status moved to done.
