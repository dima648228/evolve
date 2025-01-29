# ОСНОВНЫЕ КЛАССЫ НОД
# 
# Этот код определяет основные ноды, используемые в абстрактном синтаксическом дереве (AST) для языка программирования Evolve.
# Классы представляют различные элементы, такие как числа, строки, булевы значения, доступ к переменным, 
# присваивание переменных, операции, вызовы функций и структуры списков. Эти ноды используются 
# на этапах парсинга и интерпретации кода, написанного на этом языке.
#
# КОПИРАЙТ © 2025 justdimonn
# 
# Лицензировано на условиях никаких лол. Вы не можете использовать, распространять 
# или модифицировать этот код, за исключением случаев, предусмотренных лицензией.

class NumberNode:
    """Представляет ноду для числового значения в AST."""
    def __init__(self, tok) -> None:
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self) -> str:
        return f'{self.tok}'

class StringNode:
    """Представляет ноду для строкового значения в AST."""
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f"StringNode({self.tok.value})"

class BooleanNode:
    """Представляет ноду для булевого значения в AST."""
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f'BooleanNode({self.tok.value})'
    
class VariableAccessNode:
    """Представляет ноду для доступа к переменной в AST."""
    def __init__(self, var_name_tok) -> None:
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end
    
    def __repr__(self):
        return f"VariableAccessNode({self.var_name_tok})"

class VariableAssignNode:
    """Представляет ноду для присваивания значения переменной в AST."""
    def __init__(self, var_name_tok, value_node) -> None:
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end
    
    def __repr__(self):
        return f"VariableAssignNode({self.var_name_tok}, {self.value_node})"

class BinOpNode:
    """Представляет ноду для бинарных операций (сложение, вычитание) в AST."""
    def __init__(self, left_node, op_tok, right_node) -> None:
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.left_node},{self.op_tok},{self.right_node})'

class UnaryOpNode:
    """Представляет ноду для унарных операций (например, отрицание, логическое НЕ) в AST."""
    def __init__(self, op_tok, node) -> None:
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self) -> str:
        return f'{self.op_tok},{self.node}'

class FuncCallNode:
    """Представляет ноду для вызова функции в AST."""
    def __init__(self, func_name_tok, arg_nodes):
        self.func_name_tok = func_name_tok
        self.arg_nodes = arg_nodes
        self.pos_start = self.func_name_tok.pos_start
        if self.arg_nodes and self.arg_nodes[-1] and len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[-1].pos_end
        else:
            self.pos_end = self.func_name_tok.pos_end

    def __repr__(self):
        return f"{self.func_name_tok}({', '.join(map(str, self.arg_nodes))})"

class FuncDefNode:
    """Представляет ноду для определения функции в AST."""
    def __init__(self, func_name_tok, args_nodes, body_nodes):
        self.func_name_tok = func_name_tok 
        self.args_nodes = args_nodes 
        self.body_nodes = body_nodes
        self.pos_start = self.func_name_tok.pos_start
        self.pos_end = self.body_nodes[-1].pos_end if self.body_nodes else self.func_name_tok.pos_end

    def __repr__(self):
        args_str = ', '.join(map(str, self.args_nodes))
        return f"FuncDefNode({self.func_name_tok}, [{args_str}], {self.body_nodes})"

class ReturnNode:
    """
    Представляет ноду для ключевого слова 'return' в AST.
    """
    def __init__(self, return_value):
        """
        Инициализация узла 'return'.
        
        :param return_value: Значение, возвращаемое оператором return. 
                             Может быть None для пустого return.
        """
        self.return_value = return_value
        self.pos_start = self.return_value.pos_start
        self.pos_end = self.return_value.pos_end

    def __repr__(self):
        """
        Возвращает строковое представление узла.
        """
        return f"ReturnNode({self.return_value})"


class IfNode:
    """Представляет ноду для условного оператора."""
    def __init__(self, condition, body, elseif_cases=None, else_case=None):
        self.condition = condition              # Условие (узел)
        self.body = body                        # Тело if (узел или список узлов)
        self.elseif_cases = elseif_cases or []  # Список elif [(условие, тело)]
        self.else_case = else_case              # Тело else (если есть)

        if self.condition: self.pos_start = self.condition.pos_start
        else: self.pos_start = self.body[0].pos_start or 0

        self.pos_end = (
            self.else_case.pos_end if self.else_case
            else (self.elseif_cases[-1][1].pos_end if self.elseif_cases
                  else 0)
        )

    def __repr__(self):
        elif_str = f", elseif_cases={self.elseif_cases}" if self.elseif_cases else ""
        else_str = f", else_case={self.else_case}" if self.else_case else ""
        return f"IfNode(condition={self.condition}, body={self.body}{elif_str}{else_str})"

class BlockNode:
    def __init__(self, statements, pos_start=None, pos_end=None):
        self.statements = statements  # Список инструкций (или узлов)
        self.pos_start = pos_start    # Позиция начала блока
        self.pos_end = pos_end        # Позиция конца блока

    def __repr__(self):
        return f"<BlockNode {len(self.statements)} statements>"

class BlockDefNode:
    def __init__(self, statements, pos_start, pos_end):
        self.statements = statements  # Список инструкций (выражений), которые нужно выполнить
        self.pos_start = pos_start    # Позиция начала блока в исходном коде
        self.pos_end = pos_end        # Позиция конца блока в исходном коде

    def __repr__(self):
        return f"<BlockDefNode {len(self.statements)} statements>"

class ListNode:
    """Представляет ноду для списка элементов в AST."""
    def __init__(self, elements):
        self.elements = elements
        self.pos_start = self.elements[0].pos_start if self.elements else None
        self.pos_end = self.elements[-1].pos_end if self.elements and self.elements[-1] else None
    
    def __repr__(self):
        return f"ListNode({self.elements})"
