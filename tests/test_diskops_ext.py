# tests/test_diskops_ext.py

from flyshell.native import diskops_bridge as bridge
from flyshell.native import diskops_handler as handler
import flyshell


def test_native_extension_loaded():
    assert flyshell.check_native() is True


def test_native_bridge_reports_support():
    assert bridge.has_native_support() is True


def test_native_ping_returns_magic_number():
    assert bridge._native.ping() == 42


# --- mv ---


def test_native_mv_file(tmp_path):
    src_file = tmp_path / "move_src.txt"
    src_file.write_text("relocate me", encoding="utf-8")
    dst_file = tmp_path / "move_dst.txt"
    exit_code, msg = handler.Move().execute([str(src_file), str(dst_file)])
    assert exit_code == 0
    assert "Moved" in msg
    assert not src_file.exists()
    assert dst_file.read_text(encoding="utf-8") == "relocate me"


def test_native_mv_file_force_overwrites(tmp_path):
    dst_file = tmp_path / "move_dst.txt"
    dst_file.write_text("original", encoding="utf-8")
    replacement = tmp_path / "new_src.txt"
    replacement.write_text("overwritten", encoding="utf-8")
    exit_code, _ = handler.Move().execute(["-f", str(replacement), str(dst_file)])
    assert exit_code == 0
    assert not replacement.exists()
    assert dst_file.read_text(encoding="utf-8") == "overwritten"


def test_native_mv_directory_into_parent(tmp_path):
    src_dir = tmp_path / "dir_to_move"
    src_dir.mkdir()
    (src_dir / "item.txt").write_text("inside", encoding="utf-8")
    target_parent = tmp_path / "dest_holder"
    target_parent.mkdir()
    exit_code, _ = handler.Move().execute([str(src_dir), str(target_parent)])
    assert exit_code == 0
    assert not src_dir.exists()
    assert (target_parent / "dir_to_move" / "item.txt").read_text(
        encoding="utf-8"
    ) == "inside"


def test_native_mv_missing_source_returns_error(tmp_path):
    exit_code, msg = handler.Move().execute(
        [str(tmp_path / "missing.txt"), str(tmp_path / "out.txt")]
    )
    assert exit_code == 1
    assert "not found" in msg


def test_native_mv_existing_destination_without_force_returns_err_exists(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("1", encoding="utf-8")
    b.write_text("2", encoding="utf-8")
    code, _ = bridge._native.mv(str(a), str(b), False)
    assert code == -5  # ERR_EXISTS


# --- cp ---


def test_native_cp_file(tmp_path):
    src_file = tmp_path / "src.txt"
    src_file.write_text("hello copy", encoding="utf-8")
    dst_file = tmp_path / "dst.txt"
    exit_code, msg = handler.Copy().execute([str(src_file), str(dst_file)])
    assert exit_code == 0
    assert "Copied file" in msg
    assert dst_file.read_text(encoding="utf-8") == "hello copy"


def test_native_cp_file_force_overwrites(tmp_path):
    src_file = tmp_path / "src.txt"
    src_file.write_text("updated payload", encoding="utf-8")
    dst_file = tmp_path / "dst.txt"
    dst_file.write_text("old payload", encoding="utf-8")
    exit_code, _ = handler.Copy().execute(["-f", str(src_file), str(dst_file)])
    assert exit_code == 0
    assert dst_file.read_text(encoding="utf-8") == "updated payload"


def test_native_cp_directory_recursive(tmp_path):
    src_dir = tmp_path / "tree_src"
    (src_dir / "nested").mkdir(parents=True)
    (src_dir / "nested" / "leaf.txt").write_text("leaf", encoding="utf-8")
    dst_dir = tmp_path / "tree_dst"
    exit_code, msg = handler.Copy().execute([str(src_dir), str(dst_dir)])
    assert exit_code == 0
    assert "Copied directory" in msg
    assert (dst_dir / "nested" / "leaf.txt").read_text(encoding="utf-8") == "leaf"


def test_native_cp_missing_source_returns_error(tmp_path):
    exit_code, msg = handler.Copy().execute(
        [str(tmp_path / "missing.txt"), str(tmp_path / "out.txt")]
    )
    assert exit_code == 1
    assert "not found" in msg


def test_native_cp_same_file_returns_err_same_file(tmp_path):
    f1 = tmp_path / "same.txt"
    f1.write_text("abc", encoding="utf-8")
    code, _ = bridge._native.cp(str(f1), str(f1), True)
    assert code == -7  # ERR_SAME_FILE


def test_native_cp_existing_destination_without_force_returns_err_exists(tmp_path):
    f1 = tmp_path / "same.txt"
    f2 = tmp_path / "other.txt"
    f1.write_text("abc", encoding="utf-8")
    f2.write_text("def", encoding="utf-8")
    code, _ = bridge._native.cp(str(f1), str(f2), False)
    assert code == -5  # ERR_EXISTS


# --- rm ---


def test_native_rm_file(tmp_path):
    target_file = tmp_path / "delete_me.txt"
    target_file.write_text("bye", encoding="utf-8")
    exit_code, msg = handler.Rm().execute(["-f", str(target_file)])
    assert exit_code == 0
    assert "Deleted file" in msg
    assert not target_file.exists()


def test_native_rm_directory_without_recursive_fails(tmp_path):
    target_dir = tmp_path / "sub_tree"
    target_dir.mkdir()
    exit_code, msg = handler.Rm().execute(["-f", str(target_dir)])
    assert exit_code == 1
    assert "is a directory" in msg
    assert target_dir.exists()


def test_native_rm_directory_recursive(tmp_path):
    target_dir = tmp_path / "sub_tree"
    (target_dir / "nested").mkdir(parents=True)
    (target_dir / "nested" / "file.txt").write_text("x", encoding="utf-8")
    exit_code, msg = handler.Rm().execute(["-f", "-r", str(target_dir)])
    assert exit_code == 0
    assert "Deleted directory" in msg
    assert not target_dir.exists()


def test_native_rm_missing_target_returns_error(tmp_path):
    exit_code, msg = handler.Rm().execute(["-f", str(tmp_path / "missing.txt")])
    assert exit_code == 1
    assert "not found" in msg


def test_native_rm_direct_dir_without_recursive_returns_err_is_dir(tmp_path):
    sub_dir = tmp_path / "dir_only"
    sub_dir.mkdir()
    code, _ = bridge._native.rm(str(sub_dir), False)
    assert code == -3  # ERR_IS_DIR


# --- rmdir ---


def test_native_rmdir_empty_directory(tmp_path):
    empty_dir = tmp_path / "empty_folder"
    empty_dir.mkdir()
    exit_code, msg = handler.RmDir().execute([str(empty_dir)])
    assert exit_code == 0
    assert "Removed directory" in msg
    assert not empty_dir.exists()


def test_native_rmdir_non_empty_without_force_fails(tmp_path):
    non_empty = tmp_path / "full_folder"
    nested = non_empty / "sub_folder"
    nested.mkdir(parents=True)
    (nested / "item.txt").write_text("data", encoding="utf-8")
    exit_code, msg = handler.RmDir().execute([str(non_empty)])
    assert exit_code == 1
    assert "not empty" in msg
    assert non_empty.exists()


def test_native_rmdir_non_empty_with_force(tmp_path):
    non_empty = tmp_path / "full_folder"
    nested = non_empty / "sub_folder"
    nested.mkdir(parents=True)
    (nested / "item.txt").write_text("data", encoding="utf-8")
    exit_code, _ = handler.RmDir().execute(["-f", str(non_empty)])
    assert exit_code == 0
    assert not non_empty.exists()


def test_native_rmdir_regular_file_returns_err_not_dir(tmp_path):
    regular_file = tmp_path / "not_a_dir.txt"
    regular_file.write_text("hello", encoding="utf-8")
    code, _ = bridge._native.rmdir(str(regular_file), False)
    assert code == -4  # ERR_NOT_DIR


def test_native_rmdir_missing_directory_returns_error(tmp_path):
    exit_code, msg = handler.RmDir().execute([str(tmp_path / "missing_folder")])
    assert exit_code == 1
    assert "not found" in msg


# --- cat ---


def test_native_cat_reads_raw_content(tmp_path):
    file_path = tmp_path / "native_cat.txt"
    file_path.write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8", newline="\n")
    code, raw_content = bridge._native.cat(str(file_path))
    assert code == 0
    assert raw_content == "alpha\nbeta\ngamma\ndelta\n"


def test_native_cat_formats_line_numbers_and_limit(tmp_path):
    file_path = tmp_path / "native_cat.txt"
    file_path.write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8")
    exit_code, msg = handler.Cat().execute(["-n", "-l", "2", str(file_path)])
    assert exit_code == 0
    assert "1 | alpha" in msg
    assert "2 | beta" in msg
    assert "gamma" not in msg


def test_native_cat_missing_file_returns_error(tmp_path):
    exit_code, msg = handler.Cat().execute([str(tmp_path / "missing.txt")])
    assert exit_code == 1
    assert "File or path not found" in msg


def test_native_cat_empty_file_returns_err_empty(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    code, _ = bridge._native.cat(str(empty_file))
    assert code == -8


def test_native_cat_empty_file_handler_message(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    exit_code, msg = handler.Cat().execute([str(empty_file)])
    assert exit_code == 1
    assert "Target file is empty" in msg


# --- dir ---


def test_native_dir_returns_raw_entries(tmp_path):
    (tmp_path / "folder_a").mkdir()
    (tmp_path / "file_b.txt").write_text("hello", encoding="utf-8")
    code, items = bridge._native.dir(str(tmp_path))
    assert code == 0
    assert ("folder_a", True) in items
    assert ("file_b.txt", False) in items


def test_native_dir_formats_directory_listing(tmp_path):
    (tmp_path / "folder_a").mkdir()
    (tmp_path / "file_b.txt").write_text("hello", encoding="utf-8")
    exit_code, msg = handler.Dir().execute([str(tmp_path)])
    assert exit_code == 0
    assert "[DIR] folder_a/" in msg
    assert "[FILE] file_b.txt" in msg
    assert "Total items in directory: 2" in msg


def test_native_dir_missing_path_returns_error(tmp_path):
    exit_code, msg = handler.Dir().execute([str(tmp_path / "does_not_exist")])
    assert exit_code == 1
    assert "File or path not found" in msg


def test_native_dir_file_path_returns_not_a_directory(tmp_path):
    file_b = tmp_path / "file_b.txt"
    file_b.write_text("hello", encoding="utf-8")
    exit_code, msg = handler.Dir().execute([str(file_b)])
    assert exit_code == 1
    assert "Target is not a directory" in msg


# --- mkdir ---


def test_native_mkdir_creates_directory(tmp_path):
    target = tmp_path / "native_folder"
    code, _ = bridge._native.mkdir(str(target), False)
    assert code == 0
    assert target.is_dir()


def test_native_mkdir_existing_directory_returns_error(tmp_path):
    target = tmp_path / "native_folder"
    target.mkdir()
    exit_code, msg = handler.MkDir().execute([str(target)])
    assert exit_code == 1
    assert "Item already exists" in msg


def test_native_mkdir_missing_parent_without_flag_fails(tmp_path):
    nested = tmp_path / "parent_dir" / "child_dir" / "leaf_dir"
    exit_code, msg = handler.MkDir().execute([str(nested)])
    assert exit_code == 1
    assert "Parent directory does not exist" in msg


def test_native_mkdir_creates_parents_with_short_flag(tmp_path):
    nested = tmp_path / "parent_dir" / "child_dir" / "leaf_dir"
    exit_code, msg = handler.MkDir().execute(["-p", str(nested)])
    assert exit_code == 0
    assert "Created directory" in msg
    assert nested.is_dir()


def test_native_mkdir_parents_flag_is_idempotent(tmp_path):
    nested = tmp_path / "parent_dir" / "child_dir"
    nested.mkdir(parents=True)
    exit_code, _ = handler.MkDir().execute(["--parents", str(nested)])
    assert exit_code == 0


def test_native_mkdir_file_as_parent_returns_err_not_dir(tmp_path):
    regular_file = tmp_path / "blocker.txt"
    regular_file.write_text("file", encoding="utf-8")
    code, _ = bridge._native.mkdir(str(regular_file / "sub"), True)
    assert code == -4


def test_native_mkdir_missing_name_argument_returns_error():
    exit_code, msg = handler.MkDir().execute(["-p"])
    assert exit_code == 1
    assert "Directory name not specified" in msg


# --- touch ---


def test_native_touch_creates_new_file(tmp_path):
    target = tmp_path / "native_touch.txt"
    code, _ = bridge._native.touch(str(target))
    assert code == 0
    assert target.exists()


def test_native_touch_updates_existing_file(tmp_path):
    target = tmp_path / "native_touch.txt"
    target.write_text("existing", encoding="utf-8")
    exit_code, msg = handler.Touch().execute([str(target)])
    assert exit_code == 0
    assert "touched successfully" in msg


def test_native_touch_missing_parent_returns_err_not_found(tmp_path):
    missing_parent = tmp_path / "no_such_dir" / "file.txt"
    code, _ = bridge._native.touch(str(missing_parent))
    assert code == -1


def test_native_touch_directory_returns_error(tmp_path):
    exit_code, msg = handler.Touch().execute([str(tmp_path)])
    assert exit_code == 1
    assert "Target is a directory, not a file" in msg


# --- rename ---


def test_native_rename_file(tmp_path):
    src = tmp_path / "old_name.txt"
    src.write_text("payload", encoding="utf-8")
    exit_code, msg = handler.Rename().execute([str(src), "new_name.txt"])
    assert exit_code == 0
    assert "Renamed 'old_name.txt' -> 'new_name.txt'" in msg
    assert not src.exists()
    assert (tmp_path / "new_name.txt").read_text(encoding="utf-8") == "payload"


def test_native_rename_directory(tmp_path):
    src_dir = tmp_path / "old_dir"
    src_dir.mkdir()
    exit_code, _ = handler.Rename().execute([str(src_dir), "new_dir"])
    assert exit_code == 0
    assert not src_dir.exists()
    assert (tmp_path / "new_dir").is_dir()


def test_native_rename_missing_source_returns_error(tmp_path):
    exit_code, msg = handler.Rename().execute(
        [str(tmp_path / "ghost.txt"), "other.txt"]
    )
    assert exit_code == 1
    assert "not found" in msg


def test_native_rename_existing_target_returns_err_exists(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("1", encoding="utf-8")
    b.write_text("2", encoding="utf-8")
    code, _ = bridge._native.rename(str(a), str(b))
    assert code == -5  # ERR_EXISTS


def test_native_rename_rejects_path_traversal_name(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("1", encoding="utf-8")
    exit_code, msg = handler.Rename().execute([str(a), "../escape.txt"])
    assert exit_code == 1
    assert "Invalid file name" in msg


# --- unicode ---


def test_native_unicode_mkdir_and_dir(tmp_path):
    unicode_dir = tmp_path / "dir_日本語"
    assert bridge._native.mkdir(str(unicode_dir), False)[0] == 0
    assert unicode_dir.is_dir()
    code, items = bridge._native.dir(str(tmp_path))
    assert code == 0
    assert ("dir_日本語", True) in items


def test_native_unicode_touch_and_cat(tmp_path):
    unicode_file = tmp_path / "café_🚀.txt"
    assert bridge._native.touch(str(unicode_file))[0] == 0
    unicode_file.write_text("héllo 🌍\n", encoding="utf-8", newline="\n")
    code, content = bridge._native.cat(str(unicode_file))
    assert code == 0
    assert content == "héllo 🌍\n"
