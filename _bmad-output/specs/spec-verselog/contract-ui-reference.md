# Contract UI Reference

Observed field layout from the Star Citizen MobiGlas Contracts app, used to ground CAP-1 (extraction) and CAP-2 (validation). Source: a screenshot the user shared during spec review, not an official CIG document — reconfirm against the live UI before final implementation, since alpha patches can change it.

## Screen structure

- Tabs: **OFFERS** / **ACCEPTED** / **HISTORY**.
- Left sidebar: contract categories with a count badge each — **Collection**, **Hauling**, **Mercenary**, **Salvage**, **Bounty Hunter**. VerseLog targets Hauling (cargo), Mercenary, and Bounty categories only (see SPEC.md non-goals); Collection and Salvage are out of scope.
- Selected-contract detail panel fields:
  - **Title** (free text)
  - **Reward** (aUEC amount, e.g. `¤50,250`)
  - **Contract Availability** — seen as `N/A` on a sampled Hauling contract. Confirms CAP-1's handling of contracts with no visible countdown: this is a normal value, not missing data.
  - **Contracted By** (issuing organization name)
  - **Details** (free-text narrative — not needed for extraction, human flavor text only)
  - **Primary Objectives** — a list of pickup/delivery steps, each naming a location and an SCU quantity in `X/Y` progress format (e.g. `Deliver 0/6 SCU to <location>`)
  - **Accept Offer** action

## Extraction implication

CAP-1's target fields (departure, arrival, SCU, reward, optional remaining time) map to: pickup location and delivery location from Primary Objectives, the `Y` value of the SCU `X/Y` pair, the Reward amount, and Contract Availability when it is not `N/A`.
