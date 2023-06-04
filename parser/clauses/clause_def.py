from enum import Enum

class CLAUSE(Enum):
    SELECT = 1
    FROM = 2
    WHERE = 3
    GROUP_BY = 4
    ORDER_BY = 5

class TYPES(Enum):
    INT = 1
    FLOAT = 2
    CHAR = 3
    VARCHAR = 4
    WILDCARD = 5
    STRING = 6