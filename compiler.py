from sly import Parser
from lex import CompilerLexer
from dec import DeclarationsParser
from dec import VariableData
import sys
from pprint import pprint
import asm

class CompilerParser(DeclarationsParser):
    tokens = CompilerLexer.tokens
    number_of_var = 2
    label_id = 0
    current_proc = 0
    
    def __init__(self, p_cells, proc_order):
        super().__init__()
        self.p_cells = p_cells
        self.proc_order = proc_order
        self.var_passed_to_proc = []
    
    
    @_('procedures main')
    def program_all(self, p):
        output = [f"JUMP E_main"] + p.procedures + p.main
        print(output)
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
        output = ["E_" + p.proc_head[0]] + p.commands
        self.current_proc += 1
        return output
    
    @_('PROCEDURE proc_head IS BEGIN commands END')
    def procedure(self, p):
        index = self.get("$ret", p.proc_head[0]).id_num
        output = ["E_" + p.proc_head[0]] + p.commands + [f"JUMPI {index}"]
        
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
        
    @_('IF condition THEN commands ELSE commands ENDIF')
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
        variables_from_proc = [item[1] for item in self.p_cells if item[0] == p.proc_head[0]]
        for var_main, var_proc in zip(p.proc_head[1], variables_from_proc):
            output.append(asm.set(self.get(var_main).id_num))
            output.append(asm.store(self.get(var_proc, p.proc_head[0]).id_num))
            if self.get(var_main).is_initialized is True:
                self.get(var_proc, p.proc_head[0]).is_initialized = True
        
        output.append(asm.set(f"E_{label}"))
        output.append(asm.store(self.get("$ret", p.proc_head[0]).id_num))
        
        for var in p.proc_head[1]:
            self.get(var).is_initialized = True

        return output + [f"JUMP E_{p.proc_head[0]}", f"E_{label}"]
    
    @_('READ ID SEMICOLON')
    def command(self,p):
        if self.get(p.ID):
            self.get(p.ID).is_initialized = True
            return [asm.get(self.get(p.ID).id_num)]
    
    @_('WRITE value SEMICOLON')
    def command(self,p):       
        print("CURRENT PROC") 
        print(self.current_proc)
        if self.get(p.value):
            if not self.get(p.value).is_initialized:
                raise Exception(f"Zmienna {p.value} nie została zainicjalizowana")
            output = asm.put(self.get(p.value).id_num)
            return [f"{output}"]
        elif type(p.value) == int:
            return [
                asm.set(p.value),
                asm.put(0)
            ]

    
    @_('ID ASSIGN expression SEMICOLON')
    def command(self,p):
        output = []
        
        if(p.expression[1] == "not_operation"):
            if(type(p.expression[0]) == int):
                output.append(asm.set(p.expression[0]))
                output.append(self.GEN_STORE(p.ID))
                self.get(p.ID).is_initialized = True
            else:
                output.append(self.GEN_LOAD((p.expression[0])))
                output.append(self.GEN_STORE(p.ID))
                self.get(p.ID).is_initialized = True
        else:
            output += p.expression[0] + [self.GEN_STORE(p.ID)]
            self.get(p.ID).is_initialized = True
           
            
        return output
    
    @_('declarations COMMA ID')
    def declarations(self,p):
        return p.declarations + [p.ID]
    
    @_('ID')
    def declarations(self,p):
        return [p.ID]
    
    @_('value')
    def expression(self,p):
        return (p.value, "not_operation")
    
    @_('value PLUS value')
    def expression(self,p):
        output = []
        
        if type(p.value0) == int and type(p.value1) == int:
            return (p.value0 + p.value1, "not_operation")
        elif type(p.value0) == str and type(p.value1) == int:
            self.check_if_initialized(p.value0)
            output.append(asm.set(p.value1))
            output.append(self.GEN_ADD((p.value0)))
        elif type(p.value0) == int and type(p.value1) == str:
            self.check_if_initialized(p.value1)
            output.append(asm.set(p.value0))
            output.append(self.GEN_ADD((p.value1)))
        elif type(p.value0) == str and type(p.value1) == str:
            self.check_if_initialized(p.value0)
            self.check_if_initialized(p.value1)
            output.append(self.GEN_LOAD((p.value0)))
            output.append(self.GEN_ADD((p.value1)))
        
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
            output.append(self.GEN_LOAD((p.value0)))
            output.append(asm.sub(1))
        elif type(p.value0) == int and type(p.value1) == str:
            output.append(asm.set(p.value0))
            output.append(self.GEN_SUB((p.value1)))
        elif type(p.value0) == str and type(p.value1) == str:
            output.append(self.GEN_LOAD((p.value0)))
            output.append(self.GEN_SUB((p.value1)))
         
        
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
                self.GEN_LOAD((p.value0)), 
                self.GEN_SUB((p.value1)),
                asm.store(1),
                self.GEN_LOAD((p.value1)),
                self.GEN_SUB((p.value0)),
                asm.add(1)
            ], asm.jpos())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                self.GEN_LOAD((p.value0)),    
                asm.sub(1),
                asm.store(1),
                asm.set(p.value1),
                self.GEN_SUB((p.value0)),
                asm.add(1)
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                asm.store(1),
                self.GEN_LOAD((p.value1)),
                asm.sub(1),
                asm.store(1),
                asm.set(p.value0),
                self.GEN_SUB((p.value1)),
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
                self.GEN_LOAD((p.value0)),
                self.GEN_SUB((p.value1)),                
                asm.store(1),
                self.GEN_LOAD((p.value1)),
                self.GEN_SUB((p.value0)),
                asm.add(1)
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                self.GEN_LOAD((p.value0)),
                asm.sub(1),
                asm.store(1),
                asm.set(p.value1),
                self.GEN_SUB((p.value0)),
                asm.add(1)
            ], asm.jzero())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                asm.store(1),
                self.GEN_LOAD((p.value1)),
                asm.sub(1),
                asm.store(1),
                asm.set(p.value0),
                self.GEN_SUB((p.value1)),
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
                self.GEN_LOAD((p.value0)), 
                self.GEN_SUB((p.value1)),
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                self.GEN_LOAD((p.value0)),
                asm.sub(1)
            ], asm.jzero())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set((p.value1).id_num), 
                asm.store(1),
                asm.set((p.value0).id_num),
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
                self.GEN_LOAD((p.value1)), 
                self.GEN_SUB((p.value0)),
            ], asm.jzero())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1), 
                self.GEN_SUB((p.value0))
            ], asm.jzero())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set((p.value0).id_num), 
                asm.store(1), 
                self.GEN_LOAD((p.value1)),
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
                self.GEN_LOAD((p.value1)),
                self.GEN_SUB((p.value0))
            ], asm.jpos())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                self.GEN_SUB((p.value0))
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                asm.store(1),
                self.GEN_LOAD((p.value1)),
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
                self.GEN_LOAD((p.value0)),
                self.GEN_SUB((p.value1))
            ], asm.jpos())
        elif(type(p.value0) == str and type(p.value1) == int):
            return ([
                asm.set(p.value1),
                asm.store(1),
                self.GEN_LOAD((p.value0)),
                asm.sub(1)
            ], asm.jpos())
        elif(type(p.value0) == int and type(p.value1) == str):
            return ([
                asm.set(p.value0),
                self.GEN_SUB((p.value1))
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
    
    def get(self, name, procedure = None):
        cur_proc = self.get_current_proc_name()
        got = self.p_cells.get((cur_proc, name))
        
        if procedure is not None:
            got = self.p_cells.get((procedure, name))
        elif got is None and type(name) == str:
            raise Exception(f"Nie zadeklarowana zmienna {name}")
        return got
    
    def check_if_initialized(self, name):
        cur_proc = self.get_current_proc_name()
        got = self.p_cells.get((cur_proc, name))
        
        if got.is_initialized is False:
            raise Exception(f"Zmienna {name} nie została zainicjalizowana")
        
    def get_current_proc_name(self):
        for proc in self.proc_order:
            if proc[1] == self.current_proc:
                cur_proc = proc[0]
        return cur_proc
    
    def GEN_SUB(self, var):
        if self.get(var).is_param:
            return asm.subi(self.get(var).id_num)
        else:
            return asm.sub(self.get(var).id_num)
        
    def GEN_ADD(self, var):
        if self.get(var).is_param:
            return asm.addi(self.get(var).id_num)
        else:
            return asm.add(self.get(var).id_num)
        
    def GEN_LOAD(self, var):
        if self.get(var).is_param:
            return asm.loadi(self.get(var).id_num)
        else:
            return asm.load(self.get(var).id_num)
        
    def GEN_STORE(self, var):
        if self.get(var).is_param:
            return asm.storei(self.get(var).id_num)
        else:
            return asm.store(self.get(var).id_num)

    
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
    