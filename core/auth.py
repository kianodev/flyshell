# \core\auth.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data
import getpass
import hashlib
import re
import secrets

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hash.hex(), salt.hex()

def verify_password(stored_hash: str, stored_salt: str, password: str) -> bool:
    salt_bytes = bytes.fromhex(stored_salt)
    attempt_hash, _ = hash_password(password, salt_bytes)
    return secrets.compare_digest(attempt_hash, stored_hash)

def setup_acc() -> bool:
    print("\nWelcome to Flyshell, New User!")
    print("Please follow the prompts to create your Flyshell profile.")
    while True:
        username = input("Create Username: ").strip()
        if not username:
            print("\nAccount Error: Username cannot be empty.\n")
        else:
            print(f"\nUsername set as '{username}'\n")
            break
    i = 5
    while i > 0:
        print("Your password MUST:")
        print("- Contain at least 10 total characters")
        print("- Contain 1 or more upper case letters")
        print("- Contain 1 or more lower case letters")
        print("- Contain 1 or more numbers")
        print("- Contain 1 or more special characters\n")
        password = getpass.getpass("Create Password: ")
        confirm = getpass.getpass("Confirm Password: ")
        if password != confirm:
            print("\nAccount Error: Passwords do not match.")
            i -= 1
            if i == 0:
                print("Too many attempts.\n")
                return False
            print(f"You have {i} attempts remaining.\n")
            continue
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_speci = bool(re.search(r'[^a-zA-Z0-9]', password))
        if len(password) >= 10 and has_upper and has_lower and has_digit and has_speci:
            break
        else:
            print("\nAccount Error: Password does not meet required conditions.\n")
            i -= 1
            if i == 0:
                print("Too many attempts.\n")
                return False
            print(f"You have {i} attempts remaining.\n")
            continue
    pwd_hash, salt = hash_password(password)
    auth_data = {
        "username": username,
        "hash": pwd_hash,
        "salt": salt
    }
    data.write(["core", "auth"], auth_data)
    print("\nSUCCESS: Account created successfully!")
    return True

def login_flow() -> bool:
    auth_info = data.read(["core", "auth"])
    if not auth_info or "hash" not in auth_info:
        if not setup_acc():
            return False
        auth_info = data.read(["core", "auth"])
    stored_user = auth_info.get("username", "User")
    stored_hash = auth_info.get("hash")
    stored_salt = auth_info.get("salt")
    print(f"\nWelcome, {stored_user}!")
    i = 5
    while i > 0:
        entered_pwd = getpass.getpass("Enter Password: ")
        if verify_password(stored_hash, stored_salt, entered_pwd):
            return True
        i -= 1
        print(f"\nAccount Error: Password does not match.")
        if i == 0:
            print("Too many attempts.\n")
            return False
        print(f"You have {i} attempts remaining.\n")