# src\flyshell\builtin\diskops.py

from flyshell import constants as c
from flyshell.abstract.base_cmd import BaseCmd

from pathlib import Path
import os
import shutil


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
        if not target_path.exists():
            return (1, f"\nSystem Error: File '{raw_target}' not found.\n")
        if target_path.is_dir():
            return (1, f"\nSystem Error: '{raw_target}' is a directory, not a file.\n")
        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            total_lines = len(lines)
            if total_lines == 0:
                return (1, f"\nSystem Error: '{raw_target}' is empty.\n")
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
        except PermissionError:
            return (
                1,
                f"\nSystem Error: Permission denied. Cannot read '{raw_target}'\n",
            )
        except Exception as e:
            return (1, f"\nSystem Error: Failed to read file '{raw_target}' ({e})\n")


class Copy(BaseCmd):
    name = "cp"
    description = "Copy files or directories to a new destination"
    min_args = 2
    options = "Source, then destination"
    aliases = ["copy"]

    def execute(self, args):
        force = ("-f" in args) or ("--force" in args)
        flags = {"-f", "--force"}
        path_tokens = [arg for arg in args if arg not in flags]
        if len(path_tokens) < 2:
            return (
                1,
                "\nCommand Error: 'cp' requires both a source and destination path.\n",
            )
        raw_src = path_tokens[0].strip("\"'")
        raw_dst = path_tokens[1].strip("\"'")
        src_path = Path(raw_src).expanduser().resolve()
        dst_path = Path(raw_dst).expanduser().resolve()
        if not src_path.exists():
            return (1, f"\nSystem Error: Source '{raw_src}' not found.\n")
        if dst_path.exists() and dst_path.is_dir():
            final_dst = dst_path / src_path.name
        else:
            final_dst = dst_path
        if final_dst.exists() and not force:
            try:
                confirm = (
                    input(
                        f"\nDestination '{final_dst.name}' already exists. Overwrite? [y/n]: "
                    )
                    .strip()
                    .lower()
                )
            except KeyboardInterrupt:
                return (1, "\nCopy cancelled by user.\n")
            if confirm != "y":
                return (0, "\nOperation cancelled. No files were copied.\n")
        try:
            if src_path.is_dir():
                shutil.copytree(src_path, final_dst, dirs_exist_ok=force)
                return (
                    0,
                    f"\nSUCCESS! Copied directory '{src_path.name}' -> '{final_dst}'\n",
                )
            else:
                shutil.copy2(src_path, final_dst)
                return (
                    0,
                    f"\nSUCCESS! Copied file '{src_path.name}' -> '{final_dst}'\n",
                )
        except PermissionError:
            return (
                1,
                f"\nSystem Error: Permission denied. Cannot copy to '{final_dst}'\n",
            )
        except shutil.SameFileError:
            return (1, "\nSystem Error: Source and destination are the same.\n")
        except Exception as e:
            return (1, f"\nSystem Error: Failed to copy '{raw_src}' ({e})\n")


class Dir(BaseCmd):
    name = "dir"
    description = "List all files in the current working directory"
    min_args = 0
    options = None
    aliases = ["ls"]

    def execute(self, args):
        try:
            current_path = os.getcwd()
            items = os.listdir(current_path)
            lines = [f"\nDirectory: '{current_path}'"]
            for item in items:
                if os.path.isdir(os.path.join(current_path, item)):
                    lines.append(f"[DIR] {item}/")
                else:
                    lines.append(f"[FILE] {item}")
            lines.append(f"\nTotal items in directory: {len(items)}\n")
            return (0, "\n".join(lines))
        except Exception as e:
            return (1, f"\nSystem Error: Unable to list directory ({e})\n")


class MkDir(BaseCmd):
    name = "mkdir"
    description = "Create a new directory from the current working directory"
    min_args = 1
    options = "Directory name"
    aliases = ["md"]

    def execute(self, args):
        use_parents = ("-p" in args) or ("--parents" in args)
        path_tokens = [arg for arg in args if arg not in ("-p", "--parents")]
        target = " ".join(path_tokens).strip("\"'")
        try:
            if use_parents:
                os.makedirs(target, exist_ok=True)
            else:
                os.mkdir(target)
            return (0, f"\nSUCCESS! Created directory '{target}'\n")
        except FileExistsError:
            return (1, f"\nSystem Error: Directory '{target}' already exists.\n")
        except FileNotFoundError:
            return (
                1,
                "\nSystem Error: Parent directory does not exist. Use '-p' or '--parents' to create parent directories.\n",
            )
        except PermissionError:
            return (1, f"\nSystem Error: Permission denied. Cannot create '{target}'\n")
        except Exception as e:
            return (1, f"\nSystem Error: Unable to create directory '{target}' ({e})\n")


class Move(BaseCmd):
    name = "mv"
    description = "Move or relocate files and directories"
    min_args = 2
    options = "Source, then destination"
    aliases = ["move"]

    def execute(self, args):
        force = ("-f" in args) or ("--force" in args)
        flags = {"-f", "--force"}
        path_tokens = [arg for arg in args if arg not in flags]
        if len(path_tokens) < 2:
            return (
                1,
                "\nCommand Error: 'mv' requires both a source and a destination path.\n",
            )
        raw_src = path_tokens[0].strip("\"'")
        raw_dst = path_tokens[1].strip("\"'")
        src_path = Path(raw_src).expanduser().resolve()
        dst_path = Path(raw_dst).expanduser().resolve()
        if not src_path.exists():
            return (1, f"\nSystem Error: Source '{raw_src}' not found.\n")
        if src_path == src_path.parent or str(src_path) == src_path.anchor:
            return (
                1,
                "\nSecurity Error: Flyshell has blocked moving the root filesystem.\n",
            )
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
                    f"Source '{raw_src}' contains or belongs to Flyshell system files.\n",
                )
        if dst_path.exists() and dst_path.is_dir():
            final_dst = dst_path / src_path.name
        else:
            final_dst = dst_path
        if final_dst.exists() and not force:
            try:
                confirm = (
                    input(
                        f"\nDestination '{final_dst.name}' already exists. Overwrite? [y/n]: "
                    )
                    .strip()
                    .lower()
                )
            except KeyboardInterrupt:
                return (1, "\nMove cancelled by user.\n")
            if confirm != "y":
                return (0, "\nOperation cancelled. No files were moved.\n")
        try:
            shutil.move(str(src_path), str(final_dst))
            return (0, f"\nSUCCESS! Moved '{src_path.name}' -> '{final_dst}'\n")
        except PermissionError:
            return (
                1,
                f"\nSystem Error: Permission denied. Cannot move to '{final_dst}'\n",
            )
        except shutil.SameFileError:
            return (1, "\nSystem Error: Source and destination are the same.\n")
        except Exception as e:
            return (1, f"\nSystem Error: Failed to move '{raw_src}' ({e})\n")


class Rename(BaseCmd):
    name = "rename"
    description = "Rename a file or directory"
    min_args = 2
    options = "Old name, then new name"
    aliases = []

    def execute(self, args):
        raw_src = args[0].strip("\"'")
        raw_new_name = args[1].strip("\"'")
        if "/" in raw_new_name or "\\" in raw_new_name:
            return (
                1,
                "\nCommand Error: The new name must not contain path separators ('/' or '\\')\n"
                "Use 'mv' to move items between different folders.\n",
            )
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
        try:
            src_path.rename(new_path)
            return (0, f"\nSUCCESS! Renamed '{src_path.name}' -> '{new_path.name}'\n")
        except PermissionError:
            return (
                1,
                f"\nSystem Error: Permission denied. Cannot rename '{raw_src}'\n",
            )
        except Exception as e:
            return (1, f"\nSystem Error: Failed to rename '{raw_src}' ({e})\n")


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
        try:
            if is_directory:
                shutil.rmtree(target_path)
                return (
                    0,
                    f"\nSUCCESS! Deleted directory '{raw_target}' and all its contents.\n",
                )
            else:
                os.remove(target_path)
                return (0, f"\nSUCCESS! Deleted file '{raw_target}'\n")
        except PermissionError:
            return (
                1,
                f"\nSystem Error: Permission denied. Cannot remove '{raw_target}'\n",
            )
        except OSError as e:
            return (
                1,
                f"\nSystem Error: Unable to remove '{raw_target}' ({e.strerror})\n",
            )
        except Exception as e:
            return (
                1,
                f"\nSystem Error: Unexpected error removing '{raw_target}' ({e})\n",
            )


class RmDir(BaseCmd):
    name = "rmdir"
    description = "Remove the specified directory"
    min_args = 1
    options = "Target directory"
    aliases = []

    def execute(self, args):
        force = ("-f" in args) or ("--force" in args)
        path_tokens = [arg for arg in args if arg not in ("-f", "--force")]
        raw_target = " ".join(path_tokens).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
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
        try:
            has_contents = any(target_path.iterdir())
            if has_contents and not force:
                return (
                    1,
                    f"\nDirectory Error: Directory '{raw_target}' is not empty.\n"
                    "Use '-f' or '--force' to remove a non-empty directory and its contents.\n",
                )
            if has_contents and force:
                shutil.rmtree(target_path)
            else:
                os.rmdir(target_path)
            return (0, f"\nSUCCESS! Removed directory '{raw_target}'\n")
        except PermissionError:
            return (
                1,
                f"\nSystem Error: Permission denied. Cannot delete '{raw_target}'\n",
            )
        except OSError as e:
            return (
                1,
                f"\nSystem Error: Unable to remove directory '{raw_target}' ({e.strerror})\n",
            )
        except Exception as e:
            return (
                1,
                f"\nSystem Error: Unexpected error removing '{raw_target}' ({e})\n",
            )


class Touch(BaseCmd):
    name = "touch"
    description = "Create a new empty file or update timestamps of an existing file"
    min_args = 1
    options = "Target file"
    aliases = []

    def execute(self, args):
        raw_target = " ".join(args).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
        if target_path.is_dir():
            return (
                1,
                f"\nCommand Error: '{raw_target}' is a directory, not a file.\n",
            )
        if not target_path.parent.exists():
            return (
                1,
                f"\nSystem Error: Cannot create file '{raw_target}'. Parent directory does not exist.\n",
            )
        try:
            if target_path.exists():
                target_path.touch()
                return (
                    0,
                    f"\nSUCCESS! Updated timestamp for existing file '{raw_target}'\n",
                )
            else:
                target_path.touch(exist_ok=False)
                return (0, f"\nSUCCESS! Created file '{raw_target}'\n")
        except PermissionError:
            return (
                1,
                f"\nSystem Error: Permission denied. Cannot access '{raw_target}'.\n",
            )
        except Exception as e:
            return (
                1,
                f"\nSystem Error: Failed to touch file '{raw_target}' ({e})\n",
            )
