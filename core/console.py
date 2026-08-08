# \core\console.py

from core.data import VERSION
from core.directory import execute

def boot():
    print(f"Boot successful! Welcome to Flyshell! (Version {VERSION})")
    print("\nUSER WARNING /!\: Flyshell is still in very early development. Many features are non-functional.")
    print("\nUse 'cmds' to get started! :-D\n")
    while True:
        cmd = input(f"Flyshell [v{VERSION}]>>").split()
        execute(cmd)