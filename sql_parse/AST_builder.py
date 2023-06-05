from sql_parse.tokenizer import tokenizer  
from sql_parse import tokens
from sql_parse.ast_def import AST_KEYWORDS
from sql_parse.ast_def import _statement,_clause,_expression


class AST:
    def __init__(self, text = None):
        self.get_tokens(text)
        self.content , _ = self.build_AST(start_idx=0, cur_node=_statement())

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
    
    def get_level(self, cls, value, revisited = False):
        """
        根据cls，判断当前找到的关键词在AST中的层级
        """
        if value == "WHERE":
            pass
        if value == "WHERE" and revisited:
            return AST_KEYWORDS.EXPRESSION
        if value in ["WHERE","FROM","SELECT"]:
            return AST_KEYWORDS.CLAUSE
        if value in ["AND", "OR"]:
            return AST_KEYWORDS.EXPRESSION
    
    def create_node(self, level):
        """
        根据在AST中的层级，创建对应实例
        """
        if(level == AST_KEYWORDS.STATEMENT):
            return _statement()
        if(level == AST_KEYWORDS.CLAUSE):
            return _clause()
        if(level == AST_KEYWORDS.EXPRESSION):
            return _expression()
    
    def build_AST(self, start_idx = 0, cur_node = None, revisited=False):
        stream = self.token_stream
        idx = start_idx
        total_idx = len(stream)
        while idx < total_idx:
            cls, value = stream[idx]
            # print(cls,value)

            # 如果当前token并不特殊，非关键字，那么就是当前node需要接受的内容
            if cls not in tokens.Keyword:
                cur_node.deal(cls, value)

            # 如果当前token为标点，对于逗号，注释不用管，但如果有括号，就得注意了
            elif cls in tokens.Punctuation:
                # TODO: 实现括号的处理 
                if value in ["(", ")"]:
                    pass

            # 如果当前token特殊，为关键字
            else:
                cur_cls_level = self.get_level(cls,value.upper(),revisited)
                # 如果当前找到的关键词与自己同级，例如：
                # 如果自己就是一个clause，那么说明现在遇到下一个clause的开头了，终止当前clause
                if(cur_node.attribute == cur_cls_level):
                    return cur_node, idx # 返回的内容，一是在这个范围内build的结果，一个是处理到的idx
                # 如果当前找到的关键词比自己低级，例如：
                # 如果自己是一个statement(0)，遇到clause(1)说明有子句了，进行子句的build
                elif(cur_node.attribute == cur_cls_level - 1):
                    sub_node = self.create_node(cur_cls_level)
                    sub_node.value = value.upper()
                    # print(sub_node.value)
                    if sub_node.value in ["WHERE"] and cur_node.attribute == AST_KEYWORDS.STATEMENT:
                        builded_node, idx_get = self.build_AST(idx, sub_node,revisited=True)
                    else:
                        builded_node, idx_get = self.build_AST(idx+1, sub_node) # 子结点build结束，回到当前结点
                    cur_node.content.append(builded_node)
                    idx = idx_get
                    continue
                # 除此之外，当前关键词和自己的等级跨度不应超过1，这时说明出现错误
                else:
                    raise Exception(f"Current node level is {cur_node.attribute}, but the word level is {cur_cls_level}")
            idx = idx + 1
        return cur_node, idx
    
    def pprint(self):
        """
        用还算好看的方式打印自己的content
        """
        self.pprint_impl(cur_list = self.content.content)
        
    def pprint_impl(self,depth = 0, cur_list = None,_pre = ''):
        """
        pprint的单层实现
        """
        for idx, cur_list_i in enumerate(cur_list):
            if isinstance(cur_list_i, _clause) or isinstance(cur_list_i, _expression):
                level = "level:" + str(cur_list_i.attribute)
                item = _pre + str(cur_list_i.value)
                print(f"{item:<50} {level:<40}")
                self.pprint_impl(depth=depth+1, cur_list=cur_list_i.content, _pre=_pre+'--')
            else:
                print(f"{_pre} {cur_list_i}")


            

if __name__ == "__main__":
    sql = """
    SELECT id, name, this
    FROM table1
    WHERE id = 1 AND this < 2.3;
    """
    a = AST(sql)
    # TODO: 由于自己的实现是从左往右读TOKEN，而没有提前读等操作，因而不可能先读
    # AND再读WHERE。自己的一个暂时的解决方法是将AND和WHERE一样看作一个
    # expression，这样能保证一个CLAUSE中只有一个表达式（例如a=3），读到AND时执行
    # WHERE查询，再将AND查询的结果，与WHERE查询的结果取交集。如果后面还有AND，就
    # 再与左边的取交集……这样对于多个AND没有问题，但是如果有OR，那么优先级就被打
    # 乱了，必须要先完成OR两边的再对两边的结果取并集
    # 现在来看这部分有点困难，先不要动为好
    a.pprint()
    show = a.content
    print("\n\n",show)