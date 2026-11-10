# src/flyshell/__init__.py

try:
    from flyshell.abstract.base_plugin import BasePlugin

    __all__ = ["BasePlugin"]
except ImportError:
    BasePlugin = None
    __all__ = []
    pass


try:
    from flyshell.bin import _native_diskops
except ImportError:
    _native_diskops = None


def check_native() -> bool:
    if _native_diskops is not None:
        return _native_diskops.ping() == 42
    return False
