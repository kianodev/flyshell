# Flyshell

A modular, zero-dependency command-line environment and extensible runtime interface built in Python.

Flyshell provides a sandboxed, extensible shell environment featuring dynamic runtime plugin loading, session persistence, secure authentication, and cross-platform process isolation, using only Python standard libraries.

No extra packages required, just install and enjoy!

## Key Features

1. **Zero External Dependencies**: Flyshell is built entirely with native Python modules with absolutely zero third-party packages required to enjoy full functionality.
2. **Dynamic Plugin Architecture**: Flyshell employs a dynamic plugin architecture that automatically scans and supports any plugin in plugin/ that follows the Flyshell contract (this is defined in `base_plugin.py`).
3. **Secure Authentication**: Flyshell uses salted PBKDF2 HMAC (SHA-256, 100K iterations) with constant-time equality comparisons to prevent timing attacks on password information.
4. **Cross-Platform Support**: Flyshell is fully supported by Windows (NT), macOS (Darwin) and Linux installations with native OS management and POSIX-aware parsing. Note that Flyshell is **not** supported by any other systems.
5. **State and History Persistence**: Flyshell has a fully encapsulated JSON storage system (soon to be upgraded to a more robust SQLite3-based model) providing session metrics and ISO 8601 UTC audit logging.

## System Requirements

1. **Python**: Your Python installation or IDE must support **Python 3.10 or newer** as Flyshell utilises structural pattern matching features. Older Python installations will be rejected by Flyshell on boot or it may crash entirely.
2. **Operating System**: Your operating system must be **Windows 10/11, macOS (Darwin) or Linux**. Any other operating system will be rejected by Flyshell on boot.

## System Architecture

```
flyshell/
├── core/
│   ├── auth.py             # Salted PBKDF2 HMAC auth & lock screen logic
│   ├── base_plugin.py      # Abstract base class & plugin storage contracts
│   ├── console.py          # Main REPL execution loop
│   ├── data.py             # Centralized persistent storage engine
│   ├── directory.py        # Command dispatching & POSIX input parser
│   ├── loader.py           # Dynamic runtime plugin discovery engine
│   └── system.py           # Native shell command implementations
├── plugin/                 # Drop-in directory for community & custom plugins
├── flyshell_storage.json   # Local state file (this is auto-generated when run for the first time)
└── main.py                 # Root boot checker & platform verification entry point
```

## Getting Started

To install Flyshell on your machine and get started, follow the below process:

### 1. Installation

Clone this repository to your local machine using Git:
```bash
git clone https://github.com/kianodev/flyshell.git
cd flyshell
```

### 2. Booting the Shell

Launch Flyshell via Python 3:
```bash
python main.py
```
On initial launch, Flyshell will prompt you to initialise your profile and secure password.

### 3. Exploring the System

Once Flyshell has launched, you will see an interface that looks something like this:
```console
Flyshell [version] (current_dir)>>
```
From this stage, you can enter a wide variety of commands. To see the commands list for your installation, type 'cmds' to return a full directory.

To close Flyshell once you are done, either:
1. Press Ctrl+C at any time to force terminate the system.
2. Enter 'kill' into the command line then 'y' to confirm.

## Creating Custom Plugins

Flyshell features an extensible plugin API. This API currently supports single-file plugins but will be expanded to support multi-file plugins at a later date. Create a new .py file in the `plugin/` directory, for example:
```python
# \plugin\hello.py
from core.base_plugin import BasePlugin

class HelloPlugin(BasePlugin):
	name = "Hello"
	description = "A simple greeting plugin demonstration."

	def execute(self, args: list):
		target = args[0] if args else "World"
		print(f"\nHello, {target}!\n")
```
Flyshell will automatically discover, inspect and register your new plugin on boot.

Your plugin **must** follow the contract of BasePlugin or else it will not work properly and Flyshell will refuse to execute it / display an unexpected crash message.

Plugins get passed their own storage directory. To access a particular item:
```python
self.storage.get("key", default)
```

To update a specific attribute:
```python
self.storage["key"] = value
```
This only updates in RAM. To save to disk, see below.

To load the entire storage (refresh) your storage:
```python
self.load_storage()
```

To save everything to disk:
```python
self.save_storage()
```
However, your plugin will **automatically save** on unload and there is no need to call this before shutting the plugin as Flyshell calls it for you.