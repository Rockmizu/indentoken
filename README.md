# indentoken

協助你管理字串縮排的一個魔法小 token。

## 目錄（Table of Contents）

* [開發動機（Motivation）](#開發動機motivation)
* [關鍵特色（Features）](#關鍵特色features)
* [環境需求（Requirements）](#環境需求requirements)
* [安裝步驟（Installation）](#安裝步驟installation)
* [使用方式（Usage）](#使用方式usage)
  * [基本縮排與退縮排](#基本縮排與退縮排)
  * [使用 context manager 進行縮排](#使用-context-manager-進行縮排)
  * [多行文字縮排](#多行文字縮排)
  * [初始化](#初始化)
  * [填充（Padding）](#填充padding)
  * [縮排的加法及乘法](#縮排的加法及乘法)
  * [多參數 print](#多參數-print)
* [授權條款（License）](#授權條款license)

## 開發動機（Motivation）

你曾經有過希望讓程式輸出這種排版的時候嗎？

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

在普通情況下，你需要手動追蹤目前縮排深度：

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

這種方式不僅非常容易出錯，在將子迴圈拆進函數時更是難以追蹤前面的空白是怎麼來的。

如果有一個可以協助你追蹤縮排的工具該有多好。
這正是 indentoken 可以幫上忙的地方！
現在你可以寫：

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

注意到手動空白消失了，取而代之的是一個 `ind` 物件幫你追蹤縮排深度並轉成字串。

你也可以將它傳進函數以持續追蹤目前縮排：

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

除此之外還有更多功能，請查看[使用方式](#使用方式usage)。

## 關鍵特色（Features）

1. 多功能且便利的縮排追蹤 token。
2. 完整的型別註釋，並支援現代化的型別檢查以及型別安全開發。
3. 零套件依賴，安裝時不用擔心與虛擬環境中的其他套件發生衝突。
4. 純 Python 套件，不包含 C extension，可以在任何能跑 Python 的地方使用。

## 環境需求（Requirements）

本套件支援 Python 3.10 以上的環境。

## 安裝步驟（Installation）

你可以透過 pip 安裝本套件：

```bash
pip install indentoken
```

## 使用方式（Usage）

以下範例假設你已經匯入：

```python
from indentoken import Indentation
```

### 基本縮排與退縮排

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

### 使用 context manager 進行縮排

如果你希望在某個區塊中增加縮排，我推薦使用 `with` 加上 `indented_context()`。
這會確保在拋出例外時也能夠自動回到正確的縮排深度。

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

最後你會得到像是這樣的輸出：

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

### 多行文字縮排

對於多行文字，你可以直接將其包裹在 `ind` 裡面或使用 `apply_to()` 方法：

```python
ind = Indentation(level=1)

print('No indentation.')
print(ind('This is a multi-line text.\nAll lines will be indented.\nThe third line.'))
# ind('something') is equivalent to ind.apply_to('something')
```

會輸出

```text
No indentation.
  This is a multi-line text.
  All lines will be indented.
  The third line.
```

### 初始化

初始化階段你可以指定縮排文字、初始縮排深度和 padding（後面會提到）。

```python
ind = Indentation(word='-->', level=2)
print(f'{ind}Line 1')  # |-->-->Line 1
ind.indent()
print(f'{ind}Line 2')  # |-->-->-->Line 2
```

### 填充（Padding）

如果你希望縮排的起始點不是從最左邊開始，你可以指定 padding：

```python
# Use "+++++" as padding for visualization. You can use whitespaces.
ind = Indentation(word='-->', padding='+++++')
print(f'{ind}Line 1')  # |+++++Line 1
ind.indent()
print(f'{ind}Line 2')  # |+++++-->Line 2
ind.indent()
print(f'{ind}Line 3')  # |+++++-->-->Line 3
```

Padding 不會隨縮排深度改變，它始終存在，即使縮排深度為零。

你也可以指定 `Indentation` 物件為 padding，這會為你帶來動態 padding 效果：

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

### 縮排的加法及乘法

如果你臨時需要加深縮排，又不想要使用厚重的 `with` 陳述式，
你可以直接將想要增加的縮排深度加在縮排物件上。

另外，`Indentation` 加法只會改變縮排深度，並不會改變 padding。

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

乘法則等同於先將 `Indentation` 轉成字串後再進行字串乘法。
注意這會包含 padding 部分：

```python
ind = Indentation(word='-->', level=2)
print(f'{ind * 3}indented')  # |-->-->-->-->-->-->indented

# Note that the padding will repeat 3 times as well.
ind = Indentation(word='-->', level=2, padding='++')
print(f'{ind * 3}indented')  # |++-->-->++-->-->++-->-->indented
```

`Indentation` 的加法和乘法符合交換律：

```python
ind = Indentation(word='-->', level=2)
assert ind + 1 == 1 + ind
assert ind * 2 == 2 * ind
```

### 多參數 print

如果你希望下面這種寫法也能獲得縮排，你可以用 `Indentation` 物件包裹 `print` 函數。

```python
print('Alice', 'Bob', sep=' & ')  # |Alice & Bob

ind = Indentation(word='-->', level=1)
ind(print)('Alice', 'Bob', sep=' & ')  # |-->Alice & Bob
# Note that the parentheses wrap the `print`, not the entire statement.
```

請注意，若你將 `ind(print)` 保存下來，它會綁定這個 `Indentation` 物件。
如果你不希望 `print` 隨 `Indentation` 物件改變，你可以用 `fixed()` 方法。

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

## 授權條款（License）

本軟體採用 MIT 授權，詳細內容請看 [LICENSE](LICENSE) 檔案。
