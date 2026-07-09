from dataclasses import dataclass

from verselog.core.contract import Contract
from verselog.core.route_cost_calculator import RouteCostCalculator
from verselog.core.ship_reference_store import ShipReferenceStore


@dataclass
class LoadingStep:
    location: str
    action: str
    scu: int


@dataclass
class LoadingPlan:
    steps: list[LoadingStep]


class LoadingPlanCalculator:
    """Derives a loading plan from a single mission's already-computed route (never independently)."""

    def __init__(self, route_cost_calculator: RouteCostCalculator, ship_store: ShipReferenceStore) -> None:
        self._route_cost_calculator = route_cost_calculator
        self._ship_store = ship_store

    def derive(self, contract: Contract, ship_name: str) -> LoadingPlan:
        # Reuses Story 2.2's departure/arrival/ship/quantum-drive validation
        # instead of duplicating it - the loading plan can never be built on
        # top of a route that couldn't itself be computed.
        self._route_cost_calculator.calculate(contract.departure, contract.arrival, ship_name)

        ship = self._ship_store.get_ship(ship_name)
        if contract.scu > ship.cargo_capacity_scu:
            raise ValueError(
                f"contract requires {contract.scu} SCU, which exceeds "
                f"{ship_name!r}'s cargo capacity of {ship.cargo_capacity_scu} SCU"
            )

        return LoadingPlan(
            steps=[
                LoadingStep(location=contract.departure, action="load", scu=contract.scu),
                LoadingStep(location=contract.arrival, action="unload", scu=contract.scu),
            ]
        )
