# src\flyshell\builtin\diskops.py

from flyshell.abstract.base_cmd import BaseCmd

import os


class Dir(BaseCmd):
    name = "dir"
    description = "List all files in the current working directory"
    min_args = 0
    options = None
    aliases = ["ls"]

    def execute(self, args):
        try:
            current_path = os.getcwd()
            items = os.listdir(current_path)
            lines = [f"\nDirectory: '{current_path}'"]
            for item in items:
                if os.path.isdir(os.path.join(current_path, item)):
                    lines.append(f"[DIR] {item}/")
                else:
                    lines.append(f"[FILE] {item}")
            lines.append(f"\nTotal items in directory: {len(items)}\n")
            return (0, "\n".join(lines))
        except Exception as e:
            return (1, f"\nSystem Error: Unable to list directory ({e})\n")
