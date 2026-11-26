# tests/conftest.py

from flyshell import constants as c

import pytest


@pytest.fixture(autouse=True)
def isolate_flyshell_storage(tmp_path_factory, monkeypatch):
    app_dir = tmp_path_factory.mktemp("flyshell_app")
    monkeypatch.setattr(c, "APP_DIR", app_dir)
    monkeypatch.setattr(c, "FILE_PATH", app_dir / "flyshell.db")
    monkeypatch.setattr(c, "ENV_PATH", app_dir / "flyshell_keys.env")
    monkeypatch.setattr(c, "INITIALISED", set())
    monkeypatch.setattr(c, "PLUGINS", {})
