from sql_parse import tokens
import enum

class AST_KEYWORDS(enum.IntEnum):
    STATEMENT = 0
    CLAUSE = 1
    EXPRESSION = 2

class _statement:
    def __init__(self):
        self.attribute = AST_KEYWORDS.STATEMENT
        self.content = []
        self.value = None
    
    def deal(self, cls, value):
        if cls in tokens.Name:
            self.content.append(value)

class _clause:
    def __init__(self):
        self.attribute = AST_KEYWORDS.CLAUSE
        self.content = []

    def deal(self, cls, value):
        """
        对于一个非关键词的token，根据自己clause的类型，将其加入到自己的内容中
        """
        # 当前columns的类型决定其会记录columns
        if self.value in ["SELECT"]: 
            if cls in tokens.Name:
                self.content.append(value)
        # 当前clause的类型决定其会记录tables
        if self.value in ["FROM"]: 
            if cls in tokens.Name:
                self.content.append(value)
        # 当前clause的类型决定其会记录一个表达式
        # TODO: 完成一些例如CREATE，PRIMARY之类的处理

        # WHERE很特殊，之后WHERE会被重复利用一次，以完成多个表达式的连接
        # 因此理论上WHERE clause不可能接受到非关键词token(忽略)，WHERE　expression才会接受到
        if self.value in ["WHERE"]: 
            if cls in tokens.Name:
                raise Exception("WHERE clause should not read non-keyword token\n Only WHERE expression do")

class _expression:
    def __init__(self):
        self.attribute = AST_KEYWORDS.EXPRESSION
        self.content = []

    def deal(self, cls, value):
        """
        对于一个非关键词的token，根据自己expression的类型，将其加入到自己的内容中
        """
        if self.value in ["WHERE", "AND", "OR"]: 
            if cls in tokens.Name or cls in tokens.Literal:
                if self.content == []: # 左边
                    sub_expr_left = {"left": Numerize(cls,value), "op": None, "right": None}
                    self.content.append(sub_expr_left)
                else: # 右边
                    self.content[0]["right"] = Numerize(cls,value)
            if cls in tokens.Operator: # 中间的Operator
                self.content[0]["op"] = value


def Numerize(cls, text: str):
    """
    将token的text转换为对应的数字（如果需要的话）
    """
    if cls not in tokens.Literal:
        return text
    if cls == tokens.Literal.String:
        return text
    if cls in tokens.Literal.Number:
        if cls == tokens.Literal.Number.Float:
            return float(text)
        if cls == tokens.Literal.Number.Integer:
            return int(text)
        if cls == tokens.Literal.Number.Hexadecimal:
            return int(text, 16)
    
