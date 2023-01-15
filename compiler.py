from sly import Parser
from lex import CompilerLexer
from dec import DeclarationsParser
import sys
from pprint import pprint
import asm

class CompilerParser(DeclarationsParser):
    tokens = CompilerLexer.tokens
    number_of_var = 2
    label_id = 0
    var_passed_to_proc = []
    proc_names = {}
    current_proc = 0
    
    def __init__(self, p_cells, proc_order):
        super().__init__()
        self.p_cells = p_cells
        self.proc_order = proc_order
    
    
    @_('procedures main')
    def program_all(self, p):
        output = [f"JUMP E_main"] + p.procedures + p.main
        output = self.delete_labels(output)
        output += ["HALT"]
        print(output)
        with open("./moje_wyniki/wyniki.mr", "w") as file:
            file.write("\n".join(output))
    
    @_('procedures procedure')
    def procedures(self, p):
        return p.procedures + p.procedure
    
    @_('')
    def procedures(self, p):
        return []
    
    @_('PROCEDURE proc_head IS VAR declarations BEGIN commands END')
    def procedure(self, p):
        self.current_proc += 1
        return []
    
    @_('PROCEDURE proc_head IS BEGIN commands END')
    def procedure(self, p):
        self.proc_names.append(p.proc_head[0])
        output = ["E_" + p.proc_head[0]] + p.commands
    
        self.current_proc += 1
        return output

    @_('ID LEFT_PARENTHESIS declarations RIGHT_PARENTHESIS')    
    def proc_head(self, p):
        return (p.ID, p.declarations)
    
        
    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        main_output_instructions = ["E_main"] + p.commands
        print(p.declarations)
        print(p.commands)
        print(main_output_instructions)
    
        self.current_proc += 1
        return main_output_instructions
            
    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        main_output_instructions = p.commands
        main_output_instructions = self.delete_labels(main_output_instructions) + ["HALT"]
                
        self.current_proc += 1
        return main_output_instructions
        
    @_('commands command')
    def commands(self,p):
        return p.commands + p.command
    
    @_('command')
    def commands(self,p):
        return p.command
        
    @_(' IF condition THEN commands ELSE commands ENDIF')
    def command(self,p):
        first_cond_not_fulfilled = self.get_label()
        first_cond_fulfilled = self.get_label()
        output = []

        instructions_from_cond, jump_type = p.condition
        jump_type += f" {first_cond_not_fulfilled}"
        jump_outside_of_if = asm.jump() + first_cond_fulfilled
    
        output += instructions_from_cond + [jump_type]
        return output + p.commands0 + [jump_outside_of_if] + [first_cond_not_fulfilled] + p.commands1 + [first_cond_fulfilled]
        
    @_('IF condition THEN commands ENDIF')
    def command(self,p):
        endif_label = self.get_label()
        output = []

        instructions_from_cond, jump_type = p.condition
        jump_type += f" {endif_label}"
    
        output += instructions_from_cond + [jump_type]
        return output + p.commands + [endif_label]
         
    
    @_('WHILE condition DO commands ENDWHILE')
    def command(self,p):
        endwhile_label = self.get_label()
        go_to_while_label = self.get_label()
        output = [go_to_while_label]

        instructions_from_cond, jump_type = p.condition
        jump_type += f" {endwhile_label}"
        jump_to_while = asm.jump()
        jump_to_while += f"{go_to_while_label}"
    
        output += instructions_from_cond + [jump_type]
        return output + p.commands  + [jump_to_while] + [endwhile_label]
    
    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self,p):
        go_to_repeat_label = self.get_label()
        output = []

        instructions_from_cond, jump_type = p.condition
        if jump_type.startswith("JUMP"):
            jump_type = ""
        elif jump_type == "!":
            output.append(go_to_repeat_label)
            jump_type = f"JUMP {go_to_repeat_label}"
        elif jump_type.startswith("JPOS"):
            output.append(go_to_repeat_label)
            jump_type = f"JZERO {go_to_repeat_label}"
        elif jump_type.startswith("JZERO"):
            output.append(go_to_repeat_label)
            jump_type = f"JPOS {go_to_repeat_label}"
    
        output += p.commands + instructions_from_cond
        if jump_type != "":
            output += [jump_type]
        return output
        
    @_('proc_head SEMICOLON')
    def command(self, p):
        label = self.get_available_index()
        
        output = []
        for var in p.proc_head[1]:
            output.append(asm.set(self.p_cells[var]))
            #output.append(asm.store())
        
        return [f"JUMP E_{p.proc_head[0]}", f"E_{label}"]
    
    @_('READ ID SEMICOLON')
    def command(self,p):
        cur_proc = self.get_current_proc_name()

        if (cur_proc, p.ID) in self.p_cells:
            print("KAKAK")
            return [asm.get(self.p_cells[(cur_proc, p.ID)])]
    
    @_('WRITE value SEMICOLON')
    def command(self,p):
        cur_proc = ""
        for proc in self.proc_order:
            if proc[1] == self.current_proc:
                cur_proc = proc
        
        if (cur_proc, p.value) in self.p_cells:
            return [f"PUT {self.p_cells[p.value]}"]
        elif type(p.value) == int:
            return [
                asm.set(p.value),
                asm.put(0)
            ]

    
    @_('ID ASSIGN expression SEMICOLON')
    def command(self,p):
        if p.ID not in self.p_cells:
            raise Exception(f"Nie istnieje zmienna {p.ID}")
        
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
        pass
    
    @_('ID')
    def declarations(self,p):
        pass
    
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
    
    @_('NUM')
    def value(self, p):
        return int(p.NUM)
    
    @_('ID')
    def value(self, p):
        return p.ID
    
    @_('value EQ value')
    def condition(self, p):
        if(type(p.value0) == str and type(p.value1) == str):
            return ([
                asm.load(self.p_cells[p.value0]),
                asm.sub(self.p_cells[p.value1]),
                asm.store(1),
                asm.load(self.p_cells[p.value1]),
                asm.sub(self.p_cells[p.value0]),
                asm.add(1)
            ], asm.jpos())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                asm.load(self.p_cells[p.value0]),
                asm.sub(1),
                asm.store(1),
                asm.set(p.value1),
                asm.sub(self.p_cells[p.value0]),
                asm.add(1)
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                asm.store(1),
                asm.load(self.p_cells[p.value1]),
                asm.sub(1),
                asm.store(1),
                asm.set(p.value0),
                asm.sub(self.p_cells[p.value1]),
                asm.add(1)
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == int):
            if not(p.value0 == p.value1):
                return ([], asm.jump())
            else:
                return ([], "!")

    @_('value NEQ value')
    def condition(self, p):
        if(type(p.value0) == str and type(p.value1) == str):
            return ([
                asm.load(self.p_cells[p.value0]),
                asm.sub(self.p_cells[p.value1]),
                asm.store(1),
                asm.load(self.p_cells[p.value1]),
                asm.sub(self.p_cells[p.value0]),
                asm.add(1)
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                asm.load(self.p_cells[p.value0]),
                asm.sub(1),
                asm.store(1),
                asm.set(p.value1),
                asm.sub(self.p_cells[p.value0]),
                asm.add(1)
            ], asm.jzero())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                asm.store(1),
                asm.load(self.p_cells[p.value1]),
                asm.sub(1),
                asm.store(1),
                asm.set(p.value0),
                asm.sub(self.p_cells[p.value1]),
                asm.add(1)
            ], asm.jzero())
        elif(type(p.value0) == int and type(p.value1) == int):
            if not(p.value0 != p.value1):
                return ([], asm.jump())
            else:
                return ([], "!")

    @_('value GREATER_THAN value')
    def condition(self, p):
        if(type(p.value0) == str and type(p.value1) == str):
            return ([
                asm.load(self.p_cells[p.value0]), 
                asm.sub(self.p_cells[p.value1]),
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                asm.load(self.p_cells[p.value0]),
                asm.sub(1)
            ], asm.jzero())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(self.p_cells[p.value1]), 
                asm.store(1),
                asm.set(self.p_cells[p.value0]),
                asm.sub(1)
            ], asm.jzero())
        else:
            if not(p.value0 > p.value1):
                return ([], asm.jump())
            else:
                return ([], "!")
            
        
    @_('value LESS_THAN value')
    def condition(self, p):
        if(type(p.value0) == str and type(p.value1) == str):
            return ([
                asm.load(self.p_cells[p.value1]), 
                asm.sub(self.p_cells[p.value0]),
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1), 
                asm.sub(self.p_cells[p.value0])
            ], asm.jzero())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(self.p_cells[p.value0]), 
                asm.store(1), 
                asm.load(self.p_cells[p.value1]),
                asm.sub(1)
            ], asm.load())
        else:
            if not(p.value0 < p.value1):
                return ([], asm.jump())
            else:
                return ([], "!")

    @_('value GREATER_THAN_OR_EQUAL value')
    def condition(self, p):
        if(type(p.value0) == str and type(p.value1) == str):
            return ([
                asm.load(self.p_cells[p.value1]),
                asm.sub(self.p_cells[p.value0])
            ], asm.jpos())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.sub(self.p_cells[p.value0])
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                asm.store(1),
                asm.load(self.p_cells[p.value1]),
                asm.sub(1)
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == int):
            if not(p.value0 >= p.value1):
                return ([], asm.jump())
            else:
                return ([], "!")

    @_('value LESS_THAN_OR_EQUAL value')
    def condition(self, p):
        if(type(p.value0) == str and type(p.value1) == str):
            return ([
                asm.load(self.p_cells[p.value0]),
                asm.sub(self.p_cells[p.value1])
            ], asm.jpos())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                asm.load(self.p_cells[p.value0]),
                asm.sub(1)
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                asm.sub(self.p_cells[p.value1])
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == int):
            if not(p.value0 <= p.value1):
                return ([], asm.jump())
            else:
                return ([], "!")
    
    
        
    def get_label(self):
        label = "E_" + str(self.label_id)
        self.label_id += 1
        return label
    
    def get_available_index(self):
        index = self.number_of_var
        self.number_of_var += 1
        return index
    
    def get_current_proc_name(self):
        for proc in self.proc_order:
            if proc[1] == self.current_proc:
                cur_proc = proc[0]
        return cur_proc
    
    def delete_labels(self, instructions):
        all_labels = {}
        indexOfInstructions = 0
        instructions_after_deletion = []
      
        for instruction in instructions:
            if instruction.startswith('E'):
                all_labels[instruction] = indexOfInstructions
            else:
                if not instruction.startswith("!"):
                    instructions_after_deletion.append(instruction)
                    indexOfInstructions += 1
                   
        print(all_labels) 
        print("AAAAAAAAAA")
        for index, instruction in enumerate(instructions_after_deletion):
                splitted_instruction = instruction.split()
                first_word_instruction, second_word_instruction = splitted_instruction[0], splitted_instruction[1]
                if second_word_instruction in all_labels:
                    print(second_word_instruction)
                    instructions_after_deletion[index] = first_word_instruction + f" {all_labels[second_word_instruction]}"
            
        return instructions_after_deletion
    
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        data = f.read()
    print(data)
    lexer = CompilerLexer()
    dec = DeclarationsParser()
    dec.parse(lexer.tokenize(data))
    declared_variables = dec.p_cells
    parser = CompilerParser(dec.p_cells, dec.proc_order)
    #print(list(lexer.tokenize(data)))
    parser.parse(lexer.tokenize(data))

    print("P_cells:")
    print(parser.p_cells)
    