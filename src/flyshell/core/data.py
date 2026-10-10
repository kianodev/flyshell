# src\flyshell\core\data.py

BUILD = 90
VERSION = "0.89"

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from pathlib import Path
import json
import os
import platform
import sqlite3
import time

HOST_OS = platform.system()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def get_app_dir() -> Path:
    home = Path.home()
    if HOST_OS == "Windows":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif HOST_OS == "Darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    app_dir = base / "Flyshell"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

APP_DIR = get_app_dir()
FILE_PATH = APP_DIR / "flyshell.db"
USER_PLUGIN_DIR = APP_DIR / "plugins"

SESSION_START_TIME = time.time()
SESSION_CMD_COUNT = 0
PLUGINS = {}

def get_storage_size() -> str:
    if not FILE_PATH.exists():
        return "File not found"
    num_bytes = float(FILE_PATH.stat().st_size)
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024.0:
            return f"{int(num_bytes)} {unit}" if unit == "B" else f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} TB"

def _get_connection(filename=FILE_PATH):
    conn = sqlite3.connect(filename)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

INITIALISED = set()

def initialise(filename=FILE_PATH):
    global INITIALISED
    target = str(filename)
    if target in INITIALISED:
        return
    with _get_connection(filename) as conn:
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
    INITIALISED.add(target)

def get_auth(filename=FILE_PATH) -> dict | None:
    initialise(filename)
    with _get_connection(filename) as conn:
        row = conn.execute("SELECT username, hash, salt, created_at FROM auth WHERE id = 1").fetchone()
        if not row:
            return None
        return {"username": row[0], "hash": row[1], "salt": row[2], "created_at": row[3]}

def set_auth(username: str, pwd_hash: str, salt: str, filename=FILE_PATH) -> None:
    initialise(filename)
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with _get_connection(filename) as conn:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO auth (id, username, hash, salt, created_at)
                VALUES (1, ?, ?, ?, ?)
            """, (username, pwd_hash, salt, now_utc))

def clear_auth(filename=FILE_PATH) -> bool:
    initialise(filename)
    with _get_connection(filename) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM auth WHERE id = 1")
            return cursor.rowcount > 0

def append_history(cmd: str, timestamp: str, filename=FILE_PATH) -> None:
    initialise(filename)
    with _get_connection(filename) as conn:
        with conn:
            conn.execute("INSERT INTO cmd_history (command, timestamp) VALUES (?, ?)", (cmd, timestamp))

def get_history(limit: int | None = None, filename=FILE_PATH) -> list[dict]:
    initialise(filename)
    with _get_connection(filename) as conn:
        if limit is not None and limit > 0:
            query = "SELECT command, timestamp FROM cmd_history ORDER BY id DESC LIMIT ?"
            rows = conn.execute(query, (limit,)).fetchall()
            rows.reverse()
        else:
            query = "SELECT command, timestamp FROM cmd_history ORDER BY id ASC"
            rows = conn.execute(query).fetchall()
        return [{"command": r[0], "timestamp": r[1]} for r in rows]

def clear_history(filename=FILE_PATH) -> bool:
    initialise(filename)
    with _get_connection(filename) as conn:
        with conn:
            conn.execute("DELETE FROM cmd_history")
            return True

def get_config(key: str, default=None, filename=FILE_PATH):
    initialise(filename)
    with _get_connection(filename) as conn:
        row = conn.execute("SELECT value FROM core_config WHERE key = ?", (key,)).fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            return row[0]

def set_config(key: str, value, filename=FILE_PATH) -> None:
    initialise(filename)
    serialized = json.dumps(value)
    with _get_connection(filename) as conn:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO core_config (key, value)
                VALUES (?, ?)
            """, (key, serialized))

def delete_config(key: str, filename=FILE_PATH) -> bool:
    initialise(filename)
    with _get_connection(filename) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM core_config WHERE key = ?", (key,))
            return cursor.rowcount > 0

def register_plugin(plugin_name: str, filename=FILE_PATH) -> None:
    initialise(filename)
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with _get_connection(filename) as conn:
        with conn:
            conn.execute("""
                INSERT OR IGNORE INTO plugins (plugin_name, installed_at, is_enabled)
                VALUES (?, ?, 1)
            """, (plugin_name, now_utc))

def get_plugin_data(plugin_name: str, key: str, default=None, filename=FILE_PATH):
    initialise(filename)
    with _get_connection(filename) as conn:
        row = conn.execute("""
            SELECT value FROM plugin_kv WHERE plugin_name = ? AND key = ?
        """, (plugin_name, key)).fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            return row[0]

def set_plugin_data(plugin_name: str, key: str, value, filename=FILE_PATH) -> None:
    initialise(filename)
    register_plugin(plugin_name, filename=filename)
    serialized = json.dumps(value)
    with _get_connection(filename) as conn:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO plugin_kv (plugin_name, key, value)
                VALUES (?, ?, ?)
            """, (plugin_name, key, serialized))

def get_all_plugin_data(plugin_name: str, filename=FILE_PATH) -> dict:
    initialise(filename)
    with _get_connection(filename) as conn:
        rows = conn.execute("SELECT key, value FROM plugin_kv WHERE plugin_name = ?", (plugin_name,)).fetchall()
        result = {}
        for k, v in rows:
            try:
                result[k] = json.loads(v)
            except (ValueError, TypeError):
                result[k] = v
        return result

def purge_plugin(plugin_name: str, filename=FILE_PATH) -> bool:
    initialise(filename)
    with _get_connection(filename) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM plugins WHERE plugin_name = ?", (plugin_name,))
            return cursor.rowcount > 0