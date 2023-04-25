from abc import ABC, abstractmethod


class BaseArgument(ABC):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.check()

    @abstractmethod
    def check(self):
        ...

    def add_to_parser(self, parser):
        parser.add_argument(*self.args, **self.kwargs)


class Argument(BaseArgument):
    def check(self):
        assert not self.args[0].startswith("-")


class Option(BaseArgument):
    def check(self):
        assert self.args[0].startswith("-")
