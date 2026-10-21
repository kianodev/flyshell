# src\flyshell\main.py

from pathlib import Path
import importlib.util
import os
import sys


def boot_check():
    print("\nFlyshell will now check that your modules exist.")
    present = []
    missing = []
    try:
        from flyshell import constants as c

        if str(c.SRC_DIR) not in sys.path:
            sys.path.insert(0, str(c.SRC_DIR))
    except ImportError:
        print(
            "\nCRITICAL BOOT ERROR: Failed to initialise system due to corrupted or missing files.\n"
        )
    for obj in c.REQUIRED_COMPONENTS:
        path = Path(c.PACKAGE_ROOT / obj)
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
    tests_dir = c.PROJECT_ROOT / "tests"
    if tests_dir.exists():
        print(
            "\nFlyshell will now check internal additional packages and features. These are not required."
        )
        for path in tests_dir.glob("test_*.py"):
            print(f"✅ {path.name} - Test found")
        if importlib.util.find_spec("pytest") is not None:
            print("✅ Your tests can be run using Pytest.")
        else:
            print("⚠️ Your tests cannot be run as Pytest is not installed.")
    print(
        "\nFlyshell will now check external additional packages and features. These are not required."
    )
    from flyshell.core import console

    if console.check_readline():
        print(
            "✅ Terminal Readline - Available (Use arrow keys to navigate input history)"
        )
    else:
        print(
            "⚠️ Terminal Readline - Unavailable (This does not affect your performance)"
        )
    return True


def main():
    os.system("")
    print("\033[H\033[2J", end="")
    print("\nLaunch process initiated. Flyshell is checking it is able to launch...")
    try:
        if boot_check():
            from flyshell import constants as c
            from flyshell.core import auth, console, loader

            if c.HOST_OS in ["Windows", "Darwin", "Linux"]:
                if sys.version_info < c.SUPPORTED_PYTHON:
                    print(
                        "\nCRITICAL ERROR: Your Python version is too old to be supported by Flyshell."
                    )
                    print(
                        "Flyshell cannot launch because it requires Python 3.10 or newer."
                    )
                    sys.exit(1)
                print(f"\nYour OS '{c.HOST_OS}' is compatible with Flyshell.")
                print("Flyshell will now boot.")
                loader.scan_plugins()
                if auth.login_flow():
                    console.boot()
                else:
                    print("\nShutting down...\n")
                    sys.exit(0)
            else:
                print(
                    f"\nCRITICAL ERROR: Host operating system '{c.HOST_OS}' is not supported."
                )
                print(
                    "Flyshell cannot launch because your operating system is not supported."
                )
                sys.exit(1)
        else:
            print("\nFlyshell cannot launch until the above file paths are restored.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nFlyshell session terminated, shutting down...\n")
        sys.exit(0)
    except Exception as e:
        print("\n❌❌❌ Oops! An unexpected error occurred.")
        print(f"Error details: {e}")
        print("We don't really know what happened there. Sorry about that.\n")
        print("Print traceback message? Default is N.")
        choice = input("[y/n]?: ")
        if choice.lower() == "y":
            import traceback

            raw = traceback.extract_tb(e.__traceback__)
            last_frame = raw[-1]
            print("\nTraceback details:")
            print(f"File: '{last_frame[0]}'")
            print(f"Line: {last_frame[1]}")
            print(f"Exception message: '{e}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
