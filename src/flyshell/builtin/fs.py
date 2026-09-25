# \builtin\fs.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from flyshell.core import data
import os
import sys
import time

def execute(args):
    func = args[0].lower()
    if func == "license":
        func = "licence"
    match func:
        case "info":
            return (0, (
                "\nFlyshell System Information:\n"
                "System Name: Flyshell\n"
                f"System Version: {data.VERSION}\n"
                f"System Build: {data.BUILD}\n"
                f"Host Operating System: '{data.HOST_OS}'\n"
                f"Installed Plugin Count: {len(data.PLUGINS)}\n"
                "Original Release Date: 8th August 2026\n"
            ))
        case "licence":
            return (0, (
                "\nFlyshell Licensing Information:\n"
                "Flyshell is licensed under the MIT Licence\n\n"
                "Copyright (c) 2026 kianodev\n\n"
                "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files [the 'Software'], to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\n"
                "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\n"
                "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n"
            ))
        case "plugins":
            lines = ["\nInstalled Plugins:"]
            if data.PLUGINS:
                for name, plugin in data.PLUGINS.items():
                    p_name = getattr(plugin, "name", name)
                    p_desc = getattr(plugin, "description", "No description provided.")
                    lines.append(f"Plugin '{name}' [{p_name}]: {p_desc}")
            else:
                lines.append("No plugins installed.")
            lines.append(f"\nTotal available plugins: {len(data.PLUGINS)}\n")
            return (0, "\n".join(lines))
        case "status":
            uptime = int(time.time() - data.SESSION_START_TIME)
            mins, secs = divmod(uptime, 60)
            hours, mins = divmod(mins, 60)
            uptime_str = f"{hours}h {mins}m {secs}s"
            auth_data = data.read(["core", "auth"]) or {}
            current_user = auth_data.get("username", "Unknown")
            cmd_history = data.read(["core", "cmd_history"])
            total_history_count = len(cmd_history) if isinstance(cmd_history, list) else 0
            storage_size_str = data.get_storage_size()
            return (0, (
                "\nFlyshell System Status:\n"
                f"User: '{current_user}'\n"
                f"Session Uptime: {uptime_str}\n"
                f"Commands (Session): {data.SESSION_CMD_COUNT}\n"
                f"Commands (Lifetime): {total_history_count}\n"
                f"Working Directory: '{os.getcwd()}'\n"
                f"Storage File Size: {storage_size_str}\n"
                f"Python Environment: v{sys.version.split()[0]}\n"
                f"\nFlyshell Version {data.VERSION} (Build {data.BUILD})\n"
            ))
        case "version":
            return (0, f"\nYou are on Flyshell Version {data.VERSION} (Build {data.BUILD})\n")
        case _:
            return (1, f"\nCommand Error: Invalid argument '{func}'\n")