from collections import deque
import itertools

from sql_parse import tokens, keywords
import regex as re


class tokenizer:
    def set_SQL_REGEX(self, SQL_REGEX):
        """
        导入keywords中设计的，所有用于判断token类型的正则表达式
        """
        FLAGS = re.IGNORECASE | re.UNICODE
        self._SQL_REGEX = [
            (re.compile(rx, FLAGS).match, tt)
            for rx, tt in SQL_REGEX
        ]
    
    def default_initialization(self):
        """
        初始化
        包含内容：导入正则，导入关键字
        """
        self._SQL_REGEX = []
        self._keywords = []
        self.set_SQL_REGEX(keywords.SQL_REGEX)
        self._keywords.append(keywords.KEYWORDS_COMMON)
        self._keywords.append(keywords.KEYWORDS)

    def is_keyword(self, value):
        """
        判断当前的内容是一个NAME还是关键字

        如果当前的内容是KEYWORDS或KEYWORDS_*中的一部分，那么就返回关键字的类型
        否则返回tokens.Name，即认为这是一个NAME而非KEYWORD
        """
        val = value.upper()
        for kwdict in self._keywords:
            if val in kwdict:
                return kwdict[val], value
        else:
            return tokens.Name, value

    def consume(self,iterator, n):
        """
        将迭代器向后推动n个位置，即跳过n个元素，这里是为了在匹配到字符为token后，跳过已匹配部分
        """
        deque(itertools.islice(iterator, n), maxlen=0)

    def tokenize(self,text: str):
        """
        将文本序列token化
        返回的是一个generator，可以迭代元组（ToeknType, Value）

        为了方便，这里的Tokenize不会对文本进行预处理，即不会将tab转换为空格，也不会去除空格
        此外，多行文本被压缩为一行，并去除了换行符，并且只能处理一行token
        """
        text = text.replace("\n", " ").strip().rstrip() # 将text限制为一行
        iterable = enumerate(text)
        for pos, char in iterable: # 创建指针，处理当前指针向后看的字符
            for rexmatch, action in self._SQL_REGEX:
                m = rexmatch(text, pos)
                t = type(action)

                if not m:       # 从这个字符往后看，并不能匹配出任何的关键字或者token
                    continue
                elif isinstance(action, tokens._TokenType): # 如果这是一个普通Token
                    yield action, m.group()
                elif action is keywords.PROCESS_AS_KEYWORD: # 如果这是一个关键字
                    yield self.is_keyword(m.group())

                self.consume(iterable, m.end() - pos - 1) # 将处理的指针向后移动，直到匹配到的token的最后一个字符
                break
            else:
                yield tokens.Error, char


if __name__ == "__main__":
    sql = """
    SELECT id, name, this
    FROM table
    WHERE id = 1 AND this < 2.3;
    """
    a = tokenizer()
    a.default_initialization()
    token_my = a.tokenize(sql)
    ret = []
    for ttype, value in token_my:
        ret.append((ttype, value))
    print(ret)


    # sql = """
    # select a0, b0, c0, d0, e0 from 
    # (select * from dual) 
    # where a0=1 and b0=2'
    # """
    # a = tokenizer()
    # a.default_initialization()
    # token_my = a.tokenize(sql)
    # ret = []
    # for ttype, value in token_my:
    #     ret.append((ttype, value))
    # print(ret)