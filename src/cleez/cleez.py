"""Simple framework for building command line applications with multiple
commands and subcommands.

Similar to Cleo, but based on the stdlib's argparse module.
"""
from __future__ import annotations

import argparse
import importlib
import inspect
import sys
from dataclasses import dataclass, field
from inspect import isabstract, isclass
from pathlib import Path
from pkgutil import iter_modules

from .colors import red
from .command import Command, Option
from .help import HelpMaker

__all__ = ["CLI"]


@dataclass(frozen=True)
class CLI:
    name: str = "cleez"

    commands: list[Command] = field(default_factory=list)
    options: list[Option] = field(default_factory=list)
    help_maker: HelpMaker = field(default_factory=HelpMaker)

    #
    # Public API
    #
    def run(self, argv=None):
        if not argv:
            argv = sys.argv

        parser = self.make_parser()

        try:
            args = parser.parse_args(argv[1:])
        except argparse.ArgumentError as e:
            print(red(f"Argument parsing error: {e}\n"))
            print("Usage:\n")
            self.help_maker.print_help(self)
            sys.exit(1)

        # self.common_options(args)
        if "_command" not in args:
            self.help_maker.print_help(self)
            sys.exit()  # exit 0 or exit 1 ?

        self.call_command(args._command, args)

    def scan(self, module_name: str):
        root_module = importlib.import_module(module_name)
        root_module_name = root_module.__name__
        root_path = Path(root_module.__file__).parent  # type: ignore
        for _, module_name, _ in iter_modules([str(root_path)]):
            module = importlib.import_module(f"{root_module_name}.{module_name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)

                if isclass(attribute) and issubclass(attribute, Command):
                    self.add_command(attribute)

    def add_command(self, command_class: type[Command]):
        if isabstract(command_class):
            return

        self.commands.append(command_class(self))

    def add_option(self, *args, **kwargs):
        if args and isinstance(args[0], Option):
            option = args[0]
            self.options.append(option)
        else:
            self.options.append(Option(*args, **kwargs))

    #
    # Internal API
    #
    def get_command(self, name: str) -> Command:
        for command in self.commands:
            if command.name == name:
                return command
        raise KeyError(f"Command {name} not found")

    def make_parser(self):
        parser = MyArgParser()
        subparsers = parser.add_subparsers(parser_class=MyArgParser)

        for command in self.commands:
            if " " in command.name:
                cmd1, cmd2 = command.name.split(" ")
                parent_command = self.get_command(cmd1)
                if not parent_command.subparsers:
                    print(f"Parent command {cmd1} has not subparsers")
                    raise ValueError(f"Parent command {cmd1} has not subparsers")
                command.add_subparser_to(parent_command.subparsers)
            else:
                command.add_subparser_to(subparsers)

        return parser

    def call_command(self, command: Command, args: argparse.Namespace):
        # Inject arguments into the command `run` method.
        sign = inspect.signature(command.run)
        kwargs = {}
        for name, parameter in sign.parameters.items():
            # Needed ?
            if name == "self":
                continue
            if name in args:
                value = getattr(args, name)
            else:
                value = parameter.default
            kwargs[name] = value

        command.run(**kwargs)

    def common_options(self, args: argparse.Namespace):
        if args.help:
            self.help_maker.print_help(self)
            sys.exit(0)
        if args.version:
            print(self.get_version())
            sys.exit(0)

    def print_help(self):
        self.help_maker.print_help(self)

    def get_version(self):
        return "TODO"

    def get_command_name(self):
        return self.name


class MyArgParser(argparse.ArgumentParser):
    """Subclass of argparse.ArgumentParser that doesn't exit on error.

    See: https://github.com/python/cpython/issues/103498
    """

    def error(self, message):
        raise argparse.ArgumentError(None, message)
