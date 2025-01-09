
from lexer.lexer import *
from parser.parser_ import *
from interpreter.interpreter import *
from interpreter.builtin_funcs import *

class Shell:
    def __init__(self) -> None:
        pass

    def runProgram(self, fn,code):

        # СОЗДАНИЕ ТОКЕНОВ
        lexer_ = Lexer(fn,code)
        tokens, error = lexer_.make_tokens()

        if error: return None, error

        # СОЗДАНИЕ КОНТЕКСТА А ТАК ЖЕ ТАБИЛЦЫ СИМВОЛОВ ДЛЯ ИНТЕРПРЕТАТОРА
        global_context = Context(display_name="global")
        global_context.symbol_table = SymbolTable()
        
        # СОЗДАНИЕ СИНТАКСИЧЕСКОГО ДЕРЕВА
        parser_ = Parser(tokens)
        ast = parser_.parse()
        
        #print(ast.node)

        if ast.error: 
            print(ast.error.as_str()) 
            return None, None

        # ИНИЦИАЛИЗАЦИЯ ИНТЕРПРЕТАТОРА И ВЫПОЛНЕНИЕ КОДА
        interpreter = Interpreter()
        importer = BuiltInFuncImporter(context=global_context)

        importer.import_built_in_functions()
        result = interpreter.visit(ast.node,context=global_context)

        return ast, error

    # ПРОСТОЙ ОБРАБОТЧИК КОММАНД
    def processCommand(self, command):
        if command == "terminate":
            return True
        elif command.startswith("run "):
            filename = command[4:].strip()
            try:
                with open(filename, 'r') as file:
                    code = file.read()
                result, error = self.runProgram(filename, code)

                #print(result.value)

                if error: 
                    print(error.as_str())
            except FileNotFoundError:
                print(f"File '{filename}' not found.")
        else:
            result, error = self.runProgram("<stdin>",command)

            if error: print(error.as_str())
        
        return False
            

    def run(self):
        while True:
            command = input("evolve > ")

            result = self.processCommand(command)

            if result == True:
                break

