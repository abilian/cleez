from __future__ import annotations

from itertools import groupby

from .colors import blue, bold, green
from .command import Command, Option

__all__ = ["HelpMaker"]


class HelpMaker:
    def print_help(self, cli):
        self.print_version(cli)
        self.print_usage(cli)
        self.print_options(cli.options)
        self.print_commands(cli.commands)

    def print_version(self, cli):
        version = cli.get_version()
        command_name = cli.get_command_name()
        print(f"{bold(command_name)} ({version})")
        print()

    def print_usage(self, cli):
        print(bold("Usage:"))
        print(f"  {cli.name} <command> [options] [arguments]")
        print()

    def print_options(self, options: list[Option]):
        print(bold("Options:"))
        for option in options:
            print(f"  {blue(option.args[0])}  {option.kwargs['help']}")
        print()

    def print_commands(self, commands: list[Command]):
        print(bold("Available commands:"))

        commands = self.get_commands(commands)
        simple_commands = [
            command for command in commands if not command.is_subcommand()
        ]
        complex_commands = [command for command in commands if command.is_subcommand()]

        self.print_simple_commands_help(simple_commands)
        self.print_complex_commands_help(complex_commands)

    def print_simple_commands_help(self, commands: list[Command]):
        if not commands:
            return
        max_command_length = max(len(command.name) for command in commands)
        w = max_command_length
        for command in commands:
            cmd_name = f"{command.name:<{w}}"
            help = (command.__doc__ or "").split("\n")[0].strip()
            print(f"  {blue(cmd_name)}  {help}")

    def print_complex_commands_help(self, commands: list[Command]):
        if not commands:
            return
        max_command_length = max(len(command.name) for command in commands)
        w = max_command_length
        groups = groupby(commands, lambda command: command.main_command_name())
        for group_name, group in groups:
            print()
            print(f" {green(group_name)}")

            for command in group:
                cmd_name = f"{command.name:<{w}}"
                help = (command.__doc__ or "").split("\n")[0].strip()
                print(f"  {blue(cmd_name)}  {help}")

    def get_commands(self, commands: list[Command]):
        def sorter(command):
            return len(command), command.name

        commands = [command for command in commands if command.name]
        commands = [command for command in commands if not command.hide_from_help]
        return sorted(commands, key=sorter)
