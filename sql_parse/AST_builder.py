from sql_parse.tokenizer import tokenizer  
from sql_parse import tokens
import enum

class AST_KEYWORDS(enum.IntEnum):
    STATEMENT = 0
    CLAUSE = 1

class _statement:
    def __init__(self):
        self.attribute = AST_KEYWORDS.STATEMENT
        self.content = []
        self.value = None
    
    def deal(self, cls, value):
        if cls == tokens.Name:
            self.content.append(value)

class _clause:
    def __init__(self):
        self.attribute = AST_KEYWORDS.CLAUSE
        self.content = []

    def deal(self, cls, value):
        """
        对于一个非关键词的token，根据自己clause的属性，将其加入到自己的内容中
        """
        if cls == tokens.Name:
            self.content.append(value)

class AST:
    def __init__(self, text = None):
        pass
        # self.get_tokens(text)
        # self.content , _ = self.build_AST(start_idx=0, cur_node=_statement())

    def get_tokens(self, text: str):
        """
        完成tokenizer的工作，从text中抽取出token
        """
        a = tokenizer()
        a.default_initialization()
        token_my = a.tokenize(text)
        ret = []
        for ttype, value in token_my:
            ret.append((ttype, value))
        self.token_stream = ret
    
    def get_level(self, cls):
        """
        根据cls，判断当前找到的关键词在AST中的层级
        """
        return AST_KEYWORDS.CLAUSE
    
    def build_AST(self, start_idx = 0, cur_node = None):
        stream = self.token_stream
        idx = start_idx
        total_idx = len(stream)
        while idx < total_idx:
            cls, value = stream[idx]
            print(cls,value)

            # 如果当前token并不特殊，非关键字，那么就是当前node需要接受的内容
            if cls not in tokens.Keyword:
                cur_node.deal(cls, value)

            # 如果当前token特殊，为关键字
            else:
                cur_cls_level = self.get_level(cls)
                # 如果当前找到的关键词与自己同级，例如：
                # 如果自己就是一个clause，那么说明现在遇到下一个clause的开头了，终止当前clause
                if(cur_node.attribute == cur_cls_level):
                    return cur_node, idx # 返回的内容，一是在这个范围内build的结果，一个是处理到的idx
                # 如果当前找到的关键词比自己低级，例如：
                # 如果自己是一个statement(0)，遇到clause(1)说明有子句了，进行子句的build
                elif(cur_node.attribute == cur_cls_level - 1):
                    sub_node = _clause()
                    sub_node.value = value
                    builded_node, idx_get = self.build_AST(idx+1, sub_node) # 子结点build结束，回到当前结点
                    cur_node.content.append(builded_node)
                    idx = idx_get
                    continue
                # 除此之外，当前关键词和自己的等级跨度不应超过1，这时说明出现错误
                else:
                    raise Exception(f"Current node level is {cur_node.attribute}, but the word level is {cur_cls_level}")
            idx = idx + 1
        return cur_node, idx

        

if __name__ == "__main__":
    sql = """
    SELECT id, name, this
    FROM table1
    WHERE id = 1 AND this < 2.3;
    """
    a = AST()
    ret = _statement()
    a.get_tokens(sql)
    builded_node, idx_get = a.build_AST(0, ret)
    print(builded_node)