# tests/test_pkg.py

from flyshell import constants as c
from flyshell.builtin import pkg


def test_pkg_dispatches_help_on_empty_args(capsys):
    code, _ = pkg.Pkg().execute([])
    assert code == 0
    out = capsys.readouterr().out
    assert "Command Family: pkg" in out
    assert "api (alias: keys)" in out


def test_pkg_unknown_subcommand():
    code, msg = pkg.Pkg().execute(["unknown_cmd"])
    assert code == 1
    assert "Unknown subcommand 'unknown_cmd'" in msg


def test_pkg_api_all_keys():
    c.ENV_PATH.write_text("dummy_token=123\n", encoding="utf-8")
    code, msg = pkg.Pkg().execute(["api", "view"])
    assert code == 0
    assert "dummy_token = 123" in msg


def test_pkg_api_plugin_keys():
    c.ENV_PATH.write_text("weather_key=secret\nother_key=skip\n", encoding="utf-8")
    code, msg = pkg.Pkg().execute(["api", "view", "weather"])
    assert code == 0
    assert "key = secret" in msg
    assert "other_key" not in msg
