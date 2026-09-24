# \builtin\utils.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data
import os
import signal
import subprocess
import sys
import time

def clear(args):
    return (0, "\033[H\033[2J")

def history(args):
    if args and args[0].lower() in ["cls", "clear"]:
        choice = input(f"\nAre you sure? [y/n]: ").lower()
        if choice == "y":
            data.delete(["core", "cmd_history"])
            return (0, "\nCommand history cleared.\n")
        else:
            return (1, "\nAction cancelled.\n")
    history_entries = data.read(["core", "cmd_history"]) or []
    if not history_entries:
        return (0, "\nHistory is empty.\n")
    limit = 10
    if args:
        sub_arg = args[0].lower()
        if sub_arg == "all":
            limit = len(history_entries)
        elif sub_arg.isdigit():
            limit = int(sub_arg)
        else:
            return (1, f"\nCommand Error: Invalid argument '{args[0]}'\n")
    entries = history_entries[-limit:] if limit > 0 else []
    start_index = len(history_entries) - len(entries) + 1
    lines = [
        "\nCommand History:",
        f"Showing last {len(entries)} entries.\n"
    ]
    for i, entry in enumerate(entries, start=start_index):
        cmd = entry.get("command", "")
        time_str = entry.get("timestamp", "")
        date_part, time_part = time_str.rstrip("Z").split("T")
        lines.append(f"#{i}: {cmd} [at {date_part} @ {time_part} UTC]")
    lines.append("")
    return (0, "\n".join(lines))

def kill(args):
    choice = input("\nAre you sure [y/n]?: ").strip().lower()
    if choice == "y":
        print("\nShutting down...")
        sys.exit(0)
    else:
        return (1, "\nAction cancelled.\n")

def reboot(args):
    print(f"\nRestarting Flyshell...\n")
    if data.HOST_OS == "Windows":
        old_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            p = subprocess.run([sys.executable] + sys.argv)
            sys.exit(p.returncode)
        finally:
            signal.signal(signal.SIGINT, old_handler)
    else:
        os.execv(sys.executable, [sys.executable] + sys.argv)

def sleep(args):
    if not args or not args[0].replace(".", "", 1).isdigit():
        return (1, f"\nCommand Error: Invalid argument '{args[0] if args else ''}'\n")
    secs = float(args[0])
    try:
        print(f"\nPausing Flyshell for {secs} second(s).")
        print("Press Ctrl+C to cancel.\n")
        time.sleep(secs)
        return (0, "\nReturning...\n")
    except KeyboardInterrupt:
        return (1, "\nSleep cancelled.\n")