# src/flyshell/startup/boot.py

from flyshell import constants as c
from flyshell import accounts, pkgm
from flyshell.core import console


def launch() -> None:
    print("Flyshell will now boot.")
    c.APP_DIR.mkdir(parents=True, exist_ok=True)
    pkgm.scan_plugins()
    pkgm.check_plugin_api_keys()
    pkgm.check_all_plugin_dependencies()
    if accounts.login_flow():
        console.boot()
    else:
        print("\nShutting down...\n")


def shutdown() -> None:
    pkgm.unload_plugins()
