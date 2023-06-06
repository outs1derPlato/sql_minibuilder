from sql_parse.AST_builder import AST
from sql_command.DB import DB

class blabla:
    def __init__(self):
        """
        示例用
        """
        self.db = DB()
        self.db.create("test",["索引","姓名"], [int,str])
    
    def ast_clear(self):
        """
        清除上一个语句留下的AST
        之后也许会清除更多
        """
        self.ast = None
        self.clause = None

    def extract(self,text:str):
        """
        从text中解析出AST，并且获取不同clause（子句）的内容
        """
        # 根据text，生成AST（这里AST只实现了SELECT查询）
        self.ast = AST(sql).content
        # 将AST中的不同clause保存过来
        self.clause = {}
        for clause in self.ast.content:
            self.clause[clause.value] = clause

    def execute(self,text:str):
        """
        执行ast中的语句
        """
        # 清除上一个语句的可能影响
        self.ast_clear()
        # 获取当前语句的AST
        self.extract(text)
        # 示例用，演示怎么从AST的解析中获取table
        tables = self.get_tables()
        print(tables)

    def get_tables(self):
        #从FROM clause中获得content
        table_names = self.clause["FROM"].content
        ret = []
        for table_name_i in table_names:
            # 调用sql_commands中实现的方法，访问得到每个table的DataFrame
            table = self.db.database[table_name_i]['tabledata']
            ret.append(table)
        return ret
        


if __name__ == "__main__":
    sql = """
    SELECT id, name, this
    FROM test
    WHERE id = 1 AND this < 2.3;
    """
    a = blabla()
    a.execute(sql)