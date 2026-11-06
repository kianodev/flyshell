# src\flyshell\core\loader.py

from flyshell import constants as c
from flyshell.abstract.base_plugin import BasePlugin
from flyshell.core import data, env
from flyshell.core.directory import RESERVED_NAMES

from pathlib import Path
import importlib.util
import inspect
import sys


def scan_plugins(plugin_folder=None):
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
        if default_name in RESERVED_NAMES:
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
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    resolved_name = getattr(obj, "identifier", None) or default_name
                    if resolved_name in RESERVED_NAMES:
                        print(
                            f"\n⚠️ Collision Error - Plugin '{resolved_name}' conflicts with a built-in Flyshell command and will not be loaded."
                        )
                        break
                    ctx = build_context(resolved_name, default_name, file_path)
                    required_keys = getattr(obj, "api_keys", [])
                    found_keys = ctx["api_keys"]
                    found_keys_lower = {k.lower(): v for k, v in found_keys.items()}
                    missing_keys = [k for k in required_keys if k.lower() not in found_keys_lower]
                    if missing_keys:
                        env_file = ctx["env_path"]
                        print(
                            f"\n⚠️ API Key Error - Plugin '{resolved_name}' is missing required key(s): {', '.join(missing_keys)}"
                        )
                        print(f"Please define them in: {env_file} as:")
                        for mk in missing_keys:
                            print(f"{default_name}_{mk}=<your_key>")
                        print("You can do this once Flyshell has booted.")
                    instance = obj(ctx)
                    candidates.setdefault(resolved_name, []).append(
                        (instance, file_path)
                    )
                    break
        except Exception as e:
            print(f"\n⚠️ Plugin Failure - Failed to inspect '{default_name}'")
            print(f"Exception code: {e}, Flyshell will still launch.")
    loaded_count = 0
    first_print = True
    for name, entries in candidates.items():
        if len(entries) > 1:
            paths = "\n    - ".join(str(path) for _, path in entries)
            print(
                f"\n⚠️ Collision Error - Multiple plugins named '{name}' detected: {paths}"
            )
            print(
                "The above plugins will not be loaded. Please rename them to unique names."
            )
            continue
        instance, _ = entries[0]
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


def build_context(plugin_name, default_name, file_path=None):
    plugin_storage = data.get_all_plugin_data(plugin_name)
    api_keys = env.get_plugin_api_keys(str(default_name))
    context = {
        "plugin_name": plugin_name,
        "plugin_dir_name": str(default_name),
        "file_path": str(file_path) if file_path else None,
        "env_path": str(env.get_env_path()),
        "api_keys": api_keys,
        "metadata": {"host_os": c.HOST_OS, "version": c.VERSION, "build": c.BUILD},
        "storage": plugin_storage,
    }
    return context


def check_plugin_api_keys():
    if not c.PLUGINS:
        return
    print("\nFlyshell will now check plugin API keys.")
    has_keys_to_report = False
    for identifier, plugin in c.PLUGINS.items():
        required_keys = getattr(plugin, "api_keys", [])
        configured_keys = getattr(plugin, "api_keys_data", {})
        dir_name = plugin.context.get("plugin_dir_name", identifier)
        if not required_keys and not configured_keys:
            continue
        has_keys_to_report = True
        configured_lookup = {k.lower(): (k, v) for k, v in configured_keys.items()}
        seen_keys = set()
        print(f"\nPlugin: {plugin.name} ({identifier})")
        for req in required_keys:
            req_lower = req.lower()
            seen_keys.add(req_lower)
            if req_lower in configured_lookup:
                orig_k, _ = configured_lookup[req_lower]
                print(f"✅ {orig_k} - Key found [Required]")
            else:
                print(f"⚠️ {req} - KEY NOT FOUND [Required]")
                print(f"Please define in the .env file as: {dir_name}_{req}=<your_key>")
        for k_lower, (orig_k, _) in sorted(configured_lookup.items()):
            if k_lower not in seen_keys:
                print(f"✅ {orig_k} - Key found [Optional/Extra]")
    if not has_keys_to_report:
        print("✅ No API keys required for any loaded plugins.")
