# src/flyshell/builtin/system.py

from flyshell import constants as c
from flyshell.abstract.base_cmd import BaseCmd

import os
import shutil
import subprocess


class Cd(BaseCmd):
    name = "cd"
    description = "Change the current working directory"
    min_args = 0
    options = "Directory name (default is Home)"
    aliases = []

    def execute(self, args):
        target = os.path.expanduser(" ".join(args)) if args else os.path.expanduser("~")
        try:
            os.chdir(target)
            return (0, f"\nSwitched directory to '{os.getcwd()}'\n")
        except FileNotFoundError:
            return (1, f"\nCommand Error: Directory '{target}' not found.\n")
        except PermissionError:
            return (1, f"\nSystem Error: Permission denied. Cannot access '{target}'\n")
        except OSError as e:
            return (
                1,
                f"\nCommand Error: Invalid path syntax '{target}'. ({e.strerror})\n",
            )


class OpenFile(BaseCmd):
    name = "open"
    description = "Open the specified file path"
    min_args = 1
    options = "File path"
    aliases = []

    def execute(self, args):
        target = " ".join(args).strip().strip('"')
        if not target:
            return (0, "")
        is_path = os.path.exists(target)
        is_url = target.startswith(("http://", "https://"))
        is_bin = shutil.which(target) is not None
        if not (is_path or is_url or is_bin):
            return (
                1,
                f"\nCommand Error: File or application '{target}' could not be found.\n",
            )
        try:
            if c.HOST_OS == "Windows":
                os.startfile(target)
            elif c.HOST_OS == "Darwin":
                subprocess.Popen(["open", target], stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["xdg-open", target], stderr=subprocess.DEVNULL)
            return (0, f"\nSUCCESS! Launched '{target}' application or file.\n")
        except Exception as e:
            return (1, f"\nSystem Error: Failed to open '{target}': {e}\n")


class SysExe(BaseCmd):
    name = "sys"
    description = "Execute the subsequent command on the host system"
    min_args = 1
    options = "Any host command"
    aliases = []

    def execute(self, args):
        if not args:
            return (1, "\nCommand Error: 'sys' requires at least 1 parameter(s).\n")
        try:
            print()
            raw_cmd = " ".join(args)
            result = subprocess.run(raw_cmd, shell=True)
            print()
            return (result.returncode, "")
        except KeyboardInterrupt:
            print()
            return (130, "")
        except Exception as e:
            return (1, f"\nCommand Error: Failed to run host command ({e})\n")
