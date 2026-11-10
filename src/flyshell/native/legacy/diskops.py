# src/flyshell/native/legacy/diskops.py

from pathlib import Path


def lgc_cat(target_path: Path) -> tuple[int, str]:
    if not target_path.exists():
        return (-1, "")  # ERR_NOT_FOUND
    if target_path.is_dir():
        return (-3, "")  # ERR_IS_DIR
    try:
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if len(content) == 0:
            return (-8, "")  # ERR_EMPTY
        return (0, content)  # SUCCESS
    except PermissionError:
        return (-2, "")  # ERR_PERMISSION
    except UnicodeDecodeError:
        return (-14, "")  # ERR_DECODE
    except Exception:
        return (-13, "")  # ERR_IO


def lgc_touch(target_path: Path) -> tuple[int, str]:
    if target_path.is_dir():
        return (-3, "")  # ERR_IS_DIR
    try:
        target_path.touch(exist_ok=True)
        return (0, "")  # SUCCESS
    except PermissionError:
        return (-2, "")  # ERR_PERMISSION
    except FileNotFoundError:
        return (-1, "")  # ERR_NOT_FOUND
    except OSError as e:
        if getattr(e, "errno", None) == 28:  # ENOSPC
            return (-12, "")
        return (-13, "")  # ERR_IO
    except Exception:
        return (-99, "")  # ERR_UNKNOWN
