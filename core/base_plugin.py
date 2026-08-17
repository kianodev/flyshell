# \core\base_plugin.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from core import data

class BasePlugin:
    name = "Unnamed Plugin"
    description = "No description provided."

    def __init__(self, context):
        self.context = context
        self.storage = context.get("storage", {})

    def execute(self, args: list):
        raise NotImplementedError("Plugins must implement the execute method")

    def help(self):
        print(f"\nPlugin: {self.name}")
        print(f"Description: {self.description}")

    def load_storage(self) -> dict:
        plugin_key = self.context.get("plugin_name", self.name)
        fresh_data = data.read(["plugin", plugin_key]) or {}
        self.storage = fresh_data
        self.context["storage"] = fresh_data
        return self.storage

    def save_storage(self):
        plugin_key = self.context.get("plugin_name", self.name)
        data.write(["plugin", plugin_key], self.storage)
        self.context["storage"] = self.storage

    def on_unload(self):
        self.save_storage()    