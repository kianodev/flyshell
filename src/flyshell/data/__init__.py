# src/flyshell/data/__init__.py

from flyshell.data.auth import clear_auth, get_auth, set_auth
from flyshell.data.config import delete_config, get_config, set_config
from flyshell.data.db_manager import get_connection, get_storage_size, initialise
from flyshell.data.history import append_history, clear_history, get_history
from flyshell.data.plugins import (
    delete_plugin_data,
    get_all_plugin_data,
    get_plugin_data,
    purge_all_plugin_data,
    purge_plugin,
    register_plugin,
    set_plugin_data,
)

__all__ = [
    "append_history",
    "clear_auth",
    "clear_history",
    "delete_config",
    "delete_plugin_data",
    "get_all_plugin_data",
    "get_auth",
    "get_config",
    "get_connection",
    "get_history",
    "get_plugin_data",
    "get_storage_size",
    "initialise",
    "purge_all_plugin_data",
    "purge_plugin",
    "register_plugin",
    "set_auth",
    "set_config",
    "set_plugin_data",
]
