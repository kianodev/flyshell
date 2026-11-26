# tests/test_fs.py

from flyshell.builtin import fs


def test_fs_dispatches_version():
    code, msg = fs.Fs().execute(["version"])
    assert code == 0
    assert "Flyshell Version" in msg


def test_fs_dispatches_licence():
    code, msg = fs.Fs().execute(["licence"])
    assert code == 0
    assert "MIT Licence" in msg


def test_fs_dispatches_license_alias():
    code, msg = fs.Fs().execute(["license"])
    assert code == 0
    assert "MIT Licence" in msg


def test_fs_unknown_subcommand():
    code, msg = fs.Fs().execute(["unknown_cmd"])
    assert code == 1
    assert "Unknown subcommand" in msg


def test_fs_del_requires_target():
    code, msg = fs.FsDel().execute([])
    assert code == 1
    assert "requires a target" in msg
