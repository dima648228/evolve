mod parser;

use parser::lexer::Lexer;

use crate::parser::ast::{AST};

fn main() {
    let source_code = r#"
        let x = 10;
        let name = "MyLang";
        if x == 10 {
            x = x + 1
        }
    "#;

    let mut lexer = Lexer::new(source_code);
    let tokens = lexer.tokenize();

    let mut ast = AST::new(tokens);
    ast.create();
}
