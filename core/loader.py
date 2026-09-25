# \core\loader.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data
from core.base_plugin import BasePlugin
from core.directory import ALIAS, COMMANDS
from pathlib import Path
import importlib.util
import inspect
import os
import sys

RESERVED_NAMES = set(COMMANDS.keys()) | set(ALIAS.keys())

def scan_plugins(plugin_folder=None):
    folder = Path(plugin_folder) if plugin_folder else data.USER_PLUGIN_DIR
    data.PLUGINS.clear()
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        print("\nNo plugins found.")
        return
    folder_str = str(folder)
    if folder_str not in sys.path:
        sys.path.insert(0, folder_str)
    candidates = {}
    for item in folder.iterdir():
        file_path = None
        plugin_name = None
        if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
            file_path = item
            plugin_name = item.stem
        elif item.is_dir() and not item.name.startswith((".", "_")):
            entry = item / "plugin.py"
            if entry.exists():
                file_path = entry
                plugin_name = item.name
        if not file_path:
            continue
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    ctx = build_context(plugin_name)
                    instance = obj(ctx)
                    candidates.setdefault(plugin_name, []).append((instance, file_path))
                    break
        except Exception as e:
            print(f"\n⚠️ Plugin Failure - Failed to inspect '{plugin_name}'")
            print(f"Exception code: {e}, Flyshell will still launch.")
    loaded_count = 0
    first_print = True
    for name, entries in candidates.items():
        failed = False
        if name in RESERVED_NAMES:
            print(f"\n⚠️ Collision Error - Plugin '{name}' conflicts with a built-in Flyshell command and will not be loaded.")
            failed = True
        if len(entries) > 1:
            paths = "\n    - ".join(str(path) for _, path in entries)
            print(f"\n⚠️ Collision Error - Multiple plugins named '{name}' detected: {paths}")
            print(f"The above plugins will not be loaded. Please rename them to unique names.")
            failed = True
        if failed:
            continue
        instance, _ = entries[0]
        data.PLUGINS[name] = instance
        if first_print:
            print("\nInstalled Plugins:")
            first_print = False
        print(f"✅ - {name}")
        loaded_count += 1
    if loaded_count > 0:
        print(f"\nTotal of {loaded_count} plugin(s) found.")
    else:
        print("\nNo plugins loaded.")

def build_context(plugin_name):
    plugin_storage = data.read(["plugin", plugin_name])
    if plugin_storage is None:
        plugin_storage = {}
        data.write(["plugin", plugin_name], plugin_storage)
    context = {
        "plugin_name": plugin_name,
        "metadata": {
            "host_os": data.HOST_OS,
            "version": data.VERSION,
            "build": data.BUILD
        },
        "storage": plugin_storage
    }
    return context