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
        self.dict = self.db.database
        # 外部数据读取 test
        for file_name in file_names:
            if file_name.endswith('.csv'):
                var_name = os.path.splitext(file_name)[0]
                file_path = data_folder + '/' + file_name
                data_table = pd.read_csv(file_path)
                self.dict[var_name] = data_table

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
            tables = self.get_tables(function)
            for table in tables:
                cols = self.clause["COLUMNS"].content
                values_clauses = self.ast.content[2:]
                cur_table = self.db.database[table]
                values_for_insert = []
                for values_clause_i in values_clauses:
                    values = values_clause_i.content
                    self.check_types(cur_table['datatypes'], cols, values)
                    self.check_null(cur_table['not_null_flag'], cols, values)
                    self.check_primary(cur_table['tabledata'],cur_table['primary_key'],cols,values)
                    values_for_insert.append(values)
                _, cur_table['tabledata'] = self.db.insert(cur_table['tabledata'], cols, values_for_insert)

        # 删除
        elif function == 'DELETE':
            tables = self.get_tables(function)
            for table in tables:
                rows = self.get_row(table) if "WHERE" in self.clause.keys() else None
                self.db.delete(self.dict[table], del_rows=rows)

        # 创建新表
        elif function == 'CREATE':
            self.excute_create_statement()

        # 删除表
        elif function == 'DROP':
            print("DROP")

        else:
            print("ERROR FUNCTION")

        if function != "SELECT":
            self.save_tables()
    
    def check_types(self, requires, cols, values):
        for i in range(len(cols)):
            if requires[cols[i]].upper() in ["VARCHAR", "CHAR"]:
                if not isinstance(values[i], str):
                    raise Exception(f"Type of {cols[i]} is {requires[cols[i]]}, but {type(values[i])} is given.")
            if requires[cols[i]].upper() in ["INT"]:
                if not isinstance(values[i], int):
                    raise Exception(f"Type of {cols[i]} is {requires[cols[i]]}, but {type(values[i])} is given.")
            if requires[cols[i]].upper() in ["FLOAT"]:
                if not isinstance(values[i],float):
                    pass
                    raise Exception(f"Type of {cols[i]} is {requires[cols[i]]}, but {type(values[i])} is given.")

    def check_null(self, requires, cols, values):
        for k in requires:
            v = requires[k]
            if v is True:
                if k not in cols:
                    raise Exception(f"{k} is not null, but null is given.")
                else:
                    if values[cols.index(k)] is None:
                        raise Exception(f"{k} is not null, but null is given.")
    
    def check_primary(self, table: pd.DataFrame, primary_keys, cols, values):
        for k in primary_keys:
            if k in cols:
                if values[cols.index(k)] in table[k].values:
                    raise Exception(f"{k} is primary key, but {values[cols.index(k)]} is already in table.")
            else:
                raise Exception(f"{k} is primary key, but not given in insertion values.")

    
    def save_tables(self):
        # 待实现
        pass

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
        elif function == "INSERT":
            table_names = self.clause["INSERT"].content
        return table_names
    
    def excute_create_statement(self):
        table = self.clause["CREATE"].content[0]
        attribute_ls = []
        types_ls = []
        not_null_ls = []
        primary_key_ls = []
        char_attri_ls = []
        char_attri_len_ls = []

        for col_def in self.clause["COLUMNS"].content:
            t = col_def.content[0]
            attribute_ls.append(t["name"])
            types_ls.append(t["type"])
            if t["type"] in ["char","varchar"]:
                char_attri_ls.append(t["name"])
                char_attri_len_ls.append(t["length"])
            # attention: if it is a primary key, then it should always be not null
            not_null_ls.append(t["NOT NULL"] or t["PRIMARY"])
            if t["PRIMARY"]:
                primary_key_ls.append(t["name"])
        if self.db.create(table=table, 
                          attributes=attribute_ls, 
                          types=types_ls, 
                          not_null=not_null_ls, 
                          primary_key=primary_key_ls,
                          char_attri=char_attri_ls,
                          char_attri_len=char_attri_len_ls):
            print("创建成功!")
            # print(self.db.database[table])
        else:
            print("创建失败!")



if __name__ == "__main__":
    a = blabla()

    # 创建
    sql1 = """
    CREATE TABLE Persons
    (
        PersonID PRIMARY int,
        LastName varchar(255) NOT NULL,
        FirstName char(255),
        Address float,
        City varchar(255)
    );
    """
    a.execute(sql1)
    print(a.db.database["Persons"]['tabledata'])
    print("="*20)
    print("="*20)

    # 插入
    sql2 = """
    INSERT INTO Persons (PersonID,LastName, Address, City)
    VALUES (
        (3,'my', 2.3, "this"),
        (4,'she', 5.6, "7"),
        (5,'thistsdas',1.1,"9")
    );
    """
    a.execute(sql2)
    print(a.db.database["Persons"]['tabledata'])
    print("="*20)
    print("="*20)

    # 更新
    sql3 = """
    UPDATE Persons
    SET Address = Address * 1.1
    WHERE PersonID >= 2
    """
    a.execute(sql3)
    print(a.db.database["Persons"]['tabledata'])
    print("="*20)
    print("="*20)

    # print(a.db.database["Persons"]['datatypes'])
    # print(a.db.database["Persons"]['not_null_flag'])
    # print(a.db.database["Persons"]['primary_key'])
    # a = blabla()
    # sql1 = """
    #     SELECT id, name
    #     FROM test2
    #     WHERE id >= 2 AND this < 3.1 OR this2 = 13 AND id = 1;
    #     """
    # a.execute(sql1)

    # sql2 = """
    #     UPDATE test2
    #     SET this2 = 100, name = 'Li Si', this = this * 1.1
    #     WHERE id >= 2 AND this2 < 13;
    #     """
    # a.execute(sql2)

    # sql3 = """
    #     SELECT id, name, this, this2
    #     FROM test2
    #     """
    # a.execute(sql3)

    # sql4 = """
    #         DELETE FROM test2
    #         WHERE id = 1
    #         """
    # a.execute(sql4)
    # a.execute(sql3)

    # sql5 = """
    #         SELECT *
    #         FROM test
    #         WHERE gender = Female;
    #         """
    # a.execute(sql5)

    # sql6 = """
    #         UPDATE test
    #         SET salary = salary * 1.2
    #         WHERE id = 1 OR id = 2 OR id = 5;
    #         """
    # a.execute(sql6)

    # sql7 = """SELECT * FROM test"""
    # a.execute(sql7)