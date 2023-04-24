from __future__ import annotations

import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from cleez import CLI


__all__ = ["Command", "Argument", "Option"]


class Command(ABC):
    name: str
    cli: CLI

    arguments: list[Argument] = []
    options: list[Option] = []

    hide_from_help: bool = False

    def __init__(self, cli):
        self.cli = cli
        self.subparsers = None

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def add_subparser_to(self, subparsers):
        name = self.split()[-1]

        subparser = subparsers.add_parser(name, help=self.__doc__)
        subparser.set_defaults(_command=self)

        for argument in self.arguments:
            subparser.add_argument(*argument.args, **argument.kwargs)

        for option in self.options:
            subparser.add_argument(*option.args, **option.kwargs)

        if not self.is_subcommand():
            self.subparsers = subparser.add_subparsers()

    def is_subcommand(self):
        return " " in self.name

    def main_command_name(self):
        return self.split()[0]

    def subcommand_name(self):
        return self.split()[1]

    def __len__(self):
        return len(self.split())

    def split(self):
        args = self.name.split(" ")
        assert len(args) in {
            1,
            2,
        }, (
            "Command name must be composed of one or "
            "two words (i.e. '<command> <subcommand>')"
        )
        return args


class Argument:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Option:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
