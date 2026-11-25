# Flyshell Project Structure

> Documentation last updated: v1.6.0

This document provides a comprehensive view of the entire Flyshell repository tree, including development workflows, documentation, source packages, tests, and configuration assets.

## Architectural Layout

Below is the full architectural diagram for Flyshell:

```
flyshell/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
├── c_src/
│   └── diskops/
│       ├── posix/
│       │   ├── cat.c
│       │   ├── cp.c
│       │   ├── dir.c
│       │   ├── mkdir.c
│       │   ├── mv.c
│       │   ├── rename.c
│       │   ├── rm.c
│       │   ├── rmdir.c
│       │   └── touch.c
│       ├── shared/
│       │   ├── dir_types.c
│       │   ├── dir_types.h
│       │   ├── native_errors.h
│       │   └── win32_utf.h
│       ├── win32/
│       │   ├── cat.c
│       │   ├── cp.c
│       │   ├── dir.c
│       │   ├── mkdir.c
│       │   ├── mv.c
│       │   ├── rename.c
│       │   ├── rm.c
│       │   ├── rmdir.c
│       │   └── touch.c
│       └── diskops.c
├── docs/
│   ├── release_notes/
│   │   ├── v1.0_release_notes.md
│   │   ├── v1.1_release_notes.md
│   │   ├── v1.2_release_notes.md
│   │   ├── v1.3_release_notes.md
│   │   ├── v1.4_release_notes.md
│   │   ├── v1.5_release_notes.md
│   │   └── v1.6_release_notes.md
│   ├── CHANGELOG.md
│   └── project_structure.md
├── src/
│   └── flyshell/
│       ├── abstract/
│       │   ├── __init__.py
│       │   ├── base_cmd.py
│       │   ├── base_plugin.py
│       │   └── parent_cmd.py
│       ├── accounts/
│       │   ├── __init__.py
│       │   └── auth.py
│       ├── bin/
│       │   └── __init__.py
│       ├── builtin/
│       │   ├── __init__.py
│       │   ├── fs.py
│       │   ├── pkg.py
│       │   ├── system.py
│       │   └── utils.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── console.py
│       │   ├── data.py
│       │   └── directory.py
│       ├── native/
│       │   ├── legacy/
│       │   │   ├── __init__.py
│       │   │   └── diskops.py
│       │   ├── __init__.py
│       │   ├── diskops_bridge.py
│       │   └── diskops_handler.py
│       ├── startup/
│       │   ├── __init__.py
│       │   ├── deps.py
│       │   ├── env.py
│       │   ├── loader.py
│       │   └── seasonal.py
│       ├── __init__.py
│       ├── constants.py
│       └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_data.py
│   ├── test_deps.py
│   ├── test_directory.py
│   ├── test_diskops_ext.py
│   ├── test_diskops_lgc.py
│   ├── test_env.py
│   ├── test_fs.py
│   ├── test_loader.py
│   ├── test_pkg.py
│   └── test_utils.py
├── .clang-format
├── .clang-tidy
├── .flake8
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── README.md
├── pyproject.toml
└── setup.py
```

## Directory Breakdown

* .github/: Automation pipelines and GitHub Actions workflows.
* c_src/diskops: C-extension of diskops operations (these are compiled automatically on PyPI installations).
* docs/: Developer documentation, release notes per minor version milestone, changelogs, and workspace layout records.
* src/flyshell/: Executable package root containing command abstractions, built-in utilities, and runtime core engines.
* tests/: Pytest test suite covering command logic, plugin lifecycle, security checks, and platform stability.
* Root Files: Project metadata, static analysis rules (.flake8), version control ignores (.gitignore), licensing, and packaging build configuration (pyproject.toml / setup.py).