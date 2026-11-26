# src/flyshell/data/auth.py

from flyshell.data import db_manager as db

from pathlib import Path
import time


def get_auth(filename: str | Path | None = None) -> dict | None:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        row = conn.execute(
            "SELECT username, hash, salt, created_at FROM auth WHERE id = 1"
        ).fetchone()
        if not row:
            return None
        return {
            "username": row[0],
            "hash": row[1],
            "salt": row[2],
            "created_at": row[3],
        }


def set_auth(
    username: str, pwd_hash: str, salt: str, filename: str | Path | None = None
) -> None:
    db.initialise(filename)
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with db.get_connection(filename) as conn:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO auth (id, username, hash, salt, created_at)
                VALUES (1, ?, ?, ?, ?)
            """,
                (username, pwd_hash, salt, now_utc),
            )


def clear_auth(filename: str | Path | None = None) -> bool:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM auth WHERE id = 1")
            return cursor.rowcount > 0
