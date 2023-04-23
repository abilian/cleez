import pytest

from cleez import CLI, Command
from cleez.actions import STORE_TRUE
from cleez.testing import CliRunner


class CommandWithNoArgument(Command):
    """Some command with no argument."""

    name = "command-with-no-args"

    def run(self):
        pass


@pytest.fixture()
def cli():
    cli = CLI()
    cli.add_command(CommandWithNoArgument)
    cli.add_option(
        "-h", "--help", default=False, action=STORE_TRUE, help="Show help and exit"
    )
    cli.add_option(
        "-V",
        "--version",
        default=False,
        action=STORE_TRUE,
        help="Show version and exit",
    )
    return cli


def test_command_with_no_argument(cli):
    cli.run(["test", "command-with-no-args"])


def test_test_runner(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ["test", "command-with-no-args"])
    assert result.exit_code == 0


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

    cli.run(["test", "main", "sub2", "1"])

    cli.run(["test", "main", "sub3", "1"])
    cli.run(["test", "main", "sub3", "1", "2"])
    cli.run(["test", "main", "sub3"])
