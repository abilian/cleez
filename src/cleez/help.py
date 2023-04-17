from __future__ import annotations

from itertools import groupby

from .cleez import Command, Option
from .colors import blue, bold, green


class HelpMaker:
    def print_help(self, cli):
        self.print_version(cli)
        self.print_usage()
        self.print_options(cli.options)
        self.print_commands(cli.commands)

    def print_version(self, cli):
        version = cli.get_version()
        command_name = cli.get_command_name()
        print(f"{bold(command_name)} ({version})")
        print()

    def print_usage(self):
        print(bold("Usage:"))
        print("  <command-name> <command> [options] [arguments]")
        print()

    def print_options(self, options: list[Option]):
        print(bold("Options:"))
        for option in options:
            print(f"  {blue(option.args[0])}  {option.kwargs['help']}")
        print()

    def print_commands(self, commands: list[Command]):
        print(bold("Available commands:"))

        def sorter(command):
            return len(command.name.split(" ")), command.name

        commands = [command for command in commands if command.name]
        commands = sorted(commands, key=sorter)
        simple_commands = [command for command in commands if " " not in command.name]
        complex_commands = [command for command in commands if " " in command.name]
        max_command_length = max(len(command.name) for command in commands)
        w = max_command_length

        for command in simple_commands:
            cmd_name = f"{command.name:<{w}}"
            print(f"  {blue(cmd_name)}  {command.__doc__}")

        groups = groupby(complex_commands, lambda command: command.name.split(" ")[0])
        for group_name, group in groups:
            print()
            print(f" {green(group_name)}")

            for command in group:
                if not command.name:
                    continue
                cmd_name = f"{command.name:<{w}}"
                print(f"  {blue(cmd_name)}  {command.__doc__}")
