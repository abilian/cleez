from cleez import CLI, Command


class CommandWithNoArgument(Command):
    """Some command with no argument."""

    name = "command-with-no-args"

    def run(self):
        pass


def test_command_with_no_argument():
    cli = CLI()
    cli.add_command(CommandWithNoArgument)
    cli.add_option(
        "-h", "--help", default=False, action="store_true", help="Show help and exit"
    )
    cli.add_option(
        "-V",
        "--version",
        default=False,
        action="store_true",
        help="Show version and exit",
    )
    cli.run(["test", "command-with-no-args"])


def test_scan():
    """Test that a command with no argument can be called."""
    cli = CLI()
    cli.scan("tests.commands")
    cli.add_option(
        "-h", "--help", default=False, action="store_true", help="Show help and exit"
    )
    cli.add_option(
        "-V",
        "--version",
        default=False,
        action="store_true",
        help="Show version and exit",
    )
    cli.run(["test", "command-with-no-args"])
    cli.run(["test", "command-with-args", "1", "2"])
    cli.run(["test", "main"])
    cli.run(["test", "main", "sub"])
