
#[derive(Debug, Clone, PartialEq)]
pub enum TokenType {
    Assign,      // =
    Plus,        // +
    Minus,       // -
    Asterisk,    // *
    Slash,       // /
    LParen,      // (
    RParen,      // )
    LBrace,      // {
    RBrace,      // }
    Comma,       // ,
    Semicolon,   // ;
    Bang,        // !
    Less,        // <
    Greater,     // >

    Equal,       // ==
    NotEqual,    // !=
    LessEqual,   // <=
    GreaterEqual,// >=

    Ident(String),// Identifier
    Int(i64),     // integer val

    String(String),

    // reserved keywords
    Let,         // let
    Fn,          // fn
    If,          // if
    Else,        // else
    While,       // while
    Return,      // return
    True,        // true
    False,       // false

    Illegal(char), // Unknown symbol (for debugging)
    EOF,           // EOF
}

#[derive(Debug, Clone)]
pub struct Token {
    pub kind: TokenType,
    
    lexeme: String,
    len: usize,

    line: usize,
    column: usize,
}

impl Token {
    pub fn new(kind: TokenType, lexeme: String, len: usize, line: usize, column: usize) -> Self {
        Self {kind, lexeme, len, line, column}
    }
}