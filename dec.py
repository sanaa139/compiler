from sly import Parser
from lex import CompilerLexer
import sys
from exception import MyException

class VariableData():
    def __init__(self, id_num, is_param, is_initialized, needs_initialization):
        self.id_num = id_num
        self.is_param = is_param
        self.is_initialized = is_initialized
        self.needs_initialization = needs_initialization
    def  __repr__(self):
        return  f"Var({self.id_num}, {self.is_param}, {self.is_initialized}, {self.needs_initialization})"

class DeclarationsParser(Parser):
    tokens = CompilerLexer.tokens
    
    def __init__(self):
        self.p_cells = {}
        self.proc_order = []
        self.number_of_var = 8
        self.proc_num = 0
        self.proc_names = []
        
    
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
        self.proc_order.append((p.proc_head[0], self.get_proc_order()))
        
        if p.proc_head[0] in self.proc_names:
            raise MyException(f"Procedura o nazwie {p.proc_head[0]} zadeklarowana drugi raz w linii {p.lineno}")
        else:
            self.proc_names.append(p.proc_head[0])
        
        for var in p.proc_head[1]:
            if (p.proc_head[0], var[0]) in self.p_cells:
                raise MyException(f"Druga deklaracja zmiennej {var[0]} w linii {var[1]}")
            self.p_cells[(p.proc_head[0], var[0])] = VariableData(self.get_available_index(), True, False, False)
        for var in p.declarations:
            if (p.proc_head[0], var[0]) in self.p_cells:
                raise MyException(f"Druga deklaracja zmiennej {var[0]} w linii {var[1]}")
            self.p_cells[(p.proc_head[0], var[0])] = VariableData(self.get_available_index(), False, False, False)
        self.p_cells[(p.proc_head[0], "$ret")] = VariableData(self.get_available_index(), True, False, False)
    
    @_('PROCEDURE proc_head IS BEGIN commands END')
    def procedure(self, p):
        self.proc_order.append((p.proc_head[0], self.get_proc_order()))
        
        if p.proc_head[0] in self.proc_names:
            raise MyException(f"Procedura o nazwie {p.proc_head[0]} zadeklarowana drugi raz w linii {p.lineno}")
        else:
            self.proc_names.append(p.proc_head[0])
        
        for var in p.proc_head[1]:
            if (p.proc_head[0], var[0]) in self.p_cells:
                raise MyException(f"Druga deklaracja zmiennej {var[0]} w linii {var[1]}")
            self.p_cells[(p.proc_head[0], var[0])] = VariableData(self.get_available_index(), True, False, False)
        self.p_cells[(p.proc_head[0], "$ret")] = VariableData(self.get_available_index(), True, False, False)

    @_('ID LEFT_PARENTHESIS declarations RIGHT_PARENTHESIS')    
    def proc_head(self, p):
        return (p.ID, p.declarations)
    
        
    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        self.proc_order.append(("main", self.get_proc_order()))
        
        for var in p.declarations:
            if ("main", var[0]) in self.p_cells:
                raise MyException(f"Druga deklaracja zmiennej {var[0]} w linii {var[1]}")
            self.p_cells[("main", var[0])] = VariableData(self.get_available_index(), False, False, False)
            
    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        self.proc_order.append(("main", self.get_proc_order()))
        
        
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
        return p.declarations + [(p.ID, p.lineno)]
    
    @_('ID')
    def declarations(self,p):
        return [(p.ID, p.lineno)]
    
    @_('value')
    def expression(self,p):
        pass
    
    @_('value PLUS value')
    def expression(self,p):
        pass
    
    @_('value MINUS value')
    def expression(self,p):
        pass
    
    @_('value MUL value')
    def expression(self,p):
        pass
    
    @_('value DIV value')
    def expression(self,p):
        pass
    
    @_('value MOD value')
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
    try:
        parser.parse(lexer.tokenize(data))
    except MyException as e:
        red = '\033[91m'
        reset = '\033[0m'
        print(f"{red}[Error]{reset} {e}")