# tests\test_env_keys.py

# tests/test_env_api_keys.py

from flyshell import constants as c
from flyshell.abstract.base_plugin import BasePlugin
from flyshell.core import directory, env, loader

import pytest


@pytest.fixture
def mock_env_file(tmp_path, monkeypatch):
    """Sets up a temporary flyshell_keys.env and points env/c.APP_DIR to it."""
    env_file = tmp_path / "flyshell_keys.env"
    monkeypatch.setattr(c, "APP_DIR", tmp_path)
    monkeypatch.setattr(env, "get_env_path", lambda: env_file)
    return env_file


def test_env_read_and_key_parsing(mock_env_file):
    mock_env_file.write_text(
        "# Comments should be ignored\n"
        "sample_api_token=secret_123\n"
        'sample_secondary_key="another_val"\n'
        "otherplugin_key=val\n"
        "invalid_line_without_equals\n"
    )
    keys = env.get_plugin_api_keys("sample")
    assert keys == {
        "api_token": "secret_123",
        "secondary_key": "another_val",
    }
    assert "key" not in keys


def test_extra_keys_are_included(mock_env_file):
    mock_env_file.write_text(
        "myplug_required_one=abc\n"
        "myplug_bonus_feature=xyz\n"
        "myplug_third_param=12345\n"
    )
    keys = env.get_plugin_api_keys("myplug")
    assert keys == {
        "required_one": "abc",
        "bonus_feature": "xyz",
        "third_param": "12345",
    }


def test_loader_populates_context_correctly(tmp_path, mock_env_file, monkeypatch):
    mock_env_file.write_text("dummy_token=token123\n")
    plugin_file = tmp_path / "dummy.py"
    plugin_file.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class DummyPlugin(BasePlugin):\n"
        "    api_keys = ['token']\n"
        "    def execute(self, args): return 0\n"
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "dummy" in c.PLUGINS
    plugin = c.PLUGINS["dummy"]
    assert plugin.context["plugin_name"] == "dummy"
    assert plugin.context["plugin_dir_name"] == "dummy"
    assert plugin.context["file_path"] == str(plugin_file)
    assert plugin.context["env_path"] == str(mock_env_file)
    assert plugin.api_keys_data == {"token": "token123"}
    assert plugin.get_api_key("token") == "token123"


def test_loader_rejects_plugin_with_missing_keys(
    tmp_path, mock_env_file, monkeypatch, capsys
):
    mock_env_file.write_text("needkey_first=val1\n")
    plugin_file = tmp_path / "needkey.py"
    plugin_file.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class NeedKeyPlugin(BasePlugin):\n"
        "    api_keys = ['first', 'second']\n"
        "    def execute(self, args): return 0\n"
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    out = capsys.readouterr().out
    assert "API Key Error" in out
    assert "second" in out


def test_directory_execute_fallback_when_keys_missing(
    mock_env_file, monkeypatch, capsys
):
    class IncompletePlugin(BasePlugin):
        api_keys = ["secret_key"]
        executed = False

        def execute(self, args):
            self.executed = True
            return 0

    ctx = {
        "plugin_name": "broken_keys",
        "plugin_dir_name": "broken_keys",
        "file_path": None,
        "env_path": str(mock_env_file),
        "api_keys": {},
    }
    instance = IncompletePlugin(ctx)
    monkeypatch.setitem(c.PLUGINS, "broken_keys", instance)
    exit_code = directory._execute_single("broken_keys")
    assert exit_code == 1
    assert instance.executed is False
    out = capsys.readouterr().out
    assert "Missing required API key(s): secret_key" in out


def test_get_all_keys_success(mock_env_file):
    mock_env_file.write_text("pluginA_token=123\npluginB_secret=xyz\n")
    code, output = env.get_all_keys()
    assert code == 0
    assert "pluginA_token = 123" in output
    assert "pluginB_secret = xyz" in output


def test_get_all_keys_empty_file(mock_env_file):
    mock_env_file.write_text("")
    code, output = env.get_all_keys()
    assert code == 0
    assert "No API keys configured." in output


def test_get_all_keys_missing_file(tmp_path, monkeypatch):
    missing_path = tmp_path / "does_not_exist.env"
    monkeypatch.setattr(env, "get_env_path", lambda: missing_path)
    code, output = env.get_all_keys()
    assert code == 1
    assert "Environment file not found" in output


def test_get_plugin_keys_formatted_success(mock_env_file):
    mock_env_file.write_text("weather_api_key=token123\nweather_units=metric\n")
    code, output = env.get_plugin_keys_formatted("weather")
    assert code == 0
    assert "weather" in output
    assert "api_key = token123" in output
    assert "units = metric" in output


def test_get_plugin_keys_formatted_invalid_input():
    code, output = env.get_plugin_keys_formatted("")
    assert code == 1
    assert "valid plugin name" in output
