from sly import Parser
from lex import CompilerLexer
import sys

class DeclarationsParser(Parser):
    tokens = CompilerLexer.tokens
    
    def __init__(self):
        self.p_cells = {}
        self.proc_order = {}
        self.number_of_var = 2
        self.proc_num = 0
    
    @_('procedures main')
    def program_all(self, p):
        pass
    
    @_('procedures procedure')
    def procedures(self, p):
        pass
    
    @_('')
    def procedures(self, p):
        pass
    
    @_('PROCEDURE proc_head IS VAR declarations BEGIN commands END')
    def procedure(self, p):
        self.proc_order[p.proc_head[0]] = self.get_proc_order()
        
        for var in p.proc_head[1]:
            if (p.proc_head[0], var) in self.p_cells:
                raise Exception(f"Zmienna {var} została wcześniej zadeklarowana")
            self.p_cells[(p.proc_head[0], var)] = self.get_available_index()
        for var in p.declarations:
            if (p.proc_head[0], var) in self.p_cells:
                raise Exception(f"Zmienna {var} została wcześniej zadeklarowana")
            self.p_cells[(p.proc_head[0], var)] = self.get_available_index()
        return ''
    
    @_('PROCEDURE proc_head IS BEGIN commands END')
    def procedure(self, p):
        self.proc_order[p.proc_head[0]] = self.get_proc_order()
        
        for var in p.proc_head[1]:
            if (p.proc_head[0], var) in self.p_cells:
                raise Exception(f"Zmienna {var} została wcześniej zadeklarowana")
            self.p_cells[(p.proc_head[0], var)] = self.get_available_index()
        pass

    @_('ID LEFT_PARENTHESIS declarations RIGHT_PARENTHESIS')    
    def proc_head(self, p):
        return (p.ID, p.declarations)
    
        
    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        self.proc_order["main"] = self.get_proc_order()
        
        for var in p.declarations:
            if ("main", var) in self.p_cells:
                raise Exception(f"Zmienna {var} została wcześniej zadeklarowana")
            self.p_cells[("main", var)] = self.get_available_index()
            
    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        self.proc_order["main"] = self.get_proc_order()
        
        
    @_('commands command')
    def commands(self,p):
        pass
    
    @_('command')
    def commands(self,p):
        pass
        
    @_(' IF condition THEN commands ELSE commands ENDIF')
    def command(self,p):
       pass
        
    @_('IF condition THEN commands ENDIF')
    def command(self,p):
        pass
         
    @_('WHILE condition DO commands ENDWHILE')
    def command(self,p):
        pass
    
    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self,p):
        pass
    
    @_('proc_head SEMICOLON')
    def command(self, p):
        pass
    
    @_('READ ID SEMICOLON')
    def command(self,p):
        pass
    
    @_('WRITE value SEMICOLON')
    def command(self,p):
        pass
    
    @_('ID ASSIGN expression SEMICOLON')
    def command(self,p):
        pass
    
    @_('declarations COMMA ID')
    def declarations(self,p):
        return p.declarations + [p.ID]
    
    @_('ID')
    def declarations(self,p):
        return [p.ID]
    
    @_('value')
    def expression(self,p):
        pass
    
    @_('value PLUS value')
    def expression(self,p):
        pass
    
    @_('value MINUS value')
    def expression(self,p):
        pass
    
    @_('NUM')
    def value(self, p):
        pass
    
    @_('ID')
    def value(self, p):
        pass
    
    @_('value EQ value')
    def condition(self, p):
        pass

    @_('value NEQ value')
    def condition(self, p):
        pass

    @_('value GREATER_THAN value')
    def condition(self, p):
        pass
        
    @_('value LESS_THAN value')
    def condition(self, p):
        pass

    @_('value GREATER_THAN_OR_EQUAL value')
    def condition(self, p):
        pass

    @_('value LESS_THAN_OR_EQUAL value')
    def condition(self, p):
        pass
    
    def get_available_index(self):
        index = self.number_of_var
        self.number_of_var += 1
        return index
    
    def get_proc_order(self):
        index = self.proc_num
        self.proc_num += 1
        return index
    
    
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        data = f.read()
    lexer = CompilerLexer()
    parser = DeclarationsParser()
    parser.parse(lexer.tokenize(data))
    print(parser.p_cells)
    print(parser.proc_order)