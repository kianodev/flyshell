# src\flyshell\builtin\diskops.py

from flyshell import constants as c
from flyshell.abstract.base_cmd import BaseCmd

from pathlib import Path
import os
import shutil


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
            critical_system_dirs.extend([
                Path(f"{system_drive}\\Windows").resolve(),
                Path(f"{system_drive}\\Program Files").resolve(),
                Path(f"{system_drive}\\Program Files (x86)").resolve(),
            ])
        else:
            critical_system_dirs.extend([
                Path("/bin").resolve(),
                Path("/etc").resolve(),
                Path("/usr").resolve(),
                Path("/var").resolve(),
            ])
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
