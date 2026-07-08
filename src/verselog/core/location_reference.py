from dataclasses import dataclass


@dataclass
class LocationReference:
    """A location's real x/y/z coordinates, imported in bulk from LocationDataProvider."""

    name: str
    system: str
    x: float
    y: float
    z: float
