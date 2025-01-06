
from lexer.token_ import *
from debug.error_ import *

# THE MAIN NODE CLASSES

class NumberNode:
    def __init__(self, tok) -> None:
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self) -> str:
        return f'{self.tok}'
    
class StringNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f"StringNode({self.tok.value})"

class BooleanNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f'{self.tok.value}'
    
class VariableAccessNode:
    def __init__(self,var_name_tok) -> None:
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end
    
    def __repr__(self):
        return f"VariableAccessNode({self.var_name_tok})"

class VariableAssignNode:
    def __init__(self,var_name_tok,value_node) -> None:
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end
    
    def __repr__(self):
        return f"VariableAssignNode({self.var_name_tok}, {self.value_node})"

class BinOpNode:
    def __init__(self,left_node, op_tok, right_node) -> None:
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.left_node},{self.op_tok},{self.right_node})'
    

class UnaryOpNode:
    def __init__(self,op_tok,node) -> None:
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self) -> str:
        return f'{self.op_tok},{self.node}'

class FuncCallNode:
    def __init__(self, var_name_tok, arg_nodes):
        self.var_name_tok = var_name_tok
        self.arg_nodes = arg_nodes
        self.pos_start = self.var_name_tok.pos_start
        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[-1].pos_end
        else:
            self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f"{self.var_name_tok}({', '.join(map(str, self.arg_nodes))})"

class ListNode:
    def __init__(self, elements):
        self.elements = elements
        self.pos_start = self.elements[0].pos_start if self.elements else None
        self.pos_end = self.elements[-1].pos_end if self.elements and self.elements[-1] else None
    
    def __repr__(self):
        return f"ListNode({self.elements})"

# PARSER RESULT CLASS

class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None
    
    def register(self, res):
        if isinstance(res,ParseResult):
            if res.error:self.error = res.error

            return res.node
        
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

# PARSER CLASS

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = ParseResult()
        statements = []

        while self.current_tok.type != T_EOF:
            statement = res.register(self.statement())
            if res.error:  # Возвращаем объект с ошибкой
                return res.failure(res.error)
            if statement:  # Добавляем только непустые элементы
                statements.append(statement)
            self.advance()

        if len(statements) == 0:  # Проверка на пустой список
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected at least one statement"
            ))

        return res.success(ListNode(statements))  # Убедитесь, что это не None


    def statement(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type == T_VAR:
            res.register(self.advance())  # Пропускаем 'var'

            # Проверяем, что следующий токен — идентификатор
            if self.current_tok.type != T_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected variable name after 'var'"
                ))

            var_name = self.current_tok  # Имя переменной
            res.register(self.advance())

            # Проверяем, есть ли оператор '='
            if self.current_tok.type == T_EQUAL:
                res.register(self.advance())  # Пропускаем '='
                expr = res.register(self.expression())  # Считываем значение переменной
                if res.error: return res
                return res.success(VariableAssignNode(var_name, expr))

            # Если '=' нет — создаём переменную с None
            return res.success(VariableAssignNode(var_name, None))


        # Обработка других случаев (например, идентификаторов)
        if tok.type == T_IDENTIFIER:
            var_name = self.current_tok
            res.register(self.advance())

            # Проверяем, есть ли оператор '='
            if self.current_tok.type == T_EQUAL:
                res.register(self.advance())
                expr = res.register(self.expression())  # Присваивание
                if res.error: return res

                # Возвращаем переопределение переменной (не проверяем наличие 'var')
                return res.success(VariableAssignNode(var_name, expr))

            # Возврат для выражений, если это не присваивание
            self.tok_idx -= 1
            self.current_tok = self.tokens[self.tok_idx]
            return self.bin_op(self.term, (T_PLUS, T_MINUS))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok
    
        # Обработка унарных операторов
        if tok.type in (T_PLUS, T_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
    
        # Обработка чисел, строк, булевых значений
        elif tok.type in (T_INT, T_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
    
        elif tok.type == T_STRING:
            res.register(self.advance())
            return res.success(StringNode(tok))
    
        elif tok.type == T_TRUE or tok.type == T_FALSE:
            res.register(self.advance())
            return res.success(BooleanNode(tok))
    
        # Обработка идентификатора (переменная или функция)
        elif tok.type == T_IDENTIFIER:
            res.register(self.advance())
            if self.current_tok.type == T_LPAREN:  # Проверка, что это вызов функции
                res.register(self.advance())  # Пропускаем '('
                arg_nodes = []
                if self.current_tok.type != T_RPAREN:
                    arg_nodes.append(res.register(self.expression()))  # Добавляем первый арг
                    while self.current_tok.type == T_COMMA:  # Обрабатываем дополнительные аргументы
                        res.register(self.advance())
                        arg_nodes.append(res.register(self.expression()))
                        if res.error: return res
                if self.current_tok.type != T_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')' after function arguments"
                    ))
                res.register(self.advance())  # Пропускаем ')'
                return res.success(FuncCallNode(tok, arg_nodes))  # Возвращаем узел вызова функции
            else:
                return res.success(VariableAccessNode(tok))  # Обычная переменная
    
        # Обработка выражений в скобках
        elif tok.type == T_LPAREN:
            res.register(self.advance())
            expression = res.register(self.expression())
            if res.error: return res
            if self.current_tok.type == T_RPAREN:
                res.register(self.advance())
                return res.success(expression)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
    
        # Ошибка: ожидался литерал, идентификатор или выражение в скобках
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-' or '('"
        ))


    def term(self):
        return self.bin_op(self.factor, (T_MULTIPLY, T_DIVIDE))

    def expression(self):
        return self.bin_op(self.term, (T_PLUS, T_MINUS))

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
