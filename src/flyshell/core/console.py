# src\flyshell\core\console.py

from flyshell import constants as c
from flyshell.core import data
from flyshell.core.directory import execute_line

import os
import random
import sys

readline = None

def check_readline() -> bool:
    global readline
    try:
        import readline
        return True
    except ImportError:
        try:
            import pyreadline3 as readline
            return True
        except ImportError:
            readline = None
            return False

def load_history():
    if not readline:
        return
    history_entries = data.get_history(limit=100)
    for entry in history_entries:
        if isinstance(entry, dict) and "command" in entry:
            readline.add_history(entry["command"])

def boot():
    load_history()
    print(c.CLEAR_SCREEN, end="")
    print(f"\nBoot successful, welcome to Flyshell! (Version {c.VERSION})")
    user_info = data.get_auth() or {}
    username = user_info.get("username")
    greeting = random.choice(c.GREETINGS).format(username=username)
    print(f"\n{greeting}\n")
    while True:
        try:
            folder = os.path.basename(os.getcwd())
            raw_cmd = input(f"Flyshell [v{c.VERSION}] ({folder})>>")
            if not raw_cmd.strip():
                continue
            execute_line(raw_cmd)
        except KeyboardInterrupt:
            print()
        except EOFError:
            print("\n\nFlyshell session closed.\n")
            sys.exit(0)