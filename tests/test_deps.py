# tests/test_deps.py

from flyshell import constants as c
from flyshell import pkgm

from unittest.mock import MagicMock, patch


class DummyPlugin:
    def __init__(self, name="Dummy Plugin", libs=None):
        self.name = name
        self.third_pty_libs = libs if libs is not None else []


def test_check_module_installed_existing_builtin():
    assert pkgm.check_module_installed("sys") is True


def test_check_module_installed_nonexistent():
    assert pkgm.check_module_installed("non_existent_fake_package_xyz123") is False


def test_check_module_installed_handles_value_error():
    with patch(
        "importlib.util.find_spec", side_effect=ValueError("Invalid module name")
    ):
        assert pkgm.check_module_installed("bad.name...") is False


def test_check_module_installed_handles_module_not_found_error():
    with patch(
        "importlib.util.find_spec", side_effect=ModuleNotFoundError("Not found")
    ):
        assert pkgm.check_module_installed("missing_lib") is False


def test_verify_plugin_dependencies_empty():
    plugin = DummyPlugin(libs=[])
    installed, missing = pkgm.verify_plugin_dependencies(plugin)
    assert installed == []
    assert missing == []


def test_verify_plugin_dependencies_no_attribute():
    dummy = object()
    installed, missing = pkgm.verify_plugin_dependencies(dummy)
    assert installed == []
    assert missing == []


def test_verify_plugin_dependencies_mixed(monkeypatch):
    def fake_find_spec(name):
        return MagicMock() if name in ("sys", "math") else None

    monkeypatch.setattr("importlib.util.find_spec", fake_find_spec)
    plugin = DummyPlugin(libs=["sys", "math", "ghost_lib", "skibidi_rizz"])
    installed, missing = pkgm.verify_plugin_dependencies(plugin)
    assert installed == ["sys", "math"]
    assert missing == ["ghost_lib", "skibidi_rizz"]


def test_check_all_plugin_dependencies_empty(capsys):
    with patch.dict(c.PLUGINS, {}, clear=True):
        result = pkgm.check_all_plugin_dependencies()
        assert result == {}
        assert capsys.readouterr().out == ""


def test_check_all_plugin_dependencies_no_deps_declared(capsys):
    plugin = DummyPlugin(name="CleanPlugin", libs=[])
    with patch.dict(c.PLUGINS, {"clean": plugin}, clear=True):
        result = pkgm.check_all_plugin_dependencies()
        assert result == {}
        assert (
            "✅ No third-party dependencies required for any loaded plugins."
            in capsys.readouterr().out
        )


def test_check_all_plugin_dependencies_returns_missing_map(monkeypatch):
    def fake_find_spec(name):
        return MagicMock() if name == "numpy" else None

    monkeypatch.setattr("importlib.util.find_spec", fake_find_spec)
    plugin = DummyPlugin(name="DataPlugin", libs=["numpy", "aura", "yis"])
    with patch.dict(c.PLUGINS, {"data_plug": plugin}, clear=True):
        assert pkgm.check_all_plugin_dependencies() == {"data_plug": ["aura", "yis"]}


def test_check_all_plugin_dependencies_prints_install_instructions(capsys, monkeypatch):
    def fake_find_spec(name):
        return MagicMock() if name == "numpy" else None

    monkeypatch.setattr("importlib.util.find_spec", fake_find_spec)
    plugin = DummyPlugin(name="DataPlugin", libs=["numpy", "aura"])
    with patch.dict(c.PLUGINS, {"data_plug": plugin}, clear=True):
        pkgm.check_all_plugin_dependencies()
        out = capsys.readouterr().out
        assert "✅ numpy - Dependency found" in out
        assert "⚠️ aura - DEPENDENCY NOT FOUND" in out
        assert "Install using: 'sys pip install aura' once system has booted." in out
