# \core\system.py

from core import data
import os
import subprocess
import sys

def cmds(args):
    from core.directory import COMMANDS
    print("\nAvailable Commands:")
    for name, info in COMMANDS.items():
        args = info[0]
        desc = info[2]
        print(f"{name}: {desc} (Requires {args} parameter(s))")
    print(f"\nTotal available commands: {len(COMMANDS)}\n")

def kill(args):
    choice = input("\nAre you sure [y/n]?: ").strip().lower()
    if choice == "y":
        print("Shutting down...")
        sys.exit(0)
    else:
        print()

def open(args):
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