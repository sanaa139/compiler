from sly import Parser
from lex import CompilerLexer
import sys
from pprint import pprint

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens
    output = []
    p_cells = {}
        
    @_('commands command')
    def commands(self,p):
        pass
    
    @_('command')
    def commands(self,p):
        pass
        
    @_('READ ID SEMICOLON')
    def command(self,p):
        self.add_to_p_cells(p.ID)
        self.writeToOutput('LOAD 0')
    
    @_('WRITE value SEMICOLON')
    def command(self,p):
        self.writeToOutput('PUT 0')
    
    @_('NUM')
    def value(self, p):
        pass
    
    @_('ID')
    def value(self, p):
        pass
        
    def add_to_p_cells(self, elem):
        self.p_cells['0'] = elem
    
    def writeToOutput(self, s):
        self.output.append(s)
    
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        data = f.read()
    print(data)
    lexer = CompilerLexer()
    parser = CompilerParser()
    #pprint(list(lexer.tokenize(data)))
    parser.parse(lexer.tokenize(data))
    print(parser.output)
    print(parser.p_cells)