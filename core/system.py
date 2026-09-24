# \core\system.py

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
import signal
import subprocess
import sys
import time

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

def clear(args):
    return (0, "\033[H\033[2J")

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

def fs(args):
    func = args[0].lower()
    if func == "license":
        func = "licence"
    match func:
        case "info":
            return (0, (
                "\nFlyshell System Information:\n"
                "System Name: Flyshell\n"
                f"System Version: {data.VERSION}\n"
                f"System Build: {data.BUILD}\n"
                f"Host Operating System: '{data.HOST_OS}'\n"
                f"Installed Plugin Count: {len(data.PLUGINS)}\n"
                "Original Release Date: 8th August 2026\n"
            ))
        case "licence":
            return (0, (
                "\nFlyshell Licensing Information:\n"
                "Flyshell is licensed under the MIT Licence\n\n"
                "Copyright (c) 2026 kianodev\n\n"
                "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files [the 'Software'], to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\n"
                "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\n"
                "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n"
            ))
        case "plugins":
            lines = ["\nInstalled Plugins:"]
            if data.PLUGINS:
                for name, plugin in data.PLUGINS.items():
                    p_name = getattr(plugin, "name", name)
                    p_desc = getattr(plugin, "description", "No description provided.")
                    lines.append(f"Plugin '{name}' [{p_name}]: {p_desc}")
            else:
                lines.append("No plugins installed.")
            lines.append(f"\nTotal available plugins: {len(data.PLUGINS)}\n")
            return (0, "\n".join(lines))
        case "status":
            uptime = int(time.time() - data.SESSION_START_TIME)
            mins, secs = divmod(uptime, 60)
            hours, mins = divmod(mins, 60)
            uptime_str = f"{hours}h {mins}m {secs}s"
            auth_data = data.read(["core", "auth"]) or {}
            current_user = auth_data.get("username", "Unknown")
            cmd_history = data.read(["core", "cmd_history"])
            total_history_count = len(cmd_history) if isinstance(cmd_history, list) else 0
            storage_size_str = data.get_storage_size()
            return (0, (
                "\nFlyshell System Status:\n"
                f"User: '{current_user}'\n"
                f"Session Uptime: {uptime_str}\n"
                f"Commands (Session): {data.SESSION_CMD_COUNT}\n"
                f"Commands (Lifetime): {total_history_count}\n"
                f"Working Directory: '{os.getcwd()}'\n"
                f"Storage File Size: {storage_size_str}\n"
                f"Python Environment: v{sys.version.split()[0]}\n"
                f"\nFlyshell Version {data.VERSION} (Build {data.BUILD})\n"
            ))
        case "version":
            return (0, f"\nYou are on Flyshell Version {data.VERSION} (Build {data.BUILD})\n")
        case _:
            return (1, f"\nCommand Error: Invalid argument '{func}'\n")

def history(args):
    if args and args[0].lower() in ["cls", "clear"]:
        choice = input(f"\nAre you sure? [y/n]: ").lower()
        if choice == "y":
            data.delete(["core", "cmd_history"])
            return (0, "\nCommand history cleared.\n")
        else:
            return (1, "\nAction cancelled.\n")
    history_entries = data.read(["core", "cmd_history"]) or []
    if not history_entries:
        return (0, "\nHistory is empty.\n")
    limit = 10
    if args:
        sub_arg = args[0].lower()
        if sub_arg == "all":
            limit = len(history_entries)
        elif sub_arg.isdigit():
            limit = int(sub_arg)
        else:
            return (1, f"\nCommand Error: Invalid argument '{args[0]}'\n")
    entries = history_entries[-limit:] if limit > 0 else []
    start_index = len(history_entries) - len(entries) + 1
    lines = [
        "\nCommand History:",
        f"Showing last {len(entries)} entries.\n"
    ]
    for i, entry in enumerate(entries, start=start_index):
        cmd = entry.get("command", "")
        time_str = entry.get("timestamp", "")
        date_part, time_part = time_str.rstrip("Z").split("T")
        lines.append(f"#{i}: {cmd} [at {date_part} @ {time_part} UTC]")
    lines.append("")
    return (0, "\n".join(lines))

def kill(args):
    choice = input("\nAre you sure [y/n]?: ").strip().lower()
    if choice == "y":
        print("\nShutting down...")
        sys.exit(0)
    else:
        return (1, "\nAction cancelled.\n")

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

def reboot(args):
    print(f"\nRestarting Flyshell...\n")
    if data.HOST_OS == "Windows":
        old_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            p = subprocess.run([sys.executable] + sys.argv)
            sys.exit(p.returncode)
        finally:
            signal.signal(signal.SIGINT, old_handler)
    else:
        os.execv(sys.executable, [sys.executable] + sys.argv)

def sleep(args):
    if not args or not args[0].replace(".", "", 1).isdigit():
        return (1, f"\nCommand Error: Invalid argument '{args[0] if args else ''}'\n")
    secs = float(args[0])
    try:
        print(f"\nPausing Flyshell for {secs} second(s).")
        print("Press Ctrl+C to cancel.\n")
        time.sleep(secs)
        return (0, "\nReturning...\n")
    except KeyboardInterrupt:
        return (1, "\nSleep cancelled.\n")

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