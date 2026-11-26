# src/flyshell/data/config.py

from flyshell.data import db_manager as db

from pathlib import Path
from typing import Any
import json


def get_config(
    key: str, default: Any = None, filename: str | Path | None = None
) -> Any:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        row = conn.execute(
            "SELECT value FROM core_config WHERE key = ?", (key,)
        ).fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            return row[0]


def set_config(key: str, value: Any, filename: str | Path | None = None) -> None:
    db.initialise(filename)
    serialized = json.dumps(value)
    with db.get_connection(filename) as conn:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO core_config (key, value)
                VALUES (?, ?)
            """,
                (key, serialized),
            )


def delete_config(key: str, filename: str | Path | None = None) -> bool:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM core_config WHERE key = ?", (key,))
            return cursor.rowcount > 0
