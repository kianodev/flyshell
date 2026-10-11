# src\flyshell\abstract\base_cmd.py

from typing import List, Optional, Tuple, Union

class BaseCmd:
    name: str = ""
    description: str = ""
    min_args: int = 0
    options: Optional[str] = None
    aliases: List[str] = []

    def execute(self, args: List[str]) -> Union[int, Tuple[int, str], str, None]:
        raise NotImplementedError(f"Command '{self.__class__.__name__}' has not implemented the execute method")

    def help(self):
        print(f"\nCommand: {self.name}")
        if self.aliases:
            print(f"Aliases: {', '.join(self.aliases)}")
        print(f"Description: {self.description}")
        print(f"Required Arguments: {self.min_args}")
        if self.options:
            print(f"Accepted Arguments: {self.options}")
        print()