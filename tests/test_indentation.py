from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from typing import Any

import pytest

from indentoken import Indentation
from indentoken.feature_flags import INDENTOKEN_ENABLE_IT_METHOD


def test_indent_method() -> None:
    ind = Indentation()
    assert ind.level == 0
    assert str(ind) == ''
    assert f'{ind}' == ''
    assert f'{ind}abc' == 'abc'
    assert f'abc{ind}def' == 'abcdef'

    ind.indent()
    assert ind.level == 1
    assert str(ind) == '  '
    assert f'{ind}' == '  '
    assert f'{ind}abc' == '  abc'
    assert f'abc{ind}def' == 'abc  def'

    ind.indent(1)
    assert ind.level == 2
    assert str(ind) == '    '
    assert f'{ind}' == '    '
    assert f'{ind}abc' == '    abc'
    assert f'abc{ind}def' == 'abc    def'

    ind.indent(2)
    assert ind.level == 4
    assert str(ind) == '        '
    assert f'{ind}' == '        '
    assert f'{ind}abc' == '        abc'
    assert f'abc{ind}def' == 'abc        def'


def test_dedent_method() -> None:
    ind = Indentation(level=5)
    assert ind.level == 5
    assert str(ind) == '          '
    assert f'{ind}' == '          '
    assert f'{ind}abc' == '          abc'
    assert f'abc{ind}def' == 'abc          def'

    ind.dedent()
    assert ind.level == 4
    assert str(ind) == '        '
    assert f'{ind}' == '        '
    assert f'{ind}abc' == '        abc'
    assert f'abc{ind}def' == 'abc        def'

    ind.dedent(1)
    assert ind.level == 3
    assert str(ind) == '      '
    assert f'{ind}' == '      '
    assert f'{ind}abc' == '      abc'
    assert f'abc{ind}def' == 'abc      def'

    ind.dedent(2)
    assert ind.level == 1
    assert str(ind) == '  '
    assert f'{ind}' == '  '
    assert f'{ind}abc' == '  abc'
    assert f'abc{ind}def' == 'abc  def'

    ind.dedent(9)
    assert ind.level == 0  # won't go under 0
    assert str(ind) == ''
    assert f'{ind}' == ''
    assert f'{ind}abc' == 'abc'
    assert f'abc{ind}def' == 'abcdef'


def test_word() -> None:
    ind = Indentation('    ')
    assert ind.word == '    '
    assert str(ind) == ''
    assert f'{ind}' == ''
    assert f'{ind}abc' == 'abc'
    assert f'abc{ind}def' == 'abcdef'

    ind.indent()
    assert str(ind) == '    '
    assert f'{ind}' == '    '
    assert f'{ind}abc' == '    abc'
    assert f'abc{ind}def' == 'abc    def'

    ind = Indentation('->')
    assert ind.word == '->'
    assert str(ind) == ''
    assert f'{ind}' == ''
    assert f'{ind}abc' == 'abc'
    assert f'abc{ind}def' == 'abcdef'

    ind.indent()
    assert str(ind) == '->'
    assert f'{ind}' == '->'
    assert f'{ind}abc' == '->abc'
    assert f'abc{ind}def' == 'abc->def'

    ind.indent()
    assert str(ind) == '->->'
    assert f'{ind}' == '->->'
    assert f'{ind}abc' == '->->abc'
    assert f'abc{ind}def' == 'abc->->def'


def test_copy() -> None:
    ind = Indentation()
    copied_ind = ind.copy()
    assert ind is not copied_ind
    assert ind.word == copied_ind.word
    assert ind.level == copied_ind.level
    assert ind.padding == copied_ind.padding


def test_indented_context() -> None:
    ind = Indentation()

    assert ind.level == 0
    assert str(ind) == ''
    assert f'{ind}' == ''
    assert f'{ind}abc' == 'abc'
    assert f'abc{ind}def' == 'abcdef'

    with ind.indented_context():
        assert ind.level == 1
        assert str(ind) == '  '
        assert f'{ind}' == '  '
        assert f'{ind}abc' == '  abc'
        assert f'abc{ind}def' == 'abc  def'

        with ind.indented_context(2):
            assert ind.level == 3
            assert str(ind) == '      '
            assert f'{ind}' == '      '
            assert f'{ind}abc' == '      abc'
            assert f'abc{ind}def' == 'abc      def'

        assert ind.level == 1
        assert str(ind) == '  '
        assert f'{ind}' == '  '
        assert f'{ind}abc' == '  abc'
        assert f'abc{ind}def' == 'abc  def'

    assert ind.level == 0
    assert str(ind) == ''
    assert f'{ind}' == ''
    assert f'{ind}abc' == 'abc'
    assert f'abc{ind}def' == 'abcdef'

    with suppress(ValueError), ind.indented_context():
        assert ind.level == 1
        assert str(ind) == '  '
        assert f'{ind}' == '  '
        assert f'{ind}abc' == '  abc'
        assert f'abc{ind}def' == 'abc  def'

        raise ValueError('test exception')

    assert ind.level == 0
    assert str(ind) == ''
    assert f'{ind}' == ''
    assert f'{ind}abc' == 'abc'
    assert f'abc{ind}def' == 'abcdef'


def test_padding_and_str() -> None:
    # Test with padding string
    ind_str_pad = Indentation(word='  ', padding='++++')
    assert ind_str_pad.padding_str == '++++'
    assert str(ind_str_pad) == '++++'
    assert f'{ind_str_pad}abc' == '++++abc'

    with ind_str_pad.indented_context():
        assert str(ind_str_pad) == '====  '
        assert f'{ind_str_pad}abc' == '====  abc'

    # Test with padding object
    pad_obj = Indentation(word='+++', level=1)
    ind_pad_obj = Indentation(word='->', padding=pad_obj)
    assert ind_pad_obj.padding_str == '+++'
    assert str(ind_pad_obj) == '+++', 'the padding should exist regardless of the current indentation level'
    assert f'{ind_pad_obj}abc' == '+++abc'
    with ind_pad_obj.indented_context():
        with ind_pad_obj.indented_context():
            assert f'{ind_pad_obj}abc' == '+++->->abc'
        assert f'{ind_pad_obj}abc' == '+++->abc', 'padding object should dynamically affect the padding part'
        pad_obj.indent()
        assert f'{ind_pad_obj}abc' == '++++++->abc', 'padding object should dynamically affect the padding part'
        pad_obj.dedent()
        assert f'{ind_pad_obj}abc' == '+++->abc', 'padding object should dynamically affect the padding part'


def test_apply_to() -> None:
    ind = Indentation(word='    ', level=1)
    assert ind.apply_to('line1') == '    line1'
    assert ind.apply_to('line1\nline2\nline3') == '    line1\n    line2\n    line3'


def test_apply_to_by_call() -> None:
    ind = Indentation(word='    ', level=1)
    assert ind('line1') == '    line1'
    assert ind('line1\nline2\nline3') == '    line1\n    line2\n    line3'


@pytest.mark.parametrize(
    ('print_args', 'print_kwargs', 'expected_out'),
    (
        (('Hello World',), {}, '->->Hello World\n'),
        (('line1\nline2',), {}, '->->line1\n->->line2\n'),
        (('Arg1', 'Arg2'), {'sep': ' | '}, '->->Arg1 | Arg2\n'),
    ),
)
def test_fixed_print(
    print_args: tuple[Any],
    print_kwargs: Mapping[str, Any],
    expected_out: str,
    capsys,
) -> None:
    ind = Indentation(word='->', level=2)
    print_indented = ind.fixed(print)

    # Test with a simple string
    print_indented(*print_args, **print_kwargs)
    captured = capsys.readouterr()
    assert captured.out == expected_out


if INDENTOKEN_ENABLE_IT_METHOD:

    def test_indented_iteration() -> None:
        ind = Indentation(word='->', level=1)

        assert f'{ind}abc' == '->abc'
        for item in ind.it(['xxx', 'yyy', 'zzz']):
            assert f'{ind}{item}' == f'->->{item}'
        assert f'{ind}abc' == '->abc'

        # Test iteration with custom delta level
        assert f'{ind}abc' == '->abc'
        for item in ind.it(['xxx', 'yyy', 'zzz'], delta=2):
            assert f'{ind}{item}' == f'->->->{item}'
        assert f'{ind}abc' == '->abc'


def test_multiplication_and_addition() -> None:
    ind = Indentation(word='->')

    # Test __mul__
    assert ind * 3 == ''
    with ind.indented_context():
        assert ind * 1 == '->'
        assert ind * 3 == '->->->'
        assert ind * 5 == '->->->->->'
        with ind.indented_context():
            assert isinstance(ind * 5, str)
            assert ind * 1 == '->->'
            assert ind * 2 == '->->->->'
            assert ind * 3 == '->->->->->->'
        assert 2 * ind == '->->'

    # Test __add__
    assert ind + 2 == '->->'
    with ind.indented_context():
        assert ind + 3 == '->->->->'
        assert ind + 5 == '->->->->->->'
        with ind.indented_context():
            assert isinstance(ind + 5, str)
            assert ind + 1 == '->->->'
            assert ind + 2 == '->->->->'
            assert ind + 3 == '->->->->->'
        assert 2 + ind == '->->->'


def test_negative_level_error() -> None:
    # Test initialization with negative level
    with pytest.raises(ValueError, match='`level` must be non-negative'):
        Indentation(level=-1)

    # Test setter with negative level
    ind = Indentation()
    with pytest.raises(ValueError, match='`level` must be non-negative'):
        ind.level = -1
