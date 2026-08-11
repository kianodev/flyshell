# Flyshell, A Modular Python CLI Architecture (v0.3)

An extensible, decoupled Command-Line Interface (CLI) built in Python using a dynamic plugin loading architecture and semantic version tracking.

## Features
* **Basic Directory Management:** Basic system to change and view directory information (dir/ls dual compatibility)
* **Core Command Directory:** Decoupled execution router mapping commands to system actions.
* **Parameter Validation:** Built-in threshold checks preventing runtime index errors.
* **Version System:** Internal build-number integer tracking paired with display semantic versioning.

## Directory Structure
```text
/project
├── /core
│   ├── console.py      # Main input loop & parsing
│   ├── data.py         # Versioning & storage context
│   ├── directory.py    # Command routing registry
│   ├── loader.py       # Dynamic plugin manager (In Development)
│   └── system.py       # Core built-in commands
├── /plugin             # Future plugin space
└── main.py             # System entrypoint
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.