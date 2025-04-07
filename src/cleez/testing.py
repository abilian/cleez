"""
Copy / pasted from click.testing then simplified.

Original copytight notice:

Copyright 2014 Pallets

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the copyright holder nor the names of its contributors
  may be used to endorse or promote products derived from this software
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import annotations

import contextlib
import io
import os
import shlex
import sys
import typing as t
from collections.abc import Iterator, Mapping, Sequence
from types import TracebackType

from .cleez import CLI


class CliRunner:
    """The CLI runner provides functionality to invoke a Cleez command line
    script for unit testing purposes in a isolated environment.  This only
    works in single-threaded systems without any concurrency as it changes the
    global interpreter state.

    :param charset: the character set for the input and output data.
    :param env: a dictionary with environment variables for overriding.
    """

    def __init__(
        self,
        charset: str = "utf-8",
        env: Mapping[str, str | None] | None = None,
    ) -> None:
        self.charset = charset
        self.env = env or {}

    def invoke(
        self,
        cli: CLI,
        args: str | Sequence[str] | None = None,
        input: str | bytes | t.IO | None = None,
        env: Mapping[str, str | None] | None = None,
        catch_exceptions: bool = True,
        **extra: t.Any,
    ) -> Result:
        """Invokes a command in an isolated environment.  The arguments are
        forwarded directly to the command line script, the `extra` keyword
        arguments are passed to the :meth:`~clickpkg.Command.main` function of
        the command.

        This returns a :class:`Result` object.

        :param cli: the command to invoke
        :param args: the arguments to invoke. It may be given as an iterable
                     or a string. When given as string it will be interpreted
                     as a Unix shell command. More details at
                     :func:`shlex.split`.
        :param input: the input data for `sys.stdin`.
        :param env: the environment overrides.
        :param catch_exceptions: Whether to catch any other exceptions than
                                 ``SystemExit``.
        :param extra: the keyword arguments to pass to :meth:`main`.
        """
        exc_info = None
        with self.isolation(input=input, env=env) as outstreams:
            return_value = None
            exception: BaseException | None = None
            exit_code = 0

            if isinstance(args, str):
                args = shlex.split(args)

            try:
                prog_name = extra.pop("prog_name")
            except KeyError:
                prog_name = self.get_default_prog_name(cli)

            try:
                return_value = cli.main(args=args or (), prog_name=prog_name, **extra)
            except SystemExit as e:
                exc_info = sys.exc_info()
                e_code = t.cast(int | t.Any | None, e.code)

                if e_code is None:
                    e_code = 0

                if e_code != 0:
                    exception = e

                if not isinstance(e_code, int):
                    sys.stdout.write(str(e_code))
                    sys.stdout.write("\n")
                    e_code = 1

                exit_code = e_code

            except Exception as e:
                if not catch_exceptions:
                    raise
                exception = e
                exit_code = 1
                exc_info = sys.exc_info()
            finally:
                sys.stdout.flush()
                stdout = outstreams[0].getvalue()
                stderr = outstreams[1].getvalue()  # type: ignore

        return Result(
            runner=self,
            stdout_bytes=stdout,
            stderr_bytes=stderr,
            return_value=return_value,
            exit_code=exit_code,
            exception=exception,
            exc_info=exc_info,  # type: ignore
        )

    @contextlib.contextmanager
    def isolation(
        self,
        input: str | bytes | t.IO | None = None,
        env: Mapping[str, str | None] | None = None,
    ) -> Iterator[tuple[io.BytesIO, io.BytesIO | None]]:
        """A context manager that sets up the isolation for invoking of a
        command line tool.  This sets up stdin with the given input data and
        `os.environ` with the overrides from the given dictionary.

        This is automatically done in the :meth:`invoke` method.

        :param input: the input stream to put into sys.stdin.
        :param env: the environment overrides as dictionary.

        """
        bytes_input = make_input_stream(input, self.charset)

        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        env = self.make_env(env)

        bytes_output = io.BytesIO()

        sys.stdin = _NamedTextIOWrapper(
            bytes_input, encoding=self.charset, name="<stdin>", mode="r"
        )
        sys.stdout = _NamedTextIOWrapper(
            bytes_output, encoding=self.charset, name="<stdout>", mode="w"
        )

        bytes_error = io.BytesIO()
        sys.stderr = _NamedTextIOWrapper(
            bytes_error,
            encoding=self.charset,
            name="<stderr>",
            mode="w",
            errors="backslashreplace",
        )
        old_env = {}
        try:
            for key, value in env.items():
                old_env[key] = os.environ.get(key)
                if value is None:
                    with contextlib.suppress(Exception):
                        del os.environ[key]

                else:
                    os.environ[key] = value
            yield bytes_output, bytes_error
        finally:
            for key, value in old_env.items():
                if value is None:
                    with contextlib.suppress(Exception):
                        del os.environ[key]

                else:
                    os.environ[key] = value
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.stdin = old_stdin

    def make_env(
        self, overrides: Mapping[str, str | None] | None = None
    ) -> Mapping[str, str | None]:
        """Returns the environment overrides for invoking a script."""
        rv = dict(self.env)
        if overrides:
            rv.update(overrides)
        return rv

    def get_default_prog_name(self, cli: CLI) -> str:
        """Given a command object it will return the default program name for
        it.

        The default is the `name` attribute or ``"root"`` if not
        set.
        """
        return cli.name or "root"


class Result:
    """Holds the captured result of an invoked CLI script."""

    def __init__(
        self,
        runner: CliRunner,
        stdout_bytes: bytes,
        stderr_bytes: bytes | None,
        return_value: t.Any,
        exit_code: int,
        exception: BaseException | None,
        exc_info: (
            tuple[type[BaseException], BaseException, TracebackType] | None
        ) = None,
    ):
        #: The runner that created the result
        self.runner = runner
        #: The standard output as bytes.
        self.stdout_bytes = stdout_bytes
        #: The standard error as bytes, or None if not available
        self.stderr_bytes = stderr_bytes
        #: The value returned from the invoked command.
        #:
        #: .. versionadded:: 8.0
        self.return_value = return_value
        #: The exit code as integer.
        self.exit_code = exit_code
        #: The exception that happened if one did.
        self.exception = exception
        #: The traceback
        self.exc_info = exc_info

    @property
    def output(self) -> str:
        """The (standard) output as unicode string."""
        return self.stdout

    @property
    def stdout(self) -> str:
        """The standard output as unicode string."""
        return self.stdout_bytes.decode(self.runner.charset, "replace").replace(
            "\r\n", "\n"
        )

    @property
    def stderr(self) -> str:
        """The standard error as unicode string."""
        if self.stderr_bytes is None:
            raise ValueError("stderr not separately captured")
        return self.stderr_bytes.decode(self.runner.charset, "replace").replace(
            "\r\n", "\n"
        )

    def __repr__(self) -> str:
        exc_str = repr(self.exception) if self.exception else "okay"
        return f"<{type(self).__name__} {exc_str}>"


class _NamedTextIOWrapper(io.TextIOWrapper):
    def __init__(
        self, buffer: t.BinaryIO, name: str, mode: str, **kwargs: t.Any
    ) -> None:
        super().__init__(buffer, **kwargs)
        self._name = name
        self._mode = mode

    @property
    def name(self) -> str:
        return self._name

    @property
    def mode(self) -> str:
        return self._mode


def make_input_stream(input: str | bytes | t.IO | None, charset: str) -> t.BinaryIO:
    # Is already an input stream.
    if hasattr(input, "read"):
        rv = _find_binary_reader(t.cast(t.IO, input))

        if rv is not None:
            return rv

        raise TypeError("Could not find binary reader for input stream.")

    if input is None:
        input_b = b""
    elif isinstance(input, str):
        input_b = input.encode(charset)
    else:
        input_b = input

    return io.BytesIO(input_b)


def _is_binary_reader(stream: t.IO, default: bool = False) -> bool:
    try:
        return isinstance(stream.read(0), bytes)
    except Exception:
        return default
        # This happens in some cases where the stream was already
        # closed.  In this case, we assume the default.


def _find_binary_reader(stream: t.IO) -> t.BinaryIO | None:
    # We need to figure out if the given stream is already binary.
    # This can happen because the official docs recommend detaching
    # the streams to get binary streams.  Some code might do this, so
    # we need to deal with this case explicitly.
    if _is_binary_reader(stream, False):
        return t.cast(t.BinaryIO, stream)

    buf = getattr(stream, "buffer", None)

    # Same situation here; this time we assume that the buffer is
    # actually binary in case it's closed.
    if buf is not None and _is_binary_reader(buf, True):
        return t.cast(t.BinaryIO, buf)

    return None
