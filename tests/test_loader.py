# \tests\test_loader.py

from flyshell.core import data, loader
from flyshell.core.base_plugin import BasePlugin

def test_loader_rejects_command_name_collision(tmp_path, monkeypatch):
    bad_plugin = tmp_path / "sys.py"
    bad_plugin.write_text(
        "from flyshell.core.base_plugin import BasePlugin\n"
        "class SysPlugin(BasePlugin):\n"
        "    def execute(self, args): pass\n"
    )
    monkeypatch.setattr(data, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "sys" not in data.PLUGINS

def test_loader_discovers_and_instantiates_valid_plugin(tmp_path, monkeypatch):
    valid_plugin = tmp_path / "sample.py"
    valid_plugin.write_text(
        "from flyshell.core.base_plugin import BasePlugin\n"
        "class SamplePlugin(BasePlugin):\n"
        "    name = 'Sample Tool'\n"
        "    description = 'Testing tool'\n"
        "    def execute(self, args):\n"
        "        return (0, 'done')\n"
    )
    monkeypatch.setattr(data, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "sample" in data.PLUGINS
    plugin_instance = data.PLUGINS["sample"]
    assert isinstance(plugin_instance, BasePlugin)
    assert plugin_instance.name == "Sample Tool"

def test_loader_handles_broken_plugin_gracefully(tmp_path, monkeypatch):
    broken_plugin = tmp_path / "broken.py"
    broken_plugin.write_text("import non_existent_library_12345\n")
    monkeypatch.setattr(data, "USER_PLUGIN_DIR", tmp_path)
    loader.scan_plugins(plugin_folder=tmp_path)
    assert "broken" not in data.PLUGINS