use std::{iter::Peekable, str::Chars};

use crate::parser::token::{Token, TokenType};

pub struct Lexer<'a> {
    chars: Peekable<Chars<'a>>, 
    line: usize,
    column: usize,
}

impl<'a> Lexer<'a> {
    pub fn new(input: &'a str) -> Self {
        Self {
            chars: input.chars().peekable(),
            line: 1,
            column: 1,
        }
    }

    pub fn tokenize(&mut self) -> Vec<Token> {
        let mut tokens = Vec::new();
        
        loop {
            let token = self.next_token();
            let is_eof = matches!(token.kind, TokenType::EOF); 
            
            tokens.push(token);
            
            if is_eof {
                break;
            }
        }
        
        tokens
    }

    pub fn next_token(&mut self) -> Token {
        self.skip_whitespace();

        let current_column = self.column;

        match self.chars.next() {
            Some('=') => {
                if self.chars.peek() == Some(&'=') {
                    self.chars.next();
                    self.column += 2;

                    Token::new(TokenType::Equal, "==".to_string(), 2, self.line, current_column)
                } else {
                    self.column += 1;

                    Token::new(TokenType::Assign, "=".to_string(), 1, self.line, current_column)
                }
            },
            Some('+') => {
                self.column += 1;
                Token::new(TokenType::Plus, "+".to_string(), 1, self.line, current_column)
            },
            Some('-') => {
                self.column += 1;
                Token::new(TokenType::Minus, "-".to_string(), 1, self.line, current_column)
            },
            Some('*') => {
                self.column += 1;
                Token::new(TokenType::Asterisk, "*".to_string(), 1, self.line, current_column)
            },
            Some('/') => {
                self.column += 1;
                Token::new(TokenType::Slash, "/".to_string(), 1, self.line, current_column)
            },

            Some('(') => {
                self.column += 1;
                Token::new(TokenType::LParen, "(".to_string(), 1, self.line, current_column)
            },
            Some(')') => {
                self.column += 1;
                Token::new(TokenType::RParen, ")".to_string(), 1, self.line, current_column)
            },
            Some('{') => {
                self.column += 1;
                Token::new(TokenType::LBrace, "{".to_string(), 1, self.line, current_column)
            },
            Some('}') => {
                self.column += 1;
                Token::new(TokenType::RBrace, "}".to_string(), 1, self.line, current_column)
            },

            Some(',') => {
                self.column += 1;
                Token::new(TokenType::Comma, ",".to_string(), 1, self.line, current_column)
            },
            Some(';') => {
                self.column += 1;
                Token::new(TokenType::Semicolon, ";".to_string(), 1, self.line, current_column)
            },
            Some('!') => {
                if self.chars.peek() == Some(&'=') {
                    self.next_token();
                    self.column += 2;

                    Token::new(TokenType::NotEqual, "!=".to_string(), 2, self.line, current_column)
                } else {
                    self.column += 1;

                    Token::new(TokenType::Bang, "!".to_string(), 1, self.line, current_column)
                }
            },

            Some('>') => {
                if self.chars.peek() == Some(&'=') {
                    self.next_token();
                    self.column += 2;

                    Token::new(TokenType::GreaterEqual, ">=".to_string(), 2, self.line, current_column)
                } else {
                    self.column += 1;

                    Token::new(TokenType::Greater, ">".to_string(), 1, self.line, current_column)
                }
            },
            Some('<') => {
                if self.chars.peek() == Some(&'=') {
                    self.next_token();
                    self.column += 2;

                    Token::new(TokenType::LessEqual, "<=".to_string(), 2, self.line, current_column)
                } else {
                    self.column += 1;

                    Token::new(TokenType::Less, "<".to_string(), 1, self.line, current_column)
                }
            },

            Some('"') => self.read_string(current_column),

            Some(c) if c.is_ascii_alphabetic() || c == '_' => {
                self.read_identifier(c, current_column)
            },

            Some(c) if c.is_ascii_digit() => {
                self.read_number(c, current_column)
            },

            None => Token::new(TokenType::EOF, "".to_string(), 0, self.line, current_column),

            Some(c) => panic!("Undefined symbol on line {}:{}: {}", self.line, current_column, c),
        }
    }

    fn skip_whitespace(&mut self) {
        while let Some(&c) = self.chars.peek() {
            match c {
                ' ' | '\t' | '\r' => {
                    self.chars.next();
                    self.column += 1;
                }
                '\n' => {
                    self.chars.next();
                    self.line += 1;
                    self.column = 1;
                }
                _ => break,
            }
        }
    }

    fn read_number(&mut self, first_char: char, start_column: usize) -> Token {
        let mut value = String::new();
        value.push(first_char);
        self.column += 1;

        while let Some(&c) = self.chars.peek() {
            if c.is_ascii_digit() {
                value.push(c);
                self.chars.next();
                self.column += 1;
            } else {
                break;
            }
        }

        let int_val: i64 = value.parse().unwrap(); 
        let len = value.len();

        Token::new(TokenType::Int(int_val), value, len, self.line, start_column)
    }

    fn read_identifier(&mut self, first_char: char, start_column: usize) -> Token {
        let mut value = String::new();
        value.push(first_char);
        self.column += 1;

        while let Some(&c) = self.chars.peek() {
            if c.is_ascii_alphanumeric() || c == '_' {
                value.push(c);
                self.chars.next();
                self.column += 1;
            } else {
                break;
            }
        }

        let len = value.len();

        let kind = match value.as_str() {
            "let" => TokenType::Let,
            "fn" => TokenType::Fn,
            "if" => TokenType::If,
            "else" => TokenType::Else,
            "while" => TokenType::While,
            "return" => TokenType::Return,
            "true" => TokenType::True,
            "false" => TokenType::False,
            _ => TokenType::Ident(value.clone()),
        };

        Token::new(kind, value, len, self.line, start_column)
    }

    fn read_string(&mut self, start_column: usize) -> Token {
        let mut value = String::new();
        self.column += 1;

        while let Some(c) = self.chars.next() {
            self.column += 1;
            
            if c == '"' {
                break;
            }
            value.push(c);
        }

        let lexeme = format!("\"{}\"", value); 
        let len = lexeme.len();

        Token::new(TokenType::String(value), lexeme, len, self.line, start_column)
    }
}
