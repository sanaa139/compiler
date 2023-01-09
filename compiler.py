from sly import Parser
from lex import CompilerLexer

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', MUL, DIV)
    )

    @_('procedures main')
    def program_all(self,p):
        pass

    @_('procedures PROCEDURE proc_head IS_VAR declarations BEGIN commands END')
    def procedures(self, p):
        pass
        
    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        pass
        
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
    
    @_('ID ASSIGN expression SEMICOLON')
    def command(self,p):
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
    @_('proc_head SEMICOLON')
    def command(self,p):
        pass
    @_('READ ID SEMICOLON')
    def command(self,p):
        pass
    @_('WRITE value SEMICOLON')
    def command(self,p):
        pass
    
    @_('ID LEFT_PARENTHESIS declarations RIGHT_PARENTHESIS')
    def proc_head(self,p):
        pass
    
    @_('declarations COMMA ID')
    def declarations(self,p):
        pass
    
    @_('ID')
    def declarations(self,p):
        pass
    
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
    
    @_('NUM')
    def value(self, p):
        pass
    
    @_('ID')
    def value(self, p):
        pass
        
    