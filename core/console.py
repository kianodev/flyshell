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
    print(f"\nBoot successful! Welcome to Flyshell! (Version {VERSION})")
    print("\nUSER WARNING /!\: Flyshell is still in very early development. Many features are non-functional.")
    print("\nUse 'cmds' to get started! :-D\n")
    while True:
        folder = os.path.basename(os.getcwd())
        cmd = input(f"Flyshell [v{VERSION}] ({folder})>>").split()
        execute(cmd)