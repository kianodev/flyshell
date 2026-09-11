# \main.py

from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parent

def boot_check():
    print("\nFlyshell will now check that your modules exist.")
    core_dir = PROJECT_ROOT / "core"
    plugin_dir = PROJECT_ROOT / "plugin"
    REQUIRED_COMPONENTS = [
        core_dir,
        plugin_dir,
        core_dir / "console.py",
        core_dir / "directory.py",
        core_dir / "data.py",
        core_dir / "system.py",
        core_dir / "auth.py",
        core_dir / "base_plugin.py",
        core_dir / "loader.py",
    ]
    if core_dir.exists():
        for py_file in sorted(core_dir.glob("*.py")):
            if py_file not in REQUIRED_COMPONENTS and not py_file.name.startswith("_"):
                REQUIRED_COMPONENTS.append(py_file)
    present = []
    missing = []
    for path in REQUIRED_COMPONENTS:
        if path.exists():
            present.append(str(path))
        else:
            missing.append(str(path))
    if missing:
        print("\nCRITICAL BOOT ERROR: Critical system module(s) could not be found.")
    for i in present:
        print(f"✅ {i} - File found")
    for i in missing:
        print(f"❌ {i} - FILE NOT FOUND")
    if missing:
        return False
    print("\nFlyshell will now check additional packages. These are not required.")
    from core import console
    if console.check_readline():
        print("✅ Terminal Readline - Available (Use arrow keys to navigate input history)")
    else:
        print("⚠️ Terminal Readline - Unavailable (This does not affect your performance)")
    return True

if __name__ == "__main__":
    os.system("")
    print("\033[H\033[2J", end="")
    print("\nLaunch process initiated. Flyshell is checking it is able to launch...")
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
        print("\n\nFlyshell session terminated, shutting down...\n")
        sys.exit(0)
    except Exception as e:
        print("\nOops! An unexpected error occurred.")
        print(f"Error details: {e}")
        print("We don't really know what happened there. Sorry about that.\n")
        sys.exit(1)