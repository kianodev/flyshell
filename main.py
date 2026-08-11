# \main.py

from pathlib import Path
import sys

def boot_check():
    REQUIRED_COMPONENTS = [
    Path("core/console.py"),
    Path("core/data.py"),
    Path("core/directory.py"),
    Path("core/loader.py"),
    Path("core/system.py"),
    Path("plugin")
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
    print("\nSYSTEM MODULE CHECK")
    if present:
        for i in present:
            print(f"✅ {i} - File found")
    if not missing:
        return True
    for i in missing:
        print(f"❌ {i} - FILE NOT FOUND")
    return False

if __name__ == "__main__":
    print("\nFlyshell will now check that it is able to boot.")
    if boot_check():
        from core import console, data
        if data.HOST_OS in ["Windows", "Darwin", "Linux"]:
            print(f"\nYour OS '{data.HOST_OS}' is compatible with Flyshell.")
            print("Flyshell will now boot.")
            console.boot()
        else:
            print(f"\nCRITICAL ERROR: Host operating system '{data.HOST_OS}' is not supported.")
    else:
        print("\nFlyshell cannot launch until the above file paths are restored.")
        sys.exit(1)

