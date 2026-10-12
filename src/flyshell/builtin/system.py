# src\flyshell\builtin\system.py

from flyshell.abstract.base_cmd import BaseCmd
from flyshell.core import auth, data

import getpass
import os
import re
import shutil
import subprocess
import sys

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
            return (1, f"\nCommand Error: Invalid path syntax '{target}'. ({e.strerror})\n")

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

class OpenFile(BaseCmd):
    name = "open"
    description = "Open the specified file path"
    min_args = 1
    options = "File path"
    aliases = []

    def execute(self, args):
        target = " ".join(args).strip().strip('"\'')
        if not target:
            return (0, "")
        is_path = os.path.exists(target)
        is_url = target.startswith(("http://", "https://"))
        is_bin = shutil.which(target) is not None
        if not (is_path or is_url or is_bin):
            return (1, f"\nCommand Error: File or application '{target}' could not be found.\n")
        try:
            if data.HOST_OS == "Windows":
                os.startfile(target)
            elif data.HOST_OS == "Darwin":
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
        if args[0] in ["-f", "--force"]:
            override = True
            args = args[1:]
            if not args:
                return (1, "\nCommand Error: 'sys' requires at least 1 parameter(s).\n")
        else:
            override = False
        cmd = " ".join(args).strip().strip('"\'')
        cmd_normalised = " ".join(cmd.lower().split())
        BLOCKED_COMMANDS = {"format", "diskpart", "dd"}
        is_blocked = any(re.search(rf"\b{re.escape(b)}\b", cmd_normalised) for b in BLOCKED_COMMANDS)
        DANGER_COMMANDS = {"del", "rmdir", "rd", "rm", "taskkill", "killall"}
        is_dangerous = any(re.search(rf"\b{re.escape(d)}\b", cmd_normalised) for d in DANGER_COMMANDS)
        if is_blocked:
            return (1, (
                "\nSecurity Error: Flyshell has blocked execution of this command.\n"
                f"This command '{cmd}' is permanently restricted by Flyshell safety policy.\n"
                "Flyshell has blocked your command to prevent damage to your computer.\n"
            ))
        elif is_dangerous and not override:
            password = getpass.getpass("\nThis command is restricted. To execute, enter your password: ")
            auth_info = data.get_auth() or {}
            stored_hash = auth_info.get("hash")
            stored_salt = auth_info.get("salt")
            if not auth.verify_password(stored_hash, stored_salt, password):
                return (1, "\nAccount Error: Password does not match.\n")
        try:
            print()
            result = subprocess.run(cmd, shell=True)
            print()
            return (result.returncode, "")
        except KeyboardInterrupt:
            print()
            return (130, "")
        except Exception as e:
            return (1, f"\nCommand Error: Failed to run host command ({e})\n")