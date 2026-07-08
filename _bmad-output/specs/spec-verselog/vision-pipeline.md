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

## Adaptive model fallback chain and worker pool (CAP-3)

1. Auto-benchmark the most precise available vision model **while Star Citizen is actually running** — automatically on first launch, on detected hardware change, or any time the user manually triggers "Re-run benchmark" from settings. An idle-PC benchmark reads as artificially more powerful and leads to selecting a model that later misses the time budget during real play.
2. If it exceeds the user's time budget (default 30s), fall back one tier: `Phi-3-Vision → Moondream2 → classic OCR`.
3. The benchmark also determines a safe **worker count (N)**: how many contracts can be captured/extracted in parallel without breaking the time budget — needed because a player can have dozens of contracts visible at once (confirmed in practice, not just theoretical). Extraction runs on a pool of 1..N workers; N is re-evaluated every time the benchmark re-runs.
4. Regardless of how many workers extract in parallel, every result is handed to the trust-layer validation/quarantine service **serially** — that service is the only writer to quarantine/confidence state, so parallel capture never races on shared state.
5. The model loads only at scan time (lazy load) and unloads from VRAM immediately after extraction — footprint is a short burst, not a sustained background cost.

Dedicated tests must verify the auto-benchmark switches correctly between all three model tiers, that the worker count adapts sensibly to hardware, and that manual re-benchmarking updates both (see SPEC.md CAP-3 success criterion).
