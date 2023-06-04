from clauses.clause_SELECT import SELECT
import regex as re

RE_ALL = "select\s+(.*?)\s*from\s+(.*?)\s*(where\s(.*?)\s*)?"

class AST:
    def __init__(self, query: str):
        self.clause_select,query = self.parse_select(query)
        # self.clause_from,query = self.parse_from(query)
        # self.clause_where,query = self.parse_where(query)
    
    def parse_select(self, query: str) -> tuple[SELECT, str]:
        """
        根据query字符串，解析出SELECT语句以及其包含的columns，
        返回SELECT的内容以及剩下未解析的字符串
        """
        pattern_SELECT = "select\s+(.*?)\s*(from.*;)"
        matches = re.match(pattern_SELECT,query)

        columns = matches.group(1)
        clause_select = SELECT(columns)

        query_rest = matches.group(2)

        return clause_select, query_rest
    

if __name__ == "__main__":
    query = "select id, name, 23 from table where id = 1;"
    ast = AST(query)
    print(ast.clause_select.get_columns())
    # print(ast.clause_from)
    # print(ast.clause_where)