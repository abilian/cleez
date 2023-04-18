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

    def run(self, arg1: int, arg2: int):
        assert isinstance(arg1, int)
        assert isinstance(arg1, int)


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


class SubCommandWithArg(Command):
    """Sub command."""

    name = "main sub2"

    arguments = [
        Argument("arg", type=int),
    ]

    def run(self, arg: int):
        assert isinstance(arg, int)


class SubCommandWithStarArgs(Command):
    """Sub command."""

    name = "main sub3"

    arguments = [
        Argument("args", nargs="*", type=int),
    ]

    def run(self, args: list[int]):
        for arg in args:
            assert isinstance(arg, int)
