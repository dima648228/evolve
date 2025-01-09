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

        while self.current_tok.type != TokenType.T_EOF:
            statement = res.register(self.statement())
            if res.error:
                return res.failure(res.error)

            if statement:
                statements.append(statement)

        if len(statements) == 0:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected at least one statement"
            ))

        return res.success(ListNode(statements))


    # Вспомогательная функция для проверки токена
    def check_token(self, expected_type, error_msg):
        if self.current_tok.type != expected_type:
            return ParseResult().failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, error_msg))
        self.advance()
        return ParseResult().success(self.current_tok)

    """ 
        Обработчик токенов. Он проверяет к какому типу относиться токен. Если токен это ключевое слово, то
        он будет будет обрабатывать это как операцию присвоения либо переопределения. В противном случае
        это будет обрабатываться как выражение. 
    """
    def statement(self):
        res = ParseResult()
        tok = self.current_tok

        # Обработка объявления переменной (var a = ...)
        if tok.type == TokenType.T_KEYWORD and tok.value == "var":
            res.register(self.advance())  # Пропускаем 'var'

            if self.current_tok.type != TokenType.T_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected variable name after 'var'"
                ))

            var_name = self.current_tok
            if var_name.value in self.symbol_table:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"The variable {var_name.value} is already declared!"
                ))

            res.register(self.advance())  # Пропускаем идентификатор

            if self.current_tok.type == TokenType.T_EQUAL:
                res.register(self.advance())  # Пропускаем '='
                expr = res.register(self.expression())  # Считываем выражение
                if res.error: return res

                if self.current_tok.type != TokenType.T_SEMICOLON:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ';' after variable declaration"
                    ))
                res.register(self.advance())  # Пропускаем ';'

                # Добавляем переменную в таблицу символов
                self.symbol_table[var_name.value] = var_name
                return res.success(VariableAssignNode(var_name, expr))

            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '=' in variable declaration"
            ))

        # Обработка присваивания существующей переменной (a = ...)
        elif tok.type == TokenType.T_IDENTIFIER:
            var_name = tok
            res.register(self.advance()) 

            if self.current_tok.type == TokenType.T_EQUAL:
                res.register(self.advance())
                expr = res.register(self.expression())
                if res.error: return res

                if self.current_tok.type != TokenType.T_SEMICOLON:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ';' after assignment"
                    ))
                res.register(self.advance())  # Пропускаем ';'

                # Проверяем, существует ли переменная в таблице символов
                if var_name.value not in self.symbol_table:
                    return res.failure(InvalidSyntaxError(
                        var_name.pos_start, var_name.pos_end,
                        f"Variable '{var_name.value}' is not declared"
                    ))
                
                return res.success(VariableAssignNode(var_name, expr))
            elif self.current_tok.type == TokenType.T_LPAREN:
                return self.function_call(var_name)

            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Unexpected token {self.current_tok.type} after identifier"
            ))
        else:
            expr = res.register(self.expression())
            if res.error: return res
            return res.success(expr)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        # Обработка унарных операторов
        if tok.type in (TokenType.T_PLUS, TokenType.T_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TokenType.T_INT, TokenType.T_FLOAT, TokenType.T_STRING, TokenType.T_TRUE, TokenType.T_FALSE):
            res.register(self.advance())
            return res.success(NumberNode(tok) if tok.type in (TokenType.T_INT, TokenType.T_FLOAT) else StringNode(tok) if tok.type == TokenType.T_STRING else BooleanNode(tok))

        elif tok.type == TokenType.T_IDENTIFIER:
            var_name = tok
            res.register(self.advance())

            if self.current_tok.type == TokenType.T_LPAREN:
                return self.function_call(var_name)

            return res.success(VariableAccessNode(var_name))


        elif tok.type == TokenType.T_LPAREN:
            res.register(self.advance())
            expression = res.register(self.expression())
            if res.error: return res
    
            if self.current_tok.type != TokenType.T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')' after expression"
                ))

            res.register(self.advance())
            return res.success(expression)
        elif tok.type == TokenType.T_SEMICOLON:
            res.register(self.advance())
            return res.success(None)
        
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-' or '('"
        ))

    def function_call(self, func_name_tok):
        res = ParseResult()
        arg_nodes = []

        #print(f"Attempting to parse function call: {func_name_tok.value}")

        # Пропускаем открывающую скобку '('
        res.register(self.advance())

        if self.current_tok.type != TokenType.T_RPAREN:
            # Считывание первого аргумента
            arg_nodes.append(res.register(self.expression()))
            while self.current_tok.type == TokenType.T_COMMA:
                res.register(self.advance())
                arg_nodes.append(res.register(self.expression()))
                if res.error: return res

        # Проверка на наличие закрывающей скобки ')'
        if self.current_tok.type != TokenType.T_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')' after function arguments"
            ))

        res.register(self.advance())  # Пропускаем ')'

        # После закрывающей скобки должна быть точка с запятой
        if self.current_tok.type != TokenType.T_SEMICOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ';' after function call"
            ))

        res.register(self.advance())  # Пропускаем ';'

        #print(f"Function call successfully parsed: {func_name_tok.value}")
        #print(func_name_tok)
        return res.success(FuncCallNode(func_name_tok, arg_nodes))



    def term(self):
        return self.bin_op(self.factor, (TokenType.T_MULTIPLY, TokenType.T_DIVIDE))

    def expression(self):
        return self.bin_op(self.term, (TokenType.T_PLUS, TokenType.T_MINUS))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
