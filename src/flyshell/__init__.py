try:
    from flyshell.abstract.base_plugin import BasePlugin

    __all__ = ["BasePlugin"]
except ImportError:
    BasePlugin = None
    __all__ = []
    pass
