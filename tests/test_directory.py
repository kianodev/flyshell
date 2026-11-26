# tests/test_directory.py

from flyshell.core import directory


def test_parse_simple_command():
    assert directory._parse_commands("clear") == [(None, "clear")]


def test_parse_semicolon_chain():
    assert directory._parse_commands("clear ; history") == [
        (None, "clear"),
        (";", "history"),
    ]


def test_parse_and_chain():
    assert directory._parse_commands("cd mydir && dir") == [
        (None, "cd mydir"),
        ("&&", "dir"),
    ]


def test_parse_or_chain():
    assert directory._parse_commands("open missing.txt || echo fallback") == [
        (None, "open missing.txt"),
        ("||", "echo fallback"),
    ]


def test_parse_preserves_operators_inside_quotes():
    assert directory._parse_commands('echo "hello ; world && test"') == [
        (None, 'echo "hello ; world && test"')
    ]


def test_parse_unclosed_quote_returns_empty():
    assert directory._parse_commands('echo "unterminated quote') == []


def test_parse_empty_string():
    assert directory._parse_commands("") == []


def test_parse_whitespace_only():
    assert directory._parse_commands("   ") == []


def test_execute_line_runs_both_on_semicolon(monkeypatch):
    executed = []

    def mock_execute_single(raw_cmd):
        executed.append(raw_cmd)
        return 1

    monkeypatch.setattr(directory, "_execute_single", mock_execute_single)
    directory.execute_line("fail ; second")
    assert executed == ["fail", "second"]


def test_execute_line_runs_second_when_and_succeeds(monkeypatch):
    executed = []

    def mock_execute_single(raw_cmd):
        executed.append(raw_cmd)
        return 0

    monkeypatch.setattr(directory, "_execute_single", mock_execute_single)
    directory.execute_line("ok && second")
    assert executed == ["ok", "second"]


def test_execute_line_short_circuits_on_and_failure(monkeypatch):
    executed = []

    def mock_execute_single(raw_cmd):
        executed.append(raw_cmd)
        return 1

    monkeypatch.setattr(directory, "_execute_single", mock_execute_single)
    directory.execute_line("fail && success")
    assert executed == ["fail"]


def test_execute_line_short_circuits_on_or_success(monkeypatch):
    executed = []

    def mock_execute_single(raw_cmd):
        executed.append(raw_cmd)
        return 0

    monkeypatch.setattr(directory, "_execute_single", mock_execute_single)
    directory.execute_line("first || second")
    assert executed == ["first"]


def test_execute_line_chaining_cascades(monkeypatch):
    executed = []

    def mock_execute_single(raw_cmd):
        executed.append(raw_cmd)
        return 0 if raw_cmd == "ok" else 1

    monkeypatch.setattr(directory, "_execute_single", mock_execute_single)
    directory.execute_line("ok || fallback && never_run")
    assert executed == ["ok"]
