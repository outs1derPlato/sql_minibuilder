import pandas as pd

class DB:
    def __init__(self):
        self.dbtypes=dict[dict['tablename':str,'tabledata':pd.DataFrame,'datatypes':dict]]
        self.database = {}
        #访问某个表用 database['表名']
        #访问某个表中的数据用 database['表名']['tabledata'] 这是一个pd.DataFrame型的数据
        #访问某个表中某个属性的数据类型用 database['表名']['datatypes']['属性名']

    def create(self,
                table: str,
                attributes: list[str],
                types: list[str]) -> bool:
        #检查表是否已经存在
        if table in self.database:
            print(f"Table '{table}' already exists.")
            return False

        #创建一个新表
        newtable = {
            'tablename': table,
            'tabledata': pd.DataFrame(columns=attributes),
            'datatypes': {attr: data_type for attr, data_type in zip(attributes, types)}
        }
        #数据库添加新表
        self.database[table] = newtable
        return True


    def select(self,
                table: pd.DataFrame,       # 输入的表
                sel_columns: list[str],    # 需要筛选的列
                sel_rows: list[int]        # 已经经过where筛选，需要select展示的行
                ) -> pd.DataFrame:
        # 如果没有行需要筛选（也就是没有where语句时）（注意这要与where筛选后没有符合结果的sel_row = []区分开来）
        # 那么就返回所有行，只筛选列
        if sel_rows == None: 
            return table[sel_columns]
        # 如果是where语句筛选了，但没有符合的结果，那么就返回空表
        if sel_rows == []:
            return pd.DataFrame()
        
        # 否则就在筛选行的基础上，筛选列
        rs = table.iloc[sel_rows]
        rs = rs[sel_columns]
        return rs

    def delete(self,
                table: pd.DataFrame,
                del_rows: list[int]
                ) -> bool:
        #检测需要删除的行索引是否有效，即表中是否存在索引对应的记录
        invalid_rows = [index for index in del_rows if index not in table.index]
        #如果存在无效索引，则返回false，即删除操作失败
        if invalid_rows:
            return False
        #否则，则执行删除操作，并返回true，即删除操作成功
        table.drop(del_rows, inplace=True)
        return True

    def drop(self, 
                table: pd.DataFrame
                ) -> bool:
        #判断需要删除的表是否存在
        #如果存在则执行删除操作，并返回Ture，即操作成功
        if isinstance(table, pd.DataFrame):
            # option 1：删除整个表
            # del table
            # option 2：删除表中所有记录
            table.drop(table.index, inplace=True)
            self.dropped_tables.add(table)
            return True
        #否则返回False，即操作失败
        return False
    
    def insert(self,
            table: pd.DataFrame,
            attributes: list[str],
            values: list[list]
            ) -> tuple[bool, pd.DataFrame]:
        try:
            new_rows = pd.DataFrame(values, columns=attributes)
            # 更新表
            table = pd.concat([table, new_rows], ignore_index=True)

            return True, table
        except Exception as e:
            print(f"Insertion failed: {e}")
            return False, None

    def update(self,
                table: pd.DataFrame,
                update_rows: list[int], #更新的行
                attributes: list[str],  #更新的列
                values: list[list]
            ) -> tuple[bool,pd.DataFrame]:
        try:
            if (update_rows==None) and (attributes==None):#更新所有
                table.loc[:,:]=values
                return True, table
            elif update_rows==None:#更新指定列所有行
                table.loc[:,attributes]=values
                return True, table
            elif attributes==None:#更新指定行所有列
                table.loc[update_rows,:]=values
                return True, table
            else:#更新指定行指定列
                table.loc[update_rows,attributes]=values
                return True, table
        except Exception as e:
            print(f"update failed: {e}")
            return False, None
    
    def where(self,
                table: pd.DataFrame,
                attribute: str,
                value,
                operand
                ) -> list[int]:
        if operand == "=":
            return table[table[attribute] == value].index.tolist()
        if operand == ">":
            return table[table[attribute] > value].index.tolist()
        if operand == "<":
            return table[table[attribute] < value].index.tolist()
        if operand == ">=":
            return table[table[attribute] >= value].index.tolist()
        if operand == "<=":
            return table[table[attribute] <= value].index.tolist()


if __name__ == "__main__":
    # 读取数据
    a = DB()
    a.create("test",["索引","姓名"], [int,str])
    test_table = a.database['test']['tabledata']
    flag, test_table = a.insert(table=test_table,attributes=["索引"],values=[[23],[24]])
    print(test_table)

    #更新test表
    flag, test_table =a.update(table=test_table,update_rows=None,attributes=["姓名"], values=[["张三"],["王五"]])
    print(test_table)
    flag, test_table =a.update(table=test_table,update_rows=[1],attributes=None, values=[[1,"李四"]])
    print(test_table)
    flag, test_table =a.update(table=test_table,update_rows=[1],attributes=["索引"], values=[[24]])
    print(test_table)
    flag, test_table =a.update(table=test_table,update_rows=None,attributes=None, values=[[1,"李四"],[2,"王五"]])
    print(test_table)

    #测试where
    print("\n\n\n\n")
    print("王五的index是：")
    print(a.where(test_table,"姓名","王五","="))