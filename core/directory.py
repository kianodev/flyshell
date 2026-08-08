# \core\directory.py

from core import system

COMMANDS = {
    "cmds": [0, system.cmds, "List all available commands and their functions"],
    "kill": [0, system.kill, "Shut down the application"]
    }

def execute(cmd):
    if not cmd:
        print(f"Command Error: No command given. Use 'cmds' for help.")
        return
    cmd_name = cmd[0]
    if cmd_name in COMMANDS:
        min_args, func, desc = COMMANDS[cmd_name]
        args = cmd[1:]
        if len(args) < min_args:
            print(f"Command Error: '{cmd_name}' requires at least {min_args} parameter(s).")
        else:
            func(args)
    else:
        print(f"Command Error: '{cmd_name}' is not a recognised command. Use 'cmds' for help.")