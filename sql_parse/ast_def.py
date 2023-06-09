from sql_parse import tokens
import enum

class AST_KEYWORDS(enum.IntEnum):
    STATEMENT = 0
    CLAUSE = 1
    EXPRESSION = 2
    COLUMN_DEFINITION = 10

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
        self.value = None

    def deal(self, cls, value):
        """
        对于一个非关键词的token，根据自己的类型，将其加入到自己的内容中
        """
        # 当前columns的类型决定其会记录columns
        if self.value in ["SELECT", "CREATE", "COLUMNS"]: 
            if cls in tokens.Name:
                self.content.append(value)
            elif cls in tokens.Wildcard:
                self.content.append(tokens.Wildcard)
        # 当前clause的类型决定其会记录tables
        if self.value in ["FROM", "UPDATE", "INSERT", "DROP", "TRUNCATE"]: 
            if cls in tokens.Name:
                self.content.append(value)
        # 当前clause的类型决定其会记录values，但并不是表达式
        if self.value in ["VALUES"]:
            if cls in tokens.Name or cls in tokens.Literal:
                self.content.append(Numerize(cls,value))

        # WHERE很特殊，之后WHERE会被重复利用一次，以完成多个表达式的连接
        # 因此理论上WHERE clause不可能接受到非关键词token(忽略)，WHERE　expression才会接受到
        if self.value in ["WHERE"]: 
            if cls in tokens.Name:
                raise Exception("WHERE clause should not read non-keyword token\n Only WHERE expression do")

class _expression:
    def __init__(self):
        self.attribute = AST_KEYWORDS.EXPRESSION
        self.content = []
        self.value = None

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
        if self.value in ["SET"]:
            if cls in tokens.Name or cls in tokens.Literal:
                if self.content == []: # 左边
                    sub_expr_left = {"assignment": Numerize(cls,value), "expression": None}
                    self.content.append(sub_expr_left)
                else: # 右边
                    if self.content[0]["expression"] == None:
                        self.content[0]["expression"] = dict()
                        self.content[0]["expression"]["left"] = Numerize(cls,value)
                    else:
                        self.content[0]["expression"]["right"] = Numerize(cls,value)
            if cls in tokens.Operator or cls in tokens.Wildcard: # 中间的Operator,Wildcard是指*
                if self.content[0]["expression"] == None:
                    pass
                else:
                    self.content[0]["expression"]["op"] = value

class _coldef:
    def __init__(self):
        self.attribute = AST_KEYWORDS.COLUMN_DEFINITION
        self.content = [{"PRIMARY":False,"NOT NULL":False}]

    def deal(self, cls, value):
        """
        对于一个非关键词的token，根据自己的类型，将其加入到自己的内容中
        """
        # 说明这是一个column的类型提示
        if cls in tokens.Name.Builtin:
            self.content[0]["type"] = value
            
        elif cls in tokens.Name:
            self.content[0]["name"] = value
        
        elif cls in tokens.Literal:
            self.content[0]["length"] = Numerize(cls,value)


def Numerize(cls, text: str):
    """
    将token的text转换为对应的数字（如果需要的话）
    """
    if cls not in tokens.Literal:
        return text
    if cls in tokens.Literal.String:
        return text.strip("'\"")
    if cls in tokens.Literal.Number:
        if cls == tokens.Literal.Number.Float:
            return float(text)
        if cls == tokens.Literal.Number.Integer:
            return int(text)
        if cls == tokens.Literal.Number.Hexadecimal:
            return int(text, 16)
    raise Exception("Unhandled type of text for expression")
    
