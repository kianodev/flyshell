# tests/test_data.py

from flyshell import constants as c
from flyshell.core import data
import sqlite3


def test_database_initialises_with_user_version():
    data.initialise()
    with sqlite3.connect(c.FILE_PATH) as conn:
        version = conn.execute("PRAGMA user_version;").fetchone()[0]
    assert version == 1


def test_get_auth_returns_none_when_unset():
    assert data.get_auth() is None


def test_set_and_get_auth():
    data.set_auth("alice", "hashed_secret", "random_salt")
    record = data.get_auth()
    assert record is not None
    assert record["username"] == "alice"
    assert record["hash"] == "hashed_secret"
    assert record["salt"] == "random_salt"
    assert "created_at" in record


def test_clear_auth_removes_record():
    data.set_auth("alice", "hashed_secret", "random_salt")
    assert data.clear_auth() is True
    assert data.get_auth() is None


def test_get_history_returns_all_in_chronological_order():
    data.append_history("cd /", "2026-10-10T10:00:00Z")
    data.append_history("dir", "2026-10-10T10:01:00Z")
    data.append_history("clear", "2026-10-10T10:02:00Z")
    all_history = data.get_history()
    assert [entry["command"] for entry in all_history] == ["cd /", "dir", "clear"]


def test_get_history_with_limit():
    data.append_history("cd /", "2026-10-10T10:00:00Z")
    data.append_history("dir", "2026-10-10T10:01:00Z")
    data.append_history("clear", "2026-10-10T10:02:00Z")
    limited = data.get_history(limit=2)
    assert [entry["command"] for entry in limited] == ["dir", "clear"]


def test_clear_history_empties_table():
    data.append_history("cd /", "2026-10-10T10:00:00Z")
    assert data.clear_history() is True
    assert data.get_history() == []


def test_get_config_returns_default_when_missing():
    assert data.get_config("theme", default="light") == "light"


def test_set_and_get_config_string():
    data.set_config("theme", "dark")
    assert data.get_config("theme") == "dark"


def test_set_and_get_config_json_object():
    data.set_config("settings", {"bell": False, "font_size": 12})
    assert data.get_config("settings") == {"bell": False, "font_size": 12}


def test_delete_config_removes_key():
    data.set_config("theme", "dark")
    assert data.delete_config("theme") is True
    assert data.get_config("theme") is None


def test_set_and_get_plugin_data():
    data.set_plugin_data("notes", "font", "monospace")
    data.set_plugin_data("notes", "count", 42)
    assert data.get_plugin_data("notes", "font") == "monospace"
    assert data.get_plugin_data("notes", "count") == 42


def test_get_all_plugin_data():
    data.set_plugin_data("notes", "font", "monospace")
    data.set_plugin_data("notes", "count", 42)
    assert data.get_all_plugin_data("notes") == {"font": "monospace", "count": 42}


def test_purge_plugin_cascades_and_isolates_other_plugins():
    data.set_plugin_data("notes", "font", "monospace")
    data.set_plugin_data("scratchpad", "draft", "hello world")
    assert data.purge_plugin("notes") is True
    assert data.get_all_plugin_data("notes") == {}
    assert data.get_plugin_data("scratchpad", "draft") == "hello world"
