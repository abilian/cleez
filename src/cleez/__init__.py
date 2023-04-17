"""Top-level package for Cleez."""

__author__ = """Abilian SAS"""
__email__ = """sf@abilian.com"""
__version__ = """0.1.0"""

from .cleez import CLI
from .command import Argument, Command, Option
from .exceptions import BadArgumentError, CommandError

__all__ = ["CLI", "Command", "CommandError", "BadArgumentError", "Argument", "Option"]
