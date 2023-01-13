from sly import Parser
from lex import CompilerLexer
import sys
from pprint import pprint
import asm

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens
    p_cells = {}
    values_of_var = {}
    number_of_var = 2
    label_id = 0
        
    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        main_output_instructions = p.declarations + p.commands + ["HALT"]
        print(p.declarations)
        print(p.commands)
        print(main_output_instructions)
        main_output_instructions = self.delete_labels(main_output_instructions)
                
        print(main_output_instructions)
        
        with open("./moje_wyniki/wyniki.mr", "w") as file:
            file.write("\n".join(main_output_instructions))
        
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
        print("IF condition THEN commands ENDIF")
        endif_label = self.get_label()
        output = []

        instructions_from_cond, jump_type = p.condition
        jump_type += f" {endif_label}"
    
        output += instructions_from_cond + [jump_type] + [endif_label]
        return output + p.commands
         
    
    @_('WHILE condition DO commands ENDWHILE')
    def command(self,p):
        pass
        
    @_('READ ID SEMICOLON')
    def command(self,p):
        if p.ID in self.p_cells:
            return [asm.get(self.p_cells[p.ID])]
        else:
            raise Exception(f"Nie istnieje zmienna {p.ID}")
    
    @_('WRITE value SEMICOLON')
    def command(self,p):
        if p.value in self.p_cells:
            return [f"PUT {self.p_cells[p.value]}"]
        elif type(p.value) == int:
            return [
                asm.set(p.value),
                asm.put(0)
            ]
        else:
            raise Exception("Nie istnieje zmienna " + str(p.value))

    
    @_('ID ASSIGN expression SEMICOLON')
    def command(self,p):
        output = []
        
        if(p.expression[1] == "not_operation"):
            if(type(p.expression[0]) == int):
                output.append(asm.set(p.expression[0]))
                output.append(asm.store(self.p_cells[p.ID]))
            else:
                output.append(asm.load(self.p_cells[p.expression[0]]))
                output.append(asm.store(self.p_cells[p.ID]))
        else:
            output += p.expression[0] + [asm.store(self.p_cells[p.ID])]
            
        return output
    
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
        return (p.value, "not_operation")
    
    @_('value PLUS value')
    def expression(self,p):
        output = []
        
        if type(p.value0) == int and type(p.value1) == int:
            return (p.value0 + p.value1, "not_operation")
        elif type(p.value0) == str and type(p.value1) == int:
            output.append(asm.set(p.value1))
            output.append(asm.add(self.p_cells[p.value0]))
        elif type(p.value0) == int and type(p.value1) == str:
            output.append(asm.set(p.value0))
            output.append(asm.add(self.p_cells[p.value1]))
        elif type(p.value0) == str and type(p.value1) == str:
            output.append(asm.load(self.p_cells[p.value0]))
            output.append(asm.add(self.p_cells[p.value1]))
        
        return (output, "operation")
    
    @_('value MINUS value')
    def expression(self,p):
        output = []
        
        if type(p.value0) == int and type(p.value1) == int:
            if(p.value0 - p.value1 < 0):
                return (0, "not_operation")
            else:
                return (p.value0 - p.value1, "not_operation")
        elif type(p.value0) == str and type(p.value1) == int:
            output.append(asm.set(p.value1))
            output.append(asm.store(1))
            output.append(asm.load(self.p_cells[p.value0]))
            output.append(asm.sub(1))
        elif type(p.value0) == int and type(p.value1) == str:
            output.append(asm.set(p.value0))
            output.append(asm.sub(self.p_cells[p.value1]))
        elif type(p.value0) == str and type(p.value1) == str:
            output.append(asm.load(self.p_cells[p.value0]))
            output.append(asm.sub(self.p_cells[p.value1]))
        
        return (output, "operation")
        
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
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        if(type(p.value0) == str and type(p.value1) == str):
            print("WRRRRRRRRRRRR1")
            return ([
                asm.load(self.p_cells[p.value0]), 
                asm.sub(self.p_cells[p.value1]),
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            print("WRRRRRRRRRRRR2")
            return ([
                asm.set(p.value1),
                asm.store(1),
                asm.load(self.p_cells[p.value0]),
                asm.sub(1)
            ], "JZERO ")
        elif(type(p.value0) == int and type(p.value1) == str):
            print("WRRRRRRRRRRRR3")
            return ([
                asm.set(self.p_cells[p.value1]), 
                asm.store(1),
                asm.set(self.p_cells[p.value0]),
                asm.sub(1)
            ], asm.jzero())
        else:
            if not(p.value0 > p.value1):
                print("BBBBBBBBBBBBBBBB")
                return ([], asm.jzero())
            
        
    @_('value LESS_THAN value')
    def condition(self, p):
        if(type(p.value0) == str and type(p.value1) == str):
            return ([
                asm.load(self.p_cells[p.value1]), 
                asm.sub(self.p_cells[p.value0]),
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(self.p_cells[p.value1]), 
                asm.sub(self.p_cells[p.value0])
            ], asm.jzero)
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(self.p_cells[p.value0]), 
                asm.store(1), 
                asm.load(self.p_cells[p.value1]),
                asm.sub(1)
            ], asm.load())
        else:
            if not(p.value0 < p.value1):
                return ([], asm.jzero())

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
    
    def delete_labels(self, instructions):
        all_labels = []
        index = 1
        for instruction in instructions:
            if instruction.startswith('E'):
                all_labels.append((instruction, index))
                instructions.remove(instruction)
            else:
                index += 1
        
        for index, instruction in enumerate(instructions):
            for label in all_labels:
                if instruction.endswith(label[0]):
                    first_word_instruction = instruction.split()[0]
                    instructions[index] = first_word_instruction + " " + str(label[1])
        
        return instructions
    
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        data = f.read()
    print(data)
    lexer = CompilerLexer()
    parser = CompilerParser()
    #print(list(lexer.tokenize(data)))
    parser.parse(lexer.tokenize(data))

    print("P_cells:")
    print(parser.p_cells)
    print("value of var:")
    print(parser.values_of_var)