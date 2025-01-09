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

    def is_digital(self):
        return self.currentChar in DIGITS

    def make_tokens(self):
        tokens = []
        single_char_tokens = {
            '+': TokenType.T_PLUS,
            '-': TokenType.T_MINUS,
            '*': TokenType.T_MULTIPLY,
            '/': TokenType.T_DIVIDE,
            '=': TokenType.T_EQUAL,
            ',': TokenType.T_COMMA,
            '(': TokenType.T_LPAREN,
            ')': TokenType.T_RPAREN,
            ';': TokenType.T_SEMICOLON
        }

        keywords = {
            'true': TokenType.T_TRUE,
            'false': TokenType.T_FALSE,
            'var': TokenType.T_KEYWORD
        }

        while self.currentChar is not None:
            if self.currentChar in ' \t\n':
                self.advance()
            elif self.currentChar == '/' and self.peek() == '/':
                self.skip_comment()
            elif self.currentChar in DIGITS:
                tokens.append(self.make_number())
            elif self.currentChar == '"':
                tokens.append(self.make_string())
            elif self.currentChar in LETTERS:
                tokens.append(self.make_identifier_or_keyword(keywords))
            elif self.currentChar in single_char_tokens:
                tokens.append(Token(single_char_tokens[self.currentChar], pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.currentChar
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")

        tokens.append(Token(TokenType.T_EOF, pos_start=self.pos))
        return tokens, None

    def peek(self):
        peek_pos = self.pos.idx + 1
        return self.code[peek_pos] if peek_pos < len(self.code) else None

    def skip_comment(self):
        while self.currentChar is not None and self.currentChar != "\n":
            self.advance()
        self.advance()

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.currentChar is not None and self.currentChar in DIGITS + '.':
            if self.currentChar == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()

        token_type = TokenType.T_FLOAT if dot_count == 1 else TokenType.T_INT
        return Token(token_type, float(num_str) if dot_count == 1 else int(num_str), pos_start, self.pos)

    def make_string(self):
        self.advance()
        string = ''
        while self.currentChar != '"':
            string += self.currentChar
            self.advance()
        self.advance()
        return Token(TokenType.T_STRING, string, self.pos.copy(), self.pos)

    def make_identifier_or_keyword(self, keywords):
        id_str = ''
        pos_start = self.pos.copy()

        while self.currentChar is not None and self.currentChar in LETTERS_DIGITS + '_':
            id_str += self.currentChar
            self.advance()

        tok_type = keywords.get(id_str, TokenType.T_IDENTIFIER)
        return Token(tok_type, id_str, pos_start, self.pos)