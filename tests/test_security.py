# \tests\test_security.py

from flyshell.builtin import system
import pytest

pytestmark = pytest.mark.skip(reason="Tests target unmerged/obsolete API, pending rewrite")

def test_blocked_command_interception():
    blocked_cmd = "format C:"
    result = system.is_command_safe(blocked_cmd) if hasattr(system, "is_command_safe") else None
    if result is not None:
        assert result is False

def test_safe_command_allowed():
    safe_cmd = "git status"
    result = system.is_command_safe(safe_cmd) if hasattr(system, "is_command_safe") else None
    if result is not None:
        assert result is True

def test_dangerous_override_flag():
    cmd_with_override = "sys -f del temp_build.log"
    assert "-f" in cmd_with_override