# tests\test_utils.py

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


def test_history_limit_and_all_args(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(
        data,
        "get_history",
        lambda limit=None, filename=test_db: (
            data.get_history.__wrapped__(limit=limit, filename=test_db)
            if hasattr(data.get_history, "__wrapped__")
            else [
                entry
                for entry in (
                    lambda conn: [
                        {"command": r[0], "timestamp": r[1]}
                        for r in conn.execute(
                            "SELECT command, timestamp FROM cmd_history ORDER BY id DESC LIMIT ?"
                            if limit and limit > 0
                            else "SELECT command, timestamp FROM cmd_history ORDER BY id ASC",
                            (limit,) if limit and limit > 0 else (),
                        ).fetchall()
                    ]
                )(data._get_connection(test_db))
            ][::-1] if limit and limit > 0 else [
                {"command": r[0], "timestamp": r[1]}
                for r in data._get_connection(test_db).execute(
                    "SELECT command, timestamp FROM cmd_history ORDER BY id ASC"
                ).fetchall()
            ]
        ),
    )
    data.append_history("cmd1", "2026-01-01T00:00:00Z", filename=test_db)
    data.append_history("cmd2", "2026-01-01T00:01:00Z", filename=test_db)
    cmd = utils.History()
    code, msg = cmd.execute(["1"])
    assert code == 0
    assert "cmd2" in msg
    assert "cmd1" not in msg
    code, msg = cmd.execute(["all"])
    assert code == 0
    assert "cmd1" in msg
    assert "cmd2" in msg