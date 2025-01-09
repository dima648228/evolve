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
    """Представляет ноду для списка элементов в AST."""
    def __init__(self, elements):
        self.elements = elements
        self.pos_start = self.elements[0].pos_start if self.elements else None
        self.pos_end = self.elements[-1].pos_end if self.elements and self.elements[-1] else None
    
    def __repr__(self):
        return f"ListNode({self.elements})"
