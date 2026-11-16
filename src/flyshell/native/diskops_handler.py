# src/flyshell/native/diskops_handler.py

from flyshell import constants as c
from flyshell.abstract.base_cmd import BaseCmd
from flyshell.native import diskops_bridge as bridge
from flyshell.native.legacy import diskops as legacy

from pathlib import Path
import os


def _validate_delete_target(
    target_path: Path, raw_target: str
) -> tuple[int, str] | None:
    if target_path == target_path.parent or str(target_path) == target_path.anchor:
        return (
            1,
            "\nSecurity Error: Flyshell has blocked this action.\n"
            "You cannot delete the root filesystem directory.\n",
        )
    critical_system_dirs = [
        Path.home().parent.resolve(),
        Path.home().resolve(),
    ]
    if c.HOST_OS == "Windows":
        system_drive = os.environ.get("SystemDrive", "C:")
        critical_system_dirs.extend(
            [
                Path(f"{system_drive}\\Windows").resolve(),
                Path(f"{system_drive}\\Program Files").resolve(),
                Path(f"{system_drive}\\Program Files (x86)").resolve(),
            ]
        )
    else:
        critical_system_dirs.extend(
            [
                Path("/bin").resolve(),
                Path("/etc").resolve(),
                Path("/usr").resolve(),
                Path("/var").resolve(),
            ]
        )
    if target_path in critical_system_dirs:
        return (
            1,
            "\nSecurity Error: Flyshell has blocked this action.\n"
            f"Target '{raw_target}' is a protected operating system directory.\n",
        )
    if target_path == Path(os.getcwd()).resolve():
        return (
            1,
            "\nSystem Error: Cannot remove current working directory.\n"
            "Switch to a different directory using 'cd' first.\n",
        )
    flyshell_dirs = [
        c.APP_DIR.resolve(),
        c.PACKAGE_ROOT.resolve(),
        c.PROJECT_ROOT.resolve(),
    ]
    for protected in flyshell_dirs:
        if target_path == protected or target_path.is_relative_to(protected):
            return (
                1,
                "\nSecurity Error: Flyshell has blocked this action.\n"
                f"Target '{raw_target}' contains or belongs to Flyshell system files.\n"
                "If you wish to delete Flyshell, use the host.\n",
            )
    return None


class Cat(BaseCmd):
    name = "cat"
    description = "Display the contents of a text file"
    min_args = 1
    options = "Target file"
    aliases = ["read"]

    def execute(self, args):
        show_numbers = ("-n" in args) or ("--number" in args)
        limit = None
        filtered_args = []
        skip_next = False
        for i, token in enumerate(args):
            if skip_next:
                skip_next = False
                continue
            if token in ("-n", "--number"):
                continue
            if token in ("-l", "--limit"):
                if i + 1 < len(args) and args[i + 1].isdigit():
                    limit = int(args[i + 1])
                    skip_next = True
                    continue
                else:
                    return (
                        1,
                        f"\nCommand Error: '{token}' requires a positive integer limit.\n",
                    )
            filtered_args.append(token)
        if not filtered_args:
            return (1, "\nCommand Error: Target file not specified.\n")
        raw_target = " ".join(filtered_args).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
        if bridge.has_native_support() and hasattr(bridge._native, "cat"):
            code, content = bridge._native.cat(str(target_path))
        else:
            code, content = legacy.lgc_cat(target_path)
        if code != 0:
            return bridge.translate_error(code, raw_target)
        lines = content.splitlines(keepends=True)
        total_lines = len(lines)
        if limit is not None:
            lines = lines[:limit]
        output_lines = [
            f"\nDisplaying contents of file '{target_path.name}' ({len(lines)}/{total_lines} lines)\n"
        ]
        for line_idx, line in enumerate(lines, start=1):
            clean_line = line.rstrip("\r\n")
            if show_numbers:
                output_lines.append(f"{line_idx:4d} | {clean_line}")
            else:
                output_lines.append(clean_line)
        output_lines.append(f"\nEnd of '{target_path.name}'\n")
        return (0, "\n".join(output_lines))


class Dir(BaseCmd):
    name = "dir"
    description = "List all files in the current working directory"
    min_args = 0
    options = None
    aliases = ["ls"]

    def execute(self, args):
        target_str = args[0].strip("\"'") if args else os.getcwd()
        target_path = Path(target_str).expanduser().resolve()
        if bridge.has_native_support() and hasattr(bridge._native, "dir"):
            code, items = bridge._native.dir(str(target_path))
        else:
            code, items = legacy.lgc_dir(target_path)
        if code != 0:
            return bridge.translate_error(code, str(target_path))
        lines = [f"\nDirectory: '{target_path}'"]
        for name, is_dir in items:
            if is_dir:
                lines.append(f"[DIR] {name}/")
            else:
                lines.append(f"[FILE] {name}")
        lines.append(f"\nTotal items in directory: {len(items)}\n")
        return (0, "\n".join(lines))


class MkDir(BaseCmd):
    name = "mkdir"
    description = "Create a new directory from the current working directory"
    min_args = 1
    options = "Directory name"
    aliases = ["md"]

    def execute(self, args):
        use_parents = ("-p" in args) or ("--parents" in args)
        path_tokens = [arg for arg in args if arg not in ("-p", "--parents")]
        if not path_tokens:
            return (1, "\nCommand Error: Directory name not specified.\n")
        raw_target = " ".join(path_tokens).strip("\"'")
        target_path = Path(raw_target).expanduser()
        if bridge.has_native_support() and hasattr(bridge._native, "mkdir"):
            code, _ = bridge._native.mkdir(str(target_path), use_parents)
        else:
            code, _ = legacy.lgc_mkdir(target_path, use_parents)
        if code != 0:
            if code == -1 and not use_parents:
                return (
                    1,
                    "\nSystem Error: Parent directory does not exist. Use '-p' or '--parents' to create parent directories.\n",
                )
            return bridge.translate_error(code, raw_target)
        return (0, f"\nSUCCESS! Created directory '{raw_target}'\n")


class Rename(BaseCmd):
    name = "rename"
    description = "Rename a file or directory"
    min_args = 2
    options = "Old name, then new name"
    aliases = []

    def execute(self, args):
        raw_src = args[0].strip("\"'")
        raw_new_name = args[1].strip("\"'")
        if raw_new_name in (".", "..") or "/" in raw_new_name or "\\" in raw_new_name:
            return (1, "\nCommand Error: Invalid file name.\n")
        src_path = Path(raw_src).expanduser().resolve()
        if not src_path.exists():
            return (1, f"\nSystem Error: Target '{raw_src}' not found.\n")
        flyshell_dirs = [
            c.APP_DIR.resolve(),
            c.PACKAGE_ROOT.resolve(),
            c.PROJECT_ROOT.resolve(),
        ]
        for protected in flyshell_dirs:
            if src_path == protected or src_path.is_relative_to(protected):
                return (
                    1,
                    "\nSecurity Error: Flyshell has blocked this action.\n"
                    f"Target '{raw_src}' contains or belongs to Flyshell system files.\n",
                )
        new_path = src_path.parent / raw_new_name
        if new_path.exists():
            return (
                1,
                f"\nSystem Error: An item named '{raw_new_name}' already exists in this folder.\n",
            )
        if bridge.has_native_support() and hasattr(bridge._native, "rename"):
            code, _ = bridge._native.rename(str(src_path), str(new_path))
        else:
            code, _ = legacy.lgc_rename(src_path, new_path)
        if code != 0:
            return bridge.translate_error(code, raw_src)
        return (0, f"\nSUCCESS! Renamed '{src_path.name}' -> '{new_path.name}'\n")


class Rm(BaseCmd):
    name = "rm"
    description = "Remove files from the filesystem"
    min_args = 1
    options = "Target file"
    aliases = ["del"]

    def execute(self, args):
        force = ("-f" in args) or ("--force" in args)
        recursive = ("-r" in args) or ("--recursive" in args)
        flags = {"-f", "--force", "-r", "--recursive"}
        path_tokens = [arg for arg in args if arg not in flags]
        if not path_tokens:
            return (1, "\nCommand Error: No target file or directory specified.\n")
        raw_target = " ".join(path_tokens).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
        if not target_path.exists():
            return (1, f"\nSystem Error: Target '{raw_target}' not found.\n")
        blocked = _validate_delete_target(target_path, raw_target)
        if blocked is not None:
            return blocked
        is_directory = target_path.is_dir()
        if is_directory and not recursive:
            return (
                1,
                f"\nCommand Error: '{raw_target}' is a directory.\n"
                "Use '-r' or '--recursive' to remove directories.\n",
            )
        if not force:
            target_type = "directory and all its contents" if is_directory else "file"
            prompt_msg = f"\nAre you sure you want to permanently delete {target_type} '{raw_target}'? [y/n]: "
            try:
                confirm = input(prompt_msg).strip().lower()
            except (KeyboardInterrupt, EOFError):
                return (1, "\nDeletion cancelled by user.\n")
            if confirm != "y":
                return (0, "\nOperation cancelled. No files were deleted.\n")
        if bridge.has_native_support() and hasattr(bridge._native, "rm"):
            code, _ = bridge._native.rm(str(target_path), recursive)
        else:
            code, _ = legacy.lgc_rm(target_path, recursive)
        if code != 0:
            return bridge.translate_error(code, raw_target)
        if is_directory:
            return (
                0,
                f"\nSUCCESS! Deleted directory '{raw_target}' and all its contents.\n",
            )
        return (0, f"\nSUCCESS! Deleted file '{raw_target}'\n")


class RmDir(BaseCmd):
    name = "rmdir"
    description = "Remove the specified directory"
    min_args = 1
    options = "Target directory"
    aliases = []

    def execute(self, args):
        force = ("-f" in args) or ("--force" in args)
        path_tokens = [arg for arg in args if arg not in ("-f", "--force")]
        if not path_tokens:
            return (1, "\nCommand Error: Target directory not specified.\n")
        raw_target = " ".join(path_tokens).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
        if not target_path.exists():
            return (1, f"\nSystem Error: Target '{raw_target}' not found.\n")
        blocked = _validate_delete_target(target_path, raw_target)
        if blocked is not None:
            return blocked
        if bridge.has_native_support() and hasattr(bridge._native, "rmdir"):
            code, _ = bridge._native.rmdir(str(target_path), force)
        else:
            code, _ = legacy.lgc_rmdir(target_path, force)
        if code != 0:
            if code == -6 and not force:
                return (
                    1,
                    f"\nDirectory Error: Directory '{raw_target}' is not empty.\n"
                    "Use '-f' or '--force' to remove a non-empty directory and its contents.\n",
                )
            return bridge.translate_error(code, raw_target)
        return (0, f"\nSUCCESS! Removed directory '{raw_target}'\n")


class Touch(BaseCmd):
    name = "touch"
    description = "Create an empty file or update existing file timestamps"
    min_args = 1
    options = "Target file"

    def execute(self, args):
        if not args:
            return (1, "\nCommand Error: Target file not specified.\n")
        raw_target = " ".join(args).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
        if bridge.has_native_support() and hasattr(bridge._native, "touch"):
            code, _ = bridge._native.touch(str(target_path))
        else:
            code, _ = legacy.lgc_touch(target_path)
        if code != 0:
            return bridge.translate_error(code, raw_target)
        return (0, f"\nSUCCESS! File '{raw_target}' touched successfully.\n")
