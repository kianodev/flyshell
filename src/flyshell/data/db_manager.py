# src/flyshell/data/db_manager.py

from flyshell import constants as c

from pathlib import Path
import sqlite3


def get_storage_size(filename: str | Path | None = None) -> str:
    target = Path(filename) if filename is not None else c.FILE_PATH
    if not target.exists():
        return "File not found"
    num_bytes = float(target.stat().st_size)
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024.0:
            return (
                f"{int(num_bytes)} {unit}" if unit == "B" else f"{num_bytes:.2f} {unit}"
            )
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} TB"


def get_connection(filename: str | Path | None = None) -> sqlite3.Connection:
    target = Path(filename) if filename is not None else c.FILE_PATH
    if str(target) != ":memory:":
        target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialise(
    filename: str | Path | None = None, initialised: set[str] | None = None
) -> None:
    target = filename if filename is not None else c.FILE_PATH
    if initialised is None:
        initialised = c.INITIALISED
    target = str(target)
    if target in initialised:
        return
    with get_connection(filename) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        current_version = conn.execute("PRAGMA user_version;").fetchone()[0]
        if current_version == 0:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS auth (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        username TEXT NOT NULL,
                        hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cmd_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS core_config (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugins (
                        plugin_name TEXT PRIMARY KEY,
                        installed_at TEXT NOT NULL,
                        is_enabled INTEGER NOT NULL DEFAULT 1
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugin_kv (
                        plugin_name TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        PRIMARY KEY (plugin_name, key),
                        FOREIGN KEY (plugin_name) REFERENCES plugins(plugin_name) ON DELETE CASCADE
                    );
                """)
                conn.execute("PRAGMA user_version = 1;")
    initialised.add(target)
