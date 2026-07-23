use crate::parser::token::{Token};

pub struct AST {
    tokens: Vec<Token>
}

impl AST {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self {tokens}
    }

    pub fn create(&mut self) {
        for tok in &self.tokens {
            print!("{:?}", tok);
        }
    }
}