# Sprint Change Proposal — 2026-07-09

## 1. Issue Summary

Léon flagged, while reading the project review, that SPEC.md's platform constraint ("Target platforms are Windows and Linux... no macOS") never accounted for accessing VerseLog from a tablet (Android or iPad).

Discussion surfaced two distinct ideas under that one concern, and deliberately did not pick between them:

1. **Remote display** — the PC keeps doing all capture/compute exactly as already built (Epics 1–3, unchanged); a future UI adapter would additionally serve results over the local network so a tablet, phone, or second PC can view them without alt-tabbing out of the game.
2. **Compute offload** — go further and have a second device (the tablet) actually run the OCR/vision extraction itself, freeing the gaming PC's CPU/GPU during a scan. This directly serves the existing "don't add CPU load on top of an already CPU-bound game" constraint, but is a materially bigger architectural bet: it breaks AD-5's single-process model, Tesseract is plausibly portable to a tablet but Ollama's vision models effectively are not (no iOS support, ~no Android support today), and a weaker second device could make scans slower rather than faster.

Léon's explicit decision: don't resolve which direction (or whether either) is right today. Stay on the original Windows/Linux plan, record both directions honestly, and revisit with a dedicated architecture session later — not now, and not as part of finishing the current build.

## 2. Impact Analysis

- **Epic impact:** None. Epics 1–3 (all 14 stories, all merged) stay exactly as built.
- **Story impact:** None. No `done` story's acceptance criteria or implementation is affected.
- **Artifact conflicts:**
  - `SPEC.md` — Constraints section needed to say precisely what it constrains (the engine's platform) without foreclosing device-agnostic access later.
  - `ARCHITECTURE-SPINE.md` — Deferred section is where this belongs: an explicitly-undecided future direction, not a committed capability.
  - `epics.md` — no change. Neither direction is a committed capability (no CAP-#, no epic, no story) yet.
- **Technical impact:** None on existing code. Documentation only.

## 3. Recommended Approach

**Direct Adjustment** — precise SPEC.md wording, plus a Deferred entry in ARCHITECTURE-SPINE.md naming both open directions and the real tradeoff between them, so neither gets silently assumed later. No rollback, no MVP scope change, no story rework.

## 4. Changes Applied

### SPEC.md — Constraints section

**OLD:**
> Target platforms are Windows and Linux (Star Citizen has official Windows support and unofficial community Linux support; no macOS). Rules out Windows-only assumptions in core design — though VoiceAttack (voice trigger) is Windows-only, which is acceptable only because manual triggering (CAP-6) already covers Linux.

**NEW:**
> Target platforms for the capture/compute engine are Windows and Linux (Star Citizen has official Windows support and unofficial community Linux support; no macOS or mobile OS — the game itself doesn't run there, so neither can OCR/vision capture as currently designed). Rules out Windows-only assumptions in core design — though VoiceAttack (voice trigger) is Windows-only, which is acceptable only because manual triggering (CAP-6) already covers Linux. This is a constraint on where the engine runs today, not a closed door on other devices later — see ARCHITECTURE-SPINE.md#Deferred for two open, undecided directions (remote display vs. compute offload to a second device) flagged 2026-07-09, deliberately not designed yet.

### ARCHITECTURE-SPINE.md — Deferred section

**NEW entry, appended:**
> - **Tablet/second-device access** — flagged 2026-07-09, explicitly not designed yet, two open directions with a real tradeoff neither picked:
>   - *Remote display*: the PC engine runs exactly as built; a future `UIPort` adapter additionally serves results over the local network (self-hosted, no cloud, no cost) so a tablet/phone/second PC can view them. Small, low-risk addition once the first `UIPort` adapter exists — doesn't touch AD-2 or AD-5.
>   - *Compute offload*: the PC sends a captured screenshot to a second device and that device runs the OCR/vision extraction instead, freeing the gaming PC's CPU/GPU during a scan (directly serves the CPU-load constraint above). A materially bigger bet: breaks AD-5's single-process model (needs a real PC↔device protocol), Tesseract is plausibly portable but Ollama's vision models are not (no iOS support, effectively no Android support today — would need a different mobile inference stack), and a weaker second device could make scans slower, not faster.
>   - Neither is scheduled. Revisit with a dedicated architecture session before committing to either — don't let a future `UIPort` adapter silently assume one over the other.

## 5. Implementation Handoff

**Scope classification: Minor.** Documentation-only, applied directly in this session. No code, no story rework. The actual feature — whichever direction, if either — is explicitly deferred to a future dedicated architecture session per Léon's decision; nothing about it is scheduled now.

**Success criteria:** SPEC.md's Constraints section is accurate about what it constrains (the engine, not viewing access); ARCHITECTURE-SPINE.md's Deferred entry captures both directions and their tradeoff with enough context that revisiting it later doesn't require re-deriving this conversation.
