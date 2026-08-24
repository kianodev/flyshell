# \core\console.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core.data import VERSION
from core.directory import execute
import os

def boot():
    print("\033[H\033[2J", end="")
    print(f"\nBoot successful! Welcome to Flyshell! (Version {VERSION})")
    print("\nUse 'cmds' to get started! :-D\n")
    while True:
        folder = os.path.basename(os.getcwd())
        raw_cmd = input(f"Flyshell [v{VERSION}] ({folder})>>")
        if not raw_cmd:
            print(f"\nCommand Error: No command given. Use 'cmds' for help.\n")
            continue
        execute(raw_cmd)