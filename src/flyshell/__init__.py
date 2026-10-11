try:
    from flyshell.abstract.base_plugin import BasePlugin
    from flyshell.core import data
    __all__ = ["BasePlugin"]
    __version__ = f"{data.VERSION}+{data.BUILD}"
except ImportError:
    BasePlugin = None
    __all__ = []
    __version__ = ""
    pass