# \core\system.py

from core.data import VERSION
import sys

def cmds(args):
    from core.directory import COMMANDS
    print("\nAvailable Commands:")
    for name, info in COMMANDS.items():
        args = info[0]
        desc = info[2]
        print(f"{name}: {desc} (Requires {args} parameter(s))")
    print(f"\nTotal available commands: {len(COMMANDS)}")
    print(f"You are on Version {VERSION}\n")

def kill(args):
    choice = input("\nAre you sure [y/n]?: ").strip().lower()
    if choice == "y":
        print("Shutting down...")
        sys.exit(0)
    else:
        print()