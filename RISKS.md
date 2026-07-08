# Risks & Mitigations

*[🇫🇷 Lire en français](RISKS.fr.md)*

Known risks identified while planning VerseLog, so nobody has to rediscover them the hard way. Each one lists what could go wrong, what we're doing about it, and its current status.

## Legal / Terms of Service

### Auto-accepting contracts would violate CIG's EULA

CIG's EULA explicitly bans "automation software (bots) ... designed to modify the Game experience and/or give you an advantage over other players." Calculating the best contract is fine (external calculators like this are tolerated in the community); having the software click "Accept" for the player is not — that crosses into banned automation.
- **Mitigation:** Non-goal, by design. VerseLog never injects input into the game. Recommendations are shown in VerseLog's own window; the player always takes the in-game action manually.
- **Status:** Mitigated (hard architectural rule, verified against the EULA's actual text).

### Reading game memory/state would also violate the EULA

CIG's EULA separately bans software that "intercepts, mines, or otherwise collects information from or through the Game." This ruled out an idea we considered (a live overlay tracking the in-game contract list as it scrolls) since it would require reading game memory to stay aligned.
- **Mitigation:** VerseLog only reads the rendered screen (screenshots), never game memory or network traffic. The overlay idea was rejected in favor of a separate results window.
- **Status:** Mitigated.

### VoiceAttack triggering a scan is probably fine, but unconfirmed with certainty

VoiceAttack simulates a keypress (e.g. a screenshot hotkey) when the player speaks a command — similar in spirit to a HOTAS/controller bind, which is common and tolerated. It is not the same category as automation that plays the game, but CIG has not given VerseLog itself an explicit blessing.
- **Mitigation:** Manual triggering is always available as a fallback that carries zero ambiguity. Voice is optional convenience, never required.
- **Status:** Accepted (low risk, not eliminated).

## Third-Party Dependency (api.star-citizen.wiki)

### Single-maintainer project (bus factor)

The community API VerseLog relies on for ship/fuel/location reference data appears to be maintained by essentially one person.
- **Mitigation:** An independently-hosted mirror of the API is planned as optional infra, so VerseLog isn't stranded if the original disappears.
- **Status:** Mitigation planned, not yet built.

### Rate limits and data redistribution terms are unpublished

We couldn't find published rate limits or explicit terms for reusing the underlying game data (the API's server code is MIT, but that doesn't cover the data itself) in a third-party tool.
- **Mitigation:** Proceeding under a safe default posture — clear attribution, conservative/self-throttled request rates, strictly non-commercial and free use. Formal confirmation with the maintainer is deferred, not required to proceed.
- **Status:** Open, accepted as low-risk for now given the project's small non-commercial scope.

### Route/distance data isn't precomputed by the API

The API's per-vehicle example route fields are a single hardcoded Stanton-only pair, not a real route matrix, and don't cover Pyro or other systems.
- **Mitigation:** VerseLog computes real point-to-point cost itself from location coordinates plus each ship's stats (see Story 2.2).
- **Status:** Mitigated (design accounts for it).

## Technical / Reliability

### The game is in alpha — its UI can change without warning

A patch can change contract-screen layout, breaking OCR/vision extraction silently.
- **Mitigation:** The trust layer (validation + quarantine) catches malformed extractions instead of trusting them blindly, and the provider abstraction lets a broken capture method be swapped without touching the rest of the app.
- **Status:** Mitigated by design; still expect occasional breakage after major patches.

### Misleading hardware benchmark

Benchmarking on an idle PC reads as more powerful than it is once the game is actually running, which could pick too heavy a model tier.
- **Mitigation:** The benchmark must run while Star Citizen is running, not idle (see Story 1.6).
- **Status:** Mitigated by design.

### Adding CPU load on an already CPU-bound game

Star Citizen is demanding, especially CPU-bound; a helper tool that competes for the same resource defeats its own purpose for the modest-PC players it's meant to help most.
- **Mitigation:** Lazy model loading (burst, not continuous), a worker pool sized by the benchmark, and a hard non-goal against features that add sustained background load.
- **Status:** Mitigated by design; needs real-world verification once built.

## Project / Maintenance

### Solo, junior-developer maintainer

The project is currently maintained by one person still learning to code.
- **Mitigation:** Open-source and collaborative from day one so others can read, understand, and pick up the project; "functional first, clean second" keeps scope realistic; BMad Method planning artifacts (SPEC, architecture, epics) give any future contributor — or the author returning after a break — a clear map back into the project.
- **Status:** Accepted, actively mitigated.

### Code produced with AI assistance could read as low-quality or be distrusted by the open-source community

Contributors and users may be skeptical of AI-assisted code.
- **Mitigation:** Explicit coding conventions in `CONTRIBUTING.md` (plain, direct code, no padding/boilerplate); the project is upfront about its process rather than hiding it.
- **Status:** Accepted, actively mitigated.
