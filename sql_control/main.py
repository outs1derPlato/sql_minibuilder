from sql_parse.AST_builder import AST
from sql_command.DB import DB
import re
import os
import pandas as pd

data_folder = '../data'
file_names = os.listdir(data_folder)

class blabla:
    def __init__(self):
        """
        示例用
        """
        self.db = DB()

        # 文件读取
        mydata = {}
        for file_name in file_names:
            if file_name.endswith('.csv'):
                var_name = os.path.splitext(file_name)[0]
                file_path = data_folder + '/' + file_name
                data_table = pd.read_csv(file_path)
                header_list = data_table.columns.tolist()
                mydata[var_name] = data_table

        # 内置的test2 和 test3
        self.db.create("test2", ["id", "name", "this", "this2"], [int, str, float, float])
        self.db.create("test3", ["id2", "name2", "that", "that2"], [int, str, float, float])
        self.test2 = self.db.database['test2']['tabledata']
        self.test3 = self.db.database['test3']['tabledata']
        flag, self.test2 = self.db.insert(table=self.test2, attributes=["id"], values=[[1], [2], [3]])
        flag, self.test2 = self.db.update(table=self.test2, update_rows=None, attributes=["name"], values=["张三", "李四", "王五"])
        flag, self.test2 = self.db.update(table=self.test2, update_rows=None, attributes=["this"], values=[2.1, 3, 3.6])
        flag, self.test2 = self.db.update(table=self.test2, update_rows=None, attributes=["this2"], values=[11, 12, 13])
        self.dict = {'test2': self.test2, 'test3': self.test3}

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
        function = self.funct(text)
        # 清除上一个语句的可能影响
        self.ast_clear()
        # 获取当前语句的AST
        self.extract(text)

        # 查询
        if function == 'SELECT':
            tables = self.get_tables(function)
            cols = self.get_col()
            for table in tables:
                rows = self.get_row(text, table) if "WHERE" in text else None
                result = self.db.select(self.dict[table], cols, rows)
                print(result)

        # 更新
        elif function == 'UPDATE':
            tables = self.get_tables(function)
            for table in tables:
                rows = self.get_row(text, table) if "WHERE" in text else None
                up = self.clause["SET"].content[0].content[0]
                self.db.update(self.dict[table], update_rows=rows, attributes=up['left'], values=up['right'])

        # 添加
        elif function == 'INSERT':
            print('INSERT')

        # 删除
        elif function == 'DELETE':
            tables = self.get_tables(function)
            for table in tables:
                rows = self.get_row(text, table) if "WHERE" in text else None
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
    def funct(self, text: str):
        text = text.strip()
        index = text.find(' ')
        if index != -1:
            return text[:index]
        else:
            return text

    # SELECT功能的筛选列
    def get_col(self):
        num_col = len(self.clause["SELECT"].content)
        cols = []
        for i in range(0, num_col):
            col = self.clause["SELECT"].content[i]
            cols.append(col)
        return cols

    # WHERE语句的筛选行和对AND、OR运算结果
    def get_row(self, text: str, table):
        num_condition = len(self.clause["WHERE"].content)
        rows_ = []
        for i in range(0, num_condition):
            condition = self.clause["WHERE"].content[i].content[0]
            row = self.db.where(self.dict[table], condition['left'], condition['right'], condition['op'])
            rows_.append(set(row))
        operators = re.findall(r'AND|OR', text)
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

    def get_tables(self, function):
        if function == "SELECT" or function == "DELETE":
            table_names = self.clause["FROM"].content
        elif function == "UPDATE":
            table_names = self.clause["UPDATE"].content
        # ret = []
        # for table_name_i in table_names:
            # 调用sql_commands中实现的方法，访问得到每个table的DataFrame
            # table = self.db.database[table_name_i]['tabledata']
            # ret.append(table)
        return table_names


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
        SET this2 = 100
        WHERE id >= 2 AND this2 <= 13;
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