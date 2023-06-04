import regex as re
from clauses.clause_def import CLAUSE,TYPES

class SELECT:
    def __init__(self, columns_str: str):
        super().__init__()
        self.type = CLAUSE.SELECT
        if(columns_str == '*'):
            self.columns = TYPES.WILDCARD
        else:
            self.columns = columns_str.split(',')
    
    def get_columns(self):
        return self.columns

if __name__ == "__main__":
    s = SELECT('*')
    print(s.get_columns())