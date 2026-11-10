# src/flyshell/builtin/pkg.py

from typing import List, Tuple
from flyshell.abstract.base_cmd import BaseCmd
from flyshell.abstract.parent_cmd import ParentCmd
from flyshell.startup import env


class PkgApi(BaseCmd):
    name: str = "api"
    description: str = "View configured package/plugin API keys"
    min_args: int = 1
    options: str = "'add'/'del'/'edit'/'view', then package name and key name details"
    aliases: List[str] = ["keys"]

    def execute(self, args: List[str]) -> Tuple[int, str]:
        arg = args[0]
        remaining_args = args[1:]
        match arg:
            case "add" | "edit":
                if len(remaining_args) < 3:
                    return (
                        1,
                        "\nCommand Error: Define a package name, a key name and a value.\n",
                    )
                plugin_name = remaining_args[0]
                key_name = remaining_args[1]
                val = " ".join(remaining_args[2:])
                code, output = env.set_plugin_api_key(plugin_name, key_name, val)
                return (code, f"\n{output}\n")
            case "del" | "rm":
                if len(remaining_args) < 2:
                    return (
                        1,
                        "\nCommand Error: Define a package name and a key name for deletion.\n",
                    )
                plugin_name = remaining_args[0]
                key_name = remaining_args[1]
                code, output = env.remove_plugin_api_key(plugin_name, key_name)
                return (code, f"\n{output}\n")
            case "view":
                if not remaining_args:
                    code, output = env.get_all_keys()
                else:
                    package_name = remaining_args[0]
                    code, output = env.get_plugin_keys_formatted(package_name)
                return (code, f"\n{output}\n")
            case _:
                return (1, f"\nCommand Error: Unknown target '{arg}'\n")


class Pkg(ParentCmd):
    name: str = "pkg"
    description: str = "Manage Flyshell packages, plugins, and dependencies"
    aliases: List[str] = ["package"]

    def get_subcommands(self) -> List[BaseCmd]:
        return [
            PkgApi(),
        ]
