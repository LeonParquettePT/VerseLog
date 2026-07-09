from dataclasses import dataclass

from verselog.core.contract import Contract
from verselog.core.loading_plan_calculator import LoadingPlan, LoadingStep
from verselog.core.route_cost_calculator import RouteCostCalculator


@dataclass
class CombinedPlan:
    loading_plan: LoadingPlan
    total_distance_meters: float
    total_travel_time_seconds: float
    total_fuel_cost: float


class CombinedRoutePlanner:
    """Plans a combined route + LIFO loading order for several missions on one ship.

    Uses a greedy nearest-neighbor construction whose candidate set at every
    step only contains a not-yet-visited pickup or the current top-of-stack's
    delivery - this makes the loading order structurally LIFO-feasible by
    construction, and the same loop that builds the route emits the loading
    steps, so there is one sequence, never two computed separately.
    """

    def __init__(self, route_cost_calculator: RouteCostCalculator) -> None:
        self._route_cost_calculator = route_cost_calculator

    def plan(self, contracts: list[Contract], ship_name: str) -> CombinedPlan:
        if not contracts:
            raise ValueError("at least one contract is required")

        remaining_pickups = list(contracts)
        stack: list[Contract] = []
        steps: list[LoadingStep] = []
        current_location: str | None = None
        ship = None
        total_distance = total_time = total_fuel = 0.0

        while remaining_pickups or stack:
            candidates: list[tuple[Contract, str, str]] = [
                (contract, contract.departure, "load") for contract in remaining_pickups
            ]
            if stack:
                candidates.append((stack[-1], stack[-1].arrival, "unload"))

            if current_location is None:
                contract, location, action = candidates[0]
            else:
                # Compute each candidate's leg once and reuse the chosen
                # one's result below - calling calculate() again for the
                # winner would repeat the same SQLite/quantum-drive work.
                legs = [
                    (candidate, self._route_cost_calculator.calculate(current_location, candidate[1], ship_name))
                    for candidate in candidates
                ]
                (contract, location, action), leg = min(legs, key=lambda pair: pair[1].distance_meters)
                ship = leg.ship
                if location != current_location:
                    total_distance += leg.distance_meters
                    total_time += leg.travel_time_seconds
                    total_fuel += leg.fuel_cost

            current_location = location

            if action == "load":
                remaining_pickups.remove(contract)
                stack.append(contract)
                steps.append(LoadingStep(location=location, action="load", scu=contract.scu))
            else:
                stack.pop()
                steps.append(LoadingStep(location=location, action="unload", scu=contract.scu))

        onboard_scu = 0
        for step in steps:
            onboard_scu += step.scu if step.action == "load" else -step.scu
            if onboard_scu > ship.cargo_capacity_scu:
                raise ValueError(
                    f"combined onboard cargo of {onboard_scu} SCU exceeds "
                    f"{ship_name!r}'s cargo capacity of {ship.cargo_capacity_scu} SCU"
                )

        return CombinedPlan(
            loading_plan=LoadingPlan(steps=steps),
            total_distance_meters=total_distance,
            total_travel_time_seconds=total_time,
            total_fuel_cost=total_fuel,
        )
