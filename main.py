# \main.py

from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parent

def boot_check():
    REQUIRED_COMPONENTS = [
    PROJECT_ROOT / "core",
    PROJECT_ROOT / "core" / "auth.py",
    PROJECT_ROOT / "core" / "base_plugin.py",
    PROJECT_ROOT / "core" / "console.py",
    PROJECT_ROOT / "core" / "data.py",
    PROJECT_ROOT / "core" / "directory.py",
    PROJECT_ROOT / "core" / "loader.py",
    PROJECT_ROOT / "core" / "system.py",
    PROJECT_ROOT / "plugin",
    ]
    present = []
    missing = []
    for path in REQUIRED_COMPONENTS:
        if path.exists():
            present.append(str(path))
        else:
            missing.append(str(path))
    if missing:
        print("\nCRITICAL BOOT ERROR: Critical system module(s) could not be found.")
    print("\nSYSTEM MODULE CHECK:")
    if present:
        for i in present:
            print(f"✅ {i} - File found")
    if not missing:
        return True
    for i in missing:
        print(f"❌ {i} - FILE NOT FOUND")
    return False

if __name__ == "__main__":
    os.system("")
    print("\033[H\033[2J", end="")
    print("\nFlyshell will now check that it is able to boot.")
    try:
        if boot_check():
            from core import auth, console, data, loader
            if data.HOST_OS in ["Windows", "Darwin", "Linux"]:
                if sys.version_info < (3, 10):
                    print("\nCRITICAL ERROR: Your Python version is too old to be supported by Flyshell.")
                    print("\nFlyshell cannot launch because it requires Python 3.10 or newer.")
                    sys.exit(1)
                print(f"\nYour OS '{data.HOST_OS}' is compatible with Flyshell.")
                print("Flyshell will now boot.")
                loader.scan_plugins()
                if auth.login_flow():
                    console.boot()
                else:
                    print("Shutting down...\n")
                    sys.exit(0)
            else:
                print(f"\nCRITICAL ERROR: Host operating system '{data.HOST_OS}' is not supported.")
                print("\nFlyshell cannot launch because your operating system is not supported.")
                sys.exit(1)
        else:
            print("\nFlyshell cannot launch until the above file paths are restored.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nFlyshell session terminated by user.")
        sys.exit(0)
    except Exception as e:
        print("\nOops! An unexpected error occurred.")
        print(f"Error details: {e}")
        print("We don't really know what happened there. Sorry about that.")
        sys.exit(1)