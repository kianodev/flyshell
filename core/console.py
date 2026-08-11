# \core\console.py

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