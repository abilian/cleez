class BadArgumentError(Exception):
    """Exception raised when an argument is invalid."""


class CommandError(Exception):
    """Exception raised when a command fails."""


class ParserBuildError(Exception):
    """Exception raised when a parser cannot be built."""
