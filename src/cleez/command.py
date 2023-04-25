from __future__ import annotations

import typing
from abc import ABC, abstractmethod

from .argument import Argument, Option

if typing.TYPE_CHECKING:
    from cleez import CLI


__all__ = ["Command", "Argument", "Option"]


class Command(ABC):
    name: str
    cli: CLI

    arguments: list[Argument] = []
    options: list[Option] = []

    hide_from_help: bool = False

    _subcommands: list[Command]

    def __init__(self, cli):
        self.cli = cli
        self.subparsers = None
        self._subcommands = []

    def __repr__(self):
        return f"<Command '{self.name}'>"

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def add_to_subparsers(self, subparsers):
        name = self.split()[-1]

        subparser = subparsers.add_parser(name, help=self.__doc__)
        subparser.set_defaults(_command=self)

        for argument in self.arguments:
            argument.add_to_parser(subparser)

        for option in self.options:
            option.add_to_parser(subparser)

        if self.has_subcommands():
            self.subparsers = subparser.add_subparsers()

    def add_subcommand(self, command: Command):
        self._subcommands.append(command)

    def has_subcommands(self) -> bool:
        return bool(self._subcommands)

    def is_subcommand(self) -> bool:
        return " " in self.name

    def main_command_name(self) -> str:
        return self.split()[0]

    def __len__(self):
        return len(self.split())

    def split(self):
        args = self.name.split(" ")
        err_msg = (
            "Command name must be composed of one or "
            "two words (i.e. '<command> <subcommand>')"
        )
        assert len(args) in {1, 2}, err_msg
        return args
