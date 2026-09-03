# \core\console.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data
from core.directory import execute
import os
import random

def boot():
    print("\033[H\033[2J", end="")
    print(f"\nBoot successful, welcome to Flyshell! (Version {data.VERSION})")
    user_info = data.read(["core", "auth"])
    username = user_info.get("username")
    GREETINGS = [
        f"Hi {username}, what's it going to be today?",
        f"The mic is yours, {username}, go and blow me away!",
        f"Hey {username}, let's get this party started!",
        f"What's up, {username}? Let's go!",
        f"I'm awaiting your first command, {username}!",
        f"How's it going {username}? I'm here to help.",
        f"{username}, it's your call! Show me what you've got, what are we doing today?",
        f"My wish is your command, {username}! (unless it's not on my command list)",
        f"I have goods for you {username}, it's called a Command Interface.",
        f"I'm your boss! Wait, no... sorry... you, {username}, are my boss!",
    ]
    greeting = random.choice(GREETINGS)
    print(f"\n{greeting}\n")
    while True:
        folder = os.path.basename(os.getcwd())
        raw_cmd = input(f"Flyshell [v{data.VERSION}] ({folder})>>")
        if not raw_cmd:
            print(f"\nCommand Error: No command given. Use 'cmds' for help.\n")
            continue
        execute(raw_cmd)