# \builtin\system.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import auth, data
import getpass
import os
import re
import shutil
import subprocess
import sys

def cd(args):
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

def dirlist(args):
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

def openfile(args):
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

def syscmd(args):
    if args[0] in ["-f", "--force"]:
        override = True
        args = args[1:]
        if not args:
            return (1, "\nCommand Error: 'sys' requires at least 1 parameter(s).\n")
    else:
        override = False
    cmd = " ".join(args).strip().strip('"\'')
    base_cmd = args[0].lower().strip('"\'').replace(".exe", "")
    DANGER_COMMANDS = {"del", "rmdir", "rd", "rm", "taskkill", "killall"}
    BLOCKED_COMMANDS = {"format", "diskpart", "dd"}
    CRITICAL_TARGETS = [
        r"c:\\windows",
        r"c:\\windows\\system32",
        r"c:\\\s*$",
        r"c:\\\s+",
        r"(^|\s)/+(\s|$)",
        r"/boot",
        r"/etc",
        r"/system"
    ]
    cmd_lower = cmd.lower()
    targets_critical = any(re.search(p, cmd_lower) for p in CRITICAL_TARGETS)
    is_forkbomb = bool(re.search(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", cmd_lower))
    is_reg_hklm = "reg" in base_cmd and "delete" in cmd_lower and "hklm" in cmd_lower
    is_rm_root = "rm" in base_cmd and "-" in cmd_lower and bool(re.search(r"(?:^|\s)/+(?:\s|$)", cmd_lower))
    is_blocked_signature = is_forkbomb or is_reg_hklm or is_rm_root
    is_blocked = base_cmd in BLOCKED_COMMANDS or is_blocked_signature
    is_dangerous = base_cmd in DANGER_COMMANDS
    if is_blocked or (is_dangerous and targets_critical):
        return (1, (
            "\nSecurity Error: Flyshell has blocked execution of this command.\n"
            f"This command '{cmd}' is permanently restricted by Flyshell safety policy.\n"
            "Flyshell has blocked your command to prevent damage to your computer.\n"
        ))
    elif is_dangerous and not override:
        password = getpass.getpass("\nThis command is restricted. To execute, enter your password: ")
        auth_info = data.read(["core", "auth"])
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