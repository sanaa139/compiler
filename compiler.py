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
            if not str(self.output[len(self.output) - 1]).startswith('ADD'):
                self.writeToOutput("SET " + str(p.expression))
            if p.ID in self.p_cells:
                self.writeToOutput("STORE " + str(self.p_cells[p.ID]))
                self.values_of_var[p.ID] = int(p.expression)
            else:
                raise Exception("Nie istnieje zmienna " + str(p.ID))
        # gdy expression to ID
        elif p.expression in self.p_cells:
            self.writeToOutput("LOAD " + str(self.p_cells[p.expression]))
            if p.ID in self.p_cells:
                self.writeToOutput("STORE " + str(self.p_cells[p.ID]))
                self.values_of_var[p.ID] = self.values_of_var[p.expression]
            else:
                raise Exception("Nie istnieje zmienna " + str(p.ID))
        else:
            raise Exception("Nie istnieje zmienna " + str(p.expression))
    
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
        # gdy value1 to NUM
        if type(p.value1) == int:
            # gdy value0 to NUM
            if type(p.value0) == int:
                return p.value0 + p.value1
            # gdy value0 to ID
            elif p.value0 in self.p_cells:
                self.writeToOutput("SET " + str(p.value1))
                self.writeToOutput("ADD " + str(self.p_cells[p.value0]))
                return self.values_of_var[p.value0] + p.value1
            else:
                raise Exception("Nie istnieje zmienna " + str(p.value0))
        # gdy value1 to ID
        elif p.value1 in self.p_cells:
            # gdy value0 to NUM
            if type(p.value0) == int:
                self.writeToOutput("STORE " + str(p.value0))
                self.writeToOutput("ADD " + str(self.p_cells[p.value1]))
                return p.value0 + self.values_of_var[p.value1]
            # gdy value0 to ID
            if p.value0 in self.p_cells:
                self.writeToOutput("LOAD " + str(self.p_cells[p.value1]))
                self.writeToOutput("ADD " + str(self.p_cells[p.value0]))
                return self.values_of_var[p.value0] + self.values_of_var[p.value1]
            else:
                raise Exception("Nie istnieje zmienna " + str(p.value0))
        else:
            raise Exception("Nie istnieje zmienna " + str(p.value1))
    
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
    print("Output:")
    print(parser.output)
    print("P_cells:")
    print(parser.p_cells)
    print("value of var:")
    print(parser.values_of_var)