# tests/test_diskops_old.py

from flyshell.builtin import diskops


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
