# src/flyshell/data/history.py

from flyshell.data import db_manager as db

from pathlib import Path


def append_history(
    cmd: str, timestamp: str, filename: str | Path | None = None
) -> None:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        with conn:
            conn.execute(
                "INSERT INTO cmd_history (command, timestamp) VALUES (?, ?)",
                (cmd, timestamp),
            )


def get_history(
    limit: int | None = None, filename: str | Path | None = None
) -> list[dict]:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        if limit is not None and limit > 0:
            query = (
                "SELECT command, timestamp FROM cmd_history ORDER BY id DESC LIMIT ?"
            )
            rows = conn.execute(query, (limit,)).fetchall()
            rows.reverse()
        else:
            query = "SELECT command, timestamp FROM cmd_history ORDER BY id ASC"
            rows = conn.execute(query).fetchall()
        return [{"command": r[0], "timestamp": r[1]} for r in rows]


def clear_history(filename: str | Path | None = None) -> bool:
    db.initialise(filename)
    with db.get_connection(filename) as conn:
        with conn:
            conn.execute("DELETE FROM cmd_history")
            return True
