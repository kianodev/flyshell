# tests\test_directory.py

from flyshell.core import directory

def test_parse_simple_command():
    chain = directory._parse_commands("clear")
    assert chain == [("clear", None)]

def test_parse_semicolon_chain():
    chain = directory._parse_commands("clear ; history")
    assert chain == [("clear", ";"), ("history", None)]

def test_parse_and_chain():
    chain = directory._parse_commands("cd mydir && dir")
    assert chain == [("cd mydir", "&&"), ("dir", None)]

def test_parse_or_chain():
    chain = directory._parse_commands("open missing.txt || echo fallback")
    assert chain == [("open missing.txt", "||"), ("echo fallback", None)]

def test_parse_preserves_operators_inside_quotes():
    chain = directory._parse_commands('echo "hello ; world && test"')
    assert len(chain) == 1
    assert chain[0] == ('echo "hello ; world && test"', None)

def test_parse_unclosed_quote_returns_empty():
    chain = directory._parse_commands('echo "unterminated quote')
    assert chain == []

def test_parse_empty_input():
    assert directory._parse_commands("") == []
    assert directory._parse_commands("   ") == []

def test_execute_line_short_circuits_on_and(monkeypatch):
    executed = []
    def mock_execute_single(raw_cmd):
        executed.append(raw_cmd)
        return 1 if raw_cmd == "fail" else 0
    monkeypatch.setattr(directory, "_execute_single", mock_execute_single)
    directory.execute_line("fail && success")
    assert executed == ["fail"]

def test_execute_line_short_circuits_on_or(monkeypatch):
    executed = []
    def mock_execute_single(raw_cmd):
        executed.append(raw_cmd)
        return 0
    monkeypatch.setattr(directory, "_execute_single", mock_execute_single)
    directory.execute_line("first || second")
    assert executed == ["first"]