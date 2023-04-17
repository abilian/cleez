from cleez import Command


class CommandWithNoArgs(Command):
    """Some command with no argument."""

    name = "subcommand-with-no-args"

    def run(self, service: str):
        pass
