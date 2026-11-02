# src\flyshell\core\env.py

from flyshell import constants as c
from pathlib import Path


def get_env_path() -> Path:
    return c.APP_DIR / "flyshell_keys.env"


def create_env():
    env_path = get_env_path()
    if not env_path.exists():
        env_path.touch()


def read_env_file() -> dict[str, str]:
    env_path = get_env_path()
    if not env_path.exists():
        return {}
    entries = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            entries[key.strip()] = val.strip().strip("\"'")
        return entries


def get_plugin_api_keys(plugin_dir_name: str) -> dict[str, str]:
    all_env = read_env_file()
    prefix = f"{plugin_dir_name}_".lower()
    plugin_keys = {}
    for raw_k, val in all_env.items():
        if raw_k.lower().startswith(prefix):
            key_name = raw_k[len(prefix) :]
            plugin_keys[key_name] = val
    return plugin_keys
