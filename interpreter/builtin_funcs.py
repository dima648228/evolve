import sys


# КЛАСС ДЛЯ СОЗДАНИЯ ВСТРОЕННОЙ ФУНКЦИИ

class BuiltInFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def execute(self, args):
        return self.func(args)

    def copy(self):
        return BuiltInFunction(self.name, self.func)

# КЛАСС ДЛЯ ИМПОРТИРОВАНИЯ ВСТРОЕННЫХ ФУНКЦИЙ 

class BuiltInFuncImporter:
    def __init__(self, context):
        self.context = context

    def import_built_in_functions(self):      
        print_func = BuiltInFunction("func_print", self.function_print)
        self.context.symbol_table.set("func_print", print_func)

        input_func = BuiltInFunction("func_input", self.function_input)
        self.context.symbol_table.set("func_input", input_func)

    """ Функции встроенные в интерпретатор """

    def function_print(*args):
        output_args = args[1]
        res = ""

        for i in range(len(output_args)):
            res += str(output_args[i])

        print(res)

    def function_input(*args):
        input_args = args[1][0]
        res = ""

        return input(input_args)