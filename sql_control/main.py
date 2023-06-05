from sql_parse.AST_builder import AST
from sql_command.DB import DB

class blabla:
    def __init__(self, text:str):
        self.ast = AST(sql).content
        self.db = DB()
        self.db.create("test",["索引","姓名"], [int,str])

    def extract(self):
        for clause in self.ast.content:
            if clause.value == "WHERE":
                self.where_clause = clause
            if clause.value == "SELECT":
                self.select_clause = clause
            if clause.value == "FROM":
                self.from_caluse = clause

    def execute(self):
        self.extract()
        tables = self.get_tables()
        print(tables)

    def get_tables(self):
        table_names = self.from_caluse.content
        ret = []
        for table_name_i in table_names:
            table = self.db.database[table_name_i]['tabledata']
            ret.append(table)
        return ret
        


if __name__ == "__main__":
    sql = """
    SELECT id, name, this
    FROM test
    WHERE id = 1 AND this < 2.3;
    """
    a = blabla(sql)
    a.execute()