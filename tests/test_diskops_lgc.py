# tests/test_diskops_lgc.py

from flyshell.native import diskops_bridge as bridge
from flyshell.native import diskops_handler as handler
from flyshell.native.legacy import diskops as legacy

import pytest


@pytest.fixture(autouse=True)
def force_legacy_backend(monkeypatch):
    monkeypatch.setattr(bridge, "has_native_support", lambda: False)


def test_legacy_cp_file_and_directory(tmp_path):
    cmd = handler.Copy()
    src_file = tmp_path / "lgc_src.txt"
    src_file.write_text("payload", encoding="utf-8")
    dst_file = tmp_path / "lgc_dst.txt"
    exit_code, msg = cmd.execute([str(src_file), str(dst_file)])
    assert exit_code == 0
    assert dst_file.read_text(encoding="utf-8") == "payload"
    src_dir = tmp_path / "lgc_tree"
    src_dir.mkdir()
    (src_dir / "item.txt").write_text("inner", encoding="utf-8")
    dst_dir = tmp_path / "lgc_tree_copy"
    exit_code, msg = cmd.execute([str(src_dir), str(dst_dir)])
    assert exit_code == 0
    assert (dst_dir / "item.txt").read_text(encoding="utf-8") == "inner"
    code, _ = legacy.lgc_cp(src_file, src_file, force=True)
    assert code == -7  # ERR_SAME_FILE


def test_legacy_rm_file_and_recursive_dir(tmp_path):
    cmd = handler.Rm()
    target_file = tmp_path / "lgc_del.txt"
    target_file.write_text("bye", encoding="utf-8")
    exit_code, msg = cmd.execute(["-f", str(target_file)])
    assert exit_code == 0
    assert not target_file.exists()
    target_dir = tmp_path / "lgc_dir"
    target_dir.mkdir()
    (target_dir / "a.txt").write_text("1", encoding="utf-8")
    code, _ = legacy.lgc_rm(target_dir, recursive=False)
    assert code == -3  # ERR_IS_DIR
    exit_code, msg = cmd.execute(["-f", "-r", str(target_dir)])
    assert exit_code == 0
    assert not target_dir.exists()


def test_legacy_rmdir_empty_and_force(tmp_path):
    cmd = handler.RmDir()
    non_empty = tmp_path / "legacy_full"
    (non_empty / "child").mkdir(parents=True)
    (non_empty / "child" / "file.txt").write_text("abc", encoding="utf-8")
    exit_code, msg = cmd.execute([str(non_empty)])
    assert exit_code == 1
    assert "not empty" in msg
    exit_code, msg = cmd.execute(["-f", str(non_empty)])
    assert exit_code == 0
    assert not non_empty.exists()
    regular_file = tmp_path / "file.txt"
    regular_file.write_text("x", encoding="utf-8")
    code, _ = legacy.lgc_rmdir(regular_file, force=False)
    assert code == -4  # ERR_NOT_DIR


def test_legacy_rename_file_and_errors(tmp_path):
    src = tmp_path / "legacy_old.txt"
    src.write_text("hello", encoding="utf-8")
    cmd = handler.Rename()
    exit_code, msg = cmd.execute([str(src), "legacy_new.txt"])
    assert exit_code == 0
    assert not src.exists()
    assert (tmp_path / "legacy_new.txt").exists()
    code, _ = legacy.lgc_rename(tmp_path / "missing.txt", tmp_path / "dst.txt")
    assert code == -1  # ERR_NOT_FOUND


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


def test_legacy_mkdir_creates_and_handles_parents(tmp_path):
    cmd = handler.MkDir()
    target = tmp_path / "legacy_folder"
    exit_code, msg = cmd.execute([str(target)])
    assert exit_code == 0
    assert "Created directory" in msg
    assert target.is_dir()
    exit_code, msg = cmd.execute([str(target)])
    assert exit_code == 1
    assert "Item already exists" in msg
    nested = tmp_path / "parent_dir" / "child_dir"
    exit_code, msg = cmd.execute([str(nested)])
    assert exit_code == 1
    assert "Parent directory does not exist" in msg
    exit_code, msg = cmd.execute(["-p", str(nested)])
    assert exit_code == 0
    assert nested.is_dir()


def test_legacy_mkdir_errors(tmp_path):
    regular_file = tmp_path / "blocker.txt"
    regular_file.write_text("file", encoding="utf-8")
    code, _ = legacy.lgc_mkdir(regular_file / "sub", parents=True)
    assert code == -4  # ERR_NOT_DIR
    cmd = handler.MkDir()
    exit_code, msg = cmd.execute(["--parents"])
    assert exit_code == 1
    assert "Directory name not specified" in msg


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
