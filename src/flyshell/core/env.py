# src\flyshell\core\env.py

from flyshell import constants as c

from pathlib import Path

def create_env():
    env_path = c.APP_DIR / "flyshell_keys.env"
    if not env_path.exists():
        env_path.touch()