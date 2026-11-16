# src/flyshell/native/legacy/diskops.py

from pathlib import Path
import os
import shutil


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


def lgc_dir(target_path: Path) -> tuple[int, list[tuple[str, bool]]]:
    if not target_path.exists():
        return (-1, [])  # ERR_NOT_FOUND
    if not target_path.is_dir():
        return (-4, [])  # ERR_NOT_DIR
    try:
        entries: list[tuple[str, bool]] = []
        with os.scandir(target_path) as it:
            for entry in it:
                try:
                    entries.append((entry.name, entry.is_dir()))
                except OSError:
                    entries.append((entry.name, False))
        return (0, entries)  # SUCCESS
    except PermissionError:
        return (-2, [])  # ERR_PERMISSION
    except OSError as e:
        if getattr(e, "errno", None) == 20:
            return (-4, [])  # ERR_NOT_DIR
        return (-13, [])  # ERR_IO
    except Exception:
        return (-99, [])  # ERR_UNKNOWN


def lgc_mkdir(target_path: Path, parents: bool = False) -> tuple[int, str]:
    try:
        if parents:
            os.makedirs(target_path, exist_ok=True)
        else:
            os.mkdir(target_path)
        return (0, "")  # SUCCESS
    except FileExistsError:
        return (-5, "")  # ERR_EXISTS
    except NotADirectoryError:
        return (-4, "")  # ERR_NOT_DIR
    except FileNotFoundError:
        for parent in target_path.parents:
            if parent.exists() and not parent.is_dir():
                return (-4, "")  # ERR_NOT_DIR
        return (-1, "")  # ERR_NOT_FOUND
    except PermissionError:
        return (-2, "")  # ERR_PERMISSION
    except OSError as e:
        if getattr(e, "errno", None) == 28:
            return (-12, "")  # ERR_NO_SPACE
        return (-13, "")  # ERR_IO
    except Exception:
        return (-99, "")  # ERR_UNKNOWN


def lgc_rename(src_path: Path, dst_path: Path) -> tuple[int, str]:
    if not src_path.exists():
        return (-1, "")  # ERR_NOT_FOUND
    if src_path == dst_path:
        return (-7, "")  # ERR_SAME_FILE
    if dst_path.exists():
        return (-5, "")  # ERR_EXISTS
    try:
        src_path.rename(dst_path)
        return (0, "")  # SUCCESS
    except PermissionError:
        return (-2, "")  # ERR_PERMISSION
    except OSError as e:
        if getattr(e, "errno", None) == 18:
            return (-10, "")  # ERR_XDEV
        return (-13, "")  # ERR_IO
    except Exception:
        return (-99, "")  # ERR_UNKNOWN


def lgc_rm(target_path: Path, recursive: bool = False) -> tuple[int, str]:
    if not target_path.exists() and not target_path.is_symlink():
        return (-1, "")  # ERR_NOT_FOUND
    is_dir = target_path.is_dir() and not target_path.is_symlink()
    if is_dir and not recursive:
        return (-3, "")  # ERR_IS_DIR
    try:
        if is_dir:
            shutil.rmtree(target_path)
        else:
            os.remove(target_path)
        return (0, "")  # SUCCESS
    except PermissionError:
        return (-2, "")  # ERR_PERMISSION
    except OSError:
        return (-13, "")  # ERR_IO
    except Exception:
        return (-99, "")  # ERR_UNKNOWN


def lgc_rmdir(target_path: Path, force: bool = False) -> tuple[int, str]:
    if not target_path.exists():
        return (-1, "")  # ERR_NOT_FOUND
    if not target_path.is_dir():
        return (-4, "")  # ERR_NOT_DIR
    try:
        has_contents = any(target_path.iterdir())
        if has_contents and not force:
            return (-6, "")  # ERR_NOT_EMPTY
        if has_contents and force:
            shutil.rmtree(target_path)
        else:
            os.rmdir(target_path)
        return (0, "")  # SUCCESS
    except PermissionError:
        return (-2, "")  # ERR_PERMISSION
    except OSError as e:
        if getattr(e, "errno", None) in (39, 66, 145):
            return (-6, "")  # ERR_NOT_EMPTY
        return (-13, "")  # ERR_IO
    except Exception:
        return (-99, "")  # ERR_UNKNOWN


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
        if getattr(e, "errno", None) == 28:
            return (-12, "")  # ERR_NO_SPACE
        return (-13, "")  # ERR_IO
    except Exception:
        return (-99, "")  # ERR_UNKNOWN
