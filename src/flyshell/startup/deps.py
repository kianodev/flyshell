# src/flyshell/startup/deps.py

from typing import Any, List, Tuple
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
