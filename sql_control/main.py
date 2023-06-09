from sql_parse.AST_builder import AST
from sql_command.DB import DB
import os
import pandas as pd

from sql_parse.tokens import Token

data_folder = '../data'
file_names = os.listdir(data_folder)


class blabla:
    def __init__(self):
        """
        示例用
        """
        self.db = DB()

        self.dict ={}

        # 外部数据读取 test
        for file_name in file_names:
            if file_name.endswith('.csv'):
                var_name = os.path.splitext(file_name)[0]
                file_path = data_folder + '/' + file_name
                data_table = pd.read_csv(file_path)
                self.dict[var_name] = data_table

        # 内置 test2
        self.db.create("test2", ["id", "name", "this", "this2"], [int, str, float, float])
        self.test2 = self.db.database['test2']['tabledata']
        flag, self.test2 = self.db.insert(table=self.test2, attributes=["id"], values=[[1], [2], [3]])
        flag, self.test2 = self.db.update(table=self.test2, update_rows=None, attributes=["name"], values=["张三", "李四", "王五"])
        flag, self.test2 = self.db.update(table=self.test2, update_rows=None, attributes=["this"], values=[2.1, 3, 3.6])
        flag, self.test2 = self.db.update(table=self.test2, update_rows=None, attributes=["this2"], values=[11, 12, 13])
        self.dict['test2'] = self.test2

        print('原表test：\n', self.dict['test'], '\n')
        print('原表test2：\n', self.dict['test2'], '\n')


    def ast_clear(self):
        """
        清除上一个语句留下的AST
        之后也许会清除更多
        """
        self.ast = None
        self.clause = None

    def extract(self,text:str):
        """
        获取不同clause（子句）的内容
        """
        # 根据text，生成AST（这里AST只实现了SELECT查询）
        self.ast = AST(text).content
        # 将AST中的不同clause保存过来
        self.clause = {}
        for clause in self.ast.content:
            self.clause[clause.value] = clause

    def execute(self, text: str):
        """
        执行ast中的语句
        """
        # 清除上一个语句的可能影响
        self.ast_clear()
        # 获取当前语句的AST
        self.extract(text)
        function = self.funct()

        # 查询
        if function == 'SELECT':
            tables = self.get_tables(function)
            cols = self.get_col()
            for table in tables:
                rows = self.get_row(table) if "WHERE" in self.clause.keys() else None
                result = self.db.select(self.dict[table], cols, rows) if Token.Wildcard not in cols else self.db.select(self.dict[table], self.dict[table].columns, rows)
                print(result)

        # 更新
        elif function == 'UPDATE':
            tables = self.get_tables(function)
            for table in tables:
                rows = self.get_row(table) if "WHERE" in self.clause.keys() else None
                for up in self.clause["SET"].content:
                    v = up.content[0]['expression']
                    if len(v) == 1:
                        if isinstance(v['left'], int) or isinstance(v['left'], float) or (isinstance(v['left'], str) and f"'{v['left']}'" in text):
                            value = v['left']
                        else:
                            value = self.db.select(self.dict[table], v['left'], rows).values.tolist()
                    else:
                        value = self.get_val(table, up.content[0]['expression'], rows)
                    self.db.update(self.dict[table], update_rows=rows, attributes=[up.content[0]['assignment']], values=value)

        # 添加
        elif function == 'INSERT':
            print('INSERT')

        # 删除
        elif function == 'DELETE':
            tables = self.get_tables(function)
            for table in tables:
                rows = self.get_row(table) if "WHERE" in self.clause.keys() else None
                self.db.delete(self.dict[table], del_rows=rows)

        # 创建新表
        elif function == 'CREATE':
            print("CREATE")

        # 删除表
        elif function == 'DROP':
            print("DROP")

        else:
            print("ERROR FUNCTION")

    # 判断功能
    def funct(self):
        return self.ast.content[0].value

    # SELECT功能的筛选列
    def get_col(self):
        num_col = len(self.clause["SELECT"].content)
        cols = []
        for i in range(0, num_col):
            col = self.clause["SELECT"].content[i]
            cols.append(col)
        return cols

    # WHERE语句的筛选行和对AND、OR运算结果
    def get_row(self, table):
        num_condition = len(self.clause["WHERE"].content)
        rows_ = []
        for i in range(0, num_condition):
            condition = self.clause["WHERE"].content[i].content[0]
            row = self.db.where(self.dict[table], condition['left'], condition['right'], condition['op'])
            rows_.append(set(row))
        operators = [expression_i.value for expression_i in self.clause["WHERE"].content[1:]]
        rows = rows_[0]
        i = 1
        while i < len(rows_):
            if operators[i - 1] == "AND":
                rows = rows.intersection(rows_[i])
            elif operators[i - 1] == "OR":
                temp_result = rows_[i]
                j = i + 1
                while j < len(rows_) and operators[j - 1] == "AND":
                    temp_result = temp_result.intersection(rows_[j])
                    j += 1
                rows = rows.union(temp_result)
                i = j - 1
            i += 1
        return list(rows)

    # SET 右边为表达式的情况
    def get_val(self, table, expression, rows):
        result = self.db.select(self.dict[table], expression['left'], rows)
        if expression['op'] == '+':
            result += expression['right']
        elif expression['op'] == '-':
            result -= expression['right']
        elif expression['op'] == '*':
            result *= expression['right']
        elif expression['op'] == '/':
            result /= expression['right']
        result = result.values.tolist()
        return result

    def get_tables(self, function):
        if function == "SELECT" or function == "DELETE":
            table_names = self.clause["FROM"].content
        elif function == "UPDATE":
            table_names = self.clause["UPDATE"].content
        # ret = []
        # for table_name_i in table_names:
    
    def excute_create_statement(self):
        table = self.clause["CREATE"].content[0]
        attribute_ls = []
        types_ls = []
        not_null_ls = []
        primary_key_ls = []
        char_attri_ls = []
        char_attri_len_ls = []
        for i in range(len(self.clause["COLUMNS"].content)):
            attribute_ls.append(self.clause["COLUMNS"].content[i].content[0]["name"])
            types_ls.append(self.clause["COLUMNS"].content[i].content[0]["type"])
            if (self.clause["COLUMNS"].content[i].content[0]["type"]=="char") or (self.clause["COLUMNS"].content[i].content[0]["type"]=="varchar"):
                 char_attri_ls.append(self.clause["COLUMNS"].content[i].content[0]["name"])
                 char_attri_len_ls.append(self.clause["COLUMNS"].content[i].content[0]["length"])
            not_null_ls.append(self.clause["COLUMNS"].content[i].content[0]["PRIMARY"])
            if self.clause["COLUMNS"].content[i].content[0]["PRIMARY"]:
                primary_key_ls.append(self.clause["COLUMNS"].content[i].content[0]["name"])
        if self.db.create(table=table, attributes=attribute_ls, types=types_ls, not_null=not_null_ls, primary_key=primary_key_ls,char_attri=char_attri_ls,char_attri_len=char_attri_len_ls):
            print("创建成功!")
            print(self.db.database[table]["not_null_flag"])
        else:
            print("创建失败!")



if __name__ == "__main__":
    a = blabla()
    sql1 = """
        SELECT id, name
        FROM test2
        WHERE id >= 2 AND this < 3.1 OR this2 = 13 AND id = 1;
        """
    a.execute(sql1)

    sql2 = """
        UPDATE test2
        SET this2 = 100, name = 'Li Si', this = this * 1.1
        WHERE id >= 2 AND this2 < 13;
        """
    a.execute(sql2)

    sql3 = """
        SELECT id, name, this, this2
        FROM test2
        """
    a.execute(sql3)

    sql4 = """
            DELETE FROM test2
            WHERE id = 1
            """
    a.execute(sql4)
    a.execute(sql3)

    sql5 = """
            SELECT *
            FROM test
            WHERE gender = Female;
            """
    a.execute(sql5)

    sql6 = """
            UPDATE test
            SET salary = salary * 1.2
            WHERE id = 1 OR id = 2 OR id = 5;
            """
    a.execute(sql6)

    sql7 = """SELECT * FROM test"""
    a.execute(sql7)