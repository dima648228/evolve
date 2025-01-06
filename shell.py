
from lexer.lexer import *
from parser.parser_ import *
from interpreter.interpreter import *

class Shell:
    def __init__(self) -> None:
        pass

    def runProgram(self, fn,code):
        
        def register_builtins(symboltable):
        
            def write_func(args):
                print(" ".join(str(arg.value) for arg in args))
                return Number(0)

            import math
            
            def sin_func(args):
                if isinstance(args[0], Number):  # Проверяем, является ли аргумент объектом Number
                    args_ = args[0].value
                else:
                    args_ = args[0]  # Если это уже число (например, float), то просто используем его

                return Number(math.sin(args_))

            def cos_func(args):
                if isinstance(args[0], Number):
                    args_ = args[0].value
                else:
                    args_ = args[0]
                return Number(math.cos(args_))

            def tan_func(args):
                if isinstance(args[0], Number):
                    args_ = args[0].value
                else:
                    args_ = args[0]
                return Number(math.tan(args_))

            def ctg_func(args):
                if isinstance(args[0], Number):
                    args_ = args[0].value
                else:
                    args_ = args[0]
                return Number(1 / math.tan(args_))

            def to_rad_func(args):
                if isinstance(args[0], Number):
                    args_ = args[0].value
                else:
                    args_ = args[0]
                return Number(math.radians(args_))
            
            def to_deg_func(args):
                if isinstance(args[0], Number):
                    args_ = args[0].value
                else:
                    args_ = args[0]
                return Number(math.degrees(args_))
            
            def sqrt_func(args):
                if isinstance(args[0], Number):
                    args_ = args[0].value
                else:
                    args_ = args[0]

                return Number(math.sqrt(args_))
            
            def pow_func(args):
                if not isinstance(args,list): return

                x = args[0].value
                y = 2

                return Number(x**y)

            symboltable.set("write", BuiltInFunction("write", write_func))
            symboltable.set("sin", sin_func)
            symboltable.set("cos", cos_func)
            symboltable.set("tan", tan_func)
            symboltable.set("ctg", ctg_func)
            symboltable.set("to_rad", to_rad_func)
            symboltable.set("to_deg", to_deg_func)
            symboltable.set("sqrt", sqrt_func)
            symboltable.set("pow", pow_func)

        global_symbol_table = SymbolTable()
        global_symbol_table.set("null",Number(0))

        register_builtins(global_symbol_table)

        # TOKENS GENERATION
        lexer_ = Lexer(fn,code)
        tokens, error = lexer_.make_tokens()

        if error: return None, error
        
        # AST
        parser_ = Parser(tokens)
        ast = parser_.parse()

        if ast is None or ast.error: 
            return None, ast.error if ast else "Parsing failed: AST is None"

        #print(ast.node)

        # Run Program
        interpreter = Interpreter()
        context = Context('<program>')
        context.symbol_table = global_symbol_table
        result = interpreter.visit(ast.node,context)
        

        return result.value, result.error

    # A SIMPLE COMMAND PROCESSOR
    def processCommand(self, command):
        if command == "terminate":
            return True
        elif command.startswith("run "):
            filename = command[4:].strip()
            try:
                with open(filename, 'r') as file:
                    code = file.read()
                result, error = self.runProgram(filename, code)

                if error: 
                    print(error.as_str())
            except FileNotFoundError:
                print(f"File '{filename}' not found.")
        else:
            result, error = self.runProgram("<stdin>",command)

            if error: print(error.as_str())
            print(result)
        
        return False
            

    def run(self):
        while True:
            command = input("evolve > ")

            result = self.processCommand(command)

            if result == True:
                break

