# tests\test_security.py

from flyshell.builtin import system

def test_sysexe_blocks_prohibited_base_commands():
    for cmd in ["format C:", "diskpart", "dd if=/dev/zero"]:
        tokens = cmd.split()
        code, message = system.SysExe().execute(tokens)
        assert code == 1
        assert "Security Error" in message

def test_sysexe_blocks_forkbomb_signature():
    code, message = system.SysExe().execute([":(){ :|:& };:"])
    assert code == 1
    assert "Security Error" in message

def test_sysexe_blocks_critical_system_directories():
    for dangerous_call in ["rm -rf /", "del C:\\Windows\\System32"]:
        code, message = system.SysExe().execute(dangerous_call.split())
        assert code == 1
        assert "Security Error" in message

def test_sysexe_force_flag_without_arguments_returns_error():
    code, message = system.SysExe().execute(["-f"])
    assert code == 1
    assert "requires at least 1 parameter" in message