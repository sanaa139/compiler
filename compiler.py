from sly import Parser
from lex import CompilerLexer
import sys
from pprint import pprint

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens
    output = []
    p_cells = {}
    values_of_var = {}
    number_of_var = 2
    label_id = 0
        
    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        main_output_instrutions = p.declarations + p.commands + ["HALT"]
        print(p.declarations)
        print(p.commands)
        print(main_output_instrutions)
        f = open("./moje_wyniki/wyniki.mr", "w")
        for i in main_output_instrutions:
            f.write(f"{i} \n")
        f.close()
        
        
    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):   
        pass
        
    @_('commands command')
    def commands(self,p):
        return p.commands + p.command
    
    @_('command')
    def commands(self,p):
        return p.command
        
    @_('IF condition THEN commands ENDIF')
    def command(self,p):
        endif_label = self.get_label()
        instructions_from_cond, jump_type = p.condition
        jump_type += f" {endif_label}"
        instructions_from_cond += jump_type
        return instructions_from_cond + p.commands
         
    
    @_('WHILE condition DO commands ENDWHILE')
    def command(self,p):
        pass
        
    @_('READ ID SEMICOLON')
    def command(self,p):
        if p.ID in self.p_cells:
            return [f"GET {self.p_cells[p.ID]}"]
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
        self.p_cells[p.ID] = self.get_available_index()
        return []
    
    @_('ID')
    def declarations(self,p):
        self.p_cells[p.ID] = self.get_available_index()
        return []
    
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
    
    @_('value MINUS value')
    def expression(self,p):
        
        pass
    
    @_('NUM')
    def value(self, p):
        return int(p.NUM)
    
    @_('ID')
    def value(self, p):
        return p.ID
    
    @_('value EQ value')
    def condition(self, p):
        pass

    @_('value NEQ value')
    def condition(self, p):
        pass

    @_('value GREATER_THAN value')
    def condition(self, p):
        if(type(p.value0) != int and type(p.value1) != int):
            return ([
                f"LOAD {self.p_cells[p.value0]}", 
                f"SUB {self.p_cells[p.value1]}"
            ], "JZERO")
        elif(type(p.value0) != int and type(p.value1) == int):
            return ([
                f"SET {self.p_cells[p.value1]}",
                f"STORE {1}",
                f"LOAD {self.p_cells[p.value0]}",
                f"SUB {1}"
            ], "JZERO")
        elif(type(p.value0) == int and type(p.value1) != int):
            return ([
                f"SET {self.p_cells[p.value0]}", 
                f"SUB {self.p_cells[p.value1]}"
            ], "JZERO")
        else:
            if not(p.value0 > p.value1):
                return ([], "JZERO")
            
        
    @_('value LESS_THAN value')
    def condition(self, p):
        if(type(p.value0) != int and type(p.value1) != int):
            return ([
                f"LOAD {self.p_cells[p.value1]}", 
                f"SUB {self.p_cells[p.value0]}"
            ], "JZERO")
        elif(type(p.value0) != int and type(p.value1) == int):
            return ([
                f"SET {self.p_cells[p.value1]}", 
                f"SUB {self.p_cells[p.value0]}"
            ], "JZERO")
        elif(type(p.value0) == int and type(p.value1) != int):
            return ([
                f"SET {self.p_cells[p.value0]}", 
                f"STORE {1}", 
                f"LOAD {self.p_cells[p.value1]}"
                f"SUB {1}"
            ], "JZERO")
        else:
            if not(p.value0 < p.value1):
                return ([], "JZERO")

    @_('value GREATER_THAN_OR_EQUAL value')
    def condition(self, p):
        pass

    @_('value LESS_THAN_OR_EQUAL value')
    def condition(self, p):
        pass
    
    
    
    
    def writeToOutput(self, s):
        self.output.append(s)
        
    def get_label(self):
        label = "E_" + str(self.label_id)
        self.label_id += 1
        return label
    
    def get_available_index(self):
        index = self.number_of_var
        self.number_of_var += 1
        return index
        
        
    
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        data = f.read()
    print(data)
    lexer = CompilerLexer()
    parser = CompilerParser()
    #pprint(list(lexer.tokenize(data)))
    parser.parse(lexer.tokenize(data))
    
    parser.output.append("HALT")
    
    print("Output:")
    print(parser.output)
    print("P_cells:")
    print(parser.p_cells)
    print("value of var:")
    print(parser.values_of_var)