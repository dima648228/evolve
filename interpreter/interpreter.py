from parser.token_ import *
from debug.error_ import *
from interpreter.builtin_funcs import BuiltInFunction
from interpreter.prefixes import *
from parser.nodes import *
from parser.keywords import *

class Value:
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

    def copy(self):
        raise NotImplementedError("No copy method defined")

    def illegal_operation(self, other):
        return RTError(
            self.pos_start, other.pos_end,
            f'Illegal operation between {self} and {other}',
            self.context
        )
    
    def type_error(self,other, op):
        return RTError(
            self.pos_start, other.pos_end,
            f'Type Error: {op} not supported between {self} and {other}',
            self.context
        )

class Number(Value):
    def __init__(self, value):
        super().__init__(value)

    def added_to(self, other):
        return self._binary_op(other, lambda a, b: a + b, 'addition')

    def subbed_by(self, other):
        return self._binary_op(other, lambda a, b: a - b, 'subtraction')

    def multed_by(self, other):
        return self._binary_op(other, lambda a, b: a * b, 'multiplication')

    def dived_by(self, other):
        if isinstance(other, Number) and other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, 'Division by zero', self.context
            )
        return self._binary_op(other, lambda a, b: a / b, 'division')

    def greater_than(self, other):
        return self._binary_op(other, lambda a, b: a > b, 'comparsion_gt')
    
    def less_than(self, other):
        return self._binary_op(other, lambda a, b: a < b, 'comparsion_lt')
    
    def greater_or_equal(self, other):
        return self._binary_op(other, lambda a, b: a >= b, 'comparsion_gte')
    
    def less_or_equal(self, other):
        return self._binary_op(other, lambda a, b: a <= b, 'comparsion_lte')
    
    def equal_to(self, other):
        return self._binary_op(other, lambda a, b: a == b, 'comparsion_gt')
    
    def not_equal_to(self, other):
        return self._binary_op(other, lambda a, b: a != b, 'comparsion_gt')

    def _binary_op(self, other, op, op_name):
        if isinstance(other, Number):
            return Number(op(self.value, other.value)).set_context(self.context), None
        return None, self.illegal_operation(other)

    def copy(self):
        return Number(self.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)

    def __repr__(self):
        return str(self.value)

class String(Value):
    def __init__(self, value):
        super().__init__(value)

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def greater_than(self, other):
        return None, self.type_error(other, '>')
    
    def less_than(self, other):
        return None, self.type_error(other, '<')
    
    def greater_or_equal(self, other):
        return None, self.type_error(other, '>=')
    
    def less_or_equal(self, other):
        return None, self.type_error(other, '<=')

    def equal_to(self, other):
        return self._binary_op(other, lambda a, b: a == b, 'comparsion_gt')
    
    def not_equal_to(self, other):
        return self._binary_op(other, lambda a, b: a != b, 'comparsion_gt')
    
    def _binary_op(self, other, op, op_name):
        if isinstance(other, String):
            return String(op(self.value, other.value)).set_context(self.context), None
        return None, self.illegal_operation(other)

    def copy(self):
        return String(self.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)

    def __repr__(self):
        return f'{self.value}'

class Boolean(Value):
    def __init__(self, value):
        super().__init__(value)

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def greater_than(self, other):
        return self._binary_op(other, lambda a, b: a > b, 'comparsion_gt')
    
    def less_than(self, other):
        return self._binary_op(other, lambda a, b: a < b, 'comparsion_lt')
    
    def greater_or_equal(self, other):
        return self._binary_op(other, lambda a, b: a >= b, 'comparsion_gte')
    
    def less_or_equal(self, other):
        return self._binary_op(other, lambda a, b: a <= b, 'comparsion_lte')

    def equal_to(self, other):
        return self._binary_op(other, lambda a, b: a == b, 'comparsion_gt')
    
    def not_equal_to(self, other):
        return self._binary_op(other, lambda a, b: a != b, 'comparsion_gt')
    
    def _binary_op(self, other, op, op_name):
        if isinstance(other, Boolean):
            return Boolean(op(self.value, other.value)).set_context(self.context), None
        return None, self.illegal_operation(other)

    def copy(self):
        return Boolean(self.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)

    def __repr__(self):
        return str(self.value).lower()

class Function:
    def __init__(self, name, arg_names, body_nodes, context):
        self.name = name
        self.arg_names = arg_names
        self.body_nodes = body_nodes
        self.context = context

    def execute(self, args):
        res = RTResult()
        new_context = Context(self.name, self.context)

        if len(args) != len(self.arg_names):
            return res.failure(RTError(
                None, None,
                f'Expected {len(self.arg_names)} arguments, got {len(args)}',
                self.context
            ))

        for name, value in zip(self.arg_names, args):
            new_context.symbol_table.set(P_FUNCTION+name, value)

        return self._execute_body(new_context)

    def _execute_body(self, context):
        res = RTResult()
        last_value = None

        for statement in self.body_nodes:
            last_value = res.register(context.symbol_table.interpreter.visit(statement, context))
            if res.error:
                return res

        return res.success(last_value)

    def __repr__(self):
        return f'<Function {self.name}>'

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

# КЛАСС ИНТЕРПРЕТАТОРА

class Interpreter:

    def __init__(self, global_context):
        self.global_context = global_context

    # ГЛАВНЫЕ ФУНКЦИИ

    def visit(self, node, context):
        if node is None:
            raise Exception("Received a None node, which is invalid")

        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    # ДОЧЕРНИЕ ФУНКЦИИ

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
        value = context.symbol_table.get(P_VARIABLE+var_name)
        
        
        #if not value: value = self.global_context.symbol_table.get(var_name)

        if var_name in RESERVED_KEYWORDS:
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
    
    def visit_FuncDefNode(self, node, context):
        res = RTResult()
        
        func_name = node.func_name_tok.value
        args_nodes = [arg_tok.value for arg_tok in node.args_nodes]
        body = node.body_nodes
        
        func = Function(func_name, args_nodes, body, context)
        
        # Добавляем функцию в таблицу символов
        context.symbol_table.set(P_FUNCTION+func_name, func)
        
        return res.success(func)


    def visit_FuncCallNode(self, node, context):
        res = RTResult()

        # Получаем имя функции
        func_name = node.func_name_tok.value

        # Получаем саму функцию из таблицы символов
        func = context.symbol_table.get(P_FUNCTION+func_name)

        if not func:
            #func = self.global_context.symbol_table.get(func_name)

            if not func:
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"'{func_name}' is not defined",
                    context
                ))

        if isinstance(func, BuiltInFunction):
            args = []

            for arg_node in node.arg_nodes:
                arg_value = res.register(self.visit(arg_node, context))
                if res.error: return res
                args.append(arg_value)

            result = func.execute(args)
            if result is not None:
                return res.success(result)

            return res.success(None)
        elif isinstance(func, Function):
            new_context = Context(func_name, context)
            new_context.symbol_table = SymbolTable()
            new_context.symbol_table.parent = context.symbol_table

            if len(node.arg_nodes) != len(func.arg_names):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"'{func_name}' expected {len(func.arg_names)} arguments, "
                    f"but got {len(node.arg_nodes)}",
                    context
                ))

            for i, arg_node in enumerate(node.arg_nodes):
                print("Function name:", func.name)
                print("Argument names:", func.arg_names)
                print("Passed arguments:", [self.visit(arg_node, new_context).value for arg_node in node.arg_nodes])

                arg_value = res.register(self.visit(arg_node, new_context))
                if res.error: return res
                new_context.symbol_table.set(func.arg_names[i], arg_value)
            return self.visit_BlockNode(func.body_nodes, context)

        return res.failure(RTError(
            node.pos_start, node.pos_end,
            f"'{func_name}' is not callable",
            context
        ))
    
    def visit_ReturnNode(self,node,context):
        res = RTResult()

        return_value = res.register(self.visit(node.return_value, context))
        if res.error: return res

        return res.success(return_value)
    
    def visit_IfNode(self, node, context):
        
        def is_true(value):
            """Определяет, является ли значение истинным (включая строки, числа и булевы значения)."""
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() != "false"
            if value in [0, "0", "false", "None"]:
                return False
            return True
        
        res = RTResult()

        condition_result = None

        if isinstance(node.condition, BinOpNode):
            condition_result = self.visit_BinOpNode(node.condition, context)
        elif node.condition.tok and node.condition.tok.value in ("true", "false"):
            condition_result = node.condition.tok

        if isinstance(condition_result.value, str) and is_true(condition_result.value):
            last_result = res.register(self.visit_BlockNode(node.body, context))

            return res.success(last_result)
        elif not isinstance(condition_result.value, str) and is_true(condition_result.value.value):
            last_result = res.register(self.visit_BlockNode(node.body, context))

            return res.success(last_result)
        else:
            if len(node.elseif_cases) > 0:
                for subConditionNode in node.elseif_cases:
                    condition_result = None

                    if isinstance(subConditionNode[0], BinOpNode):
                        condition_result = self.visit_BinOpNode(subConditionNode[0], context)
                    elif subConditionNode[0].tok and subConditionNode[0].tok.value in ("true", "false"):
                        condition_result = subConditionNode[0].tok
                    
                    if isinstance(condition_result.value, str) and is_true(condition_result.value):
                        last_result = res.register(self.visit_BlockNode(subConditionNode[1], context))

                        return res.success(last_result)
                    elif not isinstance(condition_result.value, str) and is_true(condition_result.value):
                        last_result = res.register(self.visit_BlockNode(subConditionNode[1], context))

                        return res.success(last_result)
            if node.else_case != None:
                res.register(self.visit_BlockNode(node.else_case[1], context))
                        

        return res.success(None)
    
    def visit_BlockDefNode(self, node, context):
        res = RTResult()

        block_context = Context("Block", context)

        last_result = None
        for stmt in node.statements:
            last_result = res.register(self.visit(stmt, block_context))
            if res.error: return res

        return res.success(last_result)
    
    def visit_BlockNode(self, node, context):
        res = RTResult()
        last_result = None

        for statement in node:
            last_result = res.register(self.visit(statement, context))
            if res.error: return res

        return res.success(last_result)
    
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
        existing_value = context.symbol_table.get(P_VARIABLE+var_name)
        
        if existing_value:
            # Если переменная существует, обновляем её значение
            context.symbol_table.set(P_VARIABLE+var_name, value)
        else:
            # Если переменной нет в таблице, это фактически её создание
            context.symbol_table.set(P_VARIABLE+var_name, value)
        
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
    
        if node.op_tok.type == TokenType.T_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TokenType.T_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TokenType.T_MULTIPLY:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TokenType.T_DIVIDE:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TokenType.T_GT:
            result, error = left.greater_than(right)
        elif node.op_tok.type == TokenType.T_LT:
            result, error = left.less_than(right)
        elif node.op_tok.type == TokenType.T_GTE:
            result, error = left.greater_or_equal(right)
        elif node.op_tok.type == TokenType.T_LTE:
            result, error = left.less_or_equal(right)
        elif node.op_tok.type == TokenType.T_EQ:
            result, error = left.equal_to(right)
        elif node.op_tok.type == TokenType.T_NE:
            result, error = left.not_equal_to(right)

        if result and node.op_tok.type in (TokenType.T_GT,TokenType.T_LT,TokenType.T_GTE,TokenType.T_LTE, TokenType.T_EQ, TokenType.T_NE):
            result.value = str(result.value).lower()
    
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))
    
    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
    
        error = None
    
        if node.op_tok.type == TokenType.T_MINUS:
            number, error = number.multed_by(Number(-1))
    
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
    def visit_StringNode(self, node, context):
    	return RTResult().success(
    	    String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    	)

# КЛАСС КОНТЕКСТА
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
