import string

from enum import Enum


class TokenType(Enum):
    # Типы данных
    T_INT = 'T_INT'
    T_FLOAT = 'T_FLOAT'
    T_STRING = 'T_STRING'
    T_TRUE = 'T_TRUE'
    T_FALSE = 'T_FALSE'
    
    # Арифметические операторы
    T_PLUS = 'PLUS'
    T_MINUS = 'MINUS'
    T_MULTIPLY = 'MULTIPLY'
    T_DIVIDE = 'DIVIDE'
    T_MODULO = 'MODULO'
    T_POWER = 'POWER'

    # Операторы сравнения
    T_EQ = 'EQ'
    T_NE = '!='
    T_LT = 'LT'
    T_GT = 'GT'
    T_LTE = 'LTE'
    T_GTE = 'GTE'

    # Скобки и запятые
    T_LPAREN = 'LPAREN'
    T_RPAREN = 'RPAREN'
    T_LBRACE = 'LBRACE'
    T_RBRACE = 'RBRACE'
    T_LBRACKET = 'LBRACKET'
    T_RBRACKET = 'RBRACKET'
    T_COMMA = 'COMMA'
    T_DOT = 'DOT'
    T_SEMICOLON = 'SEMICOLON'
    T_COLON = 'COLON'
    T_EOF = 'EOF'

    # Общее
    T_IDENTIFIER = 'IDENTIFIER'
    T_EQUAL = 'EQUAL'

    # Ключевые слова
    T_VAR = 'VAR'
    T_IF = 'IF'
    T_ELSE = 'ELSE'
    T_WHILE = 'WHILE'
    T_FOR = 'FOR'
    T_CONTINUE = 'CONTINUE'
    T_BREAK = 'BREAK'
    T_FUNCTION = 'FUNCTION'
    T_RETURN = 'RETURN'
    


# КОНСТАНТЫ [DIGITS, ???]

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

# КЛАСС ТОКЕНА

class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
        else:
            self.pos_start = None

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end

    def matches(self,type_,value):
        return self.type == type_ and self.value == value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

