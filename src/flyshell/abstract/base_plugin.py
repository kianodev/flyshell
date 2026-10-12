# src\flyshell\abstract\base_plugin.py

from flyshell.core import data
from pathlib import Path

class BasePlugin:
    name: str = "Unnamed Plugin"
    description: str = "No description provided."
    version: str = "1.0.0"
    author: str = "Unknown"
    usage: str = ""
    extended_help: str = ""

    def __init__(self, context: dict):
        self.context = context
        self.plugin_name = context.get("plugin_name", self.name)
        self.storage = context.get("storage", {})
        self.on_load()

    def on_load(self):
        pass

    def on_unload(self):
        self.save_storage()

    def execute(self, args: list):
        raise NotImplementedError("Plugins must implement the execute method")

    def help(self):
        lines = [
            f"\nPlugin: {self.name} (v{self.version})",
            f"Description: {self.description}",
            f"Author: {self.author}"
        ]
        if self.usage:
            lines.append(f"Usage: {self.usage}")
        if self.extended_help:
            lines.append("\nDetails:")
            lines.append(self.extended_help)
        print("\n".join(lines))

    def show_docs(self) -> bool:
        plugin_path = self.context.get("file_path")
        if plugin_path:
            p = Path(plugin_path)
            doc_file = (p.parent / "README.md") if p.is_file() else (p / "README.md")
            if doc_file.exists():
                print(f"\nDocumentation: {self.name}")
                print(doc_file.read_text(encoding="utf-8"))
                print("-" * 40)
                return True
        if self.__doc__:
            print(f"\nDocumentation: {self.name}")
            print(self.__doc__.strip())
            print("-" * 40)
            return True
        return False

    def get_data(self, key: str, default=None):
        return self.storage.get(key, default)

    def set_data(self, key: str, value):
        self.storage[key] = value
        self.save_storage()

    def load_storage(self) -> dict:
        fresh_data = data.get_all_plugin_data(self.plugin_name)
        self.storage = fresh_data
        self.context["storage"] = fresh_data
        return self.storage

    def save_storage(self):
        for k, v in self.storage.items():
            data.set_plugin_data(self.plugin_name, k, v)
        self.context["storage"] = self.storage