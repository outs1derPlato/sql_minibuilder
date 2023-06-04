import pandas as pd

class DB:
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
    def delete(self,table,del_rows,):#返回布尔值
        #检测需要删除的行索引是否有效，即表中是否存在索引对应的记录
        invalid_rows = [index for index in del_rows if index not in table.index]
        #如果存在无效索引，则返回false，即删除操作失败
        if invalid_rows:
            return False
        #否则，则执行删除操作，并返回true，即删除操作成功
        table = table.drop(del_rows)
        return True
    def drop(self,table):#返回布尔值
        #判断需要删除的表是否存在
        #如果存在则执行删除操作，并返回Ture，即操作成功
        if isinstance(table, pd.DataFrame):
            del table
            return True
        #否则返回False，即操作失败
        return False
a=DB()
if __name__ == "__main__":
    # 读取数据
    data = pd.read_csv("C:\\Users\\DELL\\Desktop\\大二下\\01机器学习\\01 作业\\第7章\\chapter7\\watermelon_data_2.csv")
    # print(data)

    data2 = a.select(table=data,sel_columns=["触感"],sel_rows=[1,2,3])
    # print(data2)

    data3 = pd.DataFrame()
    print(data3)