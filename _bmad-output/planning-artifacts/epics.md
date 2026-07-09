---
stepsCompleted: [step-01, step-02, step-03]
inputDocuments: ["_bmad-output/specs/spec-verselog/SPEC.md", "_bmad-output/specs/spec-verselog/vision-pipeline.md", "_bmad-output/specs/spec-verselog/contract-ui-reference.md", "_bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md"]
---

# VerseLog - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for VerseLog, decomposing the requirements from SPEC.md (this project's Core-module equivalent of a PRD), its companions, and the Architecture Spine into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1 (CAP-1): User can trigger a scan (voice command or manual action) that captures and extracts a contract's data — departure, arrival, SCU, reward, and remaining time when shown — from the game's contract screen.
FR2 (CAP-2): The system never silently trusts an extraction — a suspect result is quarantined instead of accepted, and every calculated suggestion carries a visible confidence indicator.
FR3 (CAP-3): The system benchmarks the host machine to pick an extraction model tier AND a safe parallel-worker count. This runs ONCE at first launch/installation (while the game happens to be running, since an idle-PC reading is misleading) — NOT on every subsequent app or game launch, since hardware doesn't change that often. It only re-runs automatically if a hardware change is detected, or manually when the user clicks "Re-run benchmark" in settings (e.g. after upgrading their PC).
FR4 (CAP-4): User can get a computed route and cargo-loading plan maximizing aUEC/min across one or more accepted contracts, adapted to the selected ship's SCU capacity and legible to all crew sharing it.
FR5 (CAP-5): The system keeps the player's reputation level in sync and requires explicit confirmation before proceeding on a potentially illegal contract.
FR6 (CAP-6): User can trigger a scan by voice command or manual action, with neither required to use the other.
FR7 (CAP-8): User can rely on default per-ship fuel-consumption values, override them if the engine is modified, and reset to defaults.

### NonFunctional Requirements

NFR1: Must run acceptably on modest/low-end PCs; the game is already CPU-bound, so VerseLog must avoid adding meaningful CPU load on top of it.
NFR2: Scan-to-result processing must stay within a user-configurable time budget (default 30s, ideal 15-30s, unacceptable beyond ~60s).
NFR3: No paid cloud API, ever — local inference only, since the tool must stay free.
NFR4: Voice triggering must never be the sole trigger path — manual triggering always available.
NFR5: Open-source and collaborative on GitHub from inception, understandable/correctable by outside contributors from day one.
NFR6: Code must read as human-quality, idiomatic, with no visible AI-generation artifacts.
NFR7: Target platforms are Windows and Linux (no macOS).
NFR8: License is MIT.
NFR9: The UI must be simple and purely functional — easy to find your way around, no over-engineered/"gas factory" complexity, easy to use even for a non-technical player. Recommendations are shown in VerseLog's own separate results window with large, readable text — never as a live overlay tracking the in-game list (rejected: would require continuous screen re-scanning or game-memory reading, both out of scope — see SPEC.md non-goals).

### Additional Requirements

- **Paradigm (Architecture Spine AD-1)**: Ports & Adapters (Hexagonal) — a domain core (trust layer, route/cargo optimizer, config) with zero knowledge of concrete providers; every capture method, data source, trigger, and UI is a swappable adapter.
- **Stack (Architecture Spine)**: Python 3.12+; Ollama for local vision models; Tesseract/pytesseract for classic OCR; SQLite (stdlib) for local reference data; Tkinter (stdlib) as the seed UI, swappable later. No starter template as such (not a web-framework-shaped project) — the Ports & Adapters source tree itself is the starting scaffold for Epic 1 Story 1.
- **Source tree seed**: `core/` (domain + ports), `adapters/capture/`, `adapters/datasource/`, `adapters/trigger/`, `adapters/ui/`, `data/`, `tests/`.
- **Trust-layer ownership (AD-3)**: validation + quarantine + confidence-scoring is ONE domain service every provider's output passes through — not duplicated per-provider.
- **Local reference-data store (AD-4)**: bulk-imported community-API data (cargo capacities, fuel defaults, location data) lives in one local SQLite file.
- **Execution model (AD-5, AD-6)**: single long-running desktop process; capture may run on a 1..N worker pool (N set by the benchmark), but every result is queued into the trust layer serially — no parallel writes to shared quarantine/confidence state.
- **Settings store (AD-7)**: one local settings store (time-budget threshold, reputation level, per-ship engine overrides, benchmark results) owned by the domain core.
- **Provider abstraction (vision-pipeline.md)**: `OCRProvider` / `VisionProvider` (Ollama-backed) / `CommunityAPIProvider` (backed by api.star-citizen.wiki, SQLite-mirrored) / `OfficialAPIProvider` (stub, non-goal for now). Fallback chain: Phi-3-Vision → Moondream2 → classic OCR.
- **Community API integration detail**: `api.star-citizen.wiki` exposes `/api/vehicles` (cargo_capacity, cargo_grids, quantum/fuel fields) and `/api/locations` (starmap, multi-system incl. Pyro). Its per-vehicle example route fields are NOT a real route matrix — real point-to-point cost must be computed from location coordinates + ship stats. Rate limits/redistribution terms are unpublished; proceed under a safe default (attribution, conservative throttling, non-commercial) per SPEC.md assumptions.
- **Bus-factor mitigation**: an independently-hosted mirror of the community API is separate, optional infra — not required for the client app itself to ship.
- **Contract UI reference (contract-ui-reference.md)**: real field layout confirmed — Title, Reward, "Contract Availability" (sometimes `N/A`), Contracted By, Primary Objectives (pickup/delivery locations, SCU as an X/Y pair). In-scope contract categories: Hauling, Mercenary, Bounty Hunter. Out of scope: Collection, Salvage.
- **Deferred (Architecture Spine)**: exact route/knapsack algorithm, SQLite schema details, packaging/distribution format, CI pipeline, test framework choice, VoiceAttack plugin integration mechanics, mirrored-API hosting choice, UI toolkit beyond the Tkinter seed. These are implementation details for epics/stories to resolve, not pre-decided here.
- **Installation/onboarding docs (flagged during epics review, not yet in the architecture)**: once a packaging/distribution format is chosen (currently Deferred), a story must cover producing clear install instructions for end users — tracked here so it isn't forgotten. Not yet actionable as a story since the format itself isn't decided.

### UX Design Requirements

None — no UX design contract exists for this project (not produced; not required per the project's own scope decisions).

### FR Coverage Map

FR1: Epic 1 - contract capture/extraction
FR2: Epic 1 - trust layer (validation/quarantine/confidence)
FR3: Epic 1 - hardware benchmark (model tier + worker count)
FR6: Epic 1 - voice/manual trigger
FR4: Epic 2 - route/cargo optimization
FR7: Epic 2 - per-ship fuel-consumption config
FR5: Epic 3 - reputation/legality confirmation
NFR9 + Success Signal: Epic 4 - application entrypoint & results UI (added 2026-07-09: every other epic's capability was built and tested in isolation, but nothing wires them into one running application yet — this closes that gap. No new FR/CAP; NFR9 already specifies the UI's required properties and SPEC.md's Success Signal already describes the end-to-end experience this epic makes achievable.)
NFR7 (target platforms): Epic 5 - packaging & distribution (added 2026-07-10: ARCHITECTURE-SPINE.md's Deferred list named "packaging/distribution format" as revisit-once-there's-a-first-working-build — Epic 4 just made that true. No new FR/CAP; this makes NFR7's Windows+Linux target actually installable rather than source-only.)

## Epic List

### Epic 1: Reliable Contract Scanning

Player can trigger a scan (voice or manual) of their contract board, on their own hardware, and get back validated, trustworthy extracted contract data — whether scanning one contract or a few dozen at once — within their configured time budget. This is the foundation everything else builds on, and its scaffold (Ports & Adapters source tree, trust layer, first capture provider) is Epic 1 Story 1.
**FRs covered:** FR1, FR2, FR3, FR6

### Epic 2: Route & Cargo Optimization

Using the contract data Epic 1 already validated, the player gets a computed route and cargo-loading plan that maximizes aUEC/min across one or several accepted contracts, adapted to their ship's real SCU capacity, using accurate per-ship fuel-cost data (with override/reset if their engine is modified).
**FRs covered:** FR4, FR7

### Epic 3: Legality & Reputation Safety

Using the contract data Epic 1 already validated, the player is warned and asked to explicitly confirm before proceeding on a contract that may be illegal (e.g. a trespassing zone), based on their reputation level staying in sync automatically.
**FRs covered:** FR5

### Epic 4: Application Entrypoint & Results UI

Every capability from Epics 1–3 (capture, trust layer, route/cargo optimization, legality/reputation) exists and is tested in isolation, but nothing runs them together as one application yet, and no UI adapter exists to show a player anything. This epic wires trigger → capture → trust layer → optimization into a single running app, and gives `UIPort` its first real implementation (a results window and the risky-contract confirmation popup Story 3.2 left as an interface).
**Traces to:** NFR9 (UI must be simple, functional, its own separate window), SPEC.md's Success Signal (the end-to-end experience this epic makes achievable for the first time)

### Epic 5: Packaging & Distribution

VerseLog runs end-to-end (Epic 4) but only from source — no packaged build exists for either target platform. This epic produces a real, installable artifact for Windows now, and tracks Linux packaging as explicit, not-forgotten backlog for when a suitable build environment is available (today's session found local WSL/Docker impractical on this machine; a disposable CI environment, e.g. GitHub Actions, is the likely path).
**Traces to:** NFR7 (target platforms Windows and Linux)

## Epic 1: Reliable Contract Scanning

Player can trigger a scan (voice or manual) of their contract board, on their own hardware, and get back validated, trustworthy extracted contract data — whether scanning one contract or a few dozen at once — within their configured time budget.

### Story 1.1: Project Scaffold

As a contributor,
I want the project scaffolded per the Ports & Adapters architecture,
So that features can be built on a consistent structure instead of everyone inventing their own.

**Acceptance Criteria:**

**Given** an empty repository
**When** the scaffold is created
**Then** `core/`, `adapters/{capture,datasource,trigger,ui}/`, `data/`, `tests/` exist with the port interfaces defined
**And** a passing "hello world" test runs against the scaffold

### Story 1.2: Manual Capture via Classic OCR

As a player,
I want to manually trigger a scan that captures one contract and extracts its data via OCR,
So that I get structured data instead of reading it myself.

**Acceptance Criteria:**

**Given** a contract is visible on screen
**When** the player triggers a manual scan
**Then** departure, arrival, SCU, and reward are extracted into the internal Contract shape via `OCRProvider`

### Story 1.3: Trust Layer — Validation and Quarantine

As a player,
I want every extraction validated before I see it,
So that I can trust the result or know when to double-check it.

**Acceptance Criteria:**

**Given** an extracted contract
**When** a field fails validation (unknown station, non-integer SCU, non-numeric reward)
**Then** it is quarantined (source image kept) and flagged, rather than shown as if trustworthy
**And** a valid extraction shows a visible confidence indicator

### Story 1.4: Voice Trigger (VoiceAttack, Windows)

As a Windows player,
I want to trigger a scan by voice command,
So that I don't have to alt-tab or click while playing.

**Acceptance Criteria:**

**Given** VoiceAttack is configured
**When** the player says the scan command
**Then** the same scan as the manual trigger runs
**And** on Linux, only the manual trigger is available, with no error shown for the missing voice path

### Story 1.5: Local Vision Provider (Ollama)

As a player,
I want a more precise extraction option,
So that OCR errors on tricky UI elements are reduced.

**Acceptance Criteria:**

**Given** Ollama is available locally
**When** `VisionProvider` is selected
**Then** it returns the same Contract shape as `OCRProvider`, swappable behind the same port with no change elsewhere

### Story 1.6: Hardware Benchmark (Model Tier + Worker Count)

As a player,
I want the app to pick the right model and parallelism for my machine once,
So that scanning stays fast without me tuning anything.

**Acceptance Criteria:**

**Given** first launch (while the game is running) or a detected hardware change
**When** the benchmark runs
**Then** it selects a model tier (Vision → OCR fallback) and a safe worker count N, within the configured time budget
**And** a "Re-run benchmark" action exists in settings for manual re-trigger

### Story 1.7: Batch Scanning (Parallel Workers)

As a player facing a full contract board,
I want many contracts scanned at once instead of one by one,
So that I'm not stuck waiting when there are dozens of contracts.

**Acceptance Criteria:**

**Given** N workers from Story 1.6's benchmark
**When** the player scans a batch (e.g. ~30 contracts)
**Then** extraction runs in parallel across up to N workers
**And** every result is still handed to the trust layer (Story 1.3) serially, with no race conditions on quarantine/confidence state

## Epic 2: Route & Cargo Optimization

Using the contract data Epic 1 already validated, the player gets a computed route and cargo-loading plan that maximizes aUEC/min across one or several accepted contracts, adapted to their ship's real SCU capacity, using accurate per-ship fuel-cost data.

### Story 2.1: Reference Data Import (Local SQLite)

As a player,
I want accurate ship and fuel reference data available locally,
So that route calculations aren't guesswork.

**Acceptance Criteria:**

**Given** the app's first setup
**When** the bulk import from `CommunityAPIProvider` runs
**Then** ship cargo capacities and fuel/quantum-drive stats are stored in the local SQLite database, refreshable later

### Story 2.2: Point-to-Point Route Cost Calculation

As a player,
I want the real fuel/time cost of a trip calculated for my ship,
So that I know what a route actually costs.

**Acceptance Criteria:**

**Given** two locations and a ship (any system, e.g. Stanton or Pyro)
**When** a route cost is requested
**Then** it's computed from location coordinates plus that ship's quantum stats — not from a fake precomputed pair

### Story 2.3: Loading Plan Derived From a Single Mission's Route

As a player,
I want the loading order for a single accepted mission to be derived directly from its computed route (Story 2.2),
So that loading and travel are always consistent with each other, not calculated as two separate, possibly conflicting things.

**Acceptance Criteria:**

**Given** one accepted mission and its computed route on a ship with a known SCU capacity
**When** the loading plan is generated
**Then** the loading order follows the LIFO convention against that specific route (last delivery loaded deepest, first delivery nearest the door) — the loading step never runs independently of the route step

### Story 2.4: Combined Route and Loading Plan for Multiple Missions

As a player with several unrelated accepted missions,
I want one combined route and loading plan that avoids unnecessary back-and-forth between systems or galaxies,
So that I don't waste time or fuel on a trip a smarter ordering would have avoided, and I don't have to juggle missions manually.

**Acceptance Criteria:**

**Given** multiple accepted missions sharing one ship, potentially across different locations or star systems
**When** the combined plan is computed
**Then** the route groups nearby stops sensibly instead of zig-zagging back and forth between systems/galaxies when a more direct ordering exists
**And** the loading order (LIFO) is derived from that same optimized route — not computed separately — so cargo is always accessible in the order the ship actually visits locations
**And** the plan stays legible to any crew sharing the ship's cargo slots

### Story 2.5: Fuel Value Override and Reset

As a player who modified their ship's engine,
I want to override the default fuel value and reset it later,
So that calculations stay accurate for my actual setup.

**Acceptance Criteria:**

**Given** a ship with a modified engine
**When** the player sets an override
**Then** route calculations use it instead of the default
**And** a reset action restores the default

## Epic 3: Legality & Reputation Safety

Using the contract data Epic 1 already validated, the player is warned and asked to explicitly confirm before proceeding on a contract that may be illegal, with their reputation staying in sync automatically.

### Story 3.1: Reputation Sync

As a player,
I want my reputation level synced automatically,
So that legality checks are always based on my current standing.

**Acceptance Criteria:**

**Given** the app launches or performs a scan
**When** reputation sync runs
**Then** the current reputation level is detected/updated automatically
**And** the player can manually reconfigure it if it changes mid-session

### Story 3.2: Legality Confirmation Before a Risky Contract

As a player,
I want to be warned before accepting a contract that might be illegal,
So that I can decide knowingly instead of stumbling into trouble.

**Acceptance Criteria:**

**Given** a scanned contract flagged as potentially illegal (e.g. a trespassing zone) based on the synced reputation
**When** the player reviews it
**Then** a popup names the specific risk and requires an explicit accept/decline
**And** the tool honors whichever choice is made rather than silently filtering the contract
**And** the tool never accepts or declines the contract itself — the player always takes the in-game action manually (no input injection, see SPEC.md non-goals)

## Epic 4: Application Entrypoint & Results UI

Every capability from Epics 1–3 exists and is tested in isolation, but nothing runs them together as one application yet, and no UI adapter exists to show a player anything.

### Story 4.1: Application Entrypoint (Wiring)

As a player,
I want to launch VerseLog as one application,
So that triggering a scan runs the whole pipeline instead of me wiring the pieces together myself.

**Acceptance Criteria:**

**Given** the application is launched
**When** a manual trigger fires
**Then** capture runs through the model tier Story 1.6's benchmark selected, the result passes through the trust layer, and a validated contract's route/loading plan is computed and handed to the UI
**And** none of these steps requires the player to invoke it manually or run any code themselves

*(Scope note, added 2026-07-09: true parallel batch scanning across `BatchScanner`'s worker pool is not wired here — Story 1.7 already flagged that sourcing multiple region-scoped captures (e.g. scrolling the contract list) was left unsolved and out of scope, so there is nothing yet that produces the list of per-contract `CapturePort`s `BatchScanner` needs. This story wires the single-scan flow only; voice triggering is deferred too, since it needs a real VoiceAttack integration this story doesn't build — manual triggering already satisfies NFR4 as the required baseline.)*

### Story 4.2: Results Window (Tkinter UI Adapter)

As a player,
I want to see my scan results and recommendations in VerseLog's own window,
So that I don't have to read logs or code to know what the tool found.

**Acceptance Criteria:**

**Given** one or more validated contracts with a computed route and loading plan
**When** the results are shown
**Then** a Tkinter window displays each contract's departure, arrival, reward, route cost, and loading steps in large, readable text
**And** the window is VerseLog's own, separate from the game — never a live overlay tracking the in-game list (see SPEC.md non-goals)

### Story 4.3: Risky-Contract Confirmation Popup

As a player,
I want to be shown a clear popup when a contract is flagged as risky,
So that I can decide knowingly before proceeding.

**Acceptance Criteria:**

**Given** a contract `LegalityChecker` has flagged
**When** `UIPort.confirm_risky_contract` is called
**Then** a popup names the specific risk (faction, standing, reason) and requires an explicit accept/decline click
**And** the tool proceeds or withholds that contract from further processing based on the player's choice, exactly as Story 3.2 specified
**And** the tool never performs the accept/decline as an in-game action itself (no input injection, see SPEC.md non-goals)

## Epic 5: Packaging & Distribution

VerseLog runs end-to-end but only from source. This epic produces a real, installable artifact.

### Story 5.1: Windows Packaging (PyInstaller)

As a player,
I want a single downloadable file that runs VerseLog on Windows,
So that I don't need Python or any dependencies installed to try it.

**Acceptance Criteria:**

**Given** the current source tree
**When** the packaging build runs
**Then** it produces a single Windows executable that launches the app (Tkinter results window and console entrypoint both reachable) without a separately-installed Python
**And** the executable is published as a GitHub Release asset with a stable download link, not committed into the repository itself
**And** Tesseract and Ollama remain separate, user-installed prerequisites — documented, not bundled (see Dev Notes on why)

### Story 5.2: Linux Packaging (Deferred — Tracked, Not Forgotten)

As a Linux player,
I want an installable VerseLog build for my platform too,
So that I'm not a second-class target despite NFR7 naming Linux explicitly.

**Acceptance Criteria:**

**Given** no Linux build environment was available locally when Epic 5 started (WSL install proved impractically slow on this machine; Docker Desktop on Windows has the same underlying dependency)
**When** a suitable disposable build environment is set up (a GitHub Actions Linux runner is the likely candidate — it needs no local install and leaves no footprint on the developer's machine)
**Then** an equivalent Linux artifact (e.g. an AppImage) is produced and published as a GitHub Release asset alongside the Windows one
**And** until this story is picked up, Linux users are told plainly (README, docs site) that only source installation is available for their platform — not silently left to discover this themselves
