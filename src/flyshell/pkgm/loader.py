# src/flyshell/pkgm/loader.py

from flyshell import constants as c
from flyshell import data
from flyshell.abstract.base_plugin import BasePlugin
from flyshell.pkgm import keys

from pathlib import Path
import importlib.util
import inspect
import sys


def scan_plugins(plugin_folder: str | Path | None = None) -> None:
    folder = Path(plugin_folder) if plugin_folder else c.USER_PLUGIN_DIR
    c.PLUGINS.clear()
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
        default_name = None
        if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
            file_path = item
            default_name = item.stem
        elif item.is_dir() and not item.name.startswith((".", "_")):
            entry = item / "plugin.py"
            if entry.exists():
                file_path = entry
                default_name = item.name
        if not file_path or not default_name:
            continue
        if default_name in c.RESERVED_NAMES:
            print(
                f"\n⚠️ Collision Error - Plugin '{default_name}' conflicts with a built-in Flyshell command and will not be loaded."
            )
            continue
        try:
            module_name = f"plugin_{default_name}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BasePlugin)
                    and obj is not BasePlugin
                    and obj.__module__ == module.__name__
                ):
                    resolved_name = getattr(obj, "identifier", None) or default_name
                    if resolved_name in c.RESERVED_NAMES:
                        print(
                            f"\n⚠️ Collision Error - Plugin '{resolved_name}' conflicts with a built-in Flyshell command and will not be loaded."
                        )
                        break
                    ctx = build_context(resolved_name, default_name, file_path)
                    candidates.setdefault(resolved_name, []).append(
                        (obj, ctx, file_path)
                    )
                    break
        except Exception as e:
            print(f"\n⚠️ Plugin Failure - Failed to inspect '{default_name}'")
            print(f"Exception code: {e}, Flyshell will still launch.")
    loaded_count = 0
    first_print = True
    for name, entries in candidates.items():
        if len(entries) > 1:
            paths = "\n    - ".join(str(path) for _, _, path in entries)
            print(
                f"\n⚠️ Collision Error - Multiple plugins named '{name}' detected: {paths}"
            )
            print(
                "The above plugins will not be loaded. Please rename them to unique names."
            )
            continue
        obj, ctx, _ = entries[0]
        try:
            instance = obj(ctx)
        except Exception as e:
            print(f"\n⚠️ Plugin Failure - Failed to initialise '{name}'")
            print(f"Exception code: {e}, Flyshell will still launch.")
            continue
        c.PLUGINS[name] = instance
        if first_print:
            print("\nInstalled Plugins:")
            first_print = False
        print(f"✅ - {instance.name} ({name})")
        loaded_count += 1
    if loaded_count > 0:
        print(f"\nTotal of {loaded_count} plugin(s) found.")
    else:
        print("\nNo plugins loaded.")


def build_context(
    plugin_name: str, default_name: str, file_path: str | Path | None = None
) -> dict:
    plugin_storage = data.get_all_plugin_data(plugin_name)
    api_keys = keys.get_plugin_api_keys(str(default_name))
    context = {
        "plugin_name": plugin_name,
        "plugin_dir_name": str(default_name),
        "file_path": str(file_path) if file_path else None,
        "env_path": str(data.get_env_path()),
        "api_keys": api_keys,
        "metadata": {"host_os": c.HOST_OS, "version": c.VERSION, "build": c.BUILD},
        "storage": plugin_storage,
    }
    return context


def unload_plugins() -> None:
    for identifier, plugin in list(c.PLUGINS.items()):
        try:
            if hasattr(plugin, "on_unload"):
                plugin.on_unload()
        except Exception as e:
            print(f"\n⚠️ Plugin Unload Error - '{identifier}': {e}")
    c.PLUGINS.clear()
