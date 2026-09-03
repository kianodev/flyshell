# \core\data.py

BUILD = 44
VERSION = "0.43"

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILE_PATH = PROJECT_ROOT / "flyshell_storage.db"

SESSION_START_TIME = time.time()
SESSION_CMD_COUNT = 0

def _get_connection(filename=FILE_PATH):
    conn = sqlite3.connect(filename)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
    return conn

def initialise(filename=FILE_PATH):
    old_json = PROJECT_ROOT / "flyshell_storage.json"
    with _get_connection(filename) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM storage WHERE key = 'root'")
        if cursor.fetchone()[0] == 0 and old_json.exists():
            try:
                print("\nLegacy storage format detected ('flyshell_storage.json').")
                print("Migrating records to SQLite3...")
                with open(old_json, "r") as f:
                    old_data = json.load(f)
                _save_all(old_data, filename)
                old_json.rename(PROJECT_ROOT / "flyshell_storage.json.bak")
                print("SUCCESS: Data migrated. Saved backup as 'flyshell_storage.json.bak'\n")
            except Exception as e:
                print(f"System Error: Migration failed ({e}), starting fresh.")

def load_all(filename=FILE_PATH):
    initialise(filename)
    with _get_connection(filename) as conn:
        cursor = conn.execute("SELECT value FROM storage WHERE key = 'root'")
        row = cursor.fetchone()
        if not row:
            return {}
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            return {}

def _save_all(data, filename=FILE_PATH):
    serialised = json.dumps(data, indent=4)
    with _get_connection(filename) as conn:
        conn.execute("""
            INSERT INTO storage (key, value) VALUES ('root', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (serialised,))

def write(keys, value, filename=FILE_PATH):
    data = load_all(filename)
    if isinstance(keys, str):
        keys = [keys]
    current = data
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    _save_all(data, filename)

def read(keys=None, filename=FILE_PATH):
    data = load_all(filename)
    if keys is None:
        return data
    if isinstance(keys, str):
        keys = [keys]
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

def delete(keys, filename=FILE_PATH):
    data = load_all(filename)
    if isinstance(keys, str):
        keys = [keys]
    current = data
    for key in keys[:-1]:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    if isinstance(current, dict) and keys[-1] in current:
        del current[keys[-1]]
        _save_all(data,)
        return True
    return False