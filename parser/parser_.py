# ОСНОВНОЙ КЛАСС ПАРСЕРА
# 
# Этот код определяет парсер, используемый для непосредственного создания абстрактного синтаксического дерева (AST) для языка программирования Evolve.
#
# КОПИРАЙТ © 2025 justdimonn
# 
# Лицензировано на условиях никаких лол. Вы не можете использовать, распространять 
# или модифицировать этот код, за исключением случаев, предусмотренных лицензией.

from parser.token_ import *
from debug.error_ import *
from parser.nodes import *
from enum import Enum


class ParseResult:
    """
    Класс для хранения результата парсинга токенов.
    Содержит ошибку (если она произошла) и узел (если парсинг успешен).
    """

    def __init__(self):
        self.error = None  # Ошибка, если она произошла
        self.node = None    # Результат парсинга (узел дерева)

    def register(self, res):
        """
        Регистрирует результат парсинга.
        Если результат является ParseResult, объединяет ошибки.
        """
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def set_result(self, success, node_or_error):
        """
        Устанавливает результат: успех или ошибка.
        """
        if success:
            self.node = node_or_error
        else:
            self.error = node_or_error
        return self

    def success(self, node):
        """
        Устанавливает успешный результат.
        """
        return self.set_result(True, node)

    def failure(self, error):
        """
        Устанавливает ошибку как результат.
        """
        return self.set_result(False, error)


# Список токенов, которые парсер должен игнорировать на момент первичной обработки
SKIPPABLE_TOKENS = {
    TokenType.T_EQUAL,
    TokenType.T_FLOAT,
    TokenType.T_INT,
    TokenType.T_STRING,
    TokenType.T_SEMICOLON
}


class Parser:
    """
    Парсер для обработки токенов, полученных от лексического анализатора.
    """

    def __init__(self, tokens):
        """
        Инициализация парсера. Сохраняет токены и инициализирует таблицу символов.
        """
        self.tokens = tokens
        self.tok_idx = -1
        self.symbol_table = {
            "variables_stack": {},
            "functions_stack": {}
        }  # Локальная таблица символов

        self.advance()

    def advance(self):
        """
        Обновляет текущий токен, двигаясь по списку токенов.
        """
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        else:
            self.current_tok = None
        return self.current_tok

    def parse(self):
        """
        Основная функция парсинга, которая продолжает парсить до токена T_EOF.
        """
        res = ParseResult()
        statements = []

        # Парсим все выражения до конца файла
        while self.current_tok.type != TokenType.T_EOF:
            statement = res.register(self.statement())
            if res.error:
                return res.failure(res.error)
            if statement:
                statements.append(statement)

        # Возвращаем результат в виде узла списка
        return res.success(ListNode(statements)) if statements else res.failure(
            InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected at least one statement")
        )

    def check_token(self, expected_type, error_message):
        res = ParseResult()

        """
        Проверяет, соответствует ли текущий токен ожидаемому типу.
        Если нет, возвращает ошибку.
        """
        if self.current_tok.type != expected_type:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, error_message
            ))
        token = self.current_tok
        self.advance()
        return token

    def statement(self):
        """
        Обрабатывает отдельные операторы или выражения.
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type == TokenType.T_VAR:
            return self.handle_var_declaration(res)
        elif tok.type == TokenType.T_FUNCTION:
            return self.handle_function_declaration(res)
        elif tok.type == TokenType.T_IF:
            return self.handle_if_statement(res)
        elif tok.type == TokenType.T_IDENTIFIER:
            return self.handle_identifier(res, tok)
        elif tok.type == TokenType.T_RETURN:
            return self.handle_return_statement(res)
        else:
            expr = res.register(self.expression())
            return res.success(expr) if not res.error else res

    def handle_var_declaration(self, res):
        """
        Обрабатывает объявление переменной с ключевым словом 'var'.
        """
        res.register(self.advance())
        if self.current_tok.type != TokenType.T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected variable name after 'var'"
            ))
        var_name = self.current_tok

        if var_name.value in self.symbol_table["variables_stack"]:
            print(self.symbol_table)
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
        """
        Обрабатывает объявление функции с ключевым словом 'function'.
        """
        res.register(self.advance())

        if self.current_tok.type != TokenType.T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected function name after 'function'"
            ))
        func_name = self.current_tok

        if func_name.value in self.symbol_table["functions_stack"]:
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
            # Добавляем первый аргумент
            arg_nodes.append(res.register(self.check_token(TokenType.T_IDENTIFIER, "Expected argument name")))

            # Обрабатываем остальные аргументы
            while self.current_tok.type == TokenType.T_COMMA:
                res.register(self.advance())  # Пропускаем запятую
                arg_nodes.append(res.register(self.check_token(TokenType.T_IDENTIFIER, "Expected argument name")))

            # Убедимся, что список аргументов корректно завершён ')'
            if self.current_tok.type != TokenType.T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')' after arguments"
                ))
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
        self.symbol_table["functions_stack"][func_name.value] = func_name
        
        return res.success(FuncDefNode(func_name, arg_nodes, body))
    
    def handle_return_statement(self, res):
        """
        Обрабатывает инструкцию return.
        """
        res.register(self.advance())

        if self.current_tok.type == TokenType.T_SEMICOLON:
            # Если после return сразу идет ';', возвращаем пустой узел
            res.register(self.advance())  # Пропускаем ';'
            return res.success(ReturnNode(None))

        # Если выражение есть, парсим его
        expr = res.register(self.expression())
        if res.error:
            return res  # Возвращаем ошибку, если выражение некорректное

        # После выражения ожидаем ';'
        if self.current_tok.type != TokenType.T_SEMICOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ';' after return statement"
            ))

        res.register(self.advance())  # Пропускаем ';'
        return res.success(ReturnNode(expr))


    def handle_identifier(self, res, var_name):
        """
        Обрабатывает идентификатор: проверяет на присваивание или вызов функции.
        """

        tok = var_name  # Сохраняем сам идентификатор

        res.register(self.advance())

        if self.current_tok.type == TokenType.T_EQUAL:
            # Это присваивание переменной
            return self.parse_assignment(res, var_name)
        elif self.current_tok.type == TokenType.T_LPAREN:
            # Это вызов функции
            return self.function_call(tok)  # передаем сам идентификатор
        else:
            # Если это не присваивание и не вызов функции, выдаем ошибку
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"Unexpected token {self.current_tok.type}"
            ))


    def parse_assignment(self, res, var_name):
        """
        Обрабатывает присваивание значения переменной.
        """
        res.register(self.advance())

        expr = res.register(self.expression())

        if res.error:
            return res
        if self.current_tok.type != TokenType.T_SEMICOLON and self.current_tok.type != TokenType.T_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ';' after assignment"
            ))
        elif self.current_tok.type == TokenType.T_LPAREN:
            res.register(self.advance())
            res.register(self.expression())

            res.register(self.advance())

            if self.current_tok.type != TokenType.T_SEMICOLON:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ';' after assignment"
                ))

        res.register(self.advance())
        self.symbol_table["variables_stack"][var_name.value] = var_name
        return res.success(VariableAssignNode(var_name, expr))
    
    def handle_if_statement(self, res):
        res.register(self.advance())
        tok = self.current_tok

        if tok.type != TokenType.T_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '(' after function name"
            ))
        
        res.register(self.advance())
        expr = res.register(self.expression())

        if expr == None:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected atleast one statement"
            ))

        if self.current_tok.type != TokenType.T_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')' after statement"
            ))
        
        res.register(self.advance())

        if self.current_tok.type != TokenType.T_LBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{' after statement"
            ))
        res.register(self.advance())

        body = []

        # Обрабатываем тело условия
        while self.current_tok.type != TokenType.T_RBRACE and self.current_tok.type != TokenType.T_EOF:
            body.append(res.register(self.statement()))
            if res.error:
                return res

        # Ожидаем закрывающую фигурную скобку '}'
        if self.current_tok.type != TokenType.T_RBRACE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}' at the end of if statement body"
            ))

        # Пропускаем закрывающую фигурную скобку '}'
        res.register(self.advance())

        ifNode = IfNode(expr, body, None, None)

        self.handle_elseif_else_statements(res, ifNode)
        
        return res.success(ifNode)

    def handle_elseif_else_statements(self, res, ifNode):
        """
        Рекурсивно обрабатывает 'elseif' и 'else' блоки, добавляя их к узлу ifNode.
        """
        while self.current_tok.type in {TokenType.T_ELSEIF, TokenType.T_ELSE}:
            if self.current_tok.type == TokenType.T_ELSEIF:
                # Обрабатываем 'elseif'
                res.register(self.advance())

                if self.current_tok.type != TokenType.T_LPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected '(' after 'elseif'"
                    ))

                res.register(self.advance())
                condition = res.register(self.expression())

                if condition is None:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected a condition in 'elseif'"
                    ))

                if self.current_tok.type != TokenType.T_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')' after 'elseif' condition"
                    ))

                res.register(self.advance())

                if self.current_tok.type != TokenType.T_LBRACE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{' after 'elseif' condition"
                    ))

                res.register(self.advance())
                body = []

                while self.current_tok.type != TokenType.T_RBRACE and self.current_tok.type != TokenType.T_EOF:
                    body.append(res.register(self.statement()))
                    if res.error:
                        return res

                if self.current_tok.type != TokenType.T_RBRACE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}' to close 'elseif' block"
                    ))

                res.register(self.advance())
                ifNode.elseif_cases.append((condition, body))

            elif self.current_tok.type == TokenType.T_ELSE:
                # Обрабатываем 'else'
                res.register(self.advance())

                if self.current_tok.type != TokenType.T_LBRACE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{' after 'else'"
                    ))

                res.register(self.advance())
                body = []

                while self.current_tok.type != TokenType.T_RBRACE and self.current_tok.type != TokenType.T_EOF:
                    body.append(res.register(self.statement()))
                    if res.error:
                        return res

                if self.current_tok.type != TokenType.T_RBRACE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}' to close 'else' block"
                    ))

                res.register(self.advance())
                ifNode.else_case = (None, body)
                break


    def factor(self):
        """
        Обрабатывает базовые элементы выражений (числа, строки, переменные и т.д.).
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TokenType.T_PLUS, TokenType.T_MINUS):
            res.register(self.advance())
            return res.success(UnaryOpNode(tok, res.register(self.factor())))
        elif tok.type in (TokenType.T_INT, TokenType.T_FLOAT, TokenType.T_STRING, TokenType.T_TRUE, TokenType.T_FALSE):
            res.register(self.advance())
            return res.success(NumberNode(tok) if tok.type in (TokenType.T_INT, TokenType.T_FLOAT)
                               else StringNode(tok) if tok.type == TokenType.T_STRING
                               else BooleanNode(tok))
        elif tok.type == TokenType.T_IDENTIFIER:
            res.register(self.advance())

            if tok.value not in self.symbol_table["variables_stack"]:
                if tok.value not in self.symbol_table["functions_stack"]:
                    return res.failure(InvalidSyntaxError(
                        tok.pos_start, tok.pos_end, f"Variable '{tok.value}' is not defined"
                    ))
            
            #res.register(self.advance())
            return res.success(VariableAccessNode(tok))
        
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
        """
        Обрабатывает вызов функции.
        """
        res = ParseResult()
        arg_nodes = []

        res.register(self.advance())  # Пропускаем '('

        if self.current_tok.type != TokenType.T_RPAREN:
            # Добавляем первый аргумент
            arg_nodes.append(res.register(self.expression()))

            while self.current_tok.type == TokenType.T_COMMA:
                res.register(self.advance())  # Пропускаем запятую
                arg_nodes.append(res.register(self.expression()))

        if self.current_tok.type != TokenType.T_RPAREN and self.current_tok.type != TokenType.T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
            ))

        #res.register(self.advance())  # Пропускаем ')'

        if self.current_tok.type != TokenType.T_SEMICOLON:
            res.register(self.advance())
            if self.current_tok.type != TokenType.T_SEMICOLON:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ';' after function call"
                ))

        res.register(self.advance())  # Пропускаем ';'
        return res.success(FuncCallNode(func_name_tok, arg_nodes))

    def comparison(self):
        """
        Обрабатывает операции сравнения (>, <, >=, <=, ==, !=).
        """
        res = ParseResult()
        left = res.register(self.term())

        if res.error:
            return res
    
        while self.current_tok.type in (
            TokenType.T_GT,
            TokenType.T_LT,
            TokenType.T_GTE,
            TokenType.T_LTE,
            TokenType.T_EQ,
            TokenType.T_NE,
        ):
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(self.term())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def term(self):
        """
        Обрабатывает термы (умножение и деление) в выражениях.
        """
        return self.bin_op(self.factor, (TokenType.T_MULTIPLY, TokenType.T_DIVIDE))

    def expression(self):
        """
        Обрабатывает выражения с операциями сложения и вычитания.
        """
        return self.bin_op(self.comparison, (TokenType.T_PLUS, TokenType.T_MINUS))

    def bin_op(self, func, ops):
        """
        Обрабатывает бинарные операции, такие как сложение, вычитание, умножение и деление.
        """
        res = ParseResult()
        left = res.register(func())

        while self.current_tok and self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

