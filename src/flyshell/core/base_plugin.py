# src\flyshell\core\base_plugin.py

if __name__ == "__main__":
    print("Error: This file is a Flyshell system module and cannot be run directly.")
    print("To launch Flyshell, please launch using 'python main.py'")
    import sys
    sys.exit(0)

from flyshell.core import data

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
        fresh_data = data.get_all_plugin_data(plugin_key)
        self.storage = fresh_data
        self.context["storage"] = fresh_data
        return self.storage

    def save_storage(self):
        plugin_key = self.context.get("plugin_name", self.name)
        for k, v in self.storage.items():
            data.set_plugin_data(plugin_key, k, v)
        self.context["storage"] = self.storage

    def on_unload(self):
        self.save_storage()