# VerseLog — Brainstorm Intent

Free, open-source, community-collaborative (GitHub) external logistics assistant for Star Citizen: scans cargo/mission contracts, validates the data, computes the route/cargo plan that maximizes aUEC/min, and stays light enough to run on modest hardware alongside other work.

## Core Jobs-to-Be-Done (ranked)

1. **Save time & be reliable** — top priority; this is what makes the app worth maintaining long-term.
2. **Eliminate human calculation errors** — the software must be the reliable source that compensates for human fallibility (manual math is what's error-prone, not the tool). This is a reliability promise, not just a technical safeguard.
3. **Maximize aUEC/min** — a consequence of the above, not the primary driver.

Root motivation: a genuine personal pain point (losing more time calculating logistics than playing) plus a personal goal of leveling up as a developer. Purpose: keep the game relaxing, free of manual-calculation mental load.

Secondary value discovered late: the in-game map is resource-heavy and sometimes buggy (A→B routes miscalculate), so VerseLog also has standalone value as a clear, simple, independent route reference. Additionally, the game shows only one active quest at a time even when several are accepted in parallel — VerseLog can combine/link unrelated accepted quests into a single optimal combined route (ties into the Knapsack + geographic-filtering logic already planned).

## Key Decisions

**Data pipeline / trust layer** (identified as ONE unified priority workstream, not three separate ideas — it serves reliability, resilience to alpha breakage, and transparency simultaneously):
- Post-extraction coherence validation (known station, SCU = integer, reward = number); suspect extractions go to **quarantine**, not immediate rejection.
- Visible **confidence indicator** on every calculated suggestion — no silent trust.
- Provider abstraction: a standard `Contract` model behind interchangeable `OCRProvider` / `VisionProvider` / `CommunityAPIProvider` / `OfficialAPIProvider` implementations, so the data source can evolve (alpha instability → future clean API/JSON) without touching the core.

**Universality scope**: "universal" applies only to contract *types* (cargo / bounty / mercenary), not to the tool's overall architecture.

**Vision model strategy**:
- Lazy-load the vision model only at the "scan quest" trigger; unload from VRAM immediately after extraction. Runs in short bursts, not continuously — avoids needing a hardware/AI compatibility database (rejected as too costly to maintain).
- Auto-benchmark on first launch, with automatic fallback chain: Phi-3-Vision → Moondream2 (if too slow) → classic OCR (last resort). Each machine gets the best compromise automatically.
- Dedicated tests required to verify the auto-benchmark switches correctly between the three tiers.

**Time budgets**: two separate budgets — the player may take as long as they want to think, but the scan/processing itself must stay fast. Default recommended threshold: 30s (ideal 15–30s, unpleasant beyond 60s; logic: ~10% of total task time, i.e. 10 min flight vs. 10–30 min of current manual sorting). Threshold is user-adjustable, not fixed.

**Reputation handling**: auto-scan reputation level at app launch and/or at each quest scan (no manual setup); manual reconfiguration available if reputation changes mid-session.

**Legality filter**: popup alert for potentially illegal contracts (e.g. trespassing zones) — user explicitly accepts or refuses. No silent automatic filtering.

**Trigger modes**: voice command (VoiceAttack) is an optional comfort/accessibility layer only. Manual trigger (click/button) must always be supported — mic use is never mandatory.

**Multiplayer gain split**: equitable/even split by default. Plan for a SCU-weighted mode as a lower-probability future option, since the game is in alpha and cargo-distribution mechanics between players may change.

## Hard Constraints

- Must run well on **modest/low-end PCs** — the game itself is already demanding; a helper tool that tanks performance fails its mission.
- Key persona: a player who also does office work on the same machine — needs extraction precision *without* blocking other work during/after a scan. Precision and lightness must not be a tradeoff.
- Code produced with AI assistance must remain **human-quality with no visible AI-generation traces** (open-source scrutiny concern).
- Project is **open-source/collaborative from day one**, not retrofitted — enables outside contributors to access/correct/understand the structure from inception. Author self-identifies as a junior developer, learning along the way.
- **Functional first, clean second**: a working result quickly matters more than polished code at this stage.
- Biggest risk: game is in **alpha** — the app can break anytime due to upstream game changes. Secondary known risk: no backup/recovery path if something fails.

## Open Questions / Research Items

- **Stanton distance matrix** (recurring problem, surfaced from 3 angles — geographic filtering, fuel-cost estimation, and general route mapping — treat as one research priority): can a reliable distance matrix be sourced from existing third-party community tools/data instead of manual mapping?
- **Fuel consumption per ship engine**: likely available via existing community sources, but needs confirmation.
- **In-game contract UI**: does Star Citizen show a visible countdown/remaining time on contracts before acceptance, or only a non-visible deadline? Determines whether remaining time can be extracted directly at scan time, vs. needing repeated scans to detect disappearance/expiry.
- **Multiplayer cargo split mechanics**: how does in-game cargo distribution between multiple players actually work? Unconfirmed — affects the equitable-vs-SCU-weighted split decision above.

## Immediate Next Steps (user-stated order)

1. Consolidate tonight's decisions in writing (this document).
2. Create the GitHub repo now, to have collaborative history from the very start.
3. List concrete tasks.
4. Research the open items (distance matrix, fuel consumption).
5. Start coding.
