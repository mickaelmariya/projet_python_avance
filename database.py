import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

from models import TodoRecord


class Database:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    remote_id INTEGER NOT NULL UNIQUE,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('Terminé', 'En attente')),
                    length INTEGER NOT NULL CHECK(length >= 0),
                    downloaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def is_empty(self) -> bool:
        with self.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS total FROM todos").fetchone()
            return bool(row and row["total"] == 0)

    def clear(self) -> None:
        with self.connection() as connection:
            connection.execute("DELETE FROM todos")

    def replace_all(self, records: Iterable[TodoRecord]) -> int:
        rows = [
            (r.remote_id, r.user_id, r.name, r.state, r.length)
            for r in records
        ]
        with self.connection() as connection:
            connection.execute("DELETE FROM todos")
            connection.executemany(
                """
                INSERT INTO todos(remote_id, user_id, name, state, length)
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def append_new(self, records: Iterable[TodoRecord]) -> int:
        inserted = 0
        with self.connection() as connection:
            for record in records:
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO todos(remote_id, user_id, name, state, length)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        record.remote_id,
                        record.user_id,
                        record.name,
                        record.state,
                        record.length,
                    ),
                )
                inserted += cursor.rowcount
        return inserted

    def fetch_all(self) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return list(
                connection.execute(
                    """
                    SELECT remote_id, user_id, name, state, length, downloaded_at
                    FROM todos
                    ORDER BY remote_id
                    """
                ).fetchall()
            )

    def aggregate(self) -> dict[str, float | int]:
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COALESCE(AVG(length), 0) AS average_length,
                    COALESCE(MIN(length), 0) AS min_length,
                    COALESCE(MAX(length), 0) AS max_length,
                    SUM(CASE WHEN state = 'Terminé' THEN 1 ELSE 0 END) AS completed,
                    SUM(CASE WHEN state = 'En attente' THEN 1 ELSE 0 END) AS pending
                FROM todos
                """
            ).fetchone()
            return {
                "total": int(row["total"]),
                "average_length": float(row["average_length"]),
                "min_length": int(row["min_length"]),
                "max_length": int(row["max_length"]),
                "completed": int(row["completed"] or 0),
                "pending": int(row["pending"] or 0),
            }
