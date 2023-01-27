from sly import Lexer
import sys

class CompilerLexer(Lexer):
    tokens = {
        'IF', 'THEN', 'ELSE', 'ENDIF',
        'WHILE', 'DO', 'ENDWHILE',
        'REPEAT', 'UNTIL',
        'PROCEDURE', 'IS', 'VAR', 'BEGIN', 'BEGIN', 'END',
        'PROGRAM',
        'ASSIGN',
        'READ', 'WRITE',
        'PLUS', 'MINUS', 'MUL', 'DIV', 'MOD',
        'EQ', 'NEQ', 'GREATER_THAN', 'LESS_THAN', 'GREATER_THAN_OR_EQUAL', 'LESS_THAN_OR_EQUAL',
        'SEMICOLON', 'COMMA', 'LEFT_PARENTHESIS', 'RIGHT_PARENTHESIS',
        'NUM', 'ID'
    }

    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDIF = r'ENDIF'
    WHILE = r'WHILE'
    DO = r'DO'
    ENDWHILE =r'ENDWHILE'
    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    PROCEDURE = r'PROCEDURE'
    IS = r'IS'
    VAR = r'VAR'
    BEGIN = r'BEGIN'
    END = r'END'
    PROGRAM = r'PROGRAM'
    ASSIGN = r':='
    READ = r'READ'
    WRITE = r'WRITE'
    PLUS = r'\+'
    MINUS = r'\-'
    MUL = r'\*'
    DIV = r'/'
    MOD = r'\%'
    EQ = r'='
    NEQ = r'!='
    GREATER_THAN_OR_EQUAL = r'>='
    LESS_THAN_OR_EQUAL = r'<='
    GREATER_THAN = r'>'
    LESS_THAN = r'<'
    SEMICOLON = r';'
    COMMA = r','
    LEFT_PARENTHESIS = r'\('
    RIGHT_PARENTHESIS = r'\)'

    ignore = ' \t'
        
    @_(r'\n+')
    def ignore_newline(self, t): 
        self.lineno += len(t.value)
        
    @_(r'[\[][^\]]*[\]]')
    def ignore_comment(self, t): 
        self.lineno += t.value.count('\n')
        
    NUM = r'\d+'
    ID = r'[_a-z]+'

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        data = f.read()
    lexer = CompilerLexer()
    for tok in lexer.tokenize(data):
        print(tok)

