# indentoken

A magical little token to help you manage string indentation.

## Table of Contents

* [Motivation](#motivation)
* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
  * [Basic Indentation and Dedentation](#basic-indentation-and-dedentation)
  * [Using Context Manager for Indentation](#using-context-manager-for-indentation)
  * [Multi-line Text Indentation](#multi-line-text-indentation)
  * [Initialization](#initialization)
  * [Padding](#padding)
  * [Indentation Addition](#indentation-addition)
  * [Multi-parameter Print](#multi-parameter-print)
* [License](#license)

## Motivation

Have you ever wanted your program output to look like this?

```text
food
  fruit
    apple
    banana
  --------
  meat
    pork
    beef
  --------
```

Normally, you need to manually track the current indentation depth:

```python
foods = {'fruit': ['apple', 'banana'], 'meat': ['pork', 'beef']}

print('food')
for category, items in foods.items():
    print(f'  {category}')
    #       ^^ manually track the indentations
    for item in items:
        print(f'    {item}')
        #       ^^^^ manually track the indentations
    print(f'  --------')
    #       ^^ manually track the indentations
```

This method is not only very prone to errors, but it becomes even harder
to track the preceding whitespace when breaking down sub-loops
into functions.

How great would it be if there was a tool to help you track indentation.

This is exactly where indentoken can help!

Now you can write:

```python
from indentoken import Indentation

ind = Indentation()

foods = {'fruit': ['apple', 'banana'], 'meat': ['pork', 'beef']}

print('food')

with ind.indented_context():
    for category, items in foods.items():
        print(f'{ind}{category}')

        with ind.indented_context():
            for item in items:
                print(f'{ind}{item}')

        print(f'{ind}--------')
```

Notice how the manual whitespace disappears, replaced by an `ind` object
that tracks the indentation depth and converts it to a string for you.

You can also pass it into a function to continuously track
the current indentation:

```python
from collections.abc import Iterable

from indentoken import Indentation


def main() -> None:
    ind = Indentation()

    foods = {'fruit': ['apple', 'banana'], 'meat': ['pork', 'beef']}

    print('food')

    with ind.indented_context():
        for category, items in foods.items():
            print(f'{ind}{category}')

            with ind.indented_context():
                show_food_items(items, ind=ind)

            print(f'{ind}--------')


def show_food_items(items: Iterable[str], *, ind: Indentation) -> None:
    for item in items:
        print(f'{ind}{item}')


if __name__ == '__main__':
    main()
```

There are more features, please see [Usage](#usage).

## Features

1. Multifunctional and convenient indentation tracking token.
2. Complete type annotations, supporting modern type checking
   and type-safe development.
3. Zero package dependencies, so you don't have to worry about conflicts with
   other packages in your virtual environment during installation.
4. Pure Python package, no C extensions, usable anywhere Python runs.

## Requirements

This package supports Python 3.10 and above.

## Installation

You can install this package using pip:

```bash
pip install indentoken
```

## Usage

The following examples assume you have imported:

```python
from indentoken import Indentation
```

### Basic Indentation and Dedentation

```python
ind = Indentation()

# Have no intentation at all initally.
print(f'{ind}Line 1')  # |Line 1

# Indent by 1 level.
ind.indent()
print(f'{ind}Line 2')  # |  Line 2

# Indent by 3 levels, plus the previous 1 level.
# Now the indentation is 4 levels deep.
ind.indent(3)
print(f'{ind}Line 3')  # |        Line 3

# Dedent by 1 level.
# Now the indentation is 3 levels deep.
ind.dedent()
print(f'{ind}Line 4')  # |      Line 4

# Dedent by 99 levels.
# Note that the indentation level is always non-negative.
# The final indentation level will be clamped at 0.
ind.dedent(99)
assert ind.level == 0
print(f'{ind}Line 5')  # |Line 5

# Directly set the current indentation level to 3.
ind.level = 3
print(f'{ind}Line 6')  # |      Line 6
```

### Using Context Manager for Indentation

If you want to increase indentation within a certain block, I recommend
using `with` combined with `indented_context()`.
This ensures that the indentation automatically reverts to
the correct depth even if an exception is raised.

```python
ind = Indentation()

print(f'{ind}This line is NOT indented.')  # |This line is NOT indented.
print(f'{ind}This line is NOT indented.')  # |This line is NOT indented.
with ind.indented_context():
    print(f'{ind}This line is indented.')  # |  This line is indented.
    print(f'{ind}This line is indented.')  # |  This line is indented.
print(f'{ind}This line is NOT indented.')  # |This line is NOT indented.
print(f'{ind}This line is NOT indented.')  # |This line is NOT indented.
with ind.indented_context(2):
    print(f'{ind}This line is indented by 2 levels.')  # |    This line is indented by 2 levels.
    print(f'{ind}This line is indented by 2 levels.')  # |    This line is indented by 2 levels.
    with ind.indented_context(1):  # nested indented context will stack
        print(f'{ind}This line is indented by 3 levels.')  # |      This line is indented by 3 levels.
        print(f'{ind}This line is indented by 3 levels.')  # |      This line is indented by 3 levels.
    print(f'{ind}This line is indented by 2 levels.')  # |    This line is indented by 2 levels.
```

The output you will get is like this:

```text
This line is NOT indented.
This line is NOT indented.
  This line is indented.
  This line is indented.
This line is NOT indented.
This line is NOT indented.
    This line is indented by 2 levels.
    This line is indented by 2 levels.
      This line is indented by 3 levels.
      This line is indented by 3 levels.
    This line is indented by 2 levels.
```

### Multi-line Text Indentation

For multi-line text, you can directly wrap it in `ind`
or use the `apply_to()` method:

```python
ind = Indentation(level=1)

print('No indentation.')
print(ind('This is a multi-line text.\nAll lines will be indented.\nThe third line.'))
# ind('something') is equivalent to ind.apply_to('something')
```

It will output:

```text
No indentation.
  This is a multi-line text.
  All lines will be indented.
  The third line.
```

### Initialization

During initialization, you can specify the indentation characters,
initial indentation depth, and padding (which will be mentioned later).

```python
ind = Indentation(word='-->', level=2)
print(f'{ind}Line 1')  # |-->-->Line 1
ind.indent()
print(f'{ind}Line 2')  # |-->-->-->Line 2
```

### Padding

If you want the starting point of the indentation not to begin
from the far left, you can specify padding:

```python
# Use "+++++" as padding for visualization. You can use whitespaces.
ind = Indentation(word='-->', padding='+++++')
print(f'{ind}Line 1')  # |+++++Line 1
ind.indent()
print(f'{ind}Line 2')  # |+++++-->Line 2
ind.indent()
print(f'{ind}Line 3')  # |+++++-->-->Line 3
```

Padding does not change with indentation depth and it always exists,
even if the indentation depth is zero.

You can also specify the `Indentation` object as padding,
which gives you dynamic padding effects:

```python
pad = Indentation(word='++', level=2)
ind = Indentation(word='-->', padding=pad)
print(f'{ind}Line 1')  # |++++Line 1
ind.indent()
print(f'{ind}Line 2')  # |++++-->Line 2
ind.indent()
print(f'{ind}Line 3')  # |++++-->-->Line 3
pad.dedent()  # Note that the `pad` object is changing, not `ind`.
print(f'{ind}Line 4')  # |++-->-->Line 4

# Convert the padding to `str` on init if you want a fixed padding.
pad = Indentation(word='++', level=2)
ind = Indentation(word='-->', level=1, padding=str(pad))
print(f'{ind}Line 5')  # |++++-->Line 5
pad.dedent()  # Note that the `pad` object is changing, not `ind`.
print(f'{ind}Line 6')  # |++++-->Line 6
```

### Indentation Addition

If you temporarily need to deepen the indentation
without using the heavy `with` statement, you can directly add
the desired indentation depth to the indentation object.

Additionally, `Indentation` addition only changes
the indentation depth and does not change the padding.

```python
ind = Indentation(word='-->', level=1)
print(f'{ind}one level indented')  # |-->one level indented
print(f'{ind}one level indented')  # |-->one level indented
print(f'{ind + 1}one level deeper, two levels indented')  # |-->-->one level deeper, two levels indented
print(f'{ind + 2}two levels deeper, three levels indented')  # |-->-->-->two levels deeper, three levels indented
print(f'{ind}one level indented')  # |-->one level indented
print(f'{ind}one level indented')  # |-->one level indented

ind = Indentation(word='-->', level=1, padding='++')
print(f'{ind}one level indented')  # |++-->one level indented
print(f'{ind + 1}one level deeper, two levels indented')  # |++-->-->one level deeper, two levels indented
```

Indentation addition is commutative:

```python
ind = Indentation(word='-->', level=2)
assert ind + 1 == 1 + ind
```

### Multi-parameter Print

If you want the following usage of `print` to also receive indentation,
you can wrap the `print` function with the `Indentation` object.

```python
print('Alice', 'Bob', sep=' & ')  # |Alice & Bob

ind = Indentation(word='-->', level=1)
ind(print)('Alice', 'Bob', sep=' & ')  # |-->Alice & Bob
# Note that the parentheses wrap the `print`, not the entire statement.
```

Note that if you save `ind(print)` for later use, it will bind
this `Indentation` object.
If you do not want the `print` to change with the `Indentation` object,
you can use the `fixed()` method.

```python
ind = Indentation(word='-->', level=1)

print_indented = ind(print)

print_indented('Alice')  # |-->Alice

ind.indent()
print_indented('Bob')  # |-->-->Bob

# ===========================================
ind = Indentation(word='-->', level=1)

# Use ind.fixed() to fixed the indentation.
print_indented_fixed = ind.fixed(print)

print_indented_fixed('Alice')  # |-->Alice

ind.indent()
print_indented_fixed('Bob')  # |-->Bob
```

## License

This software is distributed under the MIT License.
Please see the [LICENSE](LICENSE) file for details.
