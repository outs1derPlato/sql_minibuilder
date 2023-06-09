from sql_parse.tokenizer import tokenizer  
from sql_parse import tokens
from sql_parse.ast_def import AST_KEYWORDS
from sql_parse.ast_def import _statement,_clause,_expression,_coldef


class AST:
    def __init__(self, text = None):
        self.get_tokens(text=text)
        new_statement = _statement()
        new_statement.attribute = AST_KEYWORDS.STATEMENT
        self.content , _ = self.build_AST(start_idx=0, cur_node=new_statement)

    def get_tokens(self, text: str):
        """
        完成tokenizer的工作，从text中抽取出token
        """
        a = tokenizer()
        a.default_initialization()
        token_iter = a.tokenize(text)
        ret = []
        for ttype, value in token_iter:
            if ttype is tokens.Error:
                raise Exception("Error tokenizing at TOKEN: %s" % value)
            else:
                ret.append((ttype, value))
        self.tokens = ret
    
    def get_level(self, value, par_value):
        """
        根据当前结点value，以及当前关键词的class，决定此token在AST中的层级
        """
        if par_value == "WHERE":
            if value == "WHERE":
                return AST_KEYWORDS.EXPRESSION
        if par_value == "SET":
            if value == "SET":
                return AST_KEYWORDS.EXPRESSION
        if value in ["WHERE","FROM","SELECT","UPDATE","SET", "DELETE"]:
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
        if(level == AST_KEYWORDS.COLUMN_DEFINITION):
            return _coldef()
    
    def build_AST_CREATE(self, start_idx = 0, statement_node = None):
        stream = self.tokens
        total_idx = len(stream)

        # 第一个必定会存在的clause: value="CREATE",content包含table的名称
        create_clause_node = self.create_node(AST_KEYWORDS.CLAUSE)
        create_clause_node.value = "CREATE"
        statement_node.content.append(create_clause_node)

        # 第二个必定会存在的clause：value="COLUMNS",content包含每一列的定义
        columns_clause_node = self.create_node(AST_KEYWORDS.CLAUSE)
        columns_clause_node.value = "COLUMNS"
        statement_node.content.append(columns_clause_node)

        # 在找到CREATE关键词后，我们希望找的是：CREATE TABLE 表名
        requireValue = "TABLE"
        cur_node = create_clause_node
        idx = start_idx + 1

        pair_level = 0

        while idx < total_idx:
            cls, value = stream[idx]

            if value == "PRIMARY":
                pass
            
            # 如果当前token并不特殊，非关键字，那么就是当前node需要接受的内容
            if (cls not in tokens.Keyword) and (cls not in tokens.Punctuation):
                cur_node.deal(cls, value)

            # 如果当前token为标点
            elif cls in tokens.Punctuation:
                # ()的处理
                if value in ["(", ")"]:
                    if value == "(":
                        pair_level = pair_level + 1
                    if pair_level == 1 and value == "(":
                        # 遇到这里，说明读到了CREATE TABLE 表名 ( 的情况，接下来该是新的clause了
                        if cur_node.value == "CREATE":
                            cur_coldef_node = self.create_node(AST_KEYWORDS.COLUMN_DEFINITION)
                            cur_coldef_node.value = "COLUMN_DEFINITION"
                            columns_clause_node.content.append(cur_coldef_node)
                            cur_node = cur_coldef_node
                            requireValue = ","
                            idx = idx + 1
                            continue
                    if pair_level == 1 and value == ")":
                        # 遇到这里，说明是在希望读取下一个列的时候，发现已经没有更多列了
                        # 那可真是个天大的喜事，说明读取完成了
                        return statement_node, idx
                    if value == ")":
                        pair_level = pair_level - 1
                # 逗号的处理
                if value in [","]:
                    # 一个列的结束，另一个列的开始
                    cur_coldef_node = self.create_node(AST_KEYWORDS.COLUMN_DEFINITION)
                    cur_coldef_node.value = "COLUMN_DEFINITION"
                    columns_clause_node.content.append(cur_coldef_node)
                    cur_node = cur_coldef_node
                    idx = idx + 1
                    continue

            # 如果当前token特殊，为关键字……（但其实唯一要看的关键字就是TABLE和PRIMARY（目前的话））
            else:
                val = value.upper()
                if val == "TABLE": pass
                if val == "PRIMARY":
                    self.search_constraint(idx, val)
                if val == "NOT NULL":
                    cur_node.content[0]["NOT NULL"] = True
            idx = idx + 1
        return statement_node, idx

    def build_AST(self, start_idx = 0, cur_node = None):
        stream = self.tokens
        idx = start_idx
        total_idx = len(stream)
        while idx < total_idx:
            cls, value = stream[idx]

            if value == "*":
                pass

            # 如果当前token并不特殊，非关键字，那么就是当前node需要接受的内容
            if (cls not in tokens.Keyword) and (cls not in tokens.Punctuation):
                cur_node.deal(cls, value)

            # 如果当前token为标点，对于注释不用管，但如果有括号、逗号，就得注意了
            elif cls in tokens.Punctuation:
                # TODO: 实现括号的处理 
                if value in ["(", ")"]:
                    pass
                # 一般来说，逗号不用管都可以正确处理，除了一种情况——SET之后用逗号分隔的多个表达式
                # SET alas = 1, country = usa, cc = 13.4
                if value in [","]:
                    if cur_node.value == "SET":
                        par_cls_level = cur_node.attribute
                        if par_cls_level is AST_KEYWORDS.EXPRESSION:
                            return cur_node, idx
                        if par_cls_level is AST_KEYWORDS.CLAUSE:
                            sub_node = self.create_node(AST_KEYWORDS.EXPRESSION)
                            sub_node.value = "SET"
                            builded_node, idx_get = self.build_AST(idx+1, sub_node)
                            cur_node.content.append(builded_node)
                            idx = idx_get
                            continue

            # 如果当前token特殊，为关键字
            else:
                # CREATE的语法区别和其他的差别太大了，放弃兼容性，直接单独处理
                if value.upper() == "CREATE":
                    node_create, _ = self.build_AST_CREATE(idx, cur_node)
                    return  node_create, None
                # 判断当前token的层级
                par_cls_level = cur_node.attribute
                cur_cls_level = self.get_level(value=value.upper(),par_value=cur_node.value)
                # 如果当前找到的关键词与自己同级，例如：
                # 如果自己就是一个clause，现在遇到下一个clause的开头，那么便终止当前clause
                if(par_cls_level == cur_cls_level):
                    return cur_node, idx # 返回的内容，一是在这个范围内build的结果，一个是处理到的idx
                # 如果当前找到的关键词比自己低级，例如：
                # 如果自己是一个statement(0)，遇到clause(1)说明有子句了，进行子句的build
                elif(par_cls_level == cur_cls_level - 1):
                    sub_node = self.create_node(cur_cls_level)
                    sub_node.value = value.upper()
                    # WHERE的特殊性在于，存在WHERE开头的clause，也存在WHERE开头的expression,WHERE需要被走两遍
                    # SET同理
                    if sub_node.value in ["WHERE", "SET"] and cur_cls_level == AST_KEYWORDS.CLAUSE:
                        builded_node, idx_get = self.build_AST(idx, sub_node)
                    else:
                        builded_node, idx_get = self.build_AST(idx+1, sub_node) # 子结点build结束，回到当前结点
                    cur_node.content.append(builded_node)
                    idx = idx_get
                    continue
                # 还有一个特殊的地方在于，expression常常是 a = b, c = d这样的形式，没有一个关键词提示最后一个expression的结束
                # 这里就让expression撞上下一个clause的开头，作为expression的结束
                elif par_cls_level == AST_KEYWORDS.EXPRESSION and cur_cls_level == AST_KEYWORDS.CLAUSE:
                    return cur_node, idx
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
            if isinstance(cur_list_i, _clause) or isinstance(cur_list_i, _expression) or isinstance(cur_list_i,_coldef):
                level = "level:" + str(cur_list_i.attribute)
                item = _pre + str(cur_list_i.value)
                print(f"{item:<60} {level:<50}")
                self.pprint_impl(depth=depth+1, cur_list=cur_list_i.content, _pre=_pre+'--')
            else:
                print(f"{_pre} {cur_list_i}")


            

if __name__ == "__main__":
    sql1 = """
    SELECT id, name, this
    FROM table1, table2
    WHERE id = 1 AND "this" < 2.3;
    """
    sql2 = """
    UPDATE table1
    SET alexa = 50000, country='USA', salary = salary * 14.5
    WHERE id = 1 AND this < 2.3 OR name>1;
    """
    sql3 = """
    DELETE table1
    WHERE id = 1 AND this < 2.3 OR name>1;
    """
    sql4 = """
    CREATE TABLE Persons (
        PersonID int,
        LastName varchar(255),
        FirstName char(255) NOT NULL,
        Address float,
        City varchar(255),
        PRIMARY KEY (PersonID)
    );
    """
    sql5 = """
    SELECT *
    FROM table1, table2
    WHERE id = 1 AND "this" < 2.3;
    """
    a = AST(sql4)
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
