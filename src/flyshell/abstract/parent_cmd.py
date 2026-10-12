# src\flyshell\abstract\parent_cmd.py

from flyshell.abstract.base_cmd import BaseCmd

from typing import Dict, List, Optional, Tuple, Union

class ParentCmd(BaseCmd):
    min_args: int = 1
    subcommands: Dict[str, BaseCmd] = {}

    def __init__(self):
        super().__init__() if hasattr(super(), "__init__") else None
        self._sub_registry: Dict[str, BaseCmd] = {}
        self._build_registry()

    def _build_registry(self):
        for cmd_obj in self.get_subcommands():
            self._sub_registry[cmd_obj.name] = cmd_obj
            for alias in getattr(cmd_obj, "aliases", []):
                self._sub_registry[alias] = cmd_obj

    def get_subcommands(self) -> List[BaseCmd]:
        return []

    def help(self):
        print(f"\nCommand Family: {self.name}")
        print(f"Description: {self.description}")
        print(f"\nSubcommands of '{self.name}':")
        seen = set()
        for sub in self._sub_registry.values():
            if sub in seen:
                continue
            seen.add(sub)
            label = f"{sub.name} (alias: {', '.join(sub.aliases)})" if sub.aliases else sub.name
            opt = f" [args: {sub.options}]" if sub.options else ""
            print(f"{label} - {sub.description}{opt}")
        print(f"\nFor subcommand assistance use '{self.name} <subcmd> -h' or '--help'\n")

    def execute(self, args: List[str]) -> Union[int, Tuple[int, str], str, None]:
        if not args or args[0] in ("-h", "--help"):
            self.help()
            return 0
        sub_name = args[0].lower()
        sub_args = args[1:]
        if sub_name not in self._sub_registry:
            print(f"\nCommand Error: Unknown subcommand '{sub_name}' for '{self.name}'.")
            print(f"Use '{self.name} -h' or '--help' to see all valid subcommands.\n")
            return 1
        target = self._sub_registry[sub_name]
        if "-h" in sub_args or "--help" in sub_args:
            target.help(prefix=self.name)
            return 0
        if len(sub_args) < target.min_args:
            print(f"\nCommand Error: '{self.name} {target.name}' requires at least {target.min_args} argument(s).")
            if target.options:
                print(f"Accepted arguments: {target.options}")
            print()
            return 1
        return target.execute(sub_args)