# \core\base_plugin.py

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