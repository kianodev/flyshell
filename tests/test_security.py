# tests\test_security.py

from flyshell.builtin import system

def test_syscmd_blocks_prohibited_base_commands():
    for cmd in ["format C:", "diskpart", "dd if=/dev/zero"]:
        tokens = cmd.split()
        code, message = system.syscmd(tokens)
        assert code == 1
        assert "Security Error" in message

def test_syscmd_blocks_forkbomb_signature():
    code, message = system.syscmd([":(){ :|:& };:"])
    assert code == 1
    assert "Security Error" in message

def test_syscmd_blocks_critical_system_directories():
    for dangerous_call in ["rm -rf /", "del C:\\Windows\\System32"]:
        code, message = system.syscmd(dangerous_call.split())
        assert code == 1
        assert "Security Error" in message

def test_syscmd_force_flag_without_arguments_returns_error():
    code, message = system.syscmd(["-f"])
    assert code == 1
    assert "requires at least 1 parameter" in message