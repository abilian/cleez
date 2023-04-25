"""Simple framework for building command line applications with multiple
commands and subcommands.

Similar to Cleo, but based on the stdlib's argparse module.
"""
from __future__ import annotations

import argparse
import importlib
import inspect
import os
import sys
from dataclasses import dataclass, field
from inspect import isabstract, isclass
from itertools import groupby
from pathlib import Path
from pkgutil import iter_modules

from .colors import red
from .command import Command, Option
from .exceptions import ParserBuildError
from .help import HelpMaker

__all__ = ["CLI"]

DEBUG = os.environ.get("DEBUG_CLEEZ", False)


@dataclass(frozen=True)
class CLI:
    name: str = "cleez"
    version: str = "0.1.0"

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

    def main(self, args, prog_name, **extra):
        return self.run(args)

    def scan(self, module_name: str):
        root_module = importlib.import_module(module_name)
        root_module_name = root_module.__name__
        root_path = Path(root_module.__file__).parent  # type: ignore
        for _, module_name, _ in iter_modules([str(root_path)]):
            module = importlib.import_module(f"{root_module_name}.{module_name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)

                if isclass(attribute) and issubclass(attribute, Command):
                    command = attribute
                    self.add_command(command)

    def add_command(self, command_class: type[Command]):
        if isabstract(command_class):
            return

        self.commands.append(command_class(self))

    def add_option(self, *args, **kwargs):
        if args and isinstance(args[0], Option):
            assert (
                len(args) == 1
            ), f"Only one option can be added at a time (got {len(args):d})"
            assert (
                not kwargs
            ), "Cannot pass keyword arguments when adding an option object"
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

        for option in self.options:
            option.add_to_parser(parser)

        def sorter(cmd):
            return cmd.main_command_name(), len(cmd)

        commands = sorted(self.commands, key=sorter)

        assert all(len(c) in [1, 2] for c in commands)

        def grouper(cmd):
            return cmd.main_command_name()

        for _k, g in groupby(commands, grouper):
            group = list(g)
            if len(group) > 1:
                main = group[0]
                for sub in group[1:]:
                    assert main.main_command_name() == sub.main_command_name()
                    main.add_subcommand(sub)

        for command in commands:
            if command.is_subcommand():
                main_cmd = command.main_command_name()
                parent_command = self.get_command(main_cmd)
                if not parent_command.subparsers:
                    raise ParserBuildError(
                        f"Parent command '{main_cmd}' has no subparsers"
                    )
                command.add_to_subparsers(parent_command.subparsers)
            else:
                command.add_to_subparsers(subparsers)

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

    # def common_options(self, args: argparse.Namespace):
    #     if args.help:
    #         self.help_maker.print_help(self)
    #         sys.exit(0)
    #     if args.version:
    #         print(self.get_version())
    #         sys.exit(0)

    def print_help(self):
        self.help_maker.print_help(self)

    def get_version(self):
        return self.version

    def get_command_name(self):
        return self.name


class MyArgParser(argparse.ArgumentParser):
    """Subclass of argparse.ArgumentParser that doesn't exit on error.

    See: https://github.com/python/cpython/issues/103498
    """

    def error(self, message):
        raise argparse.ArgumentError(None, message)
