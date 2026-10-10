# \tests\test_auth.py

from flyshell.core import auth

def test_hash_password_generates_hex():
    raw_password = "SecurePassword123!"
    pwd_hash, salt = auth.hash_password(raw_password)
    assert isinstance(pwd_hash, str)
    assert isinstance(salt, str)
    assert len(salt) == 32

def test_verify_password_success():
    raw_password = "SecurePassword123!"
    pwd_hash, salt = auth.hash_password(raw_password)
    assert auth.verify_password(pwd_hash, salt, raw_password) is True

def test_verify_password_failure():
    raw_password = "SecurePassword123!"
    pwd_hash, salt = auth.hash_password(raw_password)
    assert auth.verify_password(pwd_hash, salt, "IncorrectPassword987!") is False

def test_verify_password_tampered_salt():
    raw_password = "SecurePassword123!"
    pwd_hash, _ = auth.hash_password(raw_password)
    fake_salt = "00" * 16
    assert auth.verify_password(pwd_hash, fake_salt, raw_password) is False