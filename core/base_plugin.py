# \core\base_plugin.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

class BasePlugin:
    name = "Unnamed Plugin"
    description = "No description provided."

    def __init__(self, context):
        self.context = context

    def execute(self, args: list):
        raise NotImplementedError("Plugins must implement the execute method")

    def help(self):
        print(f"\nPlugin: {self.name}")
        print(f"Description: {self.description}")