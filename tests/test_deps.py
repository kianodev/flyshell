# tests/test_deps.py

from flyshell import constants as c
from flyshell.startup import deps, loader

from unittest.mock import MagicMock, patch


class DummyPlugin:
    def __init__(self, name="Dummy Plugin", libs=None):
        self.name = name
        self.third_pty_libs = libs if libs is not None else []


def test_check_module_installed_existing_builtin():
    assert deps.check_module_installed("sys") is True
    assert deps.check_module_installed("os") is True


def test_check_module_installed_nonexistent():
    assert deps.check_module_installed("non_existent_fake_package_xyz123") is False


def test_check_module_installed_handles_exceptions():
    with patch(
        "importlib.util.find_spec", side_effect=ValueError("Invalid module name")
    ):
        assert deps.check_module_installed("bad.name...") is False
    with patch(
        "importlib.util.find_spec", side_effect=ModuleNotFoundError("Not found")
    ):
        assert deps.check_module_installed("missing_lib") is False


def test_verify_plugin_dependencies_empty():
    plugin = DummyPlugin(libs=[])
    installed, missing = deps.verify_plugin_dependencies(plugin)
    assert installed == []
    assert missing == []


def test_verify_plugin_dependencies_no_attribute():
    dummy = object()
    installed, missing = deps.verify_plugin_dependencies(dummy)
    assert installed == []
    assert missing == []


def test_verify_plugin_dependencies_mixed(monkeypatch):
    def fake_find_spec(name):
        return MagicMock() if name in ("sys", "math") else None

    monkeypatch.setattr("importlib.util.find_spec", fake_find_spec)
    plugin = DummyPlugin(libs=["sys", "math", "ghost_lib", "skibidi_rizz"])
    installed, missing = deps.verify_plugin_dependencies(plugin)
    assert installed == ["sys", "math"]
    assert missing == ["ghost_lib", "skibidi_rizz"]


def test_check_all_plugin_dependencies_empty(capsys):
    with patch.dict(c.PLUGINS, {}, clear=True):
        result = loader.check_all_plugin_dependencies()
        assert result == {}
        captured = capsys.readouterr()
        assert captured.out == ""


def test_check_all_plugin_dependencies_no_deps_declared(capsys):
    plugin = DummyPlugin(name="CleanPlugin", libs=[])
    with patch.dict(c.PLUGINS, {"clean": plugin}, clear=True):
        result = loader.check_all_plugin_dependencies()
        assert result == {}
        captured = capsys.readouterr()
        assert (
            "✅ No third-party dependencies required for any loaded plugins."
            in captured.out
        )


def test_check_all_plugin_dependencies_with_missing(capsys, monkeypatch):
    def fake_find_spec(name):
        return MagicMock() if name == "numpy" else None

    monkeypatch.setattr("importlib.util.find_spec", fake_find_spec)
    plugin = DummyPlugin(name="DataPlugin", libs=["numpy", "aura", "yis"])
    with patch.dict(c.PLUGINS, {"data_plug": plugin}, clear=True):
        missing_dict = loader.check_all_plugin_dependencies()
        assert missing_dict == {"data_plug": ["aura", "yis"]}
        captured = capsys.readouterr()
        assert "Plugin: DataPlugin (data_plug)" in captured.out
        assert "✅ numpy - Dependency found" in captured.out
        assert "⚠️ aura - DEPENDENCY NOT FOUND" in captured.out
        assert "⚠️ yis - DEPENDENCY NOT FOUND" in captured.out
        assert (
            "Install using: 'sys pip install aura' once system has booted."
            in captured.out
        )
        assert (
            "Install using: 'sys pip install yis' once system has booted."
            in captured.out
        )
