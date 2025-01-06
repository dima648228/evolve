from lexer.token_ import *
from debug.error_ import *

# NUMBER CLASS

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)

class String:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.value}"

    def copy(self):
        return String(self.value)

    def set_context(self, context):
        self.context = context
        return self

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

class Boolean:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value).lower()

    def set_context(self, context):
        self.context = context
        return self

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def copy(self):
        return Boolean(self.value)

# RTRESULT CLASS
class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self
    
class BuiltInFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def execute(self, args):
        return self.func(args)

    def copy(self):
        return BuiltInFunction(self.name, self.func)

# INTERPRETER CLASS

class Interpreter:

    # visit node main functions

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    # visit node child functions

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_BooleanNode(self, node, context):
        return RTResult().success(
            Boolean(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VariableAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if var_name in ['var', 'if', 'else', 'while']:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is a reserved keyword and cannot be used as a variable name",
                context
            ))

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))
        
        value = value.copy().set_pos(node.pos_start,node.pos_end)
        return res.success(value)
    
    def visit_FuncCallNode(self, node, context):
        res = RTResult()

        # Получаем имя функции
        func_name = node.var_name_tok.value

        # Получаем саму функцию из таблицы символов
        func = context.symbol_table.get(func_name)

        if not func:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{func_name}' is not defined",
                context
            ))

        # Если функция встроенная, обрабатываем её
        if isinstance(func, BuiltInFunction):
            args = []
            for arg_node in node.arg_nodes:
                arg_value = res.register(self.visit(arg_node, context))
                if res.error: return res
                args.append(arg_value)

            return res.success(func.execute(args))

        # Если это не встроенная функция, нужно обработать её как обычную функцию
        return res.failure(RTError(
            node.pos_start, node.pos_end,
            f"'{func_name}' is not callable",
            context
        ))


    
    def visit_ListNode(self, node, context):
        res = RTResult()
        last_result = None 

        for element in node.elements:
            last_result = res.register(self.visit(element, context))
            if res.error: return res

        return res.success(last_result if last_result is not None else Number(0))
    
    def visit_VariableAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        
        # Получаем текущее значение переменной, если оно существует
        existing_value = context.symbol_table.get(var_name)
        
        if existing_value:
            # Если переменная существует, обновляем её значение
            context.symbol_table.set(var_name, value)
        else:
            # Если переменной нет в таблице, это фактически её создание
            context.symbol_table.set(var_name, value)
        
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
    
        if node.op_tok.type == T_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == T_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == T_MULTIPLY:
            result, error = left.multed_by(right)
        elif node.op_tok.type == T_DIVIDE:
            result, error = left.dived_by(right)
    
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))
    
    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
    
        error = None
    
        if node.op_tok.type == T_MINUS:
            number, error = number.multed_by(Number(-1))
    
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
    def visit_StringNode(self, node, context):
    	return RTResult().success(
    	    String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    	)

# CONTEXT CLASS
class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table = None

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]
