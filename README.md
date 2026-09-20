# Flyshell

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)

A modular, zero-dependency command-line environment and extensible runtime interface built in Python.

Flyshell provides a sandboxed, extensible shell environment featuring dynamic runtime plugin loading, session persistence, secure authentication, and cross-platform process isolation, using only Python standard libraries.

No extra packages required, just install and enjoy!

## Key Features

1. **Zero External Dependencies**: Flyshell is built entirely with native Python modules with absolutely zero third-party packages required to enjoy full functionality.
2. **Dynamic Plugin Architecture**: Flyshell employs a dynamic plugin architecture that automatically scans and supports any plugin in plugin/ that follows the Flyshell contract (this is defined in `base_plugin.py`).
3. **Secure Authentication**: Flyshell uses salted PBKDF2 HMAC (SHA-256, 100K iterations) with constant-time equality comparisons to prevent timing attacks on password information.
4. **Cross-Platform Support**: Flyshell is fully supported by Windows (NT), macOS (Darwin) and Linux installations with native OS management and POSIX-aware parsing. Note that Flyshell is **not** supported by any other systems.
5. **State and History Persistence**: Flyshell has a fully encapsulated SQL storage system using SQLite3 providing session metrics and ISO 8601 UTC audit logging.

Versions of Flyshell prior to v0.39 used a JSON storage file; these files are handled and migrated automatically.

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
│   ├── data.py             # Centralised persistent storage engine
│   ├── directory.py        # Command dispatching & POSIX input parser
│   ├── loader.py           # Dynamic runtime plugin discovery engine
│   └── system.py           # Native shell command implementations
├── plugin/                 # Drop-in directory for community & custom plugins
├── flyshell.db             # Local SQL state file (this is auto-generated when run for the first time)
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
If that fails, try:
```bash
python3 main.py
```
On initial launch, Flyshell will prompt you to initialise your profile and secure password.

### 3. Exploring the System

Once Flyshell has launched, you will see an interface that looks something like this:
```console
Flyshell [version] (current_dir)>>
```
From this stage, you can enter a wide variety of commands. To see the commands list for your installation, type `cmds` or `help` to return a full up-to-date directory. Use `fs plugins` to return plugin information.

Flyshell also supports command chaining out of the box. Use `;` to chain commands together regardless of result, `&&` to execute only on success and `||` to execute only on failure.

To close Flyshell once you are done, enter `kill` onto the command line then confirm.

## Creating Custom Plugins

Flyshell features an extensible plugin API. This API supports both single-file and multi-file plugins. Follow the below guide to create your own.

Plugins must inherit from the `BasePlugin` contract and be stored under the `plugin/` directory.

All plugins, whilst not required, should have a title (`name`) and desc (`description`) defined in their master file. Flyshell can read this information for both `fs plugins` and `[my_plugin] -h` / `--help` which are both supported out of the box. Flyshell will discover, inspect and import your plugin from the `plugin/` folder without you having to alter any internal code.

### Single-File Plugins

Single-file plugins should be a single file, e.g. `my_plugin.py`.

This file serves as the entry point for your file and should look like this:
```python
# \plugin\my_plugin.py

from core.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
	# Name and description (Flyshell can read these)
	name = "My Plugin"
	description = "This is my plugin. You can use it."

	def execute(self, args): # This is what Flyshell calls to execute
		print(f"Hello! Arguments: {args}")
		return
```

### Multi-File Plugins

Multi-file plugins follow the same contract but are stricter in how they must be structured.
1. Create a directory `my_plugin/` within the `plugin/` directory.
2. Create a file called `plugin.py` - this is your entrypoint. It is mandatory that it is called `plugin.py` and cannot be called anything else.
3. This file uses the same template as single-file plugins. You can import as many of your plugin's other files as you like. Flyshell will handle import errors automatically by safely killing the plugin on any error with an internally handled Exception.

### File Management

The `BasePlugin` inherited class provides storage access as context for your plugin to use.

Plugins get passed their own storage directory. To access a particular item:
```python
self.storage.get("key", default)
```

To update a specific attribute:
```python
self.storage["key"] = value
```

To load the entire storage (refresh) your storage:
```python
self.load_storage()
```

To save changes to disk:
```python
self.save_storage()
```
However, your plugin will **automatically save** on unload and there is no need to call this before shutting the plugin as Flyshell calls it for you.

For plugins using multiple files or functions, unless `self` is passed to other files they cannot be accessed except within `plugin.py`.