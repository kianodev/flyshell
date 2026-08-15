# \core\directory.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data, loader, system
from datetime import datetime, timezone
import shlex

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
    try:
        cmd = shlex.split(raw_cmd)
    except ValueError as e:
        print("\nCommand Error: Invalid syntax.")
        print(f"Details: {e}\n")
        return
    cmd_name = cmd[0]
    args = cmd[1:]
    if cmd_name in COMMANDS:
        min_args, func, desc = COMMANDS[cmd_name]
        if len(args) < min_args:
            print(f"\nCommand Error: '{cmd_name}' requires at least {min_args} parameter(s).\n")
        else:
            if cmd[0] != "history":
                log(raw_cmd)
            func(args)
    elif cmd_name in PLUGINS:
        log(raw_cmd)
        plugin_module = PLUGINS[cmd_name]
        ctx = loader.build_context(cmd_name)
        if hasattr(plugin_module, "run"):
            try:
                plugin_module.run(ctx, args)
            except Exception as e:
                print(f"\nPlugin Error: '{cmd_name}' crashed unexpectedly.")
                print(f"Returning to main Flyshell interface...\n")
        else:
            print(f"\nPlugin Error: '{cmd_name}' is missing a callable run() function.\n")
    else:
        print(f"\nCommand Error: '{cmd_name}' is not a recognised command. Use 'cmds' for help.\n")