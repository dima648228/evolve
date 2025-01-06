import re
from lexer.token_ import *
from debug.error_ import *


class Lexer:
    def __init__(self,fn, code) -> None:
        self.fn = fn
        self.code = code
        self.pos = Position(-1,0,-1,fn,code)
        self.currentChar = None

        self.advance()

    def advance(self):
        self.pos.advance(self.currentChar)
        self.currentChar = self.code[self.pos.idx] if self.pos.idx < len(self.code) else None

    def advance_n(self,n):
        for _ in range(n):
            self.advance()

    def make_tokens(self):
        tokens = []

        while self.currentChar != None:
            
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar in "\n":
                self.advance()
            elif self.currentChar == "/" and self.peek() == "/":
                self.skip_comment()
            elif self.currentChar in DIGITS:
                tokens.append(self.make_number())
            elif self.currentChar == '"':
                tokens.append(self.make_string())
            elif self.currentChar == 't' and self.pos.idx + 3 < len(self.code) and self.code[self.pos.idx:self.pos.idx+4] == 'true':
                tokens.append(Token(T_TRUE,pos_start=self.pos))
                self.advance_n(3)
            elif self.currentChar == 'f' and self.pos.idx + 4 < len(self.code) and self.code[self.pos.idx:self.pos.idx+5] == 'false':
                tokens.append(Token(T_FALSE,pos_start=self.pos))
                self.advance_n(4)
            elif self.currentChar == 'v' and self.pos.idx + 2 < len(self.code) and \
                    self.code[self.pos.idx:self.pos.idx+3] == 'var' and \
                    (self.pos.idx + 3 == len(self.code) or self.code[self.pos.idx+3] in ' \t\n()=;#//'):
            
                tokens.append(Token(T_VAR, pos_start=self.pos))
                self.advance_n(3)
            elif self.currentChar in LETTERS:
                tokens.append(self.make_identifier())
            elif self.currentChar == '+':
                tokens.append(Token(T_PLUS, pos_start=self.pos))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(T_MINUS, pos_start=self.pos))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(T_MULTIPLY, pos_start=self.pos))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(T_DIVIDE, pos_start=self.pos))
                self.advance()
            elif self.currentChar == '=':
                tokens.append(Token(T_EQUAL, pos_start=self.pos))
                self.advance()
            elif self.currentChar == ",":
                tokens.append(Token(T_COMMA,pos_start=self.pos))
            elif self.currentChar == '(':
                tokens.append(Token(T_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(T_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.currentChar
                self.advance()
                return [], IllegalCharError(pos_start,self.pos,f"'{char}'")
            
        tokens.append(Token(T_EOF,pos_start=self.pos))
        #print(tokens)

        return tokens, None

    def peek(self):
        peek_pos = self.pos.idx+1
        if peek_pos < len(self.code):
            return self.code[peek_pos]
        return None

    def skip_comment(self):
        while self.currentChar is not None and self.currentChar != "\n":
            self.advance()
        self.advance()

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.currentChar != None and self.currentChar in DIGITS  + '.':
            if self.currentChar == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.currentChar
            
            self.advance()
        
        if dot_count == 0:
            return Token(T_INT, int(num_str),pos_start, self.pos)
        else:
            return Token(T_FLOAT, float(num_str),pos_start,self.pos)
    
    def make_string(self):
        self.advance()
        string = ''
        while self.currentChar != '"':
            string += self.currentChar
            self.advance()
        self.advance()
        return Token(T_STRING, string, self.pos.copy(), self.pos)
    
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.currentChar != None and self.currentChar in LETTERS_DIGITS +'_':
            id_str+=self.currentChar
            self.advance()
        
        tok_type = T_IDENTIFIER

        return Token(tok_type,id_str,pos_start,self.pos)