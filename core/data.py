# \core\data.py

BUILD = 73
VERSION = "0.72"

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import migrations
from pathlib import Path
import json
import platform
import sqlite3
import time

HOST_OS = platform.system()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FILE_PATH = PROJECT_ROOT / "flyshell3.db"

LEGACY_JSON_PATH = PROJECT_ROOT / "flyshell_storage.json"
LEGACY_DB_PATH = PROJECT_ROOT / "flyshell_storage.db"

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

INITIALISED = False

def initialise():
    global INITIALISED
    if INITIALISED:
        return
    print("\nChecking database viability...")
    with _get_connection(FILE_PATH) as conn:
        migrations.run_migrations(conn, FILE_PATH, PROJECT_ROOT, _get_connection)
    print("\n✅ - Database is up to date.")
    INITIALISED = True

def read(keys=None, filename=FILE_PATH):
    initialise()
    if keys is None:
        return _dump_all()
    if isinstance(keys, str):
        keys = [keys]
    with _get_connection(filename) as conn:
        if keys[0] == "core" and len(keys) >= 2 and keys[1] == "auth":
            row = conn.execute("SELECT username, hash, salt FROM auth WHERE id = 1").fetchone()
            if not row:
                return None
            auth_dict = {"username": row[0], "hash": row[1], "salt": row[2]}
            if len(keys) == 2:
                return auth_dict
            return auth_dict.get(keys[2])
        if keys[0] == "core" and len(keys) >= 2 and keys[1] == "cmd_history":
            rows = conn.execute("SELECT command, timestamp FROM cmd_history ORDER BY id ASC").fetchall()
            return [{"command": r[0], "timestamp": r[1]} for r in rows]
        namespace = keys[0]
        key = keys[1] if len(keys) > 1 else "default"
        row = conn.execute("SELECT value FROM kv_store WHERE namespace = ? AND key = ?", (namespace, key)).fetchone()
        if not row:
            return None
        try:
            val = json.loads(row[0])
        except (ValueError, TypeError):
            val = row[0]
        if len(keys) > 2 and isinstance(val, dict):
            for subkey in keys[2:]:
                if isinstance(val, dict) and subkey in val:
                    val = val[subkey]
                else:
                    return None
        return val

def write(keys, value, filename=FILE_PATH):
    initialise()
    if isinstance(keys, str):
        keys = [keys]
    with _get_connection(filename) as conn:
        # Route 1: Auth
        if keys[0] == "core" and len(keys) >= 2 and keys[1] == "auth":
            if isinstance(value, dict):
                conn.execute("""
                    INSERT OR REPLACE INTO auth (id, username, hash, salt)
                    VALUES (1, ?, ?, ?)
                """, (value.get("username", "User"), value.get("hash", ""), value.get("salt", "")))
            return
        namespace = keys[0]
        key = keys[1] if len(keys) > 1 else "default"
        if len(keys) > 2:
            existing = read([namespace, key]) or {}
            curr = existing
            for subkey in keys[2:-1]:
                if subkey not in curr or not isinstance(curr[subkey], dict):
                    curr[subkey] = {}
                curr = curr[subkey]
            curr[keys[-1]] = value
            serialised = json.dumps(existing, indent=4)
        else:
            serialised = json.dumps(value, indent=4)
        conn.execute("""
            INSERT OR REPLACE INTO kv_store (namespace, key, value)
            VALUES (?, ?, ?)
        """, (namespace, key, serialised))

def delete(keys, filename=FILE_PATH):
    initialise()
    if isinstance(keys, str):
        keys = [keys]
    with _get_connection(filename) as conn:
        if keys[0] == "core" and len(keys) >= 2 and keys[1] == "cmd_history":
            conn.execute("DELETE FROM cmd_history")
            return True
        if keys[0] == "core" and len(keys) >= 2 and keys[1] == "auth":
            conn.execute("DELETE FROM auth WHERE id = 1")
            return True
        namespace = keys[0]
        key = keys[1] if len(keys) > 1 else "default"
        if len(keys) > 2:
            existing = read([namespace, key])
            if not isinstance(existing, dict):
                return False
            curr = existing
            for subkey in keys[2:-1]:
                if isinstance(curr, dict) and subkey in curr:
                    curr = curr[subkey]
                else:
                    return False
            if isinstance(curr, dict) and keys[-1] in curr:
                del curr[keys[-1]]
                conn.execute("""
                    INSERT OR REPLACE INTO kv_store (namespace, key, value)
                    VALUES (?, ?, ?)
                """, (namespace, key, json.dumps(existing, indent=4)))
                return True
            return False
        cursor = conn.execute("DELETE FROM kv_store WHERE namespace = ? AND key = ?", (namespace, key))
        return cursor.rowcount > 0

def _dump_all():
    dump = {"core": {}, "plugin": {}}
    with _get_connection(FILE_PATH) as conn:
        row = conn.execute("SELECT username, hash, salt FROM auth WHERE id = 1").fetchone()
        if row:
            dump["core"]["auth"] = {"username": row[0], "hash": row[1], "salt": row[2]}
        history_rows = conn.execute("SELECT command, timestamp FROM cmd_history ORDER BY id ASC").fetchall()
        dump["core"]["cmd_history"] = [{"command": r[0], "timestamp": r[1]} for r in history_rows]
        kv_rows = conn.execute("SELECT namespace, key, value FROM kv_store").fetchall()
        for ns, k, val in kv_rows:
            if ns not in dump:
                dump[ns] = {}
            try:
                dump[ns][k] = json.loads(val)
            except Exception:
                dump[ns][k] = val
    return dump

def append_history(cmd, timestamp):
    initialise()
    with _get_connection(FILE_PATH) as conn:
        conn.execute(
            "INSERT INTO cmd_history (command, timestamp) VALUES (?, ?)",
            (cmd, timestamp)
        )