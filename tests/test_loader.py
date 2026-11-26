# tests/test_loader.py

from flyshell import constants as c
from flyshell.abstract.base_plugin import BasePlugin
from flyshell.core import directory
from flyshell.startup import loader


def test_loader_rejects_command_name_collision(tmp_path, monkeypatch):
    bad_plugin = tmp_path / "sys.py"
    bad_plugin.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class SysPlugin(BasePlugin):\n"
        "    def execute(self, args): pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "sys" not in c.PLUGINS


def test_loader_discovers_and_instantiates_valid_plugin(tmp_path, monkeypatch):
    valid_plugin = tmp_path / "sample.py"
    valid_plugin.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class SamplePlugin(BasePlugin):\n"
        "    name = 'Sample Tool'\n"
        "    description = 'Testing tool'\n"
        "    def execute(self, args):\n"
        "        return (0, 'done')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "sample" in c.PLUGINS
    plugin_instance = c.PLUGINS["sample"]
    assert isinstance(plugin_instance, BasePlugin)
    assert plugin_instance.name == "Sample Tool"


def test_loader_handles_broken_plugin_gracefully(tmp_path, monkeypatch):
    broken_plugin = tmp_path / "broken.py"
    broken_plugin.write_text("import non_existent_library_12345\n", encoding="utf-8")
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "broken" not in c.PLUGINS


def test_loader_does_not_execute_code_in_reserved_plugin(tmp_path, monkeypatch):
    sentinel = tmp_path / "sentinel.txt"
    bad_plugin = tmp_path / "cd.py"
    bad_plugin.write_text(
        f"from pathlib import Path\nPath('{sentinel.as_posix()}').write_text('executed')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "cd" not in c.PLUGINS
    assert not sentinel.exists()


def test_loader_rejects_duplicate_plugin_identifiers(tmp_path, monkeypatch):
    for fname in ("plug_a.py", "plug_b.py"):
        (tmp_path / fname).write_text(
            "from flyshell.abstract.base_plugin import BasePlugin\n"
            "class DupPlugin(BasePlugin):\n"
            "    identifier = 'shared_id'\n"
            "    def execute(self, args): pass\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "shared_id" not in c.PLUGINS


def test_loader_does_not_call_on_load_for_duplicate_plugins(tmp_path, monkeypatch):
    sentinel = tmp_path / "on_load_called.txt"
    for fname in ("plug_a.py", "plug_b.py"):
        (tmp_path / fname).write_text(
            "from pathlib import Path\n"
            "from flyshell.abstract.base_plugin import BasePlugin\n"
            "class DupPlugin(BasePlugin):\n"
            "    identifier = 'shared_id'\n"
            "    def on_load(self):\n"
            f"        Path('{sentinel.as_posix()}').write_text('called')\n"
            "    def execute(self, args): pass\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert not sentinel.exists()


def test_execute_single_does_not_unload_plugin(monkeypatch):
    events = []

    class LifecyclePlugin(BasePlugin):
        def on_load(self):
            events.append("load")

        def execute(self, args):
            events.append("execute")
            return 0

        def on_unload(self):
            events.append("unload")

    monkeypatch.setattr(directory, "log", lambda cmd: None)
    plugin = LifecyclePlugin({"plugin_name": "life"})
    monkeypatch.setattr(c, "PLUGINS", {"life": plugin})
    code = directory._execute_single("life")
    assert code == 0
    assert events == ["load", "execute"]


def test_unload_plugins_calls_on_unload_even_if_one_raises(monkeypatch):
    unloaded = []

    class BrokenUnloadPlugin(BasePlugin):
        def execute(self, args):
            return 0

        def on_unload(self):
            unloaded.append("broken")
            raise RuntimeError("cleanup failed")

    class HealthyUnloadPlugin(BasePlugin):
        def execute(self, args):
            return 0

        def on_unload(self):
            unloaded.append("healthy")

    p1 = BrokenUnloadPlugin({"plugin_name": "p1"})
    p2 = HealthyUnloadPlugin({"plugin_name": "p2"})
    monkeypatch.setattr(c, "PLUGINS", {"p1": p1, "p2": p2})
    loader.unload_plugins()
    assert unloaded == ["broken", "healthy"]


def test_unload_plugins_clears_registry(monkeypatch):
    class HealthyUnloadPlugin(BasePlugin):
        def execute(self, args):
            return 0

    p1 = HealthyUnloadPlugin({"plugin_name": "p1"})
    monkeypatch.setattr(c, "PLUGINS", {"p1": p1})
    loader.unload_plugins()
    assert c.PLUGINS == {}


def test_loader_ignores_imported_plugin_subclasses(tmp_path, monkeypatch):
    helper_file = tmp_path / "_helper.py"
    helper_file.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class ImportedPlugin(BasePlugin):\n"
        "    identifier = 'imported_one'\n"
        "    def execute(self, args): pass\n",
        encoding="utf-8",
    )
    main_file = tmp_path / "real_plug.py"
    main_file.write_text(
        "from _helper import ImportedPlugin\n"
        "class RealPlugin(ImportedPlugin):\n"
        "    identifier = 'real_one'\n"
        "    def execute(self, args): pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "real_one" in c.PLUGINS
    assert "imported_one" not in c.PLUGINS


def test_loader_handles_on_load_exception_gracefully(tmp_path, monkeypatch):
    crashing_plugin = tmp_path / "crash_init.py"
    crashing_plugin.write_text(
        "from flyshell.abstract.base_plugin import BasePlugin\n"
        "class CrashInitPlugin(BasePlugin):\n"
        "    def on_load(self):\n"
        "        raise RuntimeError('boom in on_load')\n"
        "    def execute(self, args): pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(c, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "crash_init" not in c.PLUGINS
