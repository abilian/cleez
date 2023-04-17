from __future__ import annotations

import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from cleez import CLI


class Command(ABC):
    name: str
    cli: CLI

    arguments: list[Argument] = []
    options: list[Option] = []

    def __init__(self, cli):
        self.cli = cli

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError


class Argument:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Option:
    def __init__(self, *args: list[str], **kwargs):
        self.args = args
        self.kwargs = kwargs
