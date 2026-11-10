# src/flyshell/native/diskops_bridge.py

from typing import Any

_HAS_NATIVE: bool = False
_native: Any = None

try:
    from flyshell.bin import _native_diskops

    if hasattr(_native_diskops, "ping") and _native_diskops.ping() == 42:
        _native = _native_diskops
        _HAS_NATIVE = True
except (ImportError, AttributeError):
    _HAS_NATIVE = False
    _native = None

ERROR_MAP = {
    -1: ("System Error", "File or path not found"),
    -2: ("System Error", "Permission denied"),
    -3: ("System Error", "Target is a directory, not a file"),
    -4: ("System Error", "Target is not a directory"),
    -5: ("System Error", "Item already exists"),
    -6: ("Directory Error", "Directory is not empty"),
    -7: ("System Error", "Source and destination are the same"),
    -8: ("System Error", "Target file is empty"),
    -9: ("Command Error", "Invalid path syntax or file name"),
    -10: ("System Error", "Cannot move directly across devices or partitions"),
    -11: ("System Error", "File is currently in use or locked by another process"),
    -12: ("System Error", "No space left on device"),
    -13: ("System Error", "Read/write I/O failure"),
    -14: ("System Error", "Failed to decode content as UTF-8"),
    -15: ("System Error", "Failed to launch application or file"),
    -99: ("System Error", "Unexpected native filesystem error"),
}


def has_native_support() -> bool:
    return _HAS_NATIVE


def translate_error(code: int, target: str = "") -> tuple[int, str]:
    category, default_msg = ERROR_MAP.get(
        code, ("System Error", "Unknown native error.")
    )
    target_str = f"for '{target}'" if target else ""
    if target_str:
        return (1, f"\n{category}: {default_msg} {target_str}\n")
    return (1, f"\n{category}: {default_msg}.")
