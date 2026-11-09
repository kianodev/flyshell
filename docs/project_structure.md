# Flyshell Project Structure

> Documentation last updated: v1.3.0

This document provides a comprehensive view of the entire Flyshell repository tree, including development workflows, documentation, source packages, tests, and configuration assets.

## Architectural Layout

Below is the full architectural diagram for Flyshell:

```
flyshell/
├── .github/
│   └── workflows/
│       └── pytest.yml
├── docs/
│   ├── release_notes/
│   │   ├── v1.0_release_notes.md
│   │   ├── v1.1_release_notes.md
│   │   ├── v1.2_release_notes.md
│   │   └── v1.3_release_notes.md
│   ├── CHANGELOG.md
│   └── project_structure.md
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
│       │   ├── pkg.py
│       │   ├── system.py
│       │   └── utils.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── console.py
│       │   ├── data.py
│       │   ├── deps.py
│       │   ├── directory.py
│       │   ├── env.py
│       │   └── loader.py
│       ├── __init__.py
│       ├── constants.py
│       └── main.py
├── tests/
│   ├── test_auth.py
│   ├── test_data.py
│   ├── test_deps.py
│   ├── test_directory.py
│   ├── test_diskops.py
│   ├── test_env_keys.py
│   ├── test_fs.py
│   ├── test_loader.py
│   ├── test_pkg.py
│   ├── test_security.py
│   └── test_utils.py
├── .flake8
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

## Directory Breakdown

* .github/: Automation pipelines and GitHub Actions workflows.
* docs/: Developer documentation, release notes per minor version milestone, changelogs, and workspace layout records.
* src/flyshell/: Executable package root containing command abstractions, built-in utilities, and runtime core engines.
* tests/: Pytest test suite covering command logic, plugin lifecycle, security checks, and platform stability.
* Root Files: Project metadata, static analysis rules (.flake8), version control ignores (.gitignore), licensing, and packaging build configuration (pyproject.toml).