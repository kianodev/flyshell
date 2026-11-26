# tests/test_utils.py

from flyshell import data
from flyshell.builtin import utils


def test_echo_joins_arguments_with_spaces():
    code, msg = utils.Echo().execute(["Hello", "World"])
    assert code == 0
    assert "Hello World" in msg


def test_echo_decodes_escape_sequences():
    code, msg = utils.Echo().execute([r"Line1\nLine2"])
    assert code == 0
    assert "Line1\nLine2" in msg


def test_echo_preserves_non_ascii_characters():
    code, msg = utils.Echo().execute([r"héllo 🚀\nworld"])
    assert code == 0
    assert "héllo 🚀\nworld" in msg


def test_clear_returns_escape_code():
    code, msg = utils.Clear().execute([])
    assert code == 0
    assert msg == "\033[H\033[2J"


def test_sleep_rejects_non_numeric_argument():
    code, msg = utils.Sleep().execute(["not_a_number"])
    assert code == 1
    assert "Invalid argument" in msg


def test_sleep_rejects_missing_argument():
    code, _ = utils.Sleep().execute([])
    assert code == 1


def test_history_with_numeric_limit():
    data.append_history("cmd1", "2026-01-01T00:00:00Z")
    data.append_history("cmd2", "2026-01-01T00:01:00Z")
    code, msg = utils.History().execute(["1"])
    assert code == 0
    assert "cmd2" in msg
    assert "cmd1" not in msg


def test_history_with_all_argument():
    data.append_history("cmd1", "2026-01-01T00:00:00Z")
    data.append_history("cmd2", "2026-01-01T00:01:00Z")
    code, msg = utils.History().execute(["all"])
    assert code == 0
    assert "cmd1" in msg
    assert "cmd2" in msg
