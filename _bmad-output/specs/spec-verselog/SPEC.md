---
id: SPEC-verselog
companions: [vision-pipeline.md, contract-ui-reference.md, ../../planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md]
sources: [../../brainstorming/brainstorm-verselog-2026-07-07/brainstorm-intent.md]
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability only — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# VerseLog — External Logistics Assistant for Star Citizen

## Why

A pain to solve, paired with a vision to realize: a solo, self-taught developer keeps losing more time hand-calculating Star Citizen cargo/mission logistics (which contracts to take, how to route them, how to load the ship) than actually playing the game — turning a relaxing hobby into unpaid mental labor. VerseLog is the free, open-source, community-collaborative tool that removes that labor: it reads the contract board, validates what it reads, and hands back a route and cargo plan that maximizes aUEC earned per minute. It matters now because the game is still in alpha (no official data feed exists, the UI can change under a patch at any time) and because the intended audience includes players on modest hardware who cannot absorb a heavy companion app on top of an already demanding game.

## Capabilities

- **CAP-1**
  - **intent:** User can trigger a scan (voice command or manual action) that captures and extracts a contract's data — departure, arrival, SCU, reward, and remaining time when the contract displays one (some contracts show no timer at all) — from the game's contract screen.
  - **success:** A scanned contract's extracted fields pass format validation (known station name, integer SCU, numeric reward) within the configured time budget; a contract with no visible timer is treated as a normal, valid result, not an error.

- **CAP-2**
  - **intent:** The system never silently trusts an extraction — a suspect result is quarantined instead of accepted, and every calculated suggestion shown to the user carries a visible confidence indicator.
  - **success:** A deliberately malformed or suspect extraction is quarantined (its source image retained, the user alerted) rather than silently accepted, and each on-screen suggestion displays its confidence state.

- **CAP-3**
  - **intent:** The system benchmarks the host machine — automatically on first launch, and any time the user manually re-triggers it from settings (e.g. after a hardware upgrade) — to pick an extraction model tier AND a safe number of parallel extraction workers, so scanning a handful or several dozen contracts at once both stay within the user's time budget. Models load only on demand, never running continuously.
  - **success:** On a given machine, benchmarked while Star Citizen is actually running (not idle, which reads as artificially more powerful), a full scan-to-result cycle completes within the user-configured threshold (default 30s) whether scanning one contract or a large batch (e.g. ~30 at once), VRAM/CPU usage returns to baseline immediately after each scan, and a manual re-benchmark action is available and produces an updated model tier/worker count.

- **CAP-4**
  - **intent:** User can get a computed route and cargo-loading plan that maximizes aUEC/min across one or more accepted contracts, including contracts the game itself cannot link together into a single itinerary, adapted to the selected ship's actual SCU capacity and legible to every crew member sharing its cargo slots.
  - **success:** Given a ship's SCU capacity and one or more accepted contracts (solo or shared by multiple crew), the tool outputs a single coherent loading order (LIFO) and route plan that requires no manual recalculation or re-shuffling.

- **CAP-5**
  - **intent:** The system keeps the player's reputation level in sync and requires explicit confirmation before proceeding on a contract flagged as potentially illegal (e.g. a trespassing zone), rather than filtering silently.
  - **success:** A legally-risky contract triggers a confirmable popup naming the risk, and the tool honors whichever choice — accept or decline — the user makes.

- **CAP-6**
  - **intent:** User can trigger a scan by voice command (VoiceAttack) or by manual action, with neither mode required to use the other.
  - **success:** A voice-triggered and a manually-triggered scan produce an equivalent result, and the tool remains fully usable with no microphone connected.

- **CAP-8**
  - **intent:** User can rely on default per-ship fuel-consumption values for route cost calculations, override them if that ship's engine has been modified, and reset to defaults at any time.
  - **success:** For a given ship, route cost calculations use the default engine's fuel-consumption value unless the user has set an override, and a reset action restores the default.

## Constraints

- Target platforms for the capture/compute engine are Windows and Linux (Star Citizen has official Windows support and unofficial community Linux support; no macOS or mobile OS — the game itself doesn't run there, so neither can OCR/vision capture as currently designed). Rules out Windows-only assumptions in core design — though VoiceAttack (voice trigger) is Windows-only, which is acceptable only because manual triggering (CAP-6) already covers Linux. This is a constraint on where the engine runs, not on where results can be viewed — see ARCHITECTURE-SPINE.md#Deferred: a tablet/second-device viewer is a future `UIPort` adapter requiring no architecture change, while offloading the capture/vision engine itself to a second device is deliberately not planned (blocked by mobile-tooling maturity and unvalidated demand, not by design).
- Baseline hardware target is Star Citizen's own comfortable-minimum spec: ~Ryzen 5 3600/5600 or Intel Core i5 10th/11th gen, RTX 2060/3060 or RX 6600 class GPU, 32GB RAM, NVMe SSD. The game is CPU-bound far more than GPU-bound (dense areas are the most demanding), so VerseLog's own footprint must avoid adding meaningful CPU load on top of an already CPU-saturated game — GPU headroom is the safer place to spend, not CPU. Rules out designs that add sustained background CPU cost.
- Scan-to-result processing must stay within a user-configurable time budget: default 30s (ideal 15–30s, unacceptable beyond ~60s), sized to keep tool overhead near 10% of total task time. Rules out heavy always-on background inference.
- No paid cloud API, ever, by design — local OCR/vision-model inference only. The tool must stay free and accessible; introducing a paid dependency would force monetization or cost-passing, contradicting its purpose. Rules out cloud-only or cloud-default architectures.
- Voice-based triggering (VoiceAttack) must never be the sole trigger path — manual triggering is always required. Rules out microphone-only interaction design.
- Open-source and collaborative on GitHub from inception, not retrofitted — the structure must be understandable and correctable by outside contributors from day one. Rules out a closed-prototype-then-open-source-later approach.
- License: MIT — anyone may use, modify, or close-source/commercialize derived work, provided attribution to the source is retained. Rules out a license that permits stripping attribution.
- Code produced with AI assistance must read as human-quality, idiomatic code with no visible AI-generation artifacts (an open-source scrutiny concern). Rules out verbose boilerplate, unnecessary comments, and defensive handling of cases that cannot occur.

## Non-goals

- Not an in-game automation or macro tool: no input injection into gameplay (e.g. never auto-accepts a contract) and no game-state/memory reading — only external, passive screen-reading plus optional voice-triggered capture. Confirmed against CIG's EULA/ToS, which explicitly bans automation software giving a gameplay advantage and software that intercepts/mines game data — this non-goal is a hard line, not just a style preference. Recommendations are shown in VerseLog's own separate window (not a live overlay tracking the in-game list), for the player to act on manually.
- Not targeting production-polished code at this stage: functional correctness is prioritized over code elegance for the initial build.
- No official CIG data-API integration (none exists today) — the provider abstraction allows adding one later, but it is out of scope now.
- Contract-type universality (cargo/bounty/mercenary) only — not extending the tool's overall architecture to other categories of tool beyond contract types.
- Multiplayer reward-split calculation (formerly CAP-7) is deferred: solo route/cargo optimization is the priority, players can already divide manually or with a calculator, and expected usage is low. May be revisited later; not a committed capability now.

## Success signal

A player voice- or manually-triggers a scan of the in-game contract board and receives, within their configured time budget, a validated, confidence-flagged route and cargo plan maximizing aUEC/min across their accepted contracts — on a modest PC, without manual calculation — and the tool keeps functioning across at least one game alpha patch without requiring the user to notice or intervene.

## Assumptions

- Assumed a safe default usage posture (clear attribution to api.star-citizen.wiki, conservative empirically-tested rate limiting, strictly non-commercial free use) is sufficient without formal written permission from its maintainer, given the small non-commercial hobby-project context. Formal confirmation is deferred and optional, not required to proceed.
