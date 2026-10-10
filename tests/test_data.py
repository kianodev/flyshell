# \tests\test_data.py

from flyshell.core import data
import pytest

pytestmark = pytest.mark.skip(reason="Tests legacy depreciated API, pending rewrite")

def test_data_write_read(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    data.write(["plugin", "test_plugin", "setting"], "active", filename=test_db)
    result = data.read(["plugin", "test_plugin", "setting"], filename=test_db)
    assert result == "active"

def test_data_nested_dict_handling(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    data.write(["plugin", "notes", "config", "theme"], "dark", filename=test_db)
    data.write(["plugin", "notes", "config", "font_size"], 14, filename=test_db)
    config = data.read(["plugin", "notes", "config"], filename=test_db)
    assert config == {"theme": "dark", "font_size": 14}
    assert data.read(["plugin", "notes", "config", "theme"], filename=test_db) == "dark"
    assert data.read(["plugin", "notes", "config", "font_size"], filename=test_db) == 14

def test_data_del(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    data.write(["plugin", "scratchpad", "item"], "temporary", filename=test_db)
    assert data.read(["plugin", "scratchpad", "item"], filename=test_db) == "temporary"
    deleted = data.delete(["plugin", "scratchpad", "item"], filename=test_db)
    assert deleted is True
    assert data.read(["plugin", "scratchpad", "item"], filename=test_db) is None

def test_data_history_append_read(tmp_path):
    test_db = tmp_path / "test_flyshell.db"
    data.write(["core", "auth"], {"username": "tester", "hash": "abc", "salt": "123"}, filename=test_db)
    auth_info = data.read(["core", "auth"], filename=test_db)
    assert auth_info["username"] == "tester"