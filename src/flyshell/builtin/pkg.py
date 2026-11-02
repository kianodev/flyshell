# src\flyshell\builtin\pkg.py

from typing import List, Tuple
from flyshell.abstract.base_cmd import BaseCmd
from flyshell.abstract.parent_cmd import ParentCmd
from flyshell.core import env


class PkgApi(BaseCmd):
    name: str = "api"
    description: str = "View configured package/plugin API keys"
    min_args: int = 0
    options: str = "Package name"
    aliases: List[str] = ["keys"]

    def execute(self, args: List[str]) -> Tuple[int, str]:
        if not args:
            code, output = env.get_all_keys()
        else:
            package_name = args[0]
            code, output = env.get_plugin_keys_formatted(package_name)
        return (code, f"\n{output}\n")


class Pkg(ParentCmd):
    name: str = "pkg"
    description: str = "Manage Flyshell packages, plugins, and dependencies"
    aliases: List[str] = ["package"]

    def get_subcommands(self) -> List[BaseCmd]:
        return [
            PkgApi(),
        ]
