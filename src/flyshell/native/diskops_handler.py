# src/flyshell/native/diskops_handler.py

from flyshell.abstract.base_cmd import BaseCmd
from flyshell.native import diskops_bridge as bridge
from flyshell.native.legacy import diskops as legacy

from pathlib import Path
import os


class Cat(BaseCmd):
    name = "cat"
    description = "Display the contents of a text file"
    min_args = 1
    options = "Target file"
    aliases = ["read"]

    def execute(self, args):
        show_numbers = ("-n" in args) or ("--number" in args)
        limit = None
        filtered_args = []
        skip_next = False
        for i, token in enumerate(args):
            if skip_next:
                skip_next = False
                continue
            if token in ("-n", "--number"):
                continue
            if token in ("-l", "--limit"):
                if i + 1 < len(args) and args[i + 1].isdigit():
                    limit = int(args[i + 1])
                    skip_next = True
                    continue
                else:
                    return (
                        1,
                        f"\nCommand Error: '{token}' requires a positive integer limit.\n",
                    )
            filtered_args.append(token)
        if not filtered_args:
            return (1, "\nCommand Error: Target file not specified.\n")
        raw_target = " ".join(filtered_args).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
        if bridge.has_native_support() and hasattr(bridge._native, "cat"):
            code, content = bridge._native.cat(str(target_path))
        else:
            code, content = legacy.lgc_cat(target_path)
        if code != 0:
            return bridge.translate_error(code, raw_target)
        lines = content.splitlines(keepends=True)
        total_lines = len(lines)
        if limit is not None:
            lines = lines[:limit]
        output_lines = [
            f"\nDisplaying contents of file '{target_path.name}' ({len(lines)}/{total_lines} lines)\n"
        ]
        for line_idx, line in enumerate(lines, start=1):
            clean_line = line.rstrip("\r\n")
            if show_numbers:
                output_lines.append(f"{line_idx:4d} | {clean_line}")
            else:
                output_lines.append(clean_line)
        output_lines.append(f"\nEnd of '{target_path.name}'\n")
        return (0, "\n".join(output_lines))


class Dir(BaseCmd):
    name = "dir"
    description = "List all files in the current working directory"
    min_args = 0
    options = None
    aliases = ["ls"]

    def execute(self, args):
        target_str = args[0].strip("\"'") if args else os.getcwd()
        target_path = Path(target_str).expanduser().resolve()
        if bridge.has_native_support() and hasattr(bridge._native, "dir"):
            code, items = bridge._native.dir(str(target_path))
        else:
            code, items = legacy.lgc_dir(target_path)
        if code != 0:
            return bridge.translate_error(code, str(target_path))
        lines = [f"\nDirectory: '{target_path}'"]
        for name, is_dir in items:
            if is_dir:
                lines.append(f"[DIR] {name}/")
            else:
                lines.append(f"[FILE] {name}")
        lines.append(f"\nTotal items in directory: {len(items)}\n")
        return (0, "\n".join(lines))


class Touch(BaseCmd):
    name = "touch"
    description = "Create an empty file or update existing file timestamps"
    min_args = 1
    options = "Target file"

    def execute(self, args):
        if not args:
            return (1, "\nCommand Error: Target file not specified.\n")
        raw_target = " ".join(args).strip("\"'")
        target_path = Path(raw_target).expanduser().resolve()
        if bridge.has_native_support() and hasattr(bridge._native, "touch"):
            code, _ = bridge._native.touch(str(target_path))
        else:
            code, _ = legacy.lgc_touch(target_path)
        if code != 0:
            return bridge.translate_error(code, raw_target)
        return (0, f"\nSUCCESS! File '{raw_target}' touched successfully.\n")
