# Flyshell Changelog

> Documentation last updated: v1.3.0

##  Release Notes

The below section details all releases since v1.0.0 (12 October 2026).

### Flyshell v1.3.0 - The Plugin Suite Update 🔗

> This update was released on 9 November 2026.

Welcome to **Flyshell v1.3.0**! This release has added many new features to Flyshell's plugin suite, enabling developers to add more complex features with more control over their plugins.

#### 🌟 What's New?

The `BasePlugin` architecture has been transformed:
* Added identifiers (`identifier`) allowing a plugin's folder name and command name to be unique
* Added API keys, defined and stored in `flyshell_keys.env`
* Added commands via `pkg` to view and modify these keys
* Added the ability to define all required API keys in list `api_keys` within the `BasePlugin` standard
* Added the ability to also define third party dependencies for plugins
* Added automatic checks for both of the above

This leaves Flyshell's plugin architecture with a wide range of new and exciting features for development.

### Flyshell v1.2.0 - The Great Refactoring Update 🔨

> This update was released on 23 October 2026.

Welcome to **Flyshell v1.2.0**! This release has fundamentally altered how several Flyshell internals work, removing redundant and poor-quality code in favour of modern and sleek solutions ready for future building.

#### 🌟 What's New?

Many quick refactoring changes have occurred:
* Removed all lazy circular imports (like `constants.py` <> `core/directory.py`)
* Hardened restrictions on system shell execution (`sys`)
* Strengthened plugin collisions check in `core/loader.py`
* Refactored `BaseCmd` to mandate all commands return strict tuples
* Added multiple unit tests across the `builtin/` family of files

Furthermore, many system bugs have been fixed and the system has been left more extensible than ever, ready for future updates.

### Flyshell v1.1.0 - Filesystem Suite Update 💾

> This update was released on 18 October 2026.

Welcome to Flyshell v1.1.0! This release introduces a suite of native filesystem commands, eliminating the reliance on sys for basic Bash commands and reinforcing application security boundaries.

#### 🌟 What's New?

The Flyshell command suite has been expanded substantially:
* Directory management commands (`mkdir` / `rmdir`)
* File management commands (`touch` / `rm`)
* Text file inspection (`cat`)
* File copying and movement (`cp` / `mv`)
* File renaming (`rename`)
* Text relay to terminal output (`echo`)

System safety guards have been expanded:
* **Self-Deletion Protection**: Flyshell blocks all commands that target its own core package, user plugins or the application database.
* **Operating System Root Protection**: Flyshell prevents the deletion or relocation of critical system root drives (i.e. `/` and `C:\`) and essential OS user/program directories.
* **Active Working Directory Safeguards**: Flyshell will not remove the active working directory.

In addition, several general bug fixes have occurred.

### Flyshell v1.0.0 - Initial Stable Release 🚀

> This update was Flyshell's first stable release, released on 12 October 2026.

I'm excited to announce the first official stable release of **Flyshell**! Flyshell is a modular, zero-dependency command-line environment and extensible runtime interface built entirely using Python's standard library.

#### 🌟 Key Highlights

* **Zero External Dependencies**: Built entirely with native Python modules—no third-party dependencies required.
* **Extensible Plugin Engine**: Dynamic discovery and loading of custom single-file and directory plugins.
* **Session & History Persistence**: Encapsulated SQLite storage for session state, preferences, and ISO 8601 audit logging.
* **PBKDF2 HMAC Security**: Salted SHA-256 password hashing (600,000 iterations) with constant-time comparison to prevent timing attacks.
* **Command Chaining**: Built-in support for POSIX-style command operators (`;`, `&&`, `||`).
* **Cross-Platform Support**: Full native support for Windows, macOS, and Linux.