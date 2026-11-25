# src/flyshell/abstract/base_plugin.py

from flyshell.core import data

from pathlib import Path
from typing import Any, Optional


class BasePlugin:
    name: str = "Unnamed Plugin"
    description: str = "No description provided."
    version: str = "1.0.0"
    author: str = "Unknown"
    identifier: str = ""
    usage: str = ""
    extended_help: str = ""
    api_keys: Optional[list] = None
    third_pty_libs: Optional[list] = None

    def __init__(self, context: dict) -> None:
        self.api_keys = list(self.api_keys) if self.api_keys else []
        self.third_pty_libs = list(self.third_pty_libs) if self.third_pty_libs else []
        self.context = context
        self.plugin_name = context.get("plugin_name", self.name)
        self.storage = context.get("storage", {})
        self.api_keys_data = context.get("api_keys", {})
        self.env_file_path = context.get("env_path", None)
        self.on_load()

    def get_api_key(self, key_name: str, default: Any = None) -> Any:
        if key_name in self.api_keys_data:
            return self.api_keys_data[key_name]
        target = key_name.lower()
        for k, v in self.api_keys_data.items():
            if k.lower() == target:
                return v
        return default

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass

    def execute(self, args: list) -> Any:
        raise NotImplementedError("Plugins must implement the execute method")

    def help(self) -> None:
        lines = [
            f"\nPlugin: {self.name} (v{self.version})",
            f"Description: {self.description}",
            f"Author: {self.author}",
        ]
        if self.usage:
            lines.append(f"Usage: {self.usage}")
        if self.extended_help:
            lines.append("\nDetails:")
            lines.append(self.extended_help)
        if self.api_keys:
            lines.append("\nThis plugin requires one or more API keys.")
        if self.third_pty_libs:
            lines.append("\nThis plugin requires third party dependencies.")
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

    def get_data(self, key: str, default: Any = None) -> Any:
        return self.storage.get(key, default)

    def set_data(self, key: str, value: Any) -> None:
        self.storage[key] = value
        self.save_storage()

    def delete_data(self, key: str) -> bool:
        if key in self.storage:
            del self.storage[key]
            self.save_storage()
            return True
        return False

    def load_storage(self) -> dict:
        fresh_data = data.get_all_plugin_data(self.plugin_name)
        self.storage = fresh_data
        self.context["storage"] = fresh_data
        return self.storage

    def save_storage(self) -> None:
        existing_keys = set(data.get_all_plugin_data(self.plugin_name).keys())
        for stale_key in existing_keys - set(self.storage.keys()):
            data.delete_plugin_data(self.plugin_name, stale_key)
        for k, v in self.storage.items():
            data.set_plugin_data(self.plugin_name, k, v)
        self.context["storage"] = self.storage
