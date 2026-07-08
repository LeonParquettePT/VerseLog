# Vision Pipeline — Provider Abstraction & Fallback Chain

Implementation strategy supporting CAP-1 (capture/extraction) and CAP-3 (adaptive performance). Not kernel-shape: this is HOW, cited by SPEC.md rather than embedded in it.

## Provider abstraction

A single internal `Contract` data model (departure, arrival, SCU, reward, ...) sits behind interchangeable provider implementations, so the extraction source can evolve without touching the rest of the app:

| Provider | Role |
|---|---|
| `OCRProvider` | Classic OCR (e.g. Tesseract/EasyOCR) — lightest, least precise, most sensitive to UI transparency. |
| `VisionProvider` | Local vision-language model (e.g. Moondream2, Phi-3-Vision, Llama-3.2-Vision) — higher precision, higher resource cost. |
| `CommunityAPIProvider` | Third-party community data source. **Note:** its per-vehicle `port_olisar_to_arccorp_time/fuel` fields are a single hardcoded Stanton-only example pair, not a real route matrix, and do not cover Pyro or any other location pair. Real point-to-point route cost (any system) must be computed by VerseLog itself, from `/api/locations` coordinates plus each ship's `quantum_range`/`quantum_speed`/`fuel.usage` stats. Confirmed: **api.star-citizen.wiki** (github.com/StarCitizenWiki) exposes `/api/vehicles` (`cargo_capacity`, `cargo_grids[].scu`, `cargo_limits`, quantum/fuel fields including `quantum_fuel_capacity`, `quantum_range`, `fuel.usage` by thruster type, and sample precomputed port-to-port quantum time/fuel) and `/api/locations` (starmap, celestial objects, jump points) — this is what backs CAP-8's default fuel values and CAP-4's cargo-capacity data. Its `/api/missions` endpoint is a **static mission catalog**, not live per-player contract instances, so it does not replace CAP-1's OCR/vision capture of the actual live contract board. Confirmed working and covers multiple star systems (Stanton + Pyro), but its rate limits and game-data redistribution terms are unpublished — implement caching/backoff defensively regardless of what's eventually confirmed. The project appears single-maintainer (bus-factor risk): mitigate server-side, not client-side — fork/mirror the API service itself onto an independently-hosted server (free hosting or GitHub-hosted), as a fallback endpoint if the original goes down. VerseLog's client keeps calling "an API" either way and stays lightweight; bundling the full dataset into the app itself was considered and rejected as it would conflict with the modest-PC constraint. |
| `OfficialAPIProvider` | Official CIG data feed, if one is ever released. Currently non-existent — see SPEC.md non-goals. |

Swapping the active provider must not require changes to route/cargo optimization (CAP-4) or any other downstream capability.

## Adaptive model fallback chain (CAP-3)

1. On first launch, auto-benchmark the most precise available vision model **while Star Citizen is actually running** — an idle-PC benchmark reads as artificially more powerful and leads to selecting a model that later misses the time budget during real play.
2. If it exceeds the user's time budget (default 30s), fall back one tier: `Phi-3-Vision → Moondream2 → classic OCR`.
3. The model loads only at scan time (lazy load) and unloads from VRAM immediately after extraction — footprint is a short burst, not a sustained background cost.
4. Re-benchmark only on detected hardware change, not on every launch.

Dedicated tests must verify the auto-benchmark switches correctly between all three tiers (see SPEC.md CAP-3 success criterion).
