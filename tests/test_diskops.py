# tests\test_diskops.py

from flyshell.builtin import diskops


def test_touch_creates_file_and_updates_timestamp(tmp_path):
    cmd = diskops.Touch()
    target = tmp_path / "test.txt"
    code, msg = cmd.execute([str(target)])
    assert code == 0
    assert "Created file" in msg
    assert target.exists()
    code, msg = cmd.execute([str(target)])
    assert code == 0
    assert "Updated timestamp" in msg


def test_touch_missing_parent_directory(tmp_path):
    cmd = diskops.Touch()
    target = tmp_path / "nonexistent_dir" / "test.txt"
    code, msg = cmd.execute([str(target)])
    assert code == 1
    assert "Parent directory does not exist" in msg


def test_cat_reads_content_with_limit_and_numbers(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("line 1\nline 2\nline 3\nline 4\n")
    cmd = diskops.Cat()
    code, msg = cmd.execute([str(file_path)])
    assert code == 0
    assert "line 1" in msg and "line 4" in msg
    code, msg = cmd.execute(["-n", "-l", "2", str(file_path)])
    assert code == 0
    assert "1 | line 1" in msg
    assert "2 | line 2" in msg
    assert "line 3" not in msg


def test_cat_nonexistent_and_empty_file(tmp_path):
    cmd = diskops.Cat()
    code, msg = cmd.execute([str(tmp_path / "missing.txt")])
    assert code == 1
    assert "not found" in msg
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    code, msg = cmd.execute([str(empty_file)])
    assert code == 1
    assert "is empty" in msg


def test_mkdir_standard_and_parents(tmp_path):
    cmd = diskops.MkDir()
    target = tmp_path / "new_folder"
    code, msg = cmd.execute([str(target)])
    assert code == 0
    assert target.is_dir()
    code, msg = cmd.execute([str(target)])
    assert code == 1
    assert "already exists" in msg
    nested = tmp_path / "parent" / "child"
    code, msg = cmd.execute(["-p", str(nested)])
    assert code == 0
    assert nested.is_dir()


def test_rename_file(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("data")
    cmd = diskops.Rename()
    code, msg = cmd.execute([str(src), "new.txt"])
    assert code == 0
    assert not src.exists()
    assert (tmp_path / "new.txt").exists()


def test_copy_file_and_directory(tmp_path):
    src_file = tmp_path / "source.txt"
    src_file.write_text("payload")
    dst_file = tmp_path / "dest.txt"
    cmd = diskops.Copy()
    code, msg = cmd.execute([str(src_file), str(dst_file)])
    assert code == 0
    assert dst_file.read_text() == "payload"
    src_dir = tmp_path / "src_dir"
    src_dir.mkdir()
    (src_dir / "item.txt").write_text("inner")
    dst_dir = tmp_path / "dst_dir"
    code, msg = cmd.execute([str(src_dir), str(dst_dir)])
    assert code == 0
    assert (dst_dir / "item.txt").exists()


def test_rm_file_and_directory_recursive(tmp_path):
    target_file = tmp_path / "del.txt"
    target_file.write_text("bye")
    cmd = diskops.Rm()
    code, msg = cmd.execute(["-f", str(target_file)])
    assert code == 0
    assert not target_file.exists()
    target_dir = tmp_path / "sub_dir"
    target_dir.mkdir()
    code, msg = cmd.execute(["-f", str(target_dir)])
    assert code == 1
    assert "is a directory" in msg
    code, msg = cmd.execute(["-f", "-r", str(target_dir)])
    assert code == 0
    assert not target_dir.exists()


def test_rmdir_empty_and_non_empty(tmp_path):
    target_dir = tmp_path / "removable"
    target_dir.mkdir()
    cmd = diskops.RmDir()
    (target_dir / "file.txt").write_text("data")
    code, msg = cmd.execute([str(target_dir)])
    assert code == 1
    assert "not empty" in msg
    code, msg = cmd.execute(["-f", str(target_dir)])
    assert code == 0
    assert not target_dir.exists()
