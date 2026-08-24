# \core\data.py

BUILD = 34
VERSION = "0.33"

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from pathlib import Path
import json
import os
import platform
import time

HOST_OS = platform.system()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILE_PATH = PROJECT_ROOT / "flyshell_storage.json"

SESSION_START_TIME = time.time()
SESSION_CMD_COUNT = 0

def initialise(filename=FILE_PATH):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f, indent=4)

def load_all(filename=FILE_PATH):
    initialise(filename)
    with open(filename, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def write(keys, value, filename=FILE_PATH):
    data = load_all(filename)
    if isinstance(keys, str):
        keys = [keys]
    current = data
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def read(keys=None, filename=FILE_PATH):
    data = load_all(filename)
    if keys is None:
        return data
    if isinstance(keys, str):
        keys = [keys]
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

def delete(keys, filename=FILE_PATH):
    data = load_all(filename)
    if isinstance(keys, str):
        keys = [keys]
    current = data
    for key in keys[:-1]:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    if isinstance(current, dict) and keys[-1] in current:
        del current[keys[-1]]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        return True
    return False