# src/flyshell/pkgm/inspection.py

from flyshell import constants as c

from typing import Any, Dict, List, Tuple
import importlib.util


def check_module_installed(module_name: str) -> bool:
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ModuleNotFoundError, ValueError):
        return False


def verify_plugin_dependencies(plugin: Any) -> Tuple[List[str], List[str]]:
    declared = getattr(plugin, "third_pty_libs", None) or []
    installed = []
    missing = []
    for dep in declared:
        if check_module_installed(dep):
            installed.append(dep)
        else:
            missing.append(dep)
    return installed, missing


def check_all_plugin_dependencies() -> Dict[str, List[str]]:
    if not c.PLUGINS:
        return {}
    print("\nFlyshell will now check plugin third-party dependencies.")
    plugins_with_deps = False
    all_missing: Dict[str, List[str]] = {}
    for identifier, plugin in c.PLUGINS.items():
        declared = getattr(plugin, "third_pty_libs", None) or []
        if not declared:
            continue
        plugins_with_deps = True
        installed, missing = verify_plugin_dependencies(plugin)
        print(f"\nPlugin: {plugin.name} ({identifier})")
        for dep in installed:
            print(f"✅ {dep} - Dependency found")
        for dep in missing:
            print(f"⚠️ {dep} - DEPENDENCY NOT FOUND")
            print(f"Install using: 'sys pip install {dep}' once system has booted.")
        if missing:
            all_missing[identifier] = missing
    if not plugins_with_deps:
        print("✅ No third-party dependencies required for any loaded plugins.")
    return all_missing
