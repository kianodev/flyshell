# \core\directory.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data, system
from datetime import datetime, timezone

COMMANDS = {
    "cd": [0, system.cd, "Change the current working directory (default to Home)"],
    "clear": [0, system.clear, "Clear the screen"],
    "cls": [0, system.clear, "Clear the screen"],
    "cmds": [0, system.cmds, "List all available commands and their functions"],
    "dir": [0, system.dirlist, "List all files in the current working directory"],
    "history": [0, system.history, "View command history (specify entry count, default 10)"],
    "kill": [0, system.kill, "Shut down the application"],
    "ls": [0, system.dirlist, "List all files in the current working directory"],
    "open": [1, system.openfile, "Open the specified file path"]
    }

PLUGINS = {}

def log(cmd):
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    history = data.read(["core", "cmd_history"]) or []
    if not isinstance(history, list):
        history = []
    entry = {"command": cmd, "timestamp": utc_now}
    history.append(entry)
    data.write(["core", "cmd_history"], history)

def execute(raw_cmd):
    cmd = raw_cmd.split()
    cmd_name = cmd[0]
    if cmd_name in COMMANDS:
        min_args, func, desc = COMMANDS[cmd_name]
        args = cmd[1:]
        if len(args) < min_args:
            print(f"Command Error: '{cmd_name}' requires at least {min_args} parameter(s).")
        else:
            if cmd[0] != "history":
                log(raw_cmd)
            func(args)
    else:
        print(f"Command Error: '{cmd_name}' is not a recognised command. Use 'cmds' for help.")