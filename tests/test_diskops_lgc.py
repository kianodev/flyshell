# tests/test_diskops_lgc.py

from flyshell.native import diskops_bridge as bridge
from flyshell.native import diskops_handler as handler
from flyshell.native.legacy import diskops as legacy

import pytest


@pytest.fixture(autouse=True)
def force_legacy_backend(monkeypatch):
    monkeypatch.setattr(bridge, "has_native_support", lambda: False)


# --- mv ---


def test_legacy_mv_file(tmp_path):
    src_file = tmp_path / "lgc_move_src.txt"
    src_file.write_text("data", encoding="utf-8")
    dst_file = tmp_path / "lgc_move_dst.txt"
    exit_code, _ = handler.Move().execute([str(src_file), str(dst_file)])
    assert exit_code == 0
    assert not src_file.exists()
    assert dst_file.read_text(encoding="utf-8") == "data"


def test_legacy_mv_missing_source_returns_err_not_found(tmp_path):
    code, _ = legacy.lgc_mv(tmp_path / "ghost.txt", tmp_path / "out.txt", force=False)
    assert code == -1  # ERR_NOT_FOUND


# --- cp ---


def test_legacy_cp_file(tmp_path):
    src_file = tmp_path / "lgc_src.txt"
    src_file.write_text("payload", encoding="utf-8")
    dst_file = tmp_path / "lgc_dst.txt"
    exit_code, _ = handler.Copy().execute([str(src_file), str(dst_file)])
    assert exit_code == 0
    assert dst_file.read_text(encoding="utf-8") == "payload"


def test_legacy_cp_directory(tmp_path):
    src_dir = tmp_path / "lgc_tree"
    src_dir.mkdir()
    (src_dir / "item.txt").write_text("inner", encoding="utf-8")
    dst_dir = tmp_path / "lgc_tree_copy"
    exit_code, _ = handler.Copy().execute([str(src_dir), str(dst_dir)])
    assert exit_code == 0
    assert (dst_dir / "item.txt").read_text(encoding="utf-8") == "inner"


def test_legacy_cp_same_file_returns_err_same_file(tmp_path):
    src_file = tmp_path / "lgc_src.txt"
    src_file.write_text("payload", encoding="utf-8")
    code, _ = legacy.lgc_cp(src_file, src_file, force=True)
    assert code == -7  # ERR_SAME_FILE


# --- rm ---


def test_legacy_rm_file(tmp_path):
    target_file = tmp_path / "lgc_del.txt"
    target_file.write_text("bye", encoding="utf-8")
    exit_code, _ = handler.Rm().execute(["-f", str(target_file)])
    assert exit_code == 0
    assert not target_file.exists()


def test_legacy_rm_directory_without_recursive_returns_err_is_dir(tmp_path):
    target_dir = tmp_path / "lgc_dir"
    target_dir.mkdir()
    code, _ = legacy.lgc_rm(target_dir, recursive=False)
    assert code == -3  # ERR_IS_DIR


def test_legacy_rm_directory_recursive(tmp_path):
    target_dir = tmp_path / "lgc_dir"
    target_dir.mkdir()
    (target_dir / "a.txt").write_text("1", encoding="utf-8")
    exit_code, _ = handler.Rm().execute(["-f", "-r", str(target_dir)])
    assert exit_code == 0
    assert not target_dir.exists()


# --- rmdir ---


def test_legacy_rmdir_non_empty_without_force_fails(tmp_path):
    non_empty = tmp_path / "legacy_full"
    (non_empty / "child").mkdir(parents=True)
    (non_empty / "child" / "file.txt").write_text("abc", encoding="utf-8")
    exit_code, msg = handler.RmDir().execute([str(non_empty)])
    assert exit_code == 1
    assert "not empty" in msg


def test_legacy_rmdir_non_empty_with_force(tmp_path):
    non_empty = tmp_path / "legacy_full"
    (non_empty / "child").mkdir(parents=True)
    (non_empty / "child" / "file.txt").write_text("abc", encoding="utf-8")
    exit_code, _ = handler.RmDir().execute(["-f", str(non_empty)])
    assert exit_code == 0
    assert not non_empty.exists()


def test_legacy_rmdir_regular_file_returns_err_not_dir(tmp_path):
    regular_file = tmp_path / "file.txt"
    regular_file.write_text("x", encoding="utf-8")
    code, _ = legacy.lgc_rmdir(regular_file, force=False)
    assert code == -4  # ERR_NOT_DIR


# --- rename ---


def test_legacy_rename_file(tmp_path):
    src = tmp_path / "legacy_old.txt"
    src.write_text("hello", encoding="utf-8")
    exit_code, _ = handler.Rename().execute([str(src), "legacy_new.txt"])
    assert exit_code == 0
    assert not src.exists()
    assert (tmp_path / "legacy_new.txt").exists()


def test_legacy_rename_missing_source_returns_err_not_found(tmp_path):
    code, _ = legacy.lgc_rename(tmp_path / "missing.txt", tmp_path / "dst.txt")
    assert code == -1  # ERR_NOT_FOUND


# --- cat ---


def test_legacy_cat_reads_full_content(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("line 1\nline 2\nline 3\nline 4\n", encoding="utf-8")
    code, msg = handler.Cat().execute([str(file_path)])
    assert code == 0
    assert "line 1" in msg and "line 4" in msg


def test_legacy_cat_formats_line_numbers_and_limit(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("line 1\nline 2\nline 3\nline 4\n", encoding="utf-8")
    code, msg = handler.Cat().execute(["-n", "-l", "2", str(file_path)])
    assert code == 0
    assert "1 | line 1" in msg
    assert "2 | line 2" in msg
    assert "line 3" not in msg


def test_legacy_cat_missing_file_returns_error(tmp_path):
    code, msg = handler.Cat().execute([str(tmp_path / "missing.txt")])
    assert code == 1
    assert "File or path not found" in msg


def test_legacy_cat_empty_file_returns_error(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    code, msg = handler.Cat().execute([str(empty_file)])
    assert code == 1
    assert "Target file is empty" in msg


# --- dir ---


def test_legacy_dir_lists_entries(tmp_path):
    (tmp_path / "alpha_dir").mkdir()
    (tmp_path / "beta.txt").write_text("content", encoding="utf-8")
    code, msg = handler.Dir().execute([str(tmp_path)])
    assert code == 0
    assert "[DIR] alpha_dir/" in msg
    assert "[FILE] beta.txt" in msg
    assert "Total items in directory: 2" in msg


def test_legacy_dir_missing_path_returns_error(tmp_path):
    code, msg = handler.Dir().execute([str(tmp_path / "missing_dir")])
    assert code == 1
    assert "File or path not found" in msg


def test_legacy_dir_file_path_returns_not_a_directory(tmp_path):
    beta = tmp_path / "beta.txt"
    beta.write_text("content", encoding="utf-8")
    code, msg = handler.Dir().execute([str(beta)])
    assert code == 1
    assert "Target is not a directory" in msg


# --- mkdir ---


def test_legacy_mkdir_creates_directory(tmp_path):
    target = tmp_path / "legacy_folder"
    exit_code, msg = handler.MkDir().execute([str(target)])
    assert exit_code == 0
    assert "Created directory" in msg
    assert target.is_dir()


def test_legacy_mkdir_existing_directory_returns_error(tmp_path):
    target = tmp_path / "legacy_folder"
    target.mkdir()
    exit_code, msg = handler.MkDir().execute([str(target)])
    assert exit_code == 1
    assert "Item already exists" in msg


def test_legacy_mkdir_missing_parent_without_flag_fails(tmp_path):
    nested = tmp_path / "parent_dir" / "child_dir"
    exit_code, msg = handler.MkDir().execute([str(nested)])
    assert exit_code == 1
    assert "Parent directory does not exist" in msg


def test_legacy_mkdir_creates_parents_with_flag(tmp_path):
    nested = tmp_path / "parent_dir" / "child_dir"
    exit_code, _ = handler.MkDir().execute(["-p", str(nested)])
    assert exit_code == 0
    assert nested.is_dir()


def test_legacy_mkdir_file_as_parent_returns_err_not_dir(tmp_path):
    regular_file = tmp_path / "blocker.txt"
    regular_file.write_text("file", encoding="utf-8")
    code, _ = legacy.lgc_mkdir(regular_file / "sub", parents=True)
    assert code == -4  # ERR_NOT_DIR


def test_legacy_mkdir_missing_name_argument_returns_error():
    exit_code, msg = handler.MkDir().execute(["--parents"])
    assert exit_code == 1
    assert "Directory name not specified" in msg


# --- touch ---


def test_legacy_touch_creates_new_file(tmp_path):
    target = tmp_path / "test.txt"
    code, msg = handler.Touch().execute([str(target)])
    assert code == 0
    assert "touched successfully" in msg
    assert target.exists()


def test_legacy_touch_updates_existing_file(tmp_path):
    target = tmp_path / "test.txt"
    target.write_text("existing", encoding="utf-8")
    code, msg = handler.Touch().execute([str(target)])
    assert code == 0
    assert "touched successfully" in msg


def test_legacy_touch_missing_parent_directory_returns_error(tmp_path):
    target = tmp_path / "nonexistent_dir" / "test.txt"
    code, msg = handler.Touch().execute([str(target)])
    assert code == 1
    assert "File or path not found" in msg


def test_legacy_touch_directory_returns_err_is_dir(tmp_path):
    code, _ = legacy.lgc_touch(tmp_path)
    assert code == -3  # ERR_IS_DIR


def test_legacy_touch_directory_handler_message(tmp_path):
    exit_code, msg = handler.Touch().execute([str(tmp_path)])
    assert exit_code == 1
    assert "Target is a directory, not a file" in msg
