# src/flyshell/__init__.py

try:
    from flyshell.abstract.base_plugin import BasePlugin

    __all__ = ["BasePlugin"]
except ImportError:
    BasePlugin = None
    __all__ = []
    pass


try:
    from . import _native_disk
except ImportError:
    _native_disk = None


def check_native() -> bool:
    if _native_disk is not None:
        return _native_disk.ping() == 42
    return False
