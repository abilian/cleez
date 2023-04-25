import argparse


class PatchedArgumentParser(argparse.ArgumentParser):
    """Subclass of argparse.ArgumentParser that doesn't exit on error.

    See: https://github.com/python/cpython/issues/103498
    """

    def error(self, message):
        raise argparse.ArgumentError(None, message)
