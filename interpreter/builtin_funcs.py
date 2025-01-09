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
        print_func = BuiltInFunction("print", self.function_print)
        self.context.symbol_table.set("print", print_func)

    """ Функции встроенные в интерпретатор """

    def function_print(*args):
        output_args = args[1]
        res = ""

        for i in range(len(output_args)):
            res += str(output_args[i])

        print(res)