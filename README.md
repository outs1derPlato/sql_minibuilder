~~目前只需要改command/DB.py就行了~~

commands中的执行功能都差不多写完了，tokenize已完成，AST写了一点

可以完善AST，也可以实现AST与具体功能的结合

自己实现的功能先自己建个分支比较好

# 任务

## SQL解释器

### 1. 目标完成情况

目标： 

#### 1.1 对单串命令文本的token化

文件：（`tokenizer.py`）

完成情况：

- [x] 总体

输入：
```
"""
SELECT id, name, this
FROM table1
WHERE id = 1 AND this < 2.3;
"""

```

输出：
```
[(Token.Keyword.DML, 'SELECT'), (Token.Text.Whitespace, ' '), (Token.Name, 'id'), (Token.Punctuation, ','), (Token.Text.Whitespace, ' '), (Token.Name, 'name'), (Token.Punctuation, ','), (Token.Text.Whitespace, ' '), (Token.Name, 'this'), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Keyword, 'FROM'), (Token.Text.Whitespace, ' '), (Token.Keyword, 'table1'), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Text.Whitespace, ' '), (Token.Keyword, 'WHERE'), (Token.Text.Whitespace, ' '), (Token.Name, 'id'), (Token.Text.Whitespace, ' '), (Token.Operator.Comparison, '='), (Token.Text.Whitespace, ' '), (Token.Literal.Number.Integer, '1'), (Token.Text.Whitespace, ' '), (Token.Keyword, 'AND'), (Token.Text.Whitespace, ' '), (Token.Name, 'this'), (Token.Text.Whitespace, ' '), (Token.Operator.Comparison, '<'), (Token.Text.Whitespace, ' '), (Token.Literal.Number.Float, '2.3'), (Token.Punctuation, ';')]
```

#### 1.2 在token基础上，抽象出AST

文件：`AST_builder.py`

完成情况：

- [x] 对SELECT的解析

- [X] 对FROM的解析

- [x] 对WHERE的基础解析

- [ ] 对WHERE中AND、OR的正确顺序判断

- [x] 对SET的解析

- [x] 对UPDATE的解析

- [x] 对DELETE的解析

##### 星期五添加

- [x] 对SELECT时`WILDCARD`的解析（就是选中所有列，详见输入输出5）

- [x] 对CREATE时主键`PRIMARY`的解析

- [x] 对CREATE时非空`NOT NULL`的解析

- [ ] 对CREATE各种约束的解析（摆，不想做，因为外键有点麻烦）

- [x] 对SET赋值式右边的Binary Expression的解析（抱歉的是SET时的expression结构也换了，换成assignment了，详见输出2）

- [x] 对CREATE的解析

- [x] 对INSERT INTO的解析


**目前已部分完成，只到能够解析查询命令（SELECT）、更新命令（UPDATE）、删除命令（DELETE）与基础创建命令（CREATE）（不包含NOT NULL）的地方**

输入1：
```
SELECT id, name, this
FROM table1
WHERE id = 1 AND this < 2.3;
```

期望输出：
```
statements: [
    - SelectStmt {
        type: "select_stmt"
        - clauses: [
            - SelectClause {
                type: "select_clause"
                - columns: [
                    - "id"
                    - "name"
                    - "this"
                ]
            }
            - FromClause {
                type: "from_clause"
                - tables: [
                    - "table1"
                ]
            }
            - WhereClause {
                type: "where_clause"
                - exprs: [
                    operator: "AND"
                    left: exprs[
                        operator: "="
                        left: "id"
                        right: 1
                    ]
                    right: exprs[
                        operator: "<"
                        left: "this"
                        right: 2.3
                    ]
                ]
            }
        ]
    }
]
```

**实际输出1**：
（可以看到`WHERE`被利用了两次，一次是作为`CLAUSE`，一次是作为`EXPRESSION`）
```
SELECT                                             level:AST_KEYWORDS.CLAUSE
-- id
-- name
-- this
FROM                                               level:AST_KEYWORDS.CLAUSE
-- table1
WHERE                                              level:AST_KEYWORDS.CLAUSE
--WHERE                                            level:AST_KEYWORDS.EXPRESSION
---- {'left': 'id', 'op': '=', 'right': 1}
--AND                                              level:AST_KEYWORDS.EXPRESSION
---- {'left': 'this', 'op': '<', 'right': 2.3}
```


输入2：
```
UPDATE table1
SET alexa = 50000, country='USA', salary = salary * 14.5
WHERE id = 1 AND this < 2.3 OR name>1;
```

**实际输出2**：
```
UPDATE                                                       level:AST_KEYWORDS.CLAUSE                          
-- table1
SET                                                          level:AST_KEYWORDS.CLAUSE
--SET                                                        level:AST_KEYWORDS.EXPRESSION
---- {'assignment': 'alexa', 'expression': {'left': 50000}}
--SET                                                        level:AST_KEYWORDS.EXPRESSION
---- {'assignment': 'country', 'expression': {'left': 'USA'}}
--SET                                                        level:AST_KEYWORDS.EXPRESSION
---- {'assignment': 'salary', 'expression': {'left': 'salary', 'op': '*', 'right': 14.5}}
WHERE                                                        level:AST_KEYWORDS.CLAUSE
--WHERE                                                      level:AST_KEYWORDS.EXPRESSION
---- {'left': 'id', 'op': '=', 'right': 1}
--AND                                                        level:AST_KEYWORDS.EXPRESSION
---- {'left': 'this', 'op': '<', 'right': 2.3}
--OR                                                         level:AST_KEYWORDS.EXPRESSION
---- {'left': 'name', 'op': '>', 'right': 1}
```

输入3：
```
DELETE table1
WHERE id = 1 AND this < 2.3 OR name>1;
```

**实际输出3**：
```
DELETE                                                       level:AST_KEYWORDS.CLAUSE

WHERE                                                        level:AST_KEYWORDS.CLAUSE

--WHERE                                                      level:AST_KEYWORDS.EXPRESSION

---- {'left': 'id', 'op': '=', 'right': 1}
--AND                                                        level:AST_KEYWORDS.EXPRESSION

---- {'left': 'this', 'op': '<', 'right': 2.3}
--OR                                                         level:AST_KEYWORDS.EXPRESSION

---- {'left': 'name', 'op': '>', 'right': 1}
```

输入4：
```
CREATE TABLE Persons
(
    PersonID SERIAL int,
    LastName PRIMARY varchar(255),
    FirstName char(255) NOT NULL,
    Address float,
    City varchar(255)
);
```


**实际输出4**:
```
CREATE                                                       level:AST_KEYWORDS.CLAUSE
-- Persons
COLUMNS                                                      level:AST_KEYWORDS.CLAUSE
--COLUMN_DEFINITION                                          level:AST_KEYWORDS.COLUMN_DEFINITION
---- {'PRIMARY': False, 'NOT NULL': False, 'name': 'PERSONID', 'type': 'int'}
--COLUMN_DEFINITION                                          level:AST_KEYWORDS.COLUMN_DEFINITION
---- {'PRIMARY': True, 'NOT NULL': False, 'name': 'LASTNAME', 'type': 'varchar', 'length': 255}
--COLUMN_DEFINITION                                          level:AST_KEYWORDS.COLUMN_DEFINITION
---- {'PRIMARY': False, 'NOT NULL': True, 'name': 'FIRSTNAME', 'type': 'char', 'length': 255}
--COLUMN_DEFINITION                                          level:AST_KEYWORDS.COLUMN_DEFINITION
---- {'PRIMARY': False, 'NOT NULL': False, 'name': 'ADDRESS', 'type': 'float'}
--COLUMN_DEFINITION                                          level:AST_KEYWORDS.COLUMN_DEFINITION
---- {'PRIMARY': False, 'NOT NULL': False, 'name': 'CITY', 'type': 'varchar', 'length': 255}
```

输入5：（与输入1相比，SELECT所有列）：
```
SELECT *
FROM table1, table2
WHERE id = 1 AND "this" < 2.3;
```

**实际输出5**：
```
SELECT                                                       level:AST_KEYWORDS.CLAUSE
-- Token.Wildcard
FROM                                                         level:AST_KEYWORDS.CLAUSE
-- table1
-- table2
WHERE                                                        level:AST_KEYWORDS.CLAUSE
--WHERE                                                      level:AST_KEYWORDS.EXPRESSION
---- {'left': 'id', 'op': '=', 'right': 1}
--AND                                                        level:AST_KEYWORDS.EXPRESSION
---- {'left': 'this', 'op': '<', 'right': 2.3}
```

输入6：
```
INSERT INTO table1 (id, name, this)
VALUES (1, 'alex', 2.3);
```

**实际输出6**：
```
INSERT                                                       level:AST_KEYWORDS.CLAUSE
-- table1
COLUMNS                                                      level:AST_KEYWORDS.CLAUSE
-- id
-- name
-- this
VALUES                                                       level:AST_KEYWORDS.CLAUSE
-- 1
-- alex
-- 2.3
```

输入7：（与输入6的区别在于，INSERT INTO未指定表名）
```
INSERT INTO table1
VALUES (1, 'alex', 2.3);
```

**实际输出7**
```
INSERT                                                       level:AST_KEYWORDS.CLAUSE
-- table1
COLUMNS                                                      level:AST_KEYWORDS.CLAUSE
VALUES                                                       level:AST_KEYWORDS.CLAUSE
-- 1
-- alex
-- 2.3
```


**用语解释**：

- statement: 需要执行的一条语句，以`;`结尾

- clause: 语句中的子句，一般一个查询的SQL语句可以被分为`select caluse`，`from clause`, `where clause`

- expression: 一个表达式，一定包含一个Operator，常见的有`=`,`>`,`<`。值得注意的是表达式只会包含一个Operator，多个表达式如`WHERE a = 3 AND b = 4`，将会被解析成在名为WHERE的CLAUSE中，包含一个WHERE的EXPRESSION，和一个AND的EXPRESSION




#### 1.3 在AST基础上，实现对`sql_command`的调用，完成语句

文件：`sql_control/main.py`（示例用，之后可能会改）

- [x] 完成示例文件，演示如何结合AST与实现的`sql_command`，通过FROM语句获得databse中的表

- [ ] 完成AST与执行代码关于WHERE的结合

- [ ] 完成AST与执行代码关于SELECT的结合

- [ ] 完成AST与执行代码关于DELETE的结合

- [ ] 完成AST与执行代码关于UPDATE的结合

##### 星期五添加的

- [ ] 一个小问题：所以什么时候在硬盘写入文件，读入文件？

- [ ] 完成AST与执行代码关于SELECT的WILDCARD设置（也就是选中所有列，详见输入5，输出5）

- [ ] 完成AST与执行代码关于SET的右侧赋值式结合

- [ ] 完成AST与执行代码关于CREATE的基础结合，限制每一列的类型

- [ ] 完成AST与执行代码关于CREATE的主键设置,NOT NULL设置

- [ ] 完成AST与执行代码关于CREATE中类型有SERIAL时，在INSERT时主键的自动更新并插入



- [ ] 完成AST与执行代码关于INSERT的基础结合

- [ ] 完成AST与执行代码关于INSERT在表名未指定列时的正确处理（详见输入输出7）

- [ ] 更多……

### 2. 目标总览

## SQL代码执行
### 1. 方法完成情况

#### 交给XJW

- [x] delete方法（不完善，删去的对象没有保存于本地）

- [x] drop方法（有待争议，是丢掉整个对象，还是丢掉表中的所有行，但保留列属性？）

#### 交给CXL

- [x] select方法

- [x] where方法

#### 交给YS

- [x] insert方法

- [x] update方法

- [x] create方法

#### 交给LZH

#### 好像差不多都完成了，有问题之后再改


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
