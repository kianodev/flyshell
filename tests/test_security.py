# tests/test_security.py

from flyshell.builtin import system
from flyshell.core import auth, data


def test_sysexe_blocks_prohibited_base_commands():
    for cmd in ["format C:", "diskpart", "dd if=/dev/zero"]:
        tokens = cmd.split()
        code, message = system.SysExe().execute(tokens)
        assert code == 1
        assert "Security Error" in message


def test_sysexe_dangerous_commands_require_auth(monkeypatch):
    dummy_hash, dummy_salt = auth.hash_password("ValidPassword123!")
    monkeypatch.setattr(
        data,
        "get_auth",
        lambda: {"username": "TestUser", "hash": dummy_hash, "salt": dummy_salt},
    )
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "WrongPassword")
    for cmd in ["del some_file.txt", "rm -rf some_dir"]:
        tokens = cmd.split()
        code, message = system.SysExe().execute(tokens)
        assert code == 1
        assert "Account Error" in message or "Password does not match" in message


def test_sysexe_force_flag_without_arguments_returns_error():
    code, message = system.SysExe().execute(["-f"])
    assert code == 1
    assert "requires at least 1 parameter" in message
