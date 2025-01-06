import string

# TOKEN TYPES [DATA TYPES]
T_INT = 'T_INT'
T_FLOAT = 'T_FLOAT'
T_STRING = 'T_STRING'
T_TRUE = 'T_TRUE'
T_FALSE = 'T_FALSE'

# TOKEN TYPES [OPERATOR]
T_PLUS = 'PLUS'
T_MINUS = 'MINUS'
T_MULTIPLY = 'MULTIPLY'
T_DIVIDE = 'DIVIDE'

# TOKEN TYPES [PARENS]
T_LPAREN = 'LPAREN'
T_RPAREN = 'RPAREN'
T_COMMA = 'COMMA'
T_EOF = 'EOF'

# GENERAL
T_KEYWORD = 'KEYWORD'
T_VAR = 'VAR'
T_IDENTIFIER = 'IDENTIFIER'
T_EQUAL = 'EQUAL'

# CONSTANS [DIGITS, ???]

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

# THE TOKEN CLASS

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

