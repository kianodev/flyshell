# \main.py

from core import console, data

if __name__ == "__main__":
    if data.HOST_OS in ["Windows", "Darwin", "Linux"]:
        console.boot()
    else:
        print(f"Boot Error: Your OS, '{data.HOST_OS}', is not supported.")