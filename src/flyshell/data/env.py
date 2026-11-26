# src/flyshell/data/env.py

from pathlib import Path
from flyshell import constants as c


def get_env_path() -> Path:
    primary = c.APP_DIR / "flyshell_keys.env"
    if primary.exists():
        return primary
    fallback = c.APP_DIR / ".env"
    if fallback.exists():
        return fallback
    return primary


def create_env() -> None:
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
            raw_k, raw_v = line.split("=", 1)
            clean_k = raw_k.strip()
            clean_v = raw_v.strip().strip("\"'")
            if clean_k:
                entries[clean_k] = clean_v
    return entries


def set_env_entry(key: str, value: str) -> tuple[bool, str]:
    clean_val = value.strip().strip("\"'")
    env_path = get_env_path()
    try:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        if not env_path.exists():
            env_path.touch()
        lines = env_path.read_text(encoding="utf-8").splitlines()
        updated = False
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k, _ = stripped.split("=", 1)
                clean_k = k.strip().replace("[", "").replace("]", "")
                if clean_k.lower() == key.lower():
                    new_lines.append(f"{key}={clean_val}")
                    updated = True
                    continue
            new_lines.append(line)
        if not updated:
            new_lines.append(f"{key}={clean_val}")
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return (True, "Updated" if updated else "Added")
    except Exception as e:
        return (False, f"File Error: Failed to write to '{env_path}': {e}")


def delete_env_entry(key: str) -> tuple[bool, str]:
    env_path = get_env_path()
    if not env_path.exists():
        return (False, f"File Config Error: Environment file not found at '{env_path}'")
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
        new_lines = []
        found = False
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k, _ = stripped.split("=", 1)
                clean_k = k.strip().lower()
                if clean_k == key.lower():
                    found = True
                    continue
            new_lines.append(line)
        if not found:
            return (False, f"Command Error: Key '{key}' not found in '{env_path.name}'")
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return (True, env_path.name)
    except Exception as e:
        return (False, f"File Error: Failed to update '{env_path}': {e}")
