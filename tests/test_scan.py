from cleez import CLI
from cleez.actions import VERSION


def test_scan():
    """Test that a command with no argument can be called."""
    cli = CLI()
    cli.scan("tests.commands")
    cli.add_option(
        "-V",
        "--version",
        default=False,
        action=VERSION,
        version=cli.version,
        help="Show version and exit",
    )

    try:
        cli.run(["test", "-h"])
    except SystemExit as e:
        assert e.code == 0

    try:
        cli.run(["test", "-V"])
    except SystemExit as e:
        assert e.code == 0

    cli.run(["test", "main"])
    cli.run(["test", "main", "sub"])
    cli.run(["test", "main", "sub2", "1"])

    cli.run(["test", "command-with-no-args"])

    cli.run(["test", "command-with-args", "1", "2"])

    cli.run(["test", "main", "sub3", "1"])
    cli.run(["test", "main", "sub3", "1", "2"])
    cli.run(["test", "main", "sub3"])
