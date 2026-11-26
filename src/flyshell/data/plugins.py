# src/flyshell/data/plugins.py

from flyshell.data import db_manager as db

from pathlib import Path
from typing import Any
import json
import time


def register_plugin(plugin_name: str, filename: str | Path | None = None) -> None:
    db.initialise(filename)
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with db.get_connection(filename) as conn:
        with conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO plugins (plugin_name, installed_at, is_enabled)
                VALUES (?, ?, 1)
            """,
                (plugin_name, now_utc),
            )


def get_plugin_data(
    plugin_name: str, key: str, default: Any = None, filename: str | Path | None = None
) -> Any:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        row = conn.execute(
            """
            SELECT value FROM plugin_kv WHERE plugin_name = ? AND key = ?
        """,
            (plugin_name, key),
        ).fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            return row[0]


def set_plugin_data(
    plugin_name: str, key: str, value: Any, filename: str | Path | None = None
) -> None:
    db.initialise(filename)
    register_plugin(plugin_name, filename=filename)
    serialized = json.dumps(value)
    with db.get_connection(filename) as conn:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO plugin_kv (plugin_name, key, value)
                VALUES (?, ?, ?)
            """,
                (plugin_name, key, serialized),
            )


def get_all_plugin_data(plugin_name: str, filename: str | Path | None = None) -> dict:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        rows = conn.execute(
            "SELECT key, value FROM plugin_kv WHERE plugin_name = ?", (plugin_name,)
        ).fetchall()
        result = {}
        for k, v in rows:
            try:
                result[k] = json.loads(v)
            except (ValueError, TypeError):
                result[k] = v
        return result


def purge_plugin(plugin_name: str, filename: str | Path | None = None) -> bool:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        with conn:
            cursor = conn.execute(
                "DELETE FROM plugins WHERE plugin_name = ?", (plugin_name,)
            )
            return cursor.rowcount > 0


def purge_all_plugin_data(filename: str | Path | None = None) -> bool:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        with conn:
            conn.execute("DELETE FROM plugin_kv")
            conn.execute("DELETE FROM plugins")
            return True


def delete_plugin_data(
    plugin_name: str, key: str, filename: str | Path | None = None
) -> bool:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        with conn:
            cursor = conn.execute(
                "DELETE FROM plugin_kv WHERE plugin_name = ? AND key = ?",
                (plugin_name, key),
            )
            return cursor.rowcount > 0
