# tests/test_env.py

from flyshell import constants as c
from flyshell import data
from flyshell.abstract.base_plugin import BasePlugin
from flyshell.core import directory
from flyshell.startup import deps, loader

import pytest


@pytest.fixture
def env_file():
    return c.ENV_PATH


def test_read_env_file_ignores_comments_and_malformed_lines(env_file):
    env_file.write_text(
        "# Comments should be ignored\n"
        "sample_api_token=secret_123\n"
        "invalid_line_without_equals\n",
        encoding="utf-8",
    )
    assert data.read_env_file() == {"sample_api_token": "secret_123"}


def test_read_env_file_strips_quotes_from_values(env_file):
    env_file.write_text('sample_secondary_key="another_val"\n', encoding="utf-8")
    assert data.read_env_file() == {"sample_secondary_key": "another_val"}


def test_get_plugin_api_keys_filters_by_plugin_prefix(env_file):
    env_file.write_text(
        "sample_api_token=secret_123\n" "otherplugin_key=val\n",
        encoding="utf-8",
    )
    keys = deps.get_plugin_api_keys("sample")
    assert keys == {"api_token": "secret_123"}


def test_get_plugin_api_keys_includes_extra_undeclared_keys(env_file):
    env_file.write_text(
        "myplug_required_one=abc\n"
        "myplug_bonus_feature=xyz\n"
        "myplug_third_param=12345\n",
        encoding="utf-8",
    )
    assert deps.get_plugin_api_keys("myplug") == {
        "required_one": "abc",
        "bonus_feature": "xyz",
        "third_param": "12345",
    }


def test_loader_populates_plugin_context_paths(tmp_path, env_file, monkeypatch):
    env_file.write_text("dummy_token=token123\n", encoding="utf-8")
    plugin_file = tmp_path / "dummy.py"
    plugin_file.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class DummyPlugin(BasePlugin):\n"
        "    api_keys = ['token']\n"
        "    def execute(self, args): return 0\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    plugin = c.PLUGINS["dummy"]
    assert plugin.context["plugin_name"] == "dummy"
    assert plugin.context["plugin_dir_name"] == "dummy"
    assert plugin.context["file_path"] == str(plugin_file)
    assert plugin.context["env_path"] == str(env_file)


def test_loader_injects_plugin_api_keys(tmp_path, env_file, monkeypatch):
    env_file.write_text("dummy_token=token123\n", encoding="utf-8")
    plugin_file = tmp_path / "dummy.py"
    plugin_file.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class DummyPlugin(BasePlugin):\n"
        "    api_keys = ['token']\n"
        "    def execute(self, args): return 0\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    plugin = c.PLUGINS["dummy"]
    assert plugin.api_keys_data == {"token": "token123"}
    assert plugin.get_api_key("token") == "token123"


def test_directory_blocks_plugin_execution_when_keys_missing(
    env_file, monkeypatch, capsys
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
        "env_path": str(env_file),
        "api_keys": {},
    }
    instance = IncompletePlugin(ctx)
    monkeypatch.setitem(c.PLUGINS, "broken_keys", instance)
    exit_code = directory._execute_single("broken_keys")
    assert exit_code == 1
    assert instance.executed is False
    assert "Missing required API key(s): secret_key" in capsys.readouterr().out


def test_get_all_keys_success(env_file):
    env_file.write_text("pluginA_token=123\npluginB_secret=xyz\n", encoding="utf-8")
    code, output = deps.get_all_keys()
    assert code == 0
    assert "pluginA_token = 123" in output
    assert "pluginB_secret = xyz" in output


def test_get_all_keys_empty_file(env_file):
    env_file.write_text("", encoding="utf-8")
    code, output = deps.get_all_keys()
    assert code == 0
    assert "No API keys configured." in output


def test_get_all_keys_missing_file(tmp_path, monkeypatch):
    missing_path = tmp_path / "does_not_exist.env"
    monkeypatch.setattr(data, "get_env_path", lambda: missing_path)
    code, output = deps.get_all_keys()
    assert code == 1
    assert "Environment file not found" in output


def test_get_plugin_keys_formatted_success(env_file):
    env_file.write_text(
        "weather_api_key=token123\nweather_units=metric\n", encoding="utf-8"
    )
    code, output = deps.get_plugin_keys_formatted("weather")
    assert code == 0
    assert "api_key = token123" in output
    assert "units = metric" in output


def test_get_plugin_keys_formatted_invalid_input():
    code, output = deps.get_plugin_keys_formatted("")
    assert code == 1
    assert "valid plugin name" in output


def test_env_preserves_square_brackets_in_values(env_file):
    env_file.write_text('sample_token="abc[123]xyz"\n', encoding="utf-8")
    assert deps.get_plugin_api_keys("sample") == {"token": "abc[123]xyz"}


def test_set_plugin_api_key_resolves_plugin_identifier(env_file, monkeypatch):
    class AliasedPlugin(BasePlugin):
        name = "Weather Tool"
        identifier = "weather"

        def execute(self, args):
            return 0

    ctx = {
        "plugin_name": "weather",
        "plugin_dir_name": "weather_folder",
        "file_path": None,
        "env_path": str(env_file),
        "api_keys": {},
    }
    monkeypatch.setitem(c.PLUGINS, "weather", AliasedPlugin(ctx))
    code, _ = deps.set_plugin_api_key("weather", "api_key", "secret123")
    assert code == 0
    assert "weather_folder_API_KEY=secret123" in env_file.read_text(encoding="utf-8")


def test_remove_plugin_api_key_resolves_plugin_identifier(env_file, monkeypatch):
    class AliasedPlugin(BasePlugin):
        name = "Weather Tool"
        identifier = "weather"

        def execute(self, args):
            return 0

    env_file.write_text("weather_folder_API_KEY=secret123\n", encoding="utf-8")
    ctx = {
        "plugin_name": "weather",
        "plugin_dir_name": "weather_folder",
        "file_path": None,
        "env_path": str(env_file),
        "api_keys": {},
    }
    monkeypatch.setitem(c.PLUGINS, "weather", AliasedPlugin(ctx))
    code, _ = deps.remove_plugin_api_key("weather", "api_key")
    assert code == 0
    assert "weather_folder_API_KEY" not in env_file.read_text(encoding="utf-8")


def test_case_insensitive_get_api_key():
    class CasePlugin(BasePlugin):
        api_keys = ["API_TOKEN"]

        def execute(self, args):
            return 0

    instance = CasePlugin(
        {
            "plugin_name": "caseplug",
            "plugin_dir_name": "caseplug",
            "api_keys": {"api_token": "secret_123"},
        }
    )
    assert instance.get_api_key("API_TOKEN") == "secret_123"
    assert instance.get_api_key("api_token") == "secret_123"


def test_directory_allows_case_insensitive_required_keys(monkeypatch):
    class CasePlugin(BasePlugin):
        api_keys = ["API_TOKEN"]

        def execute(self, args):
            return 0

    instance = CasePlugin(
        {
            "plugin_name": "caseplug",
            "plugin_dir_name": "caseplug",
            "api_keys": {"api_token": "secret_123"},
        }
    )
    monkeypatch.setitem(c.PLUGINS, "caseplug", instance)
    assert directory._execute_single("caseplug") == 0


def test_get_plugin_api_keys_avoids_prefix_collision(env_file, monkeypatch):
    env_file.write_text(
        "weather_api_key=base_secret\nweather_pro_api_key=pro_secret\n",
        encoding="utf-8",
    )

    class DummyPlugin(BasePlugin):
        def execute(self, args):
            return 0

    p1 = DummyPlugin({"plugin_name": "weather", "plugin_dir_name": "weather"})
    p2 = DummyPlugin({"plugin_name": "weather_pro", "plugin_dir_name": "weather_pro"})
    monkeypatch.setitem(c.PLUGINS, "weather", p1)
    monkeypatch.setitem(c.PLUGINS, "weather_pro", p2)
    assert deps.get_plugin_api_keys("weather") == {"api_key": "base_secret"}
    assert deps.get_plugin_api_keys("weather_pro") == {"api_key": "pro_secret"}
