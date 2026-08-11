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
        print(f"\nSystem Error: Permission denied. Cannot access '{target}'.\n")

def clear(args):
    if data.HOST_OS == "Windows":
        os.system("cls")
    else:
        os.system("clear")

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