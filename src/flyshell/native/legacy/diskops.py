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
