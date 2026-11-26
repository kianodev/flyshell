# tests/test_utils.py

from flyshell.builtin import utils
from flyshell.core import data


def test_echo_output_and_escape_characters():
    cmd = utils.Echo()
    code, msg = cmd.execute(["Hello", "World"])
    assert code == 0
    assert "Hello World" in msg
    code, msg = cmd.execute([r"Line1\nLine2"])
    assert code == 0
    assert "Line1\nLine2" in msg


def test_echo_non_ascii_characters():
    cmd = utils.Echo()
    code, msg = cmd.execute([r"héllo 🚀\nworld"])
    assert code == 0
    assert "héllo 🚀\nworld" in msg


def test_clear_returns_escape_code():
    cmd = utils.Clear()
    code, msg = cmd.execute([])
    assert code == 0
    assert msg == "\033[H\033[2J"


def test_sleep_validations():
    cmd = utils.Sleep()
    code, msg = cmd.execute(["not_a_number"])
    assert code == 1
    assert "Invalid argument" in msg
    code, msg = cmd.execute([])
    assert code == 1


def test_history_limit_and_all_args():
    data.append_history("cmd1", "2026-01-01T00:00:00Z")
    data.append_history("cmd2", "2026-01-01T00:01:00Z")
    cmd = utils.History()
    code, msg = cmd.execute(["1"])
    assert code == 0
    assert "cmd2" in msg
    assert "cmd1" not in msg
    code, msg = cmd.execute(["all"])
    assert code == 0
    assert "cmd1" in msg
    assert "cmd2" in msg
