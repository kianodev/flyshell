# \core\migrations.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

import json
import sqlite3

def _setup_schema(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auth (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                username TEXT NOT NULL,
                hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cmd_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                namespace TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (namespace, key)
            )
        """)

def _migrate_json(project_root, legacy_json_path, legacy_db_path):
    if not legacy_json_path.exists():
        return
    print("\n⚠️ - Legacy 1st Generation JSON format detected ('flyshell_storage.json').")
    print("Migrating your storage to 2nd Generation SQLite...")
    conn = None
    try:
        with open(legacy_json_path, "r") as f:
            raw_data = json.load(f)
        conn = sqlite3.connect(legacy_db_path)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.execute("""
                INSERT INTO storage (key, value) VALUES ('root', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (json.dumps(raw_data, indent=4),))
        conn.close()
        legacy_json_path.rename(project_root / "flyshell_storage.json.bak")
        print("SUCCESS: Migrated to 2nd Generation SQLite. Backed up as 'flyshell_storage.json.bak'")
    except Exception as e:
        if conn:
            conn.close()
        print(f"System Error: Migration failed ({e}).")

def _migrate_sqlite(project_root, legacy_db_path, file_path, get_connection_fn):
    if not legacy_db_path.exists():
        return
    try:
        legacy_conn = sqlite3.connect(legacy_db_path)
        cursor = legacy_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='storage'")
        if not cursor.fetchone():
            legacy_conn.close()
            return
        cursor.execute("SELECT value FROM storage WHERE key = 'root'")
        row = cursor.fetchone()
        legacy_conn.close()
        if not row:
            return
        print("\n⚠️ - Legacy 2nd Generation Flat SQLite format detected ('flyshell_storage.db').")
        print("Migrating your storage to 3rd Generation Relational SQLite...")
        root_data = json.loads(row[0])
        with get_connection_fn(file_path) as new_conn:
            auth_info = root_data.get("core", {}).get("auth", {})
            if auth_info and "hash" in auth_info:
                new_conn.execute("""
                    INSERT OR REPLACE INTO auth (id, username, hash, salt)
                    VALUES (1, ?, ?, ?)
                """, (
                    auth_info.get("username", "User"),
                    auth_info.get("hash", ""),
                    auth_info.get("salt", "")
                ))
            history_list = root_data.get("core", {}).get("cmd_history", [])
            if isinstance(history_list, list):
                new_conn.execute("DELETE FROM cmd_history")
                for entry in history_list:
                    if isinstance(entry, dict):
                        new_conn.execute("""
                            INSERT INTO cmd_history (command, timestamp)
                            VALUES (?, ?)
                        """, (entry.get("command", ""), entry.get("timestamp", "")))
            for section, subdict in root_data.items():
                if not isinstance(subdict, dict):
                    continue
                for key, val in subdict.items():
                    if section == "core" and key in ("auth", "cmd_history"):
                        continue
                    new_conn.execute("""
                        INSERT OR REPLACE INTO kv_store (namespace, key, value)
                        VALUES (?, ?, ?)
                    """, (section, key, json.dumps(val)))
        legacy_db_path.rename(project_root / "flyshell_storage.db.bak")
        print("SUCCESS: Migrated to 3rd Generation Relational. Backed up as 'flyshell_storage.db.bak'")
    except Exception as e:
        print(f"System Error: Migration failed ({e}).")

def run_migrations(conn, file_path, project_root, get_connection_fn):
    legacy_json = project_root / "flyshell_storage.json"
    legacy_db = project_root / "flyshell_storage.db"
    _migrate_json(project_root, legacy_json, legacy_db)
    _migrate_sqlite(project_root, legacy_db, file_path, get_connection_fn)
    _setup_schema(conn)