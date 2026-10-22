# tests\test_fs.py

from flyshell.builtin import fs


def test_fs_parent_dispatches_subcommands():
    parent = fs.Fs()
    code, msg = parent.execute(["version"])
    assert code == 0
    assert "Flyshell Version" in msg
    code, msg = parent.execute(["licence"])
    assert code == 0
    assert "MIT Licence" in msg
    code, msg = parent.execute(["license"])
    assert code == 0
    assert "MIT Licence" in msg


def test_fs_unknown_subcommand():
    parent = fs.Fs()
    code, msg = parent.execute(["unknown_cmd"])
    assert code == 1
    assert "Unknown subcommand" in msg


def test_fs_del_requires_target():
    del_cmd = fs.FsDel()
    code, msg = del_cmd.execute([])
    assert code == 1
    assert "requires a target" in msg
