# \core\directory.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import auth, data, loader, system
from datetime import datetime, timezone
import re
import shlex

ALIAS = {
    "cls": "clear",
    "help": "cmds",
    "ls": "dir",
    "restart": "reboot",
}

COMMANDS = {
    "cd": [0, system.cd, "Change the current working directory (default to Home)", "Directory name"],
    "clear": [0, system.clear, "Clear the screen", None],
    "cmds": [0, system.cmds, "List all available commands and their functions", None],
    "dir": [0, system.dirlist, "List all files in the current working directory", None],
    "fs": [1, system.fs, "Execute various Flyshell system functions", "'info', 'licence', 'plugins', 'status', 'version'"],
    "history": [0, system.history, "View command history (specify entry count, default 10)", "'clear'/'cls' to delete or entry count to view"],
    "kill": [0, system.kill, "Shut down the Flyshell system", None],
    "lock": [0, auth.lock, "Lock the Flyshell system", None],
    "open": [1, system.openfile, "Open the specified file path", "Filepath"],
    "reboot": [0, system.reboot, "Reboot the Flyshell system", None],
    "sleep": [1, system.sleep, "Sleep the system for a specified time", "Time (in seconds)"]
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

def _execute_single(raw_cmd) -> int:
    try:
        posix_mode = False if data.HOST_OS == "Windows" else True
        cmd = shlex.split(raw_cmd, posix=posix_mode)
    except ValueError as e:
        print("\nCommand Error: Invalid syntax.")
        print(f"Details: {e}\n")
        return 1
    cmd_name = cmd[0]
    args = cmd[1:]
    if cmd_name in ALIAS:
        cmd_name = ALIAS[cmd_name]
    if "-h" in args or "--help" in args:
        if cmd_name in COMMANDS:
            min_args, _, desc, options = COMMANDS[cmd_name]
            print(f"\nCommand: {cmd_name}")
            print(f"Description: {desc}")
            print(f"Required Arguments: {min_args}")
            if options:
                print(f"Accepted Arguments: {options}")
            print()
            return 0
        elif cmd_name in PLUGINS:
            plugin = PLUGINS[cmd_name]
            if hasattr(plugin, "help"):
                plugin.help()
                print()
                return 0
            else:
                print(f"\nPlugin Error: Plugin '{cmd_name}' does not provide help details.\n")
                return 1
    if cmd_name in COMMANDS:
        min_args, func, desc, options = COMMANDS[cmd_name]
        if len(args) < min_args:
            print(f"\nCommand Error: '{cmd_name}' requires at least {min_args} parameter(s).\n")
            return 1
        else:
            if cmd[0] != "history":
                log(raw_cmd)
            result = func(args)
            data.SESSION_CMD_COUNT += 1
            if isinstance(result, tuple):
                code, message = result
                if message:
                    print(message)
                return code
            elif isinstance(result, str):
                if result:
                    print(result)
                return 0
            return 0
    elif cmd_name in PLUGINS:
        log(raw_cmd)
        plugin = PLUGINS[cmd_name]
        try:
            plugin.execute(args)
            return 0
        except NotImplementedError:
            print(f"\nPlugin Error: '{cmd_name}' has not implemented the execute method.\n")
            return 1
        except Exception as e:
            print(f"\nPlugin Error: '{cmd_name}' crashed unexpectedly.")
            print(f"Details: {e}")
            print(f"Returning to main Flyshell interface...\n")
            return 1
        finally:
            if hasattr(plugin, "on_unload"):
                plugin.on_unload()
    else:
        print(f"\nCommand Error: '{cmd_name}' is not a recognised command. Use 'cmds' for help.\n")
        return 1

def _parse_commands(raw_cmd: str) -> list[str]:
    chain = []
    current = []
    in_single_quote = False
    in_double_quote = False
    escape = False
    i = 0
    n = len(raw_cmd)
    while i < n:
        char = raw_cmd[i]
        if escape:
            current.append(char)
            escape = False
            i += 1
            continue
        if char == "\\":
            current.append(char)
            escape = True
            i += 1
            continue
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current.append(char)
            i += 1
            continue
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current.append(char)
            i += 1
            continue
        if not in_single_quote and not in_double_quote:
            if raw_cmd[i:i+2] in ("&&", "||"):
                op = raw_cmd[i:i+2]
                cmd_str = "".join(current).strip()
                if cmd_str:
                    chain.append((cmd_str, op))
                current = []
                i += 2
                continue
            if char == ";":
                cmd_str = "".join(current).strip()
                if cmd_str:
                    chain.append((cmd_str, ";"))
                current = []
                i += 1
                continue
        current.append(char)
        i += 1
    final_cmd = "".join(current).strip()
    if final_cmd:
        chain.append((final_cmd, None))
    return chain

def execute_line(raw_cmd):
    chain = _parse_commands(raw_cmd)
    if not chain:
        return
    last_code = 0
    skip_next = False
    for i, (cmd_str, operator) in enumerate(chain):
        if skip_next:
            if operator == ";":
                skip_next = False
            continue
        if i > 0:
            print("-" * 40)
        last_code = _execute_single(cmd_str)
        if operator == "&&" and last_code != 0:
            skip_next = True
        elif operator == "||" and last_code == 0:
            skip_next = True
        elif operator == ";":
            skip_next = False