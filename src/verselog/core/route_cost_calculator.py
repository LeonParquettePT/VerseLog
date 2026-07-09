import math
from dataclasses import dataclass

from verselog.core.location_reference_store import LocationReferenceStore
from verselog.core.ship_reference import ShipReference
from verselog.core.ship_reference_store import ShipReferenceStore


@dataclass
class RouteCost:
    distance_meters: float
    travel_time_seconds: float
    fuel_cost: float
    ship: ShipReference


class RouteCostCalculator:
    """Computes real point-to-point route cost from location coordinates + ship quantum stats."""

    def __init__(self, location_store: LocationReferenceStore, ship_store: ShipReferenceStore) -> None:
        self._location_store = location_store
        self._ship_store = ship_store

    def calculate(self, departure: str, arrival: str, ship_name: str) -> RouteCost:
        departure_location = self._location_store.get_location(departure)
        if departure_location is None:
            raise ValueError(f"unknown departure location: {departure!r}")

        arrival_location = self._location_store.get_location(arrival)
        if arrival_location is None:
            raise ValueError(f"unknown arrival location: {arrival!r}")

        ship = self._ship_store.get_ship(ship_name)
        if ship is None:
            raise ValueError(f"unknown ship: {ship_name!r}")
        if ship.quantum_speed <= 0 or ship.quantum_range <= 0:
            # Real data confirms this happens: ground vehicles (e.g. the Nox
            # speeder bike) have no quantum drive at all, so the API returns
            # null/0 for these fields. Dividing by them would otherwise raise
            # an opaque ZeroDivisionError instead of an explicit, actionable one.
            raise ValueError(f"ship {ship_name!r} has no quantum drive capability")

        distance_meters = math.dist(
            (departure_location.x, departure_location.y, departure_location.z),
            (arrival_location.x, arrival_location.y, arrival_location.z),
        )
        travel_time_seconds = ship.quantum_spool_time + (distance_meters / ship.quantum_speed)
        fuel_cost = distance_meters * (ship.quantum_fuel_capacity / ship.quantum_range)

        return RouteCost(
            distance_meters=distance_meters,
            travel_time_seconds=travel_time_seconds,
            fuel_cost=fuel_cost,
            ship=ship,
        )
