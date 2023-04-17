from cleez import CLI, Command, Argument
from cleez.colors import blue, green


class ListCommand(Command):
    """Some command with no argument."""

    name = "list"

    def run(self):
        print("Here's the list")


class EchoCommand(Command):
    """Echo something."""

    name = "echo"

    arguments = [
        Argument("arg", type=str),
    ]

    def run(self, arg):
        print(arg)


class ServerCommand(Command):
    """Server commands."""

    name = "server"
    hide_from_help = True

    def run(self):
        self.cli.print_help()


class ServerRestartCommand(Command):
    """Restart server (not for real!)."""

    name = "server restart"

    def run(self):
        print(blue("Restarting server..."))
        print(green("Server restarted"))


def main():
    cli = CLI("demo")
    cli.add_command(ListCommand)
    cli.add_command(EchoCommand)
    cli.add_command(ServerCommand)
    cli.add_command(ServerRestartCommand)

    cli.add_option(
        "-h",
        "--help",
        default=False,
        action="store_true",
        help="Show help and exit",
    )
    cli.add_option(
        "-V",
        "--version",
        default=False,
        action="store_true",
        help="Show version and exit",
    )
    cli.run()


if __name__ == "__main__":
    main()
