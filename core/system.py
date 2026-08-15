# \core\system.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data
import os
import subprocess
import sys

def cd(args):
    target = args[0] if args else os.path.expanduser("~")
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
    from core.directory import COMMANDS, PLUGINS
    print("\nAvailable Commands:")
    for name, info in COMMANDS.items():
        args = info[0]
        desc = info[2]
        print(f"{name}: {desc} (Requires {args} parameter(s))")
    print(f"\nTotal available commands: {len(COMMANDS)}")
    print("\nAvailable Plugins:")
    for name in PLUGINS:
        print(f"Plugin '{name}' - to activate, use name as command.")
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