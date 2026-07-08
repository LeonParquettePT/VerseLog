import sqlite3
from pathlib import Path

from verselog.core.location_reference import LocationReference


class LocationReferenceStore:
    """Local SQLite store for bulk-imported location coordinate data (AD-4)."""

    def __init__(self, db_path: Path = Path("data/verselog.db")) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS locations (
                    name TEXT PRIMARY KEY,
                    system TEXT NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    z REAL NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def save_locations(self, locations: list[LocationReference]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO locations (name, system, x, y, z)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    system = excluded.system,
                    x = excluded.x,
                    y = excluded.y,
                    z = excluded.z
                """,
                [(loc.name, loc.system, loc.x, loc.y, loc.z) for loc in locations],
            )

    def get_location(self, name: str) -> LocationReference | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT name, system, x, y, z FROM locations WHERE name = ?",
                (name,),
            ).fetchone()
        return LocationReference(*row) if row else None
