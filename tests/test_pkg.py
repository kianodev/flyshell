# tests/test_pkg.py

from flyshell import constants as c
from flyshell.builtin import pkg
from flyshell.core import env

import pytest


@pytest.fixture
def mock_env_file(tmp_path, monkeypatch):
    c.PLUGINS.clear()
    env_file = tmp_path / "flyshell_keys.env"
    monkeypatch.setattr(c, "APP_DIR", tmp_path)
    monkeypatch.setattr(env, "get_env_path", lambda: env_file)
    yield env_file
    c.PLUGINS.clear()


def test_pkg_dispatches_help_on_empty_args(capsys):
    parent = pkg.Pkg()
    code, msg = parent.execute([])
    assert code == 0
    out = capsys.readouterr().out
    assert "Command Family: pkg" in out
    assert "api (alias: keys)" in out


def test_pkg_unknown_subcommand():
    parent = pkg.Pkg()
    code, msg = parent.execute(["unknown_cmd"])
    assert code == 1
    assert "Unknown subcommand 'unknown_cmd'" in msg


def test_pkg_api_all_keys(mock_env_file):
    mock_env_file.write_text("dummy_token=123\n")
    parent = pkg.Pkg()
    code, msg = parent.execute(["api"])
    assert code == 0
    assert "dummy_token = 123" in msg


def test_pkg_api_plugin_keys(mock_env_file):
    mock_env_file.write_text("weather_key=secret\nother_key=skip\n")
    parent = pkg.Pkg()
    code, msg = parent.execute(["api", "weather"])
    assert code == 0
    assert "key = secret" in msg
    assert "other_key" not in msg
