---
baseline_commit: 058d829fb3f9d224cdf7d726053bebe8df980757
---

# Story 2.4: Combined Route and Loading Plan for Multiple Missions

Status: done

## Story

As a player with several unrelated accepted missions,
I want one combined route and loading plan that avoids unnecessary back-and-forth between systems or galaxies,
so that I don't waste time or fuel on a trip a smarter ordering would have avoided, and I don't have to juggle missions manually.

## Acceptance Criteria

1. **Given** multiple accepted missions sharing one ship, potentially across different locations or star systems, **when** the combined plan is computed, **then** the route groups nearby stops sensibly instead of zig-zagging back and forth between systems/galaxies when a more direct ordering exists, **and** the loading order (LIFO) is derived from that same optimized route — not computed separately — so cargo is always accessible in the order the ship actually visits locations, **and** the plan stays legible to any crew sharing the ship's cargo slots. [Source: epics.md#Story-2.4]

## Tasks / Subtasks

- [x] Task 1: Define the `CombinedPlan` data shape (AC: #1)
  - [x] `src/verselog/core/combined_route_planner.py` — `CombinedPlan` dataclass: `loading_plan: LoadingPlan` (reuse Story 2.3's `LoadingPlan`/`LoadingStep` as-is — no new step shape needed), `total_distance_meters: float`, `total_travel_time_seconds: float`, `total_fuel_cost: float`
  - [x] **No separate "stops" list** — `loading_plan.steps` (in order) already IS the route: each step's `location`, in sequence, defines every stop the ship visits. This is the strongest form of "the loading step never runs independently of the route step": there's only one ordered sequence, not two that could drift apart.
- [x] Task 2: Implement `CombinedRoutePlanner` using a greedy nearest-neighbor construction with LIFO-feasibility enforced by candidate restriction, not validated after the fact (AC: #1)
  - [x] `CombinedRoutePlanner(route_cost_calculator: RouteCostCalculator)` — same single-collaborator composition pattern as Story 2.3's `LoadingPlanCalculator`. Do not add a `ShipReferenceStore` or `LocationReferenceStore` dependency: every distance/cost/ship-capacity fact needed comes from `route_cost_calculator.calculate()`, exactly like Story 2.3.
  - [x] `plan(contracts: list[Contract], ship_name: str) -> CombinedPlan`. Raise `ValueError` if `contracts` is empty.
  - [x] **Algorithm** (the exact shape to implement — do not substitute a different heuristic or an exact TSP/ILP solver, see Dev Notes for why):

    ```text
    remaining_pickups = list of (contract, contract.departure) for every contract, not yet visited
    stack = []          # contracts currently loaded, in load order; stack[-1] is "on top" / nearest the door
    steps = []          # LoadingStep list being built, in final route order
    current_location = None
    total_distance = total_time = total_fuel = 0.0

    while remaining_pickups or stack:
        candidates = [(contract, contract.departure, "load") for contract in remaining_pickups]
        if stack:
            candidates.append((stack[-1], stack[-1].arrival, "unload"))  # ONLY the top of the stack may be delivered next

        if current_location is None:
            chosen = candidates[0]          # arbitrary, deterministic starting point (first contract's departure)
        else:
            chosen = candidate in candidates with the smallest
                     route_cost_calculator.calculate(current_location, candidate_location, ship_name).distance_meters
                     (a same-location candidate costs 0 and is naturally preferred first)

        if current_location is not None and chosen.location != current_location:
            leg = route_cost_calculator.calculate(current_location, chosen.location, ship_name)
            total_distance += leg.distance_meters
            total_time += leg.travel_time_seconds
            total_fuel += leg.fuel_cost
            ship = leg.ship   # same ship every call; capture once for the capacity check below

        current_location = chosen.location

        if chosen.action == "load":
            remove that contract from remaining_pickups; push onto stack
            steps.append(LoadingStep(location=current_location, action="load", scu=contract.scu))
        else:
            pop the stack (it is exactly this contract, by construction)
            steps.append(LoadingStep(location=current_location, action="unload", scu=contract.scu))
    ```

  - [x] After building `steps`, walk them tracking a running onboard-SCU total (+scu on `"load"`, -scu on `"unload"`); if it ever exceeds `ship.cargo_capacity_scu`, raise `ValueError` naming the SCU total and the capacity. This is the multi-mission generalization of Story 2.3's per-mission capacity check — several missions can each individually fit the ship yet still overflow it when carried *simultaneously* (their loaded windows overlap). Nothing in the codebase checks this yet.
  - [x] Return `CombinedPlan(loading_plan=LoadingPlan(steps=steps), total_distance_meters=total_distance, total_travel_time_seconds=total_time, total_fuel_cost=total_fuel)`
- [x] Task 3: Tests (AC: #1)
  - [x] Unit test the "avoids zig-zagging" scenario concretely, with synthetic 1D-line coordinates chosen so the answer is unambiguous: locations `X=0`, `Y=10`, `Z=20` (same system); Mission A departs X arrives Y (scu=2), Mission B departs X arrives Z (scu=2), ship capacity 10. Assert the algorithm produces `[load A @ X, load B @ X, unload B @ Z, unload A @ Y]` (both pickups first since they're co-located, then deliveries in reverse-load/LIFO order) with `total_distance_meters == 30` (0 + 20 + 10) — and assert this is cheaper than the naive un-optimized "finish mission A entirely, then mission B" ordering, which would cost 40 (10 + 10 + 20: deliver A, backtrack to X, deliver B). Show the 30 vs 40 comparison in the test/comment so the "sensible grouping" claim is verifiably grounded, not asserted by faith.
  - [x] Unit test that the LIFO stack ordering is enforced even when a nearer delivery is buried: extend the scenario above (or a variant) to confirm a delivery is never chosen out of order — i.e., the emitted `steps` sequence is always a properly-nested load/unload sequence (every `"unload"` step's contract was the most-recently-loaded still-onboard contract at that point).
  - [x] Unit test the new cross-mission capacity overflow case: two missions whose individual `scu` each fit the ship alone but whose *combined* onboard total (while both are simultaneously loaded) exceeds `ship.cargo_capacity_scu` — assert `ValueError` mentioning the capacity.
  - [x] Unit test that an unknown departure/arrival/ship name raises the same `ValueError` `RouteCostCalculator.calculate()` already raises (same propagation check as Story 2.3 — proves the route step isn't bypassed or duplicated here either).
  - [x] Unit test the empty-`contracts` case raises `ValueError`.
  - [x] Unit test a single-contract input produces the same two-step shape as Story 2.3's `LoadingPlanCalculator` would (`[load @ departure, unload @ arrival]`) — confirms the general algorithm correctly subsumes the single-mission case without a special-case branch for it.
  - [x] Reuse the real Port Tressler / Greycat Stanton IV Production Complex-A coordinates and MISC Starlancer MAX ship stats (confirmed in Story 2.2, reused in Story 2.3) for at least one grounded, non-synthetic test case.

## Dev Notes

- **Why a greedy heuristic, not an exact solver:** the general "pickup-and-delivery with LIFO stacking" problem is NP-hard in the general case (it's a stack-constrained variant of the vehicle routing problem). Building an exact TSP/ILP solver would directly violate NFR1 ("must run acceptably on modest/low-end PCs... avoid adding meaningful CPU load") and NFR9's anti-"gas factory" stance, for a benefit that doesn't matter at the realistic scale here: a player's simultaneously-accepted, not-yet-delivered missions on one ship number in the single digits to low tens, not hundreds — Story 1.7's "batch scanning ~30 contracts" is about *scanning the board*, not about how many missions one ship is hauling at once. A nearest-neighbor-with-LIFO-restricted-candidates greedy construction is O(n²) `calculate()` calls for n stops, trivially cheap at this scale, and produces a genuinely sensible (if not provably optimal) route. Do not attempt to generalize this into an exact optimizer — that would be solving a harder problem than the one that exists. [Source: ARCHITECTURE-SPINE.md#Deferred — "Route/knapsack optimization algorithm specifics" is explicitly an implementation detail, not a pre-decided algorithm]
- **Why no special-case "group by star system" step is needed:** `LocationReference` coordinates are real, absolute values across the whole game universe (confirmed Story 2.2 — Stanton and Pyro locations share one coordinate space via `scunpacked-data`'s `starmap_positions.json`). Inter-system distances dwarf intra-system ones in real data, so plain nearest-neighbor-by-distance already avoids ping-ponging between systems without a dedicated "system" grouping pass — adding one would be a special case layered on top of a mechanism (distance-based nearest-neighbor) that already generalizes to it. [Source: ARCHITECTURE-SPINE.md — Altitude: prefer generalizing the underlying mechanism over adding special cases]
- **LIFO is enforced by construction, not validated after the fact:** the algorithm's candidate set at every step only ever contains "a not-yet-visited pickup" or "the current top-of-stack's delivery" — it is structurally impossible to emit an infeasible (non-nested) load/unload sequence. This is a stronger version of Story 2.3's "never runs independently of the route step" — here the SAME loop iteration both extends the route and appends the next `LoadingStep`, so there is exactly one sequence, not two that are computed separately and then reconciled.
- **Composition, not duplication — same collaborator as Story 2.3:** `CombinedRoutePlanner` takes only `RouteCostCalculator` as a constructor dependency, exactly like `LoadingPlanCalculator`. All distance/time/fuel/ship-validation facts come from `route_cost_calculator.calculate()` (which itself now returns `RouteCost.ship`, per Story 2.3's code-review fix) — do not add a second `ShipReferenceStore`/`LocationReferenceStore` dependency just to "peek" at coordinates more cheaply; at this story's realistic scale the extra `calculate()` calls are not a real cost. [Source: 2-3-loading-plan-derived-from-single-missions-route.md#Change-Log — the ship-field fix this story's `.ship` capture is built on]
- **New constraint this story introduces:** cumulative onboard SCU across *overlapping* missions must fit `ship.cargo_capacity_scu` — Story 2.3 only checked one mission's SCU against capacity in isolation, which is correct for a single mission but insufficient once multiple missions can be aboard at once. Walk the final `steps` list with a running total; this is simpler and more reliable than trying to reason about overlaps combinatorially before the sequence exists.
- **`LoadingPlanCalculator` (Story 2.3) is not modified, removed, or delegated to.** Its single-mission algorithm happens to be a special case this story's general algorithm would also produce, but replacing it is out-of-scope scope creep for this story — leave it as-is as the dedicated single-mission entry point.
- **Legibility (third AC clause) is satisfied by the plain ordered `LoadingStep` list itself** — ship, docking, and any presentation formatting are UI-adapter concerns, out of scope for this `core/` story. Don't add any formatting/rendering logic here.
- **Coding style:** plain, direct code — no premature abstraction (no strategy pattern for "pluggable algorithms," no generic graph library dependency; stdlib data structures are enough for this scale). [Source: CONTRIBUTING.md#Ground-rules]

### Project Structure Notes

- Adds one new file to the existing `core/` package: `combined_route_planner.py`, alongside `route_cost_calculator.py` (Story 2.2) and `loading_plan_calculator.py` (Story 2.3). No structural surprises.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.4] — this story's acceptance criterion, verbatim
- [Source: _bmad-output/implementation-artifacts/2-3-loading-plan-derived-from-single-missions-route.md] — `LoadingStep`/`LoadingPlan` reused as-is; `RouteCost.ship` fix this story's design depends on; the composition-not-duplication pattern this story continues
- [Source: _bmad-output/implementation-artifacts/2-2-point-to-point-route-cost-calculation.md] — `RouteCostCalculator`, real confirmed Port Tressler/Greycat Stanton IV coordinates and MISC Starlancer MAX ship stats reused for this story's grounded test case
- [Source: _bmad-output/planning-artifacts/architecture/architecture-VERSELOG-2026-07-08/ARCHITECTURE-SPINE.md#Deferred] — confirms the exact routing algorithm is an intentionally-undecided implementation detail, not something this story is violating by choosing a heuristic
- [Source: _bmad-output/planning-artifacts/epics.md] — NFR1 (modest hardware, avoid CPU load) and NFR9 (no over-engineered "gas factory" complexity), both of which rule out an exact TSP/ILP solver for this story

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

- `uv run --extra dev pytest tests/test_combined_route_planner.py -q` → `8 passed in 0.45s`
- `uv run --extra dev pytest -q` → `68 passed in 2.56s`

### Completion Notes List

- Implemented `CombinedPlan` and `CombinedRoutePlanner` in `core/combined_route_planner.py`, taking only `RouteCostCalculator` as a constructor collaborator (same pattern as Story 2.3's `LoadingPlanCalculator`) — no `ShipReferenceStore`/`LocationReferenceStore` dependency added.
- Implemented the greedy nearest-neighbor + LIFO-restricted-candidate algorithm exactly as specified in Dev Notes: at each step the candidate set is only "a not-yet-visited pickup" or "the current top-of-stack's delivery," making the loading order structurally LIFO-feasible without a separate validation pass.
- During implementation, avoided a duplicate-`calculate()`-call bug analogous to the one Story 2.3's code review caught: computed each candidate's leg once during the nearest-neighbor comparison and reused that same result for the chosen candidate's totals/ship, rather than calling `calculate()` again after selection.
- Added the cross-mission cargo-capacity check (walks the final `steps` tracking running onboard SCU) — confirmed with a test where two missions each individually fit the ship but overflow it when carried simultaneously.
- Verified the "avoids zig-zagging" claim numerically: a synthetic 3-stop scenario where the smart order costs 30 (distance units) vs. 40 for the naive "finish mission A, then B" ordering that backtracks.
- All acceptance criteria satisfied; 69/69 tests passing (60 pre-existing + 9 new, including the tie-break regression test added during code review).

### File List

- `src/verselog/core/combined_route_planner.py` (new)
- `tests/test_combined_route_planner.py` (new)

## Change Log

- 2026-07-09: Story implemented — `CombinedPlan`/`CombinedRoutePlanner` added, deriving a multi-mission route and LIFO loading order from a single greedy-construction pass, all tasks complete, 68/68 tests passing, status moved to review.
- 2026-07-09: Code review (independent verification agent) found a real correctness bug: on a distance tie between "pick up the next mission here" and "deliver the mission on top of the stack here," candidate ordering always favored the pickup, which could stack multiple missions' cargo unnecessarily and cause a spurious "capacity exceeded" rejection for an input that actually has an equally-cheap, capacity-feasible route. Fixed by listing the unload candidate first, so ties favor delivering before picking up more. Added a regression test reproducing the exact scenario (two missions, ship capacity exactly matching one mission's SCU). 69/69 tests passing.
