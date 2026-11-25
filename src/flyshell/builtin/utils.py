# src/flyshell/builtin/utils.py

from flyshell import constants as c
from flyshell.abstract.base_cmd import BaseCmd
from flyshell.core import data

import codecs
import os
import re
import signal
import subprocess
import sys
import time


class Clear(BaseCmd):
    name = "clear"
    description = "Clear the screen"
    min_args = 0
    options = None
    aliases = ["cls"]

    def execute(self, args: list[str]) -> tuple[int, str]:
        return (0, c.CLEAR_SCREEN)


_ESCAPE_SEQ_RE = re.compile(
    r"\\(n|r|t|b|f|a|v|\\|'|\"|[0-7]{1,3}|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})"
)


class Echo(BaseCmd):
    name = "echo"
    description = "Print arguments to terminal"
    min_args = 1
    options = "Message"
    aliases = []

    def execute(self, args: list[str]) -> tuple[int, str]:
        text = " ".join(args)
        try:
            text = _ESCAPE_SEQ_RE.sub(
                lambda m: codecs.decode(m.group(0), "unicode_escape"),
                text,
            )
        except Exception:
            pass
        return (0, f"\n{text}\n")


class History(BaseCmd):
    name = "history"
    description = "View command history"
    min_args = 0
    options = "Entry count (default is 10)"
    aliases = []

    def execute(self, args: list[str]) -> tuple[int, str]:
        limit = 10
        if args:
            sub_arg = args[0].lower()
            if sub_arg == "all":
                limit = None
            elif sub_arg.isdigit():
                limit = int(sub_arg)
                if limit <= 0:
                    return (1, f"\nCommand Error: Invalid argument '{args[0]}'\n")
            else:
                return (1, f"\nCommand Error: Invalid argument '{args[0]}'\n")
        history_entries = data.get_history(limit)
        if not history_entries:
            return (0, "\nHistory is empty.\n")
        lines = [
            "\nCommand History:",
            f"Showing last {len(history_entries)} entries.\n",
        ]
        for i, entry in enumerate(history_entries, start=1):
            cmd = entry.get("command", "")
            time_str = entry.get("timestamp", "")
            date_part, time_part = time_str.rstrip("Z").split("T")
            lines.append(f"#{i}: {cmd} [at {date_part} @ {time_part} UTC]")
        lines.append("")
        return (0, "\n".join(lines))


class Kill(BaseCmd):
    name = "kill"
    description = "Shut down the Flyshell system"
    min_args = 0
    options = None
    aliases = []

    def execute(self, args: list[str]) -> tuple[int, str]:
        choice = input("\nAre you sure [y/n]?: ").strip().lower()
        if choice == "y":
            return (-1, "\nShutting down...\n")
        return (1, "\nAction cancelled.\n")


class Reboot(BaseCmd):
    name = "reboot"
    description = "Reboot the Flyshell system"
    min_args = 0
    options = None
    aliases = ["restart"]

    def execute(self, args: list[str]) -> tuple[int, str]:
        print("\nRestarting Flyshell...\n")
        is_direct_script = (
            sys.argv[0].lower().endswith(".exe")
            or os.path.basename(sys.argv[0]) == "flyshell"
        )
        if is_direct_script:
            cmd = sys.argv
        else:
            cmd = [sys.executable] + sys.argv
        if c.HOST_OS == "Windows":
            old_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
            try:
                p = subprocess.run(cmd)
                sys.exit(p.returncode)
            finally:
                signal.signal(signal.SIGINT, old_handler)
        else:
            os.execv(cmd[0], cmd)
        return (0, "")


class Sleep(BaseCmd):
    name = "sleep"
    description = "Sleep the system for a specified time"
    min_args = 1
    options = "Duration (secs)"
    aliases = []

    def execute(self, args: list[str]) -> tuple[int, str]:
        if not args or not args[0].replace(".", "", 1).isdigit():
            return (
                1,
                f"\nCommand Error: Invalid argument '{args[0] if args else ''}'\n",
            )
        secs = float(args[0])
        try:
            print(f"\nPausing Flyshell for {secs} second(s).")
            print("Press Ctrl+C to cancel.\n")
            time.sleep(secs)
            return (0, "\nReturning...\n")
        except KeyboardInterrupt:
            return (1, "\nSleep cancelled.\n")
