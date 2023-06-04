目前只需要改commands/DB.py就行了



自己实现的功能先自己建个分支比较好



# 任务

## SQL解释器

目标： 抽象出AST

反正不是现在做

## SQL代码执行
### 1. 方法完成情况

#### 交给XJW

- [ ] delete方法

- [ ] drop方法

#### 交给CXL

- [x] select方法

- [ ] where方法

#### 交给YS

#### 交给LZH

#### 无人认领

- [ ] insert方法

- [ ] update方法

- [ ] create方法

### 2. 需要做的方法总览

**delete**

```python
def delete(
    self,
    table: pd.DataFrame,
    del_rows: list[int]
) -> bool:
```


**drop**

```python
def drop(
    self,
    table: pd.DataFrame,
) -> bool:
```

**create**

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
