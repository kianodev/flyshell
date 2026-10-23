# Flyshell

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Licence](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)
![Tests](https://github.com/kianodev/flyshell/actions/workflows/pytest.yml/badge.svg)

> Documentation last updated: v1.2.0

A modular, zero-dependency command-line environment and extensible runtime interface built in Python.

Flyshell provides a modular, extensible shell environment featuring dynamic runtime plugin loading, session persistence, secure authentication, and cross-platform process isolation, using only Python standard libraries.

No extra packages required, just install and enjoy!

## Key Features

1. **Zero External Dependencies** - Flyshell is built entirely with native Python modules with absolutely zero third-party packages required to enjoy full functionality.
2. **Dynamic Plugin Architecture**: Flyshell employs a dynamic plugin architecture that automatically scans for plugins in the User Directory following the standard defined in `src/flyshell/abstract/base_plugin.py`.
3. **Secure Authentication**: Flyshell uses salted PBKDF2 HMAC (SHA-256, 600,000 iterations) with constant-time equality comparisons to prevent timing attacks on password information.
4. **Cross-Platform Support**: Flyshell is fully supported by Windows (NT), macOS (Darwin) and Linux installations with native OS management and POSIX-aware parsing. Note that Flyshell is **not** supported by any other systems.
5. **State and History Persistence**: Flyshell has a fully encapsulated SQL storage system using SQLite3 providing session metrics and ISO 8601 UTC audit logging.

## System Requirements

1. **Python**: Your Python installation or IDE must support **Python 3.10 or newer** as Flyshell utilises structural pattern matching features. Older Python installations will be rejected by Flyshell on boot or could crash the system.
2. **Operating System**: Your operating system must be **Windows 10/11, macOS (Darwin) or Linux**. Any other operating system will be rejected by Flyshell on boot.

## System Architecture

```
flyshell/
├── .github/
│   └── workflows/
│       └── pytest.yml
├── src/
│   └── flyshell/
│       ├── abstract/
│       │   ├── __init__.py
│       │   ├── base_cmd.py
│       │   ├── base_plugin.py
│       │   └── parent_cmd.py
│       ├── builtin/
│       │   ├── __init__.py
│       │   ├── diskops.py
│       │   ├── fs.py
│       │   ├── system.py
│       │   └── utils.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── console.py
│       │   ├── data.py
│       │   ├── directory.py
│       │   └── loader.py
│       ├── __init__.py
│       ├── constants.py
│       └── main.py
├── tests/
│   ├── test_auth.py
│   ├── test_data.py
│   ├── test_directory.py
│   ├── test_diskops.py
│   ├── test_fs.py
│   ├── test_loader.py
│   ├── test_security.py
│   └── test_utils.py
├── .flake8
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## Installing Flyshell

There are two methods to install Flyshell.

### Method 1: Install via `pip` (Best for General Use)

Install Flyshell through `pip`:
```bash
pip install flyshell
```

Then, you can simply run Flyshell:
```bash
flyshell
```

### Method 2: Install from source via `git` (Best for Development & Custom Plugins)

Clone the GitHub repository:
```bash
git clone https://github.com/kianodev/flyshell.git
```

Switch to the Flyshell directory and install in editable mode:
```bash
cd flyshell
pip install -e .
```

After this, you can simply run Flyshell:
```bash
flyshell
```

### Adding optional dependencies

To install Readline (on Windows):
```bash
pip install -e .[readline]
```

To install the development and testing suite (including Pytest):
```bash
pip install -e .[dev]
```

## Exploring Flyshell

Once you have installed Flyshell using either of the methods above, you will be prompted to initialise your user profile. Once this is complete, you will be greeted with a prompt that looks like this:
```console
Flyshell [v1.x.x] (current_dir)>>
```

From this stage, you can enter a wide variety of commands. To see the commands list for your installation, type `cmds` or `help` to return a full up-to-date directory. Use `fs plugins` to return plugin information.

Flyshell also supports command chaining out of the box. Use `;` to chain commands together regardless of result, `&&` to execute only on success and `||` to execute only on failure.

Use `-h` or `--help` after any command to return that command's specific help list.

To close Flyshell once you are done, enter `kill` onto the command line then confirm, or press Ctrl + D / Ctrl + Z (different keybinds depending on your host configuration) to close the session immediately.

## Creating Custom Plugins

Flyshell features an extensible plugin API. This API supports both single-file and multi-file plugins. Follow the below guide to create your own.

Plugins must inherit from the `BasePlugin` contract defined in `src/flyshell/abstract/base_plugin.py`. Plugins are stored in the User Directory. Navigate to your App Storage folder:
- **Windows**: `%APPDATA%\Flyshell\plugins`
- **macOS**: `~/Library/Application Support/Flyshell/plugins`
- **Linux**: `~/.local/share/Flyshell/plugins`

Place your plugins inside the `plugins/` folder.

All plugins should define the required attributes. Flyshell can read this information for both `fs plugins` and `[my_plugin] -h` / `--help` which are both supported out of the box. Flyshell will discover, inspect and import your plugin from the `plugins/` folder without you having to alter any internal code.

### The Entry-Point

All plugins must have an entry-point file. For single-file plugins, this is the plugin file. For multi-file plugins, this file must be named `plugin.py` and stored directly inside of your plugin's own folder.

This file is what enables Flyshell to speak to your plugin.

```python
# Entry-point (my_plugin.py or my_plugin\plugin.py)

from flyshell import BasePlugin # This is required

class MyPlugin(BasePlugin):
	name = "My Plugin" # The name you want visible to Flyshell
	description = "This is my plugin." # A short one-line explaining what your plugin does
	version = "1.0.0" # Default is 1.0.0
	author = "kianodev" # You can put your name, your GitHub handle, or leave blank to make it 'Unknown'
	usage = "" # (OPTIONAL) Explain how to use your plugin
	extended_help = "" # (OPTIONAL) A more detailed, multi-line guide containing specific assistance
	
	def on_load(self): # (OPTIONAL) Enables your program to handle specialist set-up tasks before execute()
		pass

	def on_unload(self): # (OPTIONAL) Enables your program to handle specialist shut-down tasks
		super().on_unload() # If you use a custom on_unload(), end it with this

	def execute(self, args): # This is what Flyshell calls to execute
		print(f"Hello! Arguments: {args}")
		return
```

### Extra Functions

Additional functions are available for you to use:

1. `get_data(key, default=None)`: Retrieves a value from local plugin memory.
2. `set_data(key, value)`: Updates a key in local memory and automatically persists it to SQLite via `save_storage()`.
3. `load_storage()`: Reloads fresh key-value pairs directly from SQLite into `self.storage`.
4. `save_storage()`: Writes all in-memory key-value pairs in `self.storage` back to SQLite.

Plugins save automatically on shut-down. If `on_unload()` is not used, it is automatic. If `on_unload()` is used, `super().on_unload()` saves your files.

### Built-in Attributes

Every plugin has direct access to the following instance variables:

- `self.plugin_name` (`str`): The unique name identifier used to invoke the plugin.
- `self.storage` (`dict`): In-memory key-value data automatically loaded from the persistent database.
- `self.context` (`dict`): Environmental metadata provided at start-up, within it:
  - `self.context["metadata"]["host_os"]`: Operating system (e.g., `'Windows'`, `'Linux'`, `'Darwin'`).
  - `self.context["metadata"]["version"]`: Current Flyshell version.
  - `self.context["file_path"]`: Full path to the plugin's source file.

### Extra Notes

You are welcome to catch errors yourself. However, Flyshell will handle them automatically. That said, if you would like your plugin to continue after an error, you need to implement error handling yourself as the default system closes your plugin.