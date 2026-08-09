# \core\system.py

from core import data
import os
import subprocess
import sys

def cd(args):
    target = args[0] if args else os.path.expanduser("~")
    try:
        os.chdir(target)
        print(f"\nSwitched directory to '{os.getcwd()}'")
    except FileNotFoundError:
        print(f"Command Error: Directory '{target}' not found.")
    except PermissionError:
        print(f"System Error: Permission denied. Cannot access '{target}'.")

def cmds(args):
    from core.directory import COMMANDS
    print("\nAvailable Commands:")
    for name, info in COMMANDS.items():
        args = info[0]
        desc = info[2]
        print(f"{name}: {desc} (Requires {args} parameter(s))")
    print(f"\nTotal available commands: {len(COMMANDS)}\n")

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

def kill(args):
    choice = input("\nAre you sure [y/n]?: ").strip().lower()
    if choice == "y":
        print("Shutting down...")
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
        print(f"SUCCESS! Launched '{target}' application or file.")
    except FileNotFoundError:
        print(f"Command Error: File '{target}' could not be found.")
    except Exception as e:
        print(f"System Error: Failed to open '{target}': {e}")