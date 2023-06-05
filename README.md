目前只需要改commands/DB.py就行了



自己实现的功能先自己建个分支比较好



# 任务

## SQL解释器

### 1. 目标完成情况

目标： 

- [x] 完成对单串命令文本的token化（`tokenizer.py`）

输入：
```
"""
SELECT id, name, this
FROM table
WHERE id = 1 AND this < 2.3;
"""

```

输出：
```
[(Token.Keyword.DML, 'SELECT'), (Token.Text.Whitespace, ' '), (Token.Name, 'id'), (Token.Punctuation, ','), (Token.Text.Whitespace, ' '), (Token.Name, 'name'), (Token.Punctuation, ','), (Token.Text.Whitespace, ' '), (Token.Name, 'this'), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Keyword, 'FROM'), (Token.Text.Whitespace, ' '), (Token.Keyword, 'table'), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Keyword, 'WHERE'), (Token.Text.Whitespace, ' '), (Token.Name, 'id'), (Token.Text.Whitespace, ' '), (Token.Operator.Comparison, '='), (Token.Text.Whitespace, ' '), (Token.Literal.Number.Integer, '1'), (Token.Text.Whitespace, ' '), (Token.Keyword, 'AND'), (Token.Text.Whitespace, ' '), (Token.Name, 'this'), (Token.Text.Whitespace, ' '), (Token.Operator.Comparison, '<'), (Token.Text.Whitespace, ' '), (Token.Literal.Number.Float, '2.3'), (Token.Punctuation, ';')]
```

- [ ] 在token基础上，抽象出AST（`AST_builder.py`）

- [ ] 在AST基础上，实现对`sql_commands`的调用

### 2. 目标总览

## SQL代码执行
### 1. 方法完成情况

#### 交给XJW

- [x] delete方法（不完善，删去的对象没有保存于本地）

- [x] drop方法（有待争议，是丢掉整个对象，还是丢掉表中的所有行，但保留列属性？）

#### 交给CXL

- [x] select方法

- [ ] where方法

#### 交给YS

#### 交给LZH

#### 无人认领

- [ ] insert方法

- [ ] update方法

- [ ] create方法

### 2. 方法总览

**delete**

```python
def delete(
    self,
    table: pd.DataFrame,
    del_rows: list[int]
) -> bool:
```


**drop**

是drop整张表，删除其对象，还是

```python
def drop(
    self,
    table: pd.DataFrame,
) -> bool:
```

**create**

很明显这个还需要更多属性，例如，主键的`PRIMARY`，序列化的`SERIAL`，非空的`NOT NULL`

```python
def delete(
    self,
    table: pd.DataFrame,
    attributes: list[str],
    types: list[str]
) -> bool:
```


**insert**

```python
def insert(
    self,
    table: pd.DataFrame,
    attributes: list[str],
    values: list
) -> bool:
```


**update**

```python
def update(
    self,
    table: pd.DataFrame,
    update_rows: list[int],
    attributes: list[str],
    values: list
) -> bool:
```


**select**
```python
def select(
    self,
    table: pd.DataFrame,
    sel_columns: list[int],
    sel_rows: list[int]
) -> pd.DataFrame:
```

**where**
```python
def where(
    self,
    table: pd.DataFrame,
    attribute: str,
    value,
    operand
) -> list[int]:
```
