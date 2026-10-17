# src\flyshell\constants.py

from flyshell.core.directory import COMMAND_REGISTRY

from pathlib import Path
import os
import platform
import time

BUILD = 104
VERSION = "1.0.5"


def _resolve_app_dir() -> Path:
    home = Path.home()
    if HOST_OS == "Windows":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif HOST_OS == "Darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    target = base / "Flyshell"
    target.mkdir(parents=True, exist_ok=True)
    return target


HOST_OS = platform.system()
PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_ROOT.parent
PROJECT_ROOT = SRC_DIR.parent
APP_DIR = _resolve_app_dir()
FILE_PATH = APP_DIR / "flyshell.db"
USER_PLUGIN_DIR = APP_DIR / "plugins"

SESSION_START_TIME = time.time()
SESSION_CMD_COUNT = 0

PLUGINS = {}
RESERVED_NAMES = set(COMMAND_REGISTRY.keys())

BLOCKED_COMMANDS = frozenset({"format", "diskpart", "dd"})
DANGER_COMMANDS = frozenset({"del", "rmdir", "rd", "rm", "taskkill", "killall"})
SUPPORTED_OS = frozenset({"Windows", "Darwin", "Linux"})
SUPPORTED_PYTHON = (3, 10)

CLEAR_SCREEN = "\033[H\033[2J"

INITIALISED = set()

REQUIRED_COMPONENTS = [
    "abstract",
    "abstract/base_cmd.py",
    "abstract/base_plugin.py",
    "abstract/parent_cmd.py",
    "builtin",
    "builtin/fs.py",
    "builtin/system.py",
    "builtin/utils.py",
    "constants.py",
    "core",
    "core/auth.py",
    "core/console.py",
    "core/data.py",
    "core/directory.py",
    "core/loader.py",
]

GREETINGS = [
    "Hi {username}, what's it going to be today?",
    "The mic is yours, {username}, go and blow me away!",
    "Hey {username}, let's get this party started!",
    "What's up, {username}? Let's go!",
    "I'm awaiting your first command, {username}!",
    "How's it going {username}? I'm here to help.",
    "{username}, it's your call! Show me what you've got, what are we doing today?",
    "My wish is your command, {username}! (unless it's not on my command list)",
    "I have goods for you {username}, it's called a Command Interface.",
    "I'm your boss! Wait, no... sorry... you, {username}, are my boss!",
]
