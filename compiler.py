from sly import Parser
from lex import CompilerLexer
import sys
from pprint import pprint

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens
    output = []
    p_cells = {}
    values_of_var = {}
    number_of_var = 1
        
    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        pass
        
    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):   
        pass
        
    @_('commands command')
    def commands(self,p):
        pass
    
    @_('command')
    def commands(self,p):
        pass
        
    @_('READ ID SEMICOLON')
    def command(self,p):
        if p.ID in self.p_cells:
            #DAC WCZYTYWANIE WARTOSCI Z KLAWIATURY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            self.values_of_var[p.ID] = 1
        else:
            raise Exception("Nie istnieje zmienna " + str(p.ID))
    
    @_('WRITE value SEMICOLON')
    def command(self,p):
        if p.value in self.p_cells:
            self.writeToOutput("PUT " + str(self.p_cells[p.value]))
        elif type(p.value) == int:
            self.writeToOutput("SET " + str(p.value))
            self.writeToOutput("PUT 0")
        else:
            raise Exception("Nie istnieje zmienna " + str(p.value))

    
    @_('ID ASSIGN expression SEMICOLON')
    def command(self,p):
        # gdy expression to NUM
        if type(p.expression) == int:
            self.writeToOutput("SET " + str(p.expression))
            if p.ID in self.p_cells:
                self.writeToOutput("ADD " + str(self.p_cells[p.ID]))
            else:
                raise Exception("Nie istnieje zmienna " + str(p.ID))
        # gdy expression to ID
        elif p.expression in self.p_cells:
            self.writeToOutput("LOAD " + str(self.p_cells[p.expression]))
            if p.ID in self.p_cells:
                self.writeToOutput("ADD " + str(self.p_cells[p.ID]))
            else:
                raise Exception("Nie istnieje zmienna " + str(p.ID))
        else:
            raise Exception("Nie istnieje zmienna " + str(p.expression))
        self.writeToOutput("STORE " + str(self.p_cells[p.ID]))
    
    @_('declarations COMMA ID')
    def declarations(self,p):
        self.p_cells[p.ID] = self.number_of_var
        self.writeToOutput('GET ' + str(self.number_of_var))
        self.number_of_var += 1
    
    @_('ID')
    def declarations(self,p):
        self.p_cells[p.ID] = self.number_of_var
        self.writeToOutput('GET ' + str(self.number_of_var))
        self.number_of_var += 1
        pass
    
    @_('value')
    def expression(self,p):
        return p.value
    
    @_('value PLUS value')
    def expression(self,p):
        pass
    
    @_('NUM')
    def value(self, p):
        return int(p.NUM)
    
    @_('ID')
    def value(self, p):
        return p.ID
    
    
    
    
    
    
        
    def add_to_p_cells(self, elem):
        self.p_cells['0'] = elem
    
    def writeToOutput(self, s):
        self.output.append(s)
        
    def getKey(self, value):
        for key in self.p_cells:
            if self.p_cells[key] == value:
                return key
        return -1
        
    
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