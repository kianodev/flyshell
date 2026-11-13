# tests/test_diskops_ext.py

from flyshell.native import diskops_bridge as bridge
from flyshell.native import diskops_handler as handler
import flyshell


def test_native_extension_loaded():
    assert flyshell.check_native() is True
    assert bridge.has_native_support() is True
    assert bridge._native.ping() == 42


def test_native_touch_creates_and_updates_file(tmp_path):
    target = tmp_path / "native_touch.txt"
    code, _ = bridge._native.touch(str(target))
    assert code == 0
    assert target.exists()
    cmd = handler.Touch()
    exit_code, msg = cmd.execute([str(target)])
    assert exit_code == 0
    assert "touched successfully" in msg


def test_native_touch_errors(tmp_path):
    missing_parent = tmp_path / "no_such_dir" / "file.txt"
    code, _ = bridge._native.touch(str(missing_parent))
    assert code == -1
    cmd = handler.Touch()
    exit_code, msg = cmd.execute([str(tmp_path)])
    assert exit_code == 1
    assert "Target is a directory, not a file" in msg


def test_native_cat_reads_and_formats_content(tmp_path):
    file_path = tmp_path / "native_cat.txt"
    file_path.write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8")
    code, raw_content = bridge._native.cat(str(file_path))
    assert code == 0
    assert "alpha" in raw_content and "delta" in raw_content
    cmd = handler.Cat()
    exit_code, msg = cmd.execute(["-n", "-l", "2", str(file_path)])
    assert exit_code == 0
    assert "1 | alpha" in msg
    assert "2 | beta" in msg
    assert "gamma" not in msg


def test_native_cat_errors(tmp_path):
    cmd = handler.Cat()
    exit_code, msg = cmd.execute([str(tmp_path / "missing.txt")])
    assert exit_code == 1
    assert "File or path not found" in msg
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    code, _ = bridge._native.cat(str(empty_file))
    assert code == -8
    exit_code, msg = cmd.execute([str(empty_file)])
    assert exit_code == 1
    assert "Target file is empty" in msg


def test_native_dir_lists_entries_and_handles_errors(tmp_path):
    (tmp_path / "folder_a").mkdir()
    (tmp_path / "file_b.txt").write_text("hello", encoding="utf-8")
    code, items = bridge._native.dir(str(tmp_path))
    assert code == 0
    assert ("folder_a", True) in items
    assert ("file_b.txt", False) in items
    cmd = handler.Dir()
    exit_code, msg = cmd.execute([str(tmp_path)])
    assert exit_code == 0
    assert "[DIR] folder_a/" in msg
    assert "[FILE] file_b.txt" in msg
    assert "Total items in directory: 2" in msg
    exit_code, msg = cmd.execute([str(tmp_path / "does_not_exist")])
    assert exit_code == 1
    assert "File or path not found" in msg
