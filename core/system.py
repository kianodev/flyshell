# \core\system.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data, directory
import os
import subprocess
import sys
import time

def cd(args):
    target = " ".join(args) if args else os.path.expanduser("~")
    try:
        os.chdir(target)
        print(f"\nSwitched directory to '{os.getcwd()}'\n")
    except FileNotFoundError:
        print(f"\nCommand Error: Directory '{target}' not found.\n")
    except PermissionError:
        print(f"\nSystem Error: Permission denied. Cannot access '{target}'\n")

def clear(args):
    print("\033[H\033[2J", end="")

def cmds(args):
    from core.directory import ALIAS, COMMANDS, PLUGINS
    print("\nAvailable Commands:")
    for name, info in COMMANDS.items():
        req_args = info[0]
        desc = info[2]
        aliases = [alias_name for alias_name, target in ALIAS.items() if target == name]
        if aliases:
            alias_str = ", ".join(aliases)
            cmd_label = f"{name} (alias: {alias_str})"
        else:
            cmd_label = name  
        print(f"{cmd_label}: {desc} (Requires {req_args} parameter(s))")
    print(f"\nTotal available commands: {len(COMMANDS)}")
    print("\nAvailable Plugins:")
    if PLUGINS:
        for name, plugin in PLUGINS.items():
            p_name = getattr(plugin, "name", name)
            p_desc = getattr(plugin, "description", "No description provided.")
            print(f"Plugin '{name}' [{p_name}]: {p_desc}")
    else:
        print("No plugins installed.")
    print(f"\nTotal available plugins: {len(PLUGINS)}\n")

def dirlist(args):
    current_path = os.getcwd()
    items = os.listdir(current_path)
    print(f"\nDirectory: '{current_path}'")
    for item in items:
        if os.path.isdir(os.path.join(current_path, item)):
            print(f"[DIR] {item}/")
        else:
            print(f"[FILE] {item}")
    print(f"\nTotal items in directory: {len(items)}\n")

def fs(args):
    func = args[0].lower()
    if func == "license":
        func = "licence"
    match func:
        case "info":
            print("\nFlyshell System Information:")
            print("System Name: Flyshell")
            print(f"System Version: {data.VERSION}")
            print(f"System Build: {data.BUILD}")
            print(f"Host Operating System: '{data.HOST_OS}'")
            print(f"Installed Plugin Count: {len(directory.PLUGINS)}")
            print("Original Release Date: 8th August 2026\n")
        case "licence":
            print("\nFlyshell Licensing Information:")
            print("Flyshell is licensed under the MIT Licence")
            print("\nCopyright (c) 2026 kianodev")
            print("\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files [the 'Software'], to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:")
            print("The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.")
            print("THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n")
        case "status":
            uptime = int(time.time() - data.SESSION_START_TIME)
            mins, secs = divmod(uptime, 60)
            hours, mins = divmod(mins, 60)
            uptime_str = f"{hours}h {mins}m {secs}s"
            auth_data = data.read(["core", "auth"]) or {}
            current_user = auth_data.get("username", "Unknown")
            cmd_history = data.read(["core", "cmd_history"])
            total_history_count = len(cmd_history) if isinstance(cmd_history, list) else 0
            core_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.abspath(os.path.join(core_dir, ".."))
            storage_path = os.path.join(root_dir, "flyshell_storage.json")
            if os.path.exists(storage_path):
                size = os.path.getsize(storage_path)
                size = float(size)
                for unit in ["B", "KB", "MB", "GB", "TB"]:
                    if size < 1024.0 or unit == "TB":
                        storage_size_str = f"{int(size)} {unit}" if unit == "B" else f"{size:.2f} {unit}"
                        break
                    size /= 1024.0
            else:
                storage_size_str = "File not found"
            print("\nFlyshell System Status:")
            print(f"User: '{current_user}'")
            print(f"Session Uptime: {uptime_str}")
            print(f"Commands (Session): {data.SESSION_CMD_COUNT}")
            print(f"Commands (Lifetime): {total_history_count}")
            print(f"Working Directory: '{os.getcwd()}'")
            print(f"Storage File Size: {storage_size_str}")
            print(f"Python Environment: v{sys.version.split()[0]}")
            print(f"\nFlyshell Version {data.VERSION} (Build {data.BUILD})\n")
        case _:
            print(f"\nCommand Error: Invalid argument '{func}'\n")

def history(args):
    if args and args[0].lower() in ["cls", "clear"]:
        choice = input(f"\nAre you sure? [y/n]: ").lower()
        if choice == "y":
            data.delete(["core", "cmd_history"])
            print("\nCommand history cleared.\n")
            return
    history = data.read(["core", "cmd_history"]) or []
    if not history:
        print("\nHistory is empty.\n")
        return
    limit = 10
    if args:
        sub_arg = args[0].lower()
        if sub_arg == "all":
            limit = len(history)
        elif sub_arg.isdigit():
            limit = int(sub_arg)
        else:
            print(f"\nCommand Error: Invalid argument '{args[0]}'\n")
            return
    entries = history[-limit:] if limit > 0 else []
    start_index = len(history) - len(entries) + 1
    print("\nCommand History:")
    print(f"Showing last {len(entries)} entries.\n")
    for i, entry in enumerate(entries, start=start_index):
        cmd = entry.get("command", "")
        time_str = entry.get("timestamp", "")
        date_part, time_part = time_str.rstrip("Z").split("T")
        formatted = f"{date_part} @ {time_part} UTC"
        print(f"#{i}: {cmd} [{formatted}]")
    print()

def kill(args):
    choice = input("\nAre you sure [y/n]?: ").strip().lower()
    if choice == "y":
        print("\nShutting down...")
        sys.exit(0)
    else:
        print()

def openfile(args):
    target = args[0]
    try:
        if data.HOST_OS == "Windows":
            os.startfile(target)
        elif data.HOST_OS == "Darwin":
            subprocess.Popen(["open", target])
        else:
            subprocess.Popen(["xdg-open", target])
        print(f"\nSUCCESS! Launched '{target}' application or file.\n")
    except FileNotFoundError:
        print(f"\nCommand Error: File '{target}' could not be found.\n")
    except Exception as e:
        print(f"\nSystem Error: Failed to open '{target}': {e}\n")

def sleep(args):
    if not args[0].replace(".", "", 1).isdigit():
        print(f"\nCommand Error: Invalid argument '{args[0]}'\n")
        return
    secs = float(args[0])
    try:
        print(f"\nPausing Flyshell for {secs} second(s).")
        print("Press Ctrl+C to cancel.\n")
        time.sleep(secs)
    except KeyboardInterrupt:
        print("\nSleep cancelled.")
    finally:
        print("\nReturning...\n")