import sqlite3
from pathlib import Path

from verselog.core.ship_reference import ShipReference


class ShipReferenceStore:
    """Local SQLite store for bulk-imported ship reference data (AD-4)."""

    def __init__(self, db_path: Path = Path("data/verselog.db")) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ships (
                    name TEXT PRIMARY KEY,
                    cargo_capacity_scu INTEGER NOT NULL,
                    quantum_fuel_capacity REAL NOT NULL,
                    quantum_range REAL NOT NULL,
                    fuel_usage_main REAL NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def save_ships(self, ships: list[ShipReference]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO ships (name, cargo_capacity_scu, quantum_fuel_capacity, quantum_range, fuel_usage_main)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    cargo_capacity_scu = excluded.cargo_capacity_scu,
                    quantum_fuel_capacity = excluded.quantum_fuel_capacity,
                    quantum_range = excluded.quantum_range,
                    fuel_usage_main = excluded.fuel_usage_main
                """,
                [
                    (s.name, s.cargo_capacity_scu, s.quantum_fuel_capacity, s.quantum_range, s.fuel_usage_main)
                    for s in ships
                ],
            )

    def get_ship(self, name: str) -> ShipReference | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT name, cargo_capacity_scu, quantum_fuel_capacity, quantum_range, fuel_usage_main "
                "FROM ships WHERE name = ?",
                (name,),
            ).fetchone()
        return ShipReference(*row) if row else None
