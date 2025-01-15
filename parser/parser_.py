from lexer.token_ import *
from debug.error_ import *
from parser.nodes import *

from enum import Enum

# КЛАСС ДЛЯ ВОЗВРАЩЕНИЯ РЕЗУЛЬТАТА О ПАРСИНГЕ ТОКЕНА

class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def set_result(self, success, node_or_error):
        if success:
            self.node = node_or_error
        else:
            self.error = node_or_error
        return self

    def success(self, node):
        return self.set_result(True, node)

    def failure(self, error):
        return self.set_result(False, error)

# СПИСОК ТОКЕНОВ, КОТОРЫЕ ДОЛЖЕН ПРОПУСКАТЬ ПАРСЕР НА МОМЕНТЕ ПЕРВИЧНОЙ ОБРАБОТКИ ТОКЕНОВ

SKIPPABLE_TOKENS = {
    TokenType.T_EQUAL,
    TokenType.T_FLOAT,
    TokenType.T_INT,
    TokenType.T_STRING,
    TokenType.T_SEMICOLON
}


# КЛАСС ПАРСЕРА

class Parser:
    """Инициализация парсера. Он принимает в качестве аргумента токены из лексического анализатора."""

    def __init__(self, tokens):
        self.tokens = tokens
        #print(tokens)
        self.tok_idx = -1
        self.symbol_table = {} # Локальная таблица символов. Это вспомогательная таблица для того, чтобы выявить повторения обьявления каких нибудь структур данных

        self.advance()

    """Обновление позиции при чтении токенов."""
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        else:
            self.current_tok = None
        return self.current_tok

    """Сам парсинг токенов. Он будет продолжаться до того момента, пока не увидит {TokenType.T_EOF} токен."""
    def parse(self):
        res = ParseResult()
        statements = []

        # Парсим все выражения до конца файла
        while self.current_tok.type != TokenType.T_EOF:
            statement = res.register(self.statement())
            if res.error:
                return res.failure(res.error)
            if statement:
                statements.append(statement)

        # Возвращаем список всех выражений в виде узла
        return res.success(ListNode(statements)) if statements else res.failure(
            InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected at least one statement")
        )

    def check_token(self, expected_type, error_msg):
        if self.current_tok.type != expected_type:
            return ParseResult().failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, error_msg))
        self.advance()
        return ParseResult().success(self.current_tok)

    def statement(self):
        res = ParseResult()
        tok = self.current_tok

        # Обрабатываем ключевое слово var
        if tok.type == TokenType.T_VAR:
            return self.handle_var_declaration(res)
        # Обрабатываем ключевое слово function
        elif tok.type == TokenType.T_FUNCTION:
            return self.handle_function_declaration(res)
        # Обрабатываем идентификаторы
        elif tok.type == TokenType.T_IDENTIFIER:
            return self.handle_identifier(res, tok)
        else:
            expr = res.register(self.expression())
            return res.success(expr) if not res.error else res

    def handle_var_declaration(self, res):
        res.register(self.advance())
        if self.current_tok.type != TokenType.T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected variable name after 'var'"
            ))
        var_name = self.current_tok
        if var_name.value in self.symbol_table:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Variable '{var_name.value}' already declared"
            ))
        res.register(self.advance())
        if self.current_tok.type == TokenType.T_EQUAL:
            return self.parse_assignment(res, var_name)
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end, "Expected '=' in variable declaration"
        ))

    def handle_function_declaration(self, res):
        res.register(self.advance())

        if self.current_tok.type != TokenType.T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected function name after 'function'"
            ))
        func_name = self.current_tok

        if func_name.value in self.symbol_table:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Function '{func_name.value}' already declared"
            ))

        res.register(self.advance())

        if self.current_tok.type != TokenType.T_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '(' after function name"
            ))
        res.register(self.advance())

        arg_nodes = []
        if self.current_tok.type == TokenType.T_RPAREN:
            res.register(self.advance())
        else:
            arg_nodes.append(res.register(self.check_token(TokenType.T_IDENTIFIER, "Expected argument name")))

            # Обрабатываем остальные аргументы, если они есть
            while self.current_tok.type == TokenType.T_COMMA and self.current_tok.type != TokenType.T_RPAREN:
                res.register(self.advance())
                arg_nodes.append(res.register(self.check_token(TokenType.T_IDENTIFIER, "Expected argument name")))
            res.register(self.advance())

        # Проверяем, что после закрывающей скобки идёт открывающая фигурная скобка '{'
        if self.current_tok.type != TokenType.T_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{' at the start of function body"
            ))

        # Пропускаем открывающую фигурную скобку '{'
        res.register(self.advance())

        body = []
        # Обрабатываем тело функции
        while self.current_tok.type != TokenType.T_RBRACE and self.current_tok.type != TokenType.T_EOF:
            body.append(res.register(self.statement()))
            if res.error:
                return res

        # Ожидаем закрывающую фигурную скобку '}'
        if self.current_tok.type != TokenType.T_RBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}' at the end of function body"
            ))

        # Пропускаем закрывающую фигурную скобку '}'
        res.register(self.advance())

        # Сохраняем функцию в таблице символов
        self.symbol_table[func_name.value] = func_name
        
        return res.success(FuncDefNode(func_name, arg_nodes, body))



    def handle_identifier(self, res, var_name):
        res.register(self.advance())
        if self.current_tok.type == TokenType.T_EQUAL:
            return self.parse_assignment(res, var_name)
        elif self.current_tok.type == TokenType.T_LPAREN:
            return self.function_call(var_name)
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end, f"Unexpected token {self.current_tok.type}"
        ))

    def parse_assignment(self, res, var_name):
        res.register(self.advance())
        expr = res.register(self.expression())
        if res.error:
            return res
        if self.current_tok.type != TokenType.T_SEMICOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ';' after assignment"
            ))
        res.register(self.advance())
        self.symbol_table[var_name.value] = var_name
        return res.success(VariableAssignNode(var_name, expr))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TokenType.T_PLUS, TokenType.T_MINUS):
            res.register(self.advance())
            return res.success(UnaryOpNode(tok, res.register(self.factor())))
        elif tok.type in (TokenType.T_INT, TokenType.T_FLOAT, TokenType.T_STRING, TokenType.T_TRUE, TokenType.T_FALSE):
            res.register(self.advance())
            return res.success(NumberNode(tok) if tok.type in (TokenType.T_INT, TokenType.T_FLOAT) else StringNode(tok) if tok.type == TokenType.T_STRING else BooleanNode(tok))
        elif tok.type == TokenType.T_IDENTIFIER:
            return res.success(VariableAccessNode(res.register(self.advance())))
        elif tok.type == TokenType.T_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expression())
            if res.error or self.current_tok.type != TokenType.T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
                ))
            res.register(self.advance())
            return res.success(expr)
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end, "Expected int, float, identifier, '+', '-', or '('"
        ))

    def function_call(self, func_name_tok):
        res = ParseResult()
        arg_nodes = []
        res.register(self.advance())
        if self.current_tok.type != TokenType.T_RPAREN:
            arg_nodes.append(res.register(self.expression()))
            while self.current_tok.type == TokenType.T_COMMA:
                res.register(self.advance())
                arg_nodes.append(res.register(self.expression()))
        if self.current_tok.type != TokenType.T_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
            ))
        res.register(self.advance())
        if self.current_tok.type != TokenType.T_SEMICOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ';' after function call"
            ))
        res.register(self.advance())
        return res.success(FuncCallNode(func_name_tok, arg_nodes))

    def term(self):
        return self.bin_op(self.factor, (TokenType.T_MULTIPLY, TokenType.T_DIVIDE))

    def expression(self):
        return self.bin_op(self.term, (TokenType.T_PLUS, TokenType.T_MINUS))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        while not res.error and self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            left = BinOpNode(left, op_tok, res.register(func()))
        return res.success(left)