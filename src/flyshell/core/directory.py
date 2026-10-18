# src\flyshell\core\directory.py

from flyshell import constants as c
from flyshell.abstract.base_cmd import BaseCmd
from flyshell.abstract.parent_cmd import ParentCmd
from flyshell.builtin import diskops, fs, system, utils
from flyshell.core import auth, data

from datetime import datetime, timezone
import shlex


class Cmds(BaseCmd):
    name = "cmds"
    description = "List all available commands and their functions"
    min_args = 0
    options = None
    aliases = ["help"]

    def execute(self, args):
        lines = ["\nAvailable Commands:"]
        seen_cmds = set()
        for cmd in COMMAND_REGISTRY.values():
            if cmd in seen_cmds:
                continue
            seen_cmds.add(cmd)
            cmd_label = (
                f"{cmd.name} (alias: {', '.join(cmd.aliases)})"
                if cmd.aliases
                else cmd.name
            )
            if not cmd.options:
                lines.append(
                    f"{cmd_label}: {cmd.description} (Requires {cmd.min_args} parameter(s))"
                )
            else:
                lines.append(
                    f"{cmd_label}: {cmd.description} (Requires {cmd.min_args} parameter(s)) [args: {cmd.options}]"
                )

        lines.append(f"\nTotal available commands: {len(seen_cmds)}")
        lines.append(
            "Use '-h' or '--help' after any command to reveal its specific help list."
        )
        lines.append(
            "Flyshell also supports ;, && and || command chaining. Give it a go!\n"
        )
        return (0, "\n".join(lines))


INSTALLED_COMMANDS: list[BaseCmd] = [
    diskops.Cat(),
    system.Cd(),
    Cmds(),
    utils.Clear(),
    diskops.Copy(),
    diskops.Dir(),
    fs.Fs(),
    utils.History(),
    utils.Kill(),
    auth.Lock(),
    diskops.MkDir(),
    diskops.Move(),
    system.OpenFile(),
    utils.Reboot(),
    diskops.Rm(),
    diskops.RmDir(),
    utils.Sleep(),
    system.SysExe(),
    diskops.Touch(),
]
COMMAND_REGISTRY: dict[str, BaseCmd] = {}
for cmd_obj in INSTALLED_COMMANDS:
    COMMAND_REGISTRY[cmd_obj.name] = cmd_obj
    for alias_name in cmd_obj.aliases:
        COMMAND_REGISTRY[alias_name] = cmd_obj


def log(cmd):
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data.append_history(cmd, utc_now)


def _execute_single(raw_cmd: str) -> int:
    try:
        posix_mode = False if c.HOST_OS == "Windows" else True
        cmd = shlex.split(raw_cmd, posix=posix_mode)
    except ValueError as e:
        print("\nCommand Error: Invalid syntax.")
        print(f"Details: {e}\n")
        return 1
    if not cmd:
        return 0
    cmd_name = cmd[0]
    args = cmd[1:]
    if "-h" in args or "--help" in args:
        if cmd_name in COMMAND_REGISTRY:
            command = COMMAND_REGISTRY[cmd_name]
            if isinstance(command, ParentCmd):
                return command.execute(args)
            command.help()
            return 0
        elif cmd_name in c.PLUGINS:
            plugin = c.PLUGINS[cmd_name]
            if hasattr(plugin, "help"):
                plugin.help()
                print()
                return 0
            else:
                print(
                    f"\nPlugin Error: Plugin '{cmd_name}' does not provide help details.\n"
                )
                return 1
    if "-d" in args or "--docs" in args:
        if cmd_name in c.PLUGINS:
            plugin = c.PLUGINS[cmd_name]
            if hasattr(plugin, "show_docs") and plugin.show_docs():
                return 0
            print(
                f"\nPlugin Error: Plugin '{cmd_name}' has not provided documentation.\n"
            )
            return 1
    if cmd_name in COMMAND_REGISTRY:
        command = COMMAND_REGISTRY[cmd_name]
        if len(args) < command.min_args:
            print(
                f"\nCommand Error: '{cmd_name}' requires at least {command.min_args} parameter(s).\n"
            )
            return 1
        if cmd[0] != "history":
            log(raw_cmd)
        try:
            result = command.execute(args)
        except Exception as e:
            print(f"\nCommand Error: Failed during execution of '{cmd_name}'.")
            print(f"Details: {e}\n")
            return 1
        c.SESSION_CMD_COUNT += 1
        if isinstance(result, tuple):
            code, message = result
            if message:
                print(message)
            return code
        elif isinstance(result, int):
            return result
        elif isinstance(result, str):
            if result:
                print(result)
            return 0
        return 0
    elif cmd_name in c.PLUGINS:
        log(raw_cmd)
        plugin = c.PLUGINS[cmd_name]
        try:
            result = plugin.execute(args)
            return result if isinstance(result, int) else 0
        except NotImplementedError:
            print(
                f"\nPlugin Error: '{cmd_name}' has not implemented the execute method.\n"
            )
            return 1
        except Exception as e:
            print(f"\nPlugin Error: '{cmd_name}' crashed unexpectedly.")
            print(f"Details: {e}")
            print("Returning to main Flyshell interface...\n")
            return 1
        finally:
            if hasattr(plugin, "on_unload"):
                plugin.on_unload()
    else:
        print(
            f"\nCommand Error: '{cmd_name}' is not a recognised command. Use 'cmds' for help.\n"
        )
        return 1


def _parse_commands(raw_cmd: str) -> list:
    chain = []
    current = []
    in_single_quote = False
    in_double_quote = False
    escape = False
    i = 0
    n = len(raw_cmd)
    pending_op = None
    while i < n:
        char = raw_cmd[i]
        if escape:
            current.append(char)
            escape = False
            i += 1
            continue
        is_windows = c.HOST_OS == "Windows"
        if char == "\\":
            if not is_windows:
                escape = True
                i += 1
                continue
            else:
                if i + 1 < n and raw_cmd[i + 1] in ('"', "'"):
                    escape = True
                    i += 1
                    continue
                current.append(char)
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
            if raw_cmd[i : i + 2] in ("&&", "||"):
                op = raw_cmd[i : i + 2]
                cmd_str = "".join(current).strip()
                if cmd_str:
                    chain.append((pending_op, cmd_str))
                pending_op = op
                current = []
                i += 2
                continue
            if char == ";":
                cmd_str = "".join(current).strip()
                if cmd_str:
                    chain.append((pending_op, cmd_str))
                pending_op = ";"
                current = []
                i += 1
                continue
        current.append(char)
        i += 1
    if in_single_quote or in_double_quote:
        quote_char = "'" if in_single_quote else '"'
        print(f"\nSyntax Error: Unclosed {quote_char} quote detected.\n")
        return []
    if escape:
        print("\nSyntax Error: Dangling '\\' escape character at end of command.\n")
        return []
    final_cmd = "".join(current).strip()
    if final_cmd:
        chain.append((pending_op, final_cmd))
    return chain


def execute_line(raw_cmd: str):
    chain = _parse_commands(raw_cmd)
    if not chain:
        return
    last_code = 0
    skipped_last = False
    for i, (prev_op, cmd_str) in enumerate(chain):
        should_run = True
        if prev_op == ";":
            should_run = True
            skipped_last = False
        elif skipped_last:
            if prev_op == "&&":
                should_run = False
            elif prev_op == "||":
                should_run = True
        else:
            if prev_op == "&&" and last_code != 0:
                should_run = False
            elif prev_op == "||" and last_code == 0:
                should_run = False
        if should_run:
            if i > 0:
                print("-" * 40)
            last_code = _execute_single(cmd_str)
            skipped_last = False
        else:
            skipped_last = True
