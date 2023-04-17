from cleez import Argument, Command


class CommandWithNoArgs(Command):
    """Some command with no argument."""

    name = "command-with-no-args"

    def run(self):
        pass


class CommandWithArgs(Command):
    """Some command with no argument."""

    name = "command-with-args"

    arguments = [
        Argument("arg1", type=int),
        Argument("arg2", type=int),
    ]

    def run(self):
        pass


class MainCommand(Command):
    """Main command."""

    name = "main"

    def run(self):
        pass


class SubCommand(Command):
    """Sub command."""

    name = "main sub"

    def run(self):
        pass
