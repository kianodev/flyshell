# src/flyshell/pkgm/__init__.py

from flyshell.pkgm.inspection import (
    check_all_plugin_dependencies,
    check_module_installed,
    verify_plugin_dependencies,
)
from flyshell.pkgm.keys import (
    check_plugin_api_keys,
    get_all_keys,
    get_plugin_api_keys,
    get_plugin_keys_formatted,
    remove_plugin_api_key,
    set_plugin_api_key,
)
from flyshell.pkgm.loader import (
    build_context,
    scan_plugins,
    unload_plugins,
)

__all__ = [
    "build_context",
    "check_all_plugin_dependencies",
    "check_module_installed",
    "check_plugin_api_keys",
    "get_all_keys",
    "get_plugin_api_keys",
    "get_plugin_keys_formatted",
    "remove_plugin_api_key",
    "scan_plugins",
    "set_plugin_api_key",
    "unload_plugins",
    "verify_plugin_dependencies",
]
