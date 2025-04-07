import pytest

from cleez import CLI, Command
from cleez.actions import VERSION
from cleez.testing import CliRunner


class CommandWithNoArgument(Command):
    """Some command with no argument."""

    name = "command-with-no-args"

    def run(self):
        print("Hello!")


@pytest.fixture
def cli():
    cli = CLI()
    cli.add_command(CommandWithNoArgument)
    cli.add_option(
        "-V",
        "--version",
        action=VERSION,
        version="cleez version: 0.1.0",
        help="Show version and exit",
    )
    return cli


# Directly call the CLI
def test_command_with_no_argument(cli):
    cli.run(["test", "command-with-no-args"])


def test_help(cli):
    try:
        cli.run(["test", "command-with-no-args", "-h"])
    except SystemExit as e:
        assert e.code == 0


def test_version(cli):
    try:
        cli.run(["test", "-V", "command-with-no-args"])
    except SystemExit as e:
        assert e.code == 0


# With CliRunner
def test_test_runner(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ["test", "command-with-no-args"])
    assert result.exit_code == 0
    assert "Hello!" in result.stdout


def test_test_runner_version(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ["test", "-V", "command-with-no-args"])
    assert "version:" in result.stdout
    assert result.exit_code == 0


def test_test_runner_help_1(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ["test", "-h"])
    assert "usage:" in result.stdout.lower()
    assert result.exit_code == 0


def test_test_runner_help_2(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ["test", "command-with-no-args", "-h"])
    assert "usage:" in result.stdout.lower()
    assert result.exit_code == 0
