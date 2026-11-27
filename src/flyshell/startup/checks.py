# src/flyshell/startup/checks.py

from flyshell import constants as c
from flyshell.core import console
from flyshell.native import diskops_bridge

from pathlib import Path
import importlib.util
import sys


def check_components() -> bool:
    print("\nFlyshell will now check that your modules exist.")
    if str(c.SRC_DIR) not in sys.path:
        sys.path.insert(0, str(c.SRC_DIR))
    present = []
    missing = []
    for obj in c.REQUIRED_COMPONENTS:
        path = Path(c.PACKAGE_ROOT / obj)
        if path.exists():
            present.append(str(path))
        else:
            missing.append(str(path))
    if missing:
        print("\nCRITICAL BOOT ERROR: Critical system module(s) could not be found.")
    for item in present:
        print(f"✅ {item} - File found")
    for item in missing:
        print(f"❌ {item} - FILE NOT FOUND")
    return len(missing) == 0


def check_environment() -> bool:
    if c.HOST_OS not in c.SUPPORTED_OS:
        print(
            f"\nCRITICAL ERROR: Host operating system '{c.HOST_OS}' is not supported."
        )
        print("Flyshell cannot launch because your operating system is not supported.")
        return False
    if sys.version_info < c.SUPPORTED_PYTHON:
        print(
            "\nCRITICAL ERROR: Your Python version is too old to be supported by Flyshell."
        )
        print("Flyshell cannot launch because it requires Python 3.10 or newer.")
        return False
    print(f"\nYour OS '{c.HOST_OS}' is compatible with Flyshell.")
    return True


def check_optional_features() -> None:
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
    if console.check_readline():
        print(
            "✅ Terminal Readline - Available (Use arrow keys to navigate input history)"
        )
    else:
        print(
            "⚠️ Terminal Readline - Unavailable (This does not affect your performance)"
        )
    if diskops_bridge.has_native_support():
        print(
            "\n✅ C Extensions Available - Native C binaries are present and will be used where applicable.\n"
        )
    else:
        print(
            "\n⚠️ C Extensions Unavailable - Flyshell will revert to legacy Python objects where applicable.\n"
        )


def run_preflight() -> bool:
    if not check_components():
        print("\nFlyshell cannot launch until the above file paths are restored.")
        return False
    if not check_environment():
        return False
    check_optional_features()
    return True
