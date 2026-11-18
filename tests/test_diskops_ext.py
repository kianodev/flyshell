# tests/test_diskops_ext.py

from flyshell.native import diskops_bridge as bridge
from flyshell.native import diskops_handler as handler
import flyshell


def test_native_extension_loaded():
    assert flyshell.check_native() is True
    assert bridge.has_native_support() is True
    assert bridge._native.ping() == 42


def test_native_cp_file_and_directory(tmp_path):
    cmd = handler.Copy()
    src_file = tmp_path / "src.txt"
    src_file.write_text("hello copy", encoding="utf-8")
    dst_file = tmp_path / "dst.txt"
    exit_code, msg = cmd.execute([str(src_file), str(dst_file)])
    assert exit_code == 0
    assert "Copied file" in msg
    assert dst_file.read_text(encoding="utf-8") == "hello copy"
    src_file.write_text("updated payload", encoding="utf-8")
    exit_code, msg = cmd.execute(["-f", str(src_file), str(dst_file)])
    assert exit_code == 0
    assert dst_file.read_text(encoding="utf-8") == "updated payload"
    src_dir = tmp_path / "tree_src"
    (src_dir / "nested").mkdir(parents=True)
    (src_dir / "nested" / "leaf.txt").write_text("leaf", encoding="utf-8")
    dst_dir = tmp_path / "tree_dst"
    exit_code, msg = cmd.execute([str(src_dir), str(dst_dir)])
    assert exit_code == 0
    assert "Copied directory" in msg
    assert (dst_dir / "nested" / "leaf.txt").read_text(encoding="utf-8") == "leaf"


def test_native_cp_errors(tmp_path):
    cmd = handler.Copy()
    exit_code, msg = cmd.execute(
        [str(tmp_path / "missing.txt"), str(tmp_path / "out.txt")]
    )
    assert exit_code == 1
    assert "not found" in msg
    f1 = tmp_path / "same.txt"
    f1.write_text("abc", encoding="utf-8")
    code, _ = bridge._native.cp(str(f1), str(f1), True)
    assert code == -7  # ERR_SAME_FILE
    f2 = tmp_path / "other.txt"
    f2.write_text("def", encoding="utf-8")
    code, _ = bridge._native.cp(str(f1), str(f2), False)
    assert code == -5  # ERR_EXISTS


def test_native_rm_file_and_recursive_dir(tmp_path):
    cmd = handler.Rm()
    target_file = tmp_path / "delete_me.txt"
    target_file.write_text("bye", encoding="utf-8")
    exit_code, msg = cmd.execute(["-f", str(target_file)])
    assert exit_code == 0
    assert "Deleted file" in msg
    assert not target_file.exists()
    target_dir = tmp_path / "sub_tree"
    (target_dir / "nested").mkdir(parents=True)
    (target_dir / "nested" / "file.txt").write_text("x", encoding="utf-8")
    exit_code, msg = cmd.execute(["-f", str(target_dir)])
    assert exit_code == 1
    assert "is a directory" in msg
    assert target_dir.exists()
    exit_code, msg = cmd.execute(["-f", "-r", str(target_dir)])
    assert exit_code == 0
    assert "Deleted directory" in msg
    assert not target_dir.exists()


def test_native_rm_errors(tmp_path):
    cmd = handler.Rm()
    exit_code, msg = cmd.execute(["-f", str(tmp_path / "missing.txt")])
    assert exit_code == 1
    assert "not found" in msg
    sub_dir = tmp_path / "dir_only"
    sub_dir.mkdir()
    code, _ = bridge._native.rm(str(sub_dir), False)
    assert code == -3  # ERR_IS_DIR


def test_native_rmdir_empty_and_force(tmp_path):
    cmd = handler.RmDir()
    empty_dir = tmp_path / "empty_folder"
    empty_dir.mkdir()
    exit_code, msg = cmd.execute([str(empty_dir)])
    assert exit_code == 0
    assert "Removed directory" in msg
    assert not empty_dir.exists()
    non_empty = tmp_path / "full_folder"
    nested = non_empty / "sub_folder"
    nested.mkdir(parents=True)
    (nested / "item.txt").write_text("data", encoding="utf-8")
    exit_code, msg = cmd.execute([str(non_empty)])
    assert exit_code == 1
    assert "not empty" in msg
    assert non_empty.exists()
    exit_code, msg = cmd.execute(["-f", str(non_empty)])
    assert exit_code == 0
    assert not non_empty.exists()


def test_native_rmdir_errors(tmp_path):
    regular_file = tmp_path / "not_a_dir.txt"
    regular_file.write_text("hello", encoding="utf-8")
    code, _ = bridge._native.rmdir(str(regular_file), False)
    assert code == -4  # ERR_NOT_DIR
    cmd = handler.RmDir()
    exit_code, msg = cmd.execute([str(tmp_path / "missing_folder")])
    assert exit_code == 1
    assert "not found" in msg


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
    file_b = tmp_path / "file_b.txt"
    file_b.write_text("hello", encoding="utf-8")
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
    exit_code, msg = cmd.execute([str(file_b)])
    assert exit_code == 1
    assert "Target is not a directory" in msg


def test_native_mkdir_creates_and_handles_parents(tmp_path):
    cmd = handler.MkDir()
    target = tmp_path / "native_folder"
    code, _ = bridge._native.mkdir(str(target), False)
    assert code == 0
    assert target.is_dir()
    exit_code, msg = cmd.execute([str(target)])
    assert exit_code == 1
    assert "Item already exists" in msg
    nested = tmp_path / "parent_dir" / "child_dir" / "leaf_dir"
    exit_code, msg = cmd.execute([str(nested)])
    assert exit_code == 1
    assert "Parent directory does not exist" in msg
    exit_code, msg = cmd.execute(["-p", str(nested)])
    assert exit_code == 0
    assert "Created directory" in msg
    assert nested.is_dir()
    exit_code, msg = cmd.execute(["--parents", str(nested)])
    assert exit_code == 0


def test_native_mkdir_errors(tmp_path):
    regular_file = tmp_path / "blocker.txt"
    regular_file.write_text("file", encoding="utf-8")
    code, _ = bridge._native.mkdir(str(regular_file / "sub"), True)
    assert code == -4
    cmd = handler.MkDir()
    exit_code, msg = cmd.execute(["-p"])
    assert exit_code == 1
    assert "Directory name not specified" in msg


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


def test_native_rename_file_and_directory(tmp_path):
    src = tmp_path / "old_name.txt"
    src.write_text("payload", encoding="utf-8")
    cmd = handler.Rename()
    exit_code, msg = cmd.execute([str(src), "new_name.txt"])
    assert exit_code == 0
    assert "Renamed 'old_name.txt' -> 'new_name.txt'" in msg
    assert not src.exists()
    assert (tmp_path / "new_name.txt").read_text(encoding="utf-8") == "payload"
    src_dir = tmp_path / "old_dir"
    src_dir.mkdir()
    exit_code, msg = cmd.execute([str(src_dir), "new_dir"])
    assert exit_code == 0
    assert not src_dir.exists()
    assert (tmp_path / "new_dir").is_dir()


def test_native_rename_errors(tmp_path):
    cmd = handler.Rename()
    exit_code, msg = cmd.execute([str(tmp_path / "ghost.txt"), "other.txt"])
    assert exit_code == 1
    assert "not found" in msg
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("1", encoding="utf-8")
    b.write_text("2", encoding="utf-8")
    code, _ = bridge._native.rename(str(a), str(b))
    assert code == -5  # ERR_EXISTS
    exit_code, msg = cmd.execute([str(a), "../escape.txt"])
    assert exit_code == 1
    assert "Invalid file name" in msg


def test_native_unicode_paths(tmp_path):
    unicode_dir = tmp_path / "dir_日本語"
    code, _ = bridge._native.mkdir(str(unicode_dir), False)
    assert code == 0
    assert unicode_dir.is_dir()
    unicode_file = unicode_dir / "café_🚀.txt"
    code, _ = bridge._native.touch(str(unicode_file))
    assert code == 0
    assert unicode_file.exists()
    unicode_file.write_text("héllo 🌍\n", encoding="utf-8", newline="\n")
    code, content = bridge._native.cat(str(unicode_file))
    assert code == 0
    assert content == "héllo 🌍\n"
    code, items = bridge._native.dir(str(tmp_path))
    assert code == 0
    assert ("dir_日本語", True) in items
    code, sub_items = bridge._native.dir(str(unicode_dir))
    assert code == 0
    assert ("café_🚀.txt", False) in sub_items
