# \tests\test_data.py

from flyshell.core import data
import pytest
import sqlite3

def test_database_initialises_with_user_version(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    data.initialise(filename=test_db)
    with sqlite3.connect(test_db) as conn:
        version = conn.execute("PRAGMA user_version;").fetchone()[0]
    assert version == 1

def test_auth_set_get_and_clear(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    assert data.get_auth(filename=test_db) is None
    data.set_auth("alice", "hashed_secret", "random_salt", filename=test_db)
    record = data.get_auth(filename=test_db)
    assert record is not None
    assert record["username"] == "alice"
    assert record["hash"] == "hashed_secret"
    assert record["salt"] == "random_salt"
    assert "created_at" in record
    deleted = data.clear_auth(filename=test_db)
    assert deleted is True
    assert data.get_auth(filename=test_db) is None

def test_cmd_history_append_order_and_limit(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    data.append_history("cd /", "2026-10-10T10:00:00Z", filename=test_db)
    data.append_history("dir", "2026-10-10T10:01:00Z", filename=test_db)
    data.append_history("clear", "2026-10-10T10:02:00Z", filename=test_db)
    all_history = data.get_history(filename=test_db)
    assert len(all_history) == 3
    assert [entry["command"] for entry in all_history] == ["cd /", "dir", "clear"]
    limited = data.get_history(limit=2, filename=test_db)
    assert len(limited) == 2
    assert [entry["command"] for entry in limited] == ["dir", "clear"]
    data.clear_history(filename=test_db)
    assert data.get_history(filename=test_db) == []

def test_core_config_crud(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    assert data.get_config("theme", default="light", filename=test_db) == "light"
    data.set_config("theme", "dark", filename=test_db)
    assert data.get_config("theme", filename=test_db) == "dark"
    data.set_config("settings", {"bell": False, "font_size": 12}, filename=test_db)
    assert data.get_config("settings", filename=test_db) == {"bell": False, "font_size": 12}
    deleted = data.delete_config("theme", filename=test_db)
    assert deleted is True
    assert data.get_config("theme", filename=test_db) is None

def test_plugin_storage_and_cascading_purge(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    data.set_plugin_data("notes", "font", "monospace", filename=test_db)
    data.set_plugin_data("notes", "count", 42, filename=test_db)
    data.set_plugin_data("scratchpad", "draft", "hello world", filename=test_db)
    assert data.get_plugin_data("notes", "font", filename=test_db) == "monospace"
    assert data.get_plugin_data("notes", "count", filename=test_db) == 42
    assert data.get_all_plugin_data("notes", filename=test_db) == {"font": "monospace", "count": 42}
    purged = data.purge_plugin("notes", filename=test_db)
    assert purged is True
    assert data.get_all_plugin_data("notes", filename=test_db) == {}
    assert data.get_plugin_data("scratchpad", "draft", filename=test_db) == "hello world"