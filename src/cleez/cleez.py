"""Simple framework for building command line applications with multiple
commands and subcommands.

Similar to Cleo, but based on the stdlib's argparse module.
"""
from __future__ import annotations

import argparse
import importlib
import inspect
import sys
from dataclasses import field, dataclass
from inspect import isabstract, isclass
from pathlib import Path
from pkgutil import iter_modules

from .colors import red
from .command import Command, Option
from .exceptions import BadArgument, CommandError
from .help import HelpMaker


@dataclass(frozen=True)
class CLI:
    commands: list[type[Command]] = field(default_factory=list)
    options: list[Option] = field(default_factory=list)
    help_maker: HelpMaker = field(default_factory=HelpMaker)

    #
    # Public API
    #
    def __call__(self):
        # Convenience. Needed?
        return self.run()

    def run(self, argv=None):
        if not argv:
            argv = sys.argv
        command = self.find_command(argv)
        try:
            args = self.parse_args(command, argv)
        except argparse.ArgumentError as e:
            print(red(f"Argument parsing error: {e}\n"))
            print("Usage:\n")
            self.help_maker.print_help(self)
            sys.exit(1)
        self.common_options(args)
        self.run_command(command, args)

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

    def add_option(self, *args, **kwargs):
        if args and isinstance(args[0], Option):
            option = args[0]
            self.options.append(option)
        else:
            self.options.append(Option(*args, **kwargs))

    #
    # Internal API
    #
    def find_command(self, argv: list[str]) -> Command:
        args = argv[1:]
        args = [arg for arg in args if not arg.startswith("-")]
        args_str = " ".join(args)
        commands = sorted(self.commands, key=lambda command: -len(command.name))
        for command in commands:
            if args_str.startswith(command.name):
                return command(self)
        raise CommandError("No command found")

    def parse_args(self, command: Command, argv: list[str]) -> argparse.Namespace:
        parser = MyArgParser(add_help=False, exit_on_error=False)
        for argument in command.arguments:
            parser.add_argument(*argument.args, **argument.kwargs)
        for option in self.options:
            parser.add_argument(*option.args, **option.kwargs)
        argv = argv[len(command.name.split()) + 1 :]
        args = parser.parse_args(argv)
        return args

    def run_command(self, command: Command, args: argparse.Namespace):
        try:
            self.call_command(command, args)
        except (BadArgument, CommandError) as e:
            print(red(e))
            sys.exit(1)

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

    def add_command(self, command_class: type[Command]):
        if isabstract(command_class):
            return
        self.commands.append(command_class)

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
        return "<command-name>"


class MyArgParser(argparse.ArgumentParser):
    """Subclass of argparse.ArgumentParser that doesn't exit on error.

    See: https://github.com/python/cpython/issues/103498
    """

    def error(self, message):
        raise argparse.ArgumentError(None, message)
