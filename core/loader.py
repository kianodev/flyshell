# \core\loader.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data, directory
from pathlib import Path
import importlib.util
import os

def scan_plugins(plugin_folder="plugin"):
    folder = Path(plugin_folder)
    count = 0
    for file_path in folder.glob("*py"):
        if file_path.name.startswith("_"):
            continue
        plugin_name = file_path.stem
        spec = importlib.util.spec_from_file_location(plugin_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        directory.PLUGINS[plugin_name] = module
        if count == 0:
            print("\nInstalled Plugins:")
        print(f"✅ - {plugin_name}")
        count += 1
    print(f"\nTotal of {count} plugin(s) found.") if count > 0 else print("\nNo plugins found.")

def build_context(plugin_name):
    plugin_storage = data.read(["plugin", plugin_name])
    if plugin_storage is None:
        plugin_storage = {}
        data.write(["plugin", plugin_name], plugin_storage)
    context = {
        "metadata": {
            "host_os": data.HOST_OS,
            "version": data.VERSION,
            "build": data.BUILD
        },
        "storage": plugin_storage
    }
    return context
