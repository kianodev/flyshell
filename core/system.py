# \core\system.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data, directory
import os
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

def cmds(args):
    from core.directory import ALIAS, COMMANDS
    lines = ["\nAvailable Commands:"]
    for name, info in COMMANDS.items():
        req_args = info[0]
        desc = info[2]
        options = info[3]
        aliases = [alias_name for alias_name, target in ALIAS.items() if target == name]
        cmd_label = f"{name} (alias: {', '.join(aliases)})" if aliases else name
        if not options:
            lines.append(f"\n{cmd_label}: {desc} (Requires {req_args} parameter(s))")
        else:
            lines.append(f"\n{cmd_label}: {desc} (Requires {req_args} parameter(s)) [args: {options}]")
    lines.append(f"\nTotal available commands: {len(COMMANDS)}")
    lines.append("Use '-h' or '--help' after any command to reveal its specific help list.")
    lines.append("Flyshell also supports ;, && and || command chaining. Give it a go!\n")
    return (0, "\n".join(lines))

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
                f"Installed Plugin Count: {len(directory.PLUGINS)}\n"
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
            if directory.PLUGINS:
                for name, plugin in directory.PLUGINS.items():
                    p_name = getattr(plugin, "name", name)
                    p_desc = getattr(plugin, "description", "No description provided.")
                    lines.append(f"Plugin '{name}' [{p_name}]: {p_desc}")
            else:
                lines.append("No plugins installed.")
            lines.append(f"\nTotal available plugins: {len(directory.PLUGINS)}\n")
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
            if os.path.exists(data.FILE_PATH):
                size = float(os.path.getsize(data.FILE_PATH))
                for unit in ["B", "KB", "MB", "GB", "TB"]:
                    if size < 1024.0 or unit == "TB":
                        storage_size_str = f"{int(size)} {unit}" if unit == "B" else f"{size:.2f} {unit}"
                        break
                    size /= 1024.0
            else:
                storage_size_str = "File not found"
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