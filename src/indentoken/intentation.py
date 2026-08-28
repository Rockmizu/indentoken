from __future__ import annotations

import contextlib
import functools
import textwrap
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from io import StringIO
from typing import ParamSpec, TypeVar, overload

from .feature_flags import INDENTOKEN_ENABLE_IT_METHOD

__all__ = ['Indentation']


T = TypeVar('T')

P = ParamSpec('P')
R = TypeVar('R')


def _wrap_print_with_post_process(
    print_fn: Callable[P, R],
    post_process: Callable[[str], str],
) -> Callable[P, R]:
    @functools.wraps(print_fn)
    def print_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        file = kwargs.pop('file', None)
        flush = kwargs.pop('flush', False)
        buffer = StringIO()
        print_fn(*args, **kwargs, file=buffer, flush=False)  # type: ignore

        text = buffer.getvalue()
        text = post_process(text)
        return print_fn(text, end='', file=file, flush=flush)  # type: ignore

    return print_wrapper


@dataclass(slots=True, init=False, eq=False)
class Indentation:
    """
    A magic token that can be used as an indentation string.
    """

    word: str = '  '
    _level: int = field(init=False)
    padding: str | Indentation = field(default='', kw_only=True)

    def __init__(
        self,
        word: str = '  ',
        level: int = 0,
        *,
        padding: str | Indentation = '',
    ) -> None:
        """
        Initialize the Indentation object.

        Args:
            word: The string used for indentation (e.g., '  ').
            level: The initial indentation level. Must be non-negative.
            padding: Optional padding object or string.
        """
        if level < 0:
            raise ValueError('`level` must be non-negative')
        self.word = word
        self.level = level
        self.padding = padding

    @property
    def level(self) -> int:
        """
        Get the current indentation level.

        Returns:
            The current indentation level.
        """
        return self._level

    @level.setter
    def level(self, level: int, /) -> None:
        """
        Set the current indentation level.

        Args:
            level: The new indentation level.

        Raises:
            ValueError: If the provided `level` is negative.
        """
        if level < 0:
            raise ValueError('`level` must be non-negative')
        self._level = level

    @property
    def padding_str(self) -> str:
        """
        Get the padding string representation.

        Returns:
            The string representation of the padding.
        """
        return str(self.padding)

    def copy(self) -> Indentation:
        """
        Create a copy of the current Indentation object.

        Returns:
            A new Indentation instance with the same properties.
        """
        return Indentation(
            word=self.word,
            level=self._level,
            padding=self.padding,
        )

    def indent(self, delta: int = 1, /) -> None:
        """
        Increase the indentation level by `delta`.

        * Positive values increase the indentation level.
        * Negative values decrease the indentation level.
        * The level is clamped at zero.

        Args:
            delta: The amount to increase the level by. Defaults to 1.
        """
        self._level = max(0, self.level + delta)

    def dedent(self, delta: int = 1, /) -> None:
        """
        Decrease the indentation level by `delta`.

        * Positive values decrease the indentation level.
        * Negative values increase the indentation level.
        * The level is clamped at zero.

        Args:
            delta: The amount to decrease the level by. Defaults to 1.
        """
        self._level = max(0, self.level - delta)

    @contextlib.contextmanager
    def indented_context(self, level: int = 1, /):
        """
        Context manager to temporarily change the indentation level.

        Args:
            level: The amount to change the indentation level by. Defaults to 1.

        Yields:
            Indentation: The current Indentation instance within the context.
        """
        if level < -self._level:  # noqa: PLR1730
            level = -self._level

        self.indent(level)
        try:
            yield self
        finally:
            self.dedent(level)

    def apply_to(self, text: str, /) -> str:
        """
        Apply the current indentation to a given string.

        Args:
            text: The string to be indented.

        Returns:
            The indented string.
        """
        return textwrap.indent(text, prefix=str(self))

    def fixed(self, print_fn: Callable[P, R], /) -> Callable[P, R]:
        """
        Create a print function wrapper that applies indentation.

        Args:
            print_fn: The original print function to wrap.

        Returns:
            A wrapped print function that applies indentation.
        """
        return _wrap_print_with_post_process(
            print_fn,
            functools.partial(textwrap.indent, prefix=str(self)),
        )

    if INDENTOKEN_ENABLE_IT_METHOD:

        def it(self, iterable: Iterable[T], /, delta: int = 1) -> Iterable[T]:
            """
            Wrap an iterable to provide the effect of `indented_context()`
            before the iteration completes.

            This method is particularly useful when you want additional
            indentation during a `for` loop without adding an extra layer of
            indentation to the source code.

            E.g. You can write

            ```python
            ind = Indentation()

            for item in ind.it(items):
                print(f'{ind}{item}')

            print(f'{ind}no indentation after loop')
            ```

            instead of

            ```python
            ind = Indentation()

            with ind.indented_context():
                for item in items:
                    print(f'{ind}{item}')

            print(f'{ind}no indentation after loop')
            ```

            Args:
                iterable: The iterable to yield from.
                delta: The amount to change the indentation level by. Defaults to 1.

            Yields:
                Elements from the iterable, indented.
            """
            with self.indented_context(delta):
                yield from iterable

    @overload
    def __call__(self, text: str, /) -> str: ...
    @overload
    def __call__(self, print_fn: Callable[P, R], /) -> Callable[P, R]: ...
    def __call__(self, text_or_print_fn: str | Callable[P, R], /) -> str | Callable[P, R]:
        """
        Apply the current indentation to a given text or
        wrap a print function to apply indentation to its output.

        Args:
            text_or_print_fn: The string to indent, or the print function to wrap.

        Returns:
            The indented string if `text_or_print_fn` is a string, or the wrapped print function if it is a callable.
        """
        if isinstance(text_or_print_fn, str):
            return self.apply_to(text_or_print_fn)

        return _wrap_print_with_post_process(
            text_or_print_fn,
            self.apply_to,
        )

    def __mul__(self, times: int, /) -> str:
        """
        Repeat the indentation string by a given number of times.

        This method works essentially the same as the built-in `str` type.
        Note that this repetition is based on the current
        indentation depth (including padding).

        Args:
            times: The number of times to repeat the indentation string.

        Returns:
            The repeated indentation string.
        """
        return str(self) * times

    def __rmul__(self, times: int, /) -> str:
        """
        Repeat the indentation string by a given number of times.

        This method works essentially the same as the built-in `str` type.
        Note that this repetition is based on the current
        indentation depth (including padding).

        Args:
            times: The number of times to repeat the indentation string.

        Returns:
            The repeated indentation string.
        """
        return times * str(self)

    def __add__(self, amount: int, /) -> str:
        """
        Return a string, which is the stringified result
        as if adding `delta` level to this object.

        ```python
        ind = Indentation('->', level=2)
        s1 = ind + 3  # s1 = '->->->->->'
        assert ind.level == 2  # won't affect the original object
        ind.indent(2)
        s2 = str(ind)  # s2 = '->->->->->'
        assert s1 == s2
        ```

        This is useful when you suddenly need more indentation levels
        but don't want to use a context manager.

        E.g.:

        ```python
        ind = Indentation()

        print(f'{ind}not indented')
        with ind.indented_context():
            print(f'{ind}one level indented')
            print(f'{ind}one level indented')
            print(f'{ind + 1}one level deeper; two level indented')
            print(f'{ind}one level indented')
            print(f'{ind}one level indented')

        # will output:
        # not indented
        #   one level indented
        #   one level indented
        #     one level deeper; two level indented
        #   one level indented
        #   one level indented
        ```

        Args:
            times: The number of times to append the indentation string.

        Returns:
            The extended indentation string.
        """
        return str(self) + self.word * amount

    def __radd__(self, amount: int, /) -> str:
        """
        Return a string, which is the stringified result
        as if adding `amount` level to this object.

        This is useful when you suddenly need more indentation levels
        but don't want to use a context manager.

        E.g.:

        ```python
        ind = Indentation()

        print(f'{ind}not indented')
        with ind.indented_context():
            print(f'{ind}one level indented')
            print(f'{ind}one level indented')
            print(f'{1 + ind}one level deeper; two level indented')
            print(f'{ind}one level indented')
            print(f'{ind}one level indented')

        # will output:
        # not indented
        #   one level indented
        #   one level indented
        #     one level deeper; two level indented
        #   one level indented
        #   one level indented
        ```

        Args:
            times: The number of times to append the indentation string.

        Returns:
            The extended indentation string.
        """
        return str(self) + self.word * amount

    def __str__(self) -> str:
        """
        Return the string representation of the indentation.

        Returns:
            The string representing the indentation (padding + word * level).
        """
        return str(self.padding) + self.word * self._level
