# tests/test_diskops_lgc.py

from flyshell.native import diskops_bridge as bridge
from flyshell.native import diskops_handler as handler
from flyshell.native.legacy import diskops as legacy

import pytest


@pytest.fixture(autouse=True)
def force_legacy_backend(monkeypatch):
    monkeypatch.setattr(bridge, "has_native_support", lambda: False)


def test_legacy_touch_creates_file_and_updates_timestamp(tmp_path):
    cmd = handler.Touch()
    target = tmp_path / "test.txt"
    code, msg = cmd.execute([str(target)])
    assert code == 0
    assert "touched successfully" in msg
    assert target.exists()
    code, msg = cmd.execute([str(target)])
    assert code == 0
    assert "touched successfully" in msg


def test_legacy_touch_missing_parent_directory(tmp_path):
    cmd = handler.Touch()
    target = tmp_path / "nonexistent_dir" / "test.txt"
    code, msg = cmd.execute([str(target)])
    assert code == 1
    assert "File or path not found" in msg


def test_legacy_touch_directory_error(tmp_path):
    code, _ = legacy.lgc_touch(tmp_path)
    assert code == -3  # ERR_IS_DIR
    cmd = handler.Touch()
    exit_code, msg = cmd.execute([str(tmp_path)])
    assert exit_code == 1
    assert "Target is a directory, not a file" in msg


def test_legacy_cat_reads_content_with_limit_and_numbers(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("line 1\nline 2\nline 3\nline 4\n", encoding="utf-8")
    cmd = handler.Cat()
    code, msg = cmd.execute([str(file_path)])
    assert code == 0
    assert "line 1" in msg and "line 4" in msg
    code, msg = cmd.execute(["-n", "-l", "2", str(file_path)])
    assert code == 0
    assert "1 | line 1" in msg
    assert "2 | line 2" in msg
    assert "line 3" not in msg


def test_legacy_cat_nonexistent_and_empty_file(tmp_path):
    cmd = handler.Cat()
    code, msg = cmd.execute([str(tmp_path / "missing.txt")])
    assert code == 1
    assert "File or path not found" in msg
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    code, msg = cmd.execute([str(empty_file)])
    assert code == 1
    assert "Target file is empty" in msg


def test_legacy_dir_lists_files_and_handles_errors(tmp_path):
    (tmp_path / "alpha_dir").mkdir()
    (tmp_path / "beta.txt").write_text("content", encoding="utf-8")
    cmd = handler.Dir()
    code, msg = cmd.execute([str(tmp_path)])
    assert code == 0
    assert "[DIR] alpha_dir/" in msg
    assert "[FILE] beta.txt" in msg
    assert "Total items in directory: 2" in msg
    code, msg = cmd.execute([str(tmp_path / "missing_dir")])
    assert code == 1
    assert "File or path not found" in msg
    code, msg = cmd.execute([str(tmp_path / "beta.txt")])
    assert code == 1
    assert "Target is not a directory" in msg
